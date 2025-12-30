from rest_framework import serializers
from .models import BusinessProfile, Invoice, InvoiceItem, InvoiceNumberSequence, INDIAN_STATES
from django.conf import settings
from decimal import Decimal
from datetime import date


class BusinessProfileSerializer(serializers.ModelSerializer):
    """Serializer for user's business profile"""

    class Meta:
        model = BusinessProfile
        fields = [
            'id', 'user_id', 'business_name', 'gstin', 'address',
            'pincode', 'state', 'phone', 'email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_gstin(self, value):
        """Validate GSTIN format"""
        if not value:
            raise serializers.ValidationError("GSTIN is required")

        # GSTIN format: 2 digits state code + 10 chars PAN + 1 char entity + 1 char Z + 1 check digit
        if len(value) != 15:
            raise serializers.ValidationError("GSTIN must be 15 characters")

        import re
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Invalid GSTIN format")

        return value.upper()

    def validate_pincode(self, value):
        """Validate pincode"""
        if not value or len(value) != 6 or not value.isdigit():
            raise serializers.ValidationError("Pincode must be 6 digits")
        return value


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for invoice line items"""

    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'serial_number', 'description', 'hsn_sac',
            'quantity', 'unit_price', 'amount'
        ]
        read_only_fields = ['id', 'serial_number', 'amount']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than 0")
        return value


class InvoiceSerializer(serializers.ModelSerializer):
    """Main invoice serializer"""
    items = InvoiceItemSerializer(many=True)
    state_name = serializers.SerializerMethodField()
    buyer_state_name = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_type', 'user_id',
            'invoice_date', 'due_date',
            'seller_name', 'seller_gstin', 'seller_address', 'seller_pincode',
            'seller_state', 'state_name', 'seller_phone', 'seller_email',
            'buyer_name', 'buyer_gstin', 'buyer_address', 'buyer_pincode',
            'buyer_state', 'buyer_state_name', 'buyer_phone', 'buyer_email',
            'subtotal', 'cgst', 'sgst', 'igst', 'total', 'gst_rate',
            'is_interstate', 'notes', 'payment_terms',
            'pdf_url', 'pdf_file', 'items',
            'is_draft', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'cgst', 'sgst', 'igst', 'total',
            'is_interstate', 'pdf_url', 'pdf_file', 'created_at', 'updated_at'
        ]

    def get_state_name(self, obj):
        """Get full state name for seller"""
        states_dict = dict(INDIAN_STATES)
        return states_dict.get(obj.seller_state, obj.seller_state)

    def get_buyer_state_name(self, obj):
        """Get full state name for buyer"""
        states_dict = dict(INDIAN_STATES)
        return states_dict.get(obj.buyer_state, obj.buyer_state)

    def validate(self, data):
        """Validate invoice data"""
        # Validate seller GSTIN (always required)
        if not data.get('seller_gstin'):
            raise serializers.ValidationError({"seller_gstin": "Seller GSTIN is required"})

        # Validate items
        items_data = data.get('items', [])
        if not items_data:
            raise serializers.ValidationError({"items": "At least one item is required"})

        # Validate invoice type specific rules
        invoice_type = data.get('invoice_type')
        if invoice_type == 'topmate':
            # For Topmate invoices, seller details should match Topmate
            topmate_settings = settings.INVOICE_SETTINGS
            data['seller_name'] = topmate_settings['TOPMATE_COMPANY_NAME']
            data['seller_gstin'] = topmate_settings['TOPMATE_GSTIN']
            data['seller_address'] = topmate_settings['TOPMATE_ADDRESS']
            data['seller_pincode'] = topmate_settings['TOPMATE_PINCODE']
            data['seller_state'] = topmate_settings['TOPMATE_STATE_CODE']
            data['seller_phone'] = topmate_settings['TOPMATE_PHONE']
            data['seller_email'] = topmate_settings['TOPMATE_EMAIL']
        elif invoice_type == 'user':
            # For user invoices, seller GSTIN is mandatory
            if not data.get('seller_gstin'):
                raise serializers.ValidationError({
                    "seller_gstin": "Seller GSTIN is mandatory for user invoices"
                })

        return data

    def create(self, validated_data):
        """Create invoice with items and generate invoice number"""
        items_data = validated_data.pop('items')

        # Generate invoice number
        invoice_type = validated_data['invoice_type']
        user_id = validated_data['user_id']

        if invoice_type == 'topmate':
            # Get or create Topmate sequence
            sequence, _ = InvoiceNumberSequence.objects.get_or_create(
                sequence_type='topmate',
                user_id=None,
                defaults={'current_number': 0}
            )
            prefix = settings.INVOICE_SETTINGS['TOPMATE_INVOICE_PREFIX']
            number = sequence.get_next_number()
            invoice_number = f"{prefix}-{number:06d}"
        else:
            # Get or create user-specific sequence
            sequence, _ = InvoiceNumberSequence.objects.get_or_create(
                sequence_type='user',
                user_id=user_id,
                defaults={'current_number': 0}
            )
            # Create a hash of user_id to keep invoice number clean
            import hashlib
            user_hash = hashlib.md5(user_id.encode()).hexdigest()[:6].upper()
            number = sequence.get_next_number()
            invoice_number = f"INV-{user_hash}-{number:04d}"

        validated_data['invoice_number'] = invoice_number

        # Get GST rate first (needed for price extraction)
        gst_rate_percent = validated_data.get('gst_rate', Decimal(str(settings.INVOICE_SETTINGS['GST_RATE'])))
        gst_rate = gst_rate_percent / 100
        gst_multiplier = Decimal('1') + gst_rate

        # Calculate subtotal from items
        # NOTE: unit_price comes as GST-inclusive, so we extract the base price
        subtotal = Decimal('0.00')
        for item_data in items_data:
            qty = item_data['quantity']
            price_with_gst = item_data['unit_price']

            # Extract base price (GST-exclusive) from GST-inclusive price
            base_price = (price_with_gst / gst_multiplier).quantize(Decimal('0.01'))
            item_data['unit_price'] = base_price

            subtotal += (qty * base_price)

        validated_data['subtotal'] = subtotal

        # Pre-calculate taxes before creating invoice
        seller_state = validated_data['seller_state']
        buyer_state = validated_data['buyer_state']

        if seller_state == buyer_state:
            # Same state: CGST + SGST (split equally)
            validated_data['is_interstate'] = False
            half_rate = gst_rate / 2
            validated_data['cgst'] = (subtotal * half_rate).quantize(Decimal('0.01'))
            validated_data['sgst'] = (subtotal * half_rate).quantize(Decimal('0.01'))
            validated_data['igst'] = Decimal('0.00')
        else:
            # Different states: IGST (full rate)
            validated_data['is_interstate'] = True
            validated_data['igst'] = (subtotal * gst_rate).quantize(Decimal('0.01'))
            validated_data['cgst'] = Decimal('0.00')
            validated_data['sgst'] = Decimal('0.00')

        validated_data['total'] = (
            subtotal + validated_data['cgst'] + validated_data['sgst'] + validated_data['igst']
        ).quantize(Decimal('0.01'))

        # Create invoice with all calculated fields
        invoice = Invoice.objects.create(**validated_data)

        # Create items
        for idx, item_data in enumerate(items_data, start=1):
            item_data['serial_number'] = idx
            InvoiceItem.objects.create(invoice=invoice, **item_data)

        return invoice

    def update(self, instance, validated_data):
        """Update invoice (only if draft)"""
        if not instance.is_draft:
            raise serializers.ValidationError("Cannot update a finalized invoice")

        items_data = validated_data.pop('items', None)

        # Update invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Recalculate subtotal if items provided
        if items_data is not None:
            # Delete existing items
            instance.items.all().delete()

            # Get GST rate for price extraction
            gst_rate_percent = instance.gst_rate if instance.gst_rate else Decimal(str(settings.INVOICE_SETTINGS['GST_RATE']))
            gst_rate = gst_rate_percent / 100
            gst_multiplier = Decimal('1') + gst_rate

            # Calculate new subtotal
            # NOTE: unit_price comes as GST-inclusive, so we extract the base price
            subtotal = Decimal('0.00')
            for item_data in items_data:
                qty = item_data['quantity']
                price_with_gst = item_data['unit_price']

                # Extract base price (GST-exclusive) from GST-inclusive price
                base_price = (price_with_gst / gst_multiplier).quantize(Decimal('0.01'))
                item_data['unit_price'] = base_price

                subtotal += (qty * base_price)

            instance.subtotal = subtotal

            # Recreate items
            for idx, item_data in enumerate(items_data, start=1):
                item_data['serial_number'] = idx
                InvoiceItem.objects.create(invoice=instance, **item_data)

        # Recalculate taxes
        instance.calculate_taxes()
        instance.save()

        return instance


class InvoiceCreateSerializer(serializers.Serializer):
    """Simplified serializer for creating invoices from frontend"""
    # Invoice type
    invoice_type = serializers.ChoiceField(choices=['topmate', 'user'])
    user_id = serializers.CharField(max_length=100)

    # Dates
    invoice_date = serializers.DateField(default=date.today)
    due_date = serializers.DateField(required=False, allow_null=True)

    # Seller (only for user invoices)
    seller_name = serializers.CharField(required=False, allow_blank=True)
    seller_gstin = serializers.CharField(required=False, allow_blank=True)
    seller_address = serializers.CharField(required=False, allow_blank=True)
    seller_pincode = serializers.CharField(required=False, allow_blank=True)
    seller_state = serializers.ChoiceField(choices=INDIAN_STATES, required=False)
    seller_phone = serializers.CharField(required=False, allow_blank=True)
    seller_email = serializers.EmailField(required=False, allow_blank=True)

    # Buyer
    buyer_name = serializers.CharField(max_length=255)
    buyer_gstin = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    buyer_address = serializers.CharField()
    buyer_pincode = serializers.CharField(max_length=6)
    buyer_state = serializers.ChoiceField(choices=INDIAN_STATES)
    buyer_phone = serializers.CharField(required=False, allow_blank=True)
    buyer_email = serializers.EmailField(required=False, allow_blank=True)

    # Items
    items = InvoiceItemSerializer(many=True)

    # GST Rate (optional, defaults to 18%)
    gst_rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, default=18.00)

    # Additional
    notes = serializers.CharField(required=False, allow_blank=True)
    payment_terms = serializers.CharField(required=False, allow_blank=True)
    is_draft = serializers.BooleanField(default=False)

    def validate(self, data):
        invoice_type = data.get('invoice_type')

        if invoice_type == 'topmate':
            # For Topmate invoices, auto-fill seller details
            topmate_settings = settings.INVOICE_SETTINGS
            data['seller_name'] = topmate_settings['TOPMATE_COMPANY_NAME']
            data['seller_gstin'] = topmate_settings['TOPMATE_GSTIN']
            data['seller_address'] = topmate_settings['TOPMATE_ADDRESS']
            data['seller_pincode'] = topmate_settings['TOPMATE_PINCODE']
            data['seller_state'] = 'KA'  # Karnataka
            data['seller_phone'] = topmate_settings.get('TOPMATE_PHONE', '')
            data['seller_email'] = topmate_settings.get('TOPMATE_EMAIL', '')
        elif invoice_type == 'user':
            # For user invoices, seller details are required
            required_fields = ['seller_name', 'seller_gstin', 'seller_address',
                             'seller_pincode', 'seller_state']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({
                        field: f"{field} is required for user invoices"
                    })

        return data

    def create(self, validated_data):
        """Create invoice directly"""
        # Use InvoiceSerializer's create method directly
        invoice_serializer = InvoiceSerializer()
        return invoice_serializer.create(validated_data)


class InvoiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing invoices"""
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_type', 'buyer_name',
            'total', 'invoice_date', 'is_draft', 'created_at', 'item_count'
        ]

    def get_item_count(self, obj):
        return obj.items.count()
