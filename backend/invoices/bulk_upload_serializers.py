"""
Serializers for bulk invoice upload via CSV
"""
from rest_framework import serializers
from decimal import Decimal
import re


class BulkInvoiceCSVRowSerializer(serializers.Serializer):
    """Validates a single CSV row for invoice creation"""
    receiver_name = serializers.CharField(max_length=255)
    receiver_address = serializers.CharField()
    pincode = serializers.CharField(max_length=6)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    gstin = serializers.CharField(max_length=15, required=False, allow_blank=True, allow_null=True)

    # Comma-separated fields
    product_descriptions = serializers.CharField()
    hsn_sac_codes = serializers.CharField()
    quantities = serializers.CharField()
    total_values = serializers.CharField()  # GST-inclusive prices

    def validate_pincode(self, value):
        """Validate pincode format"""
        if not value or len(value) != 6 or not value.isdigit():
            raise serializers.ValidationError("Pincode must be 6 digits")
        return value

    def validate_gstin(self, value):
        """Validate GSTIN format"""
        if not value:
            return None
        if len(value) != 15:
            raise serializers.ValidationError("GSTIN must be 15 characters")

        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Invalid GSTIN format")
        return value.upper()

    def validate(self, data):
        """Cross-field validation: ensure all product arrays have same length"""
        # Parse comma-separated fields
        descriptions = [d.strip() for d in data['product_descriptions'].split(',') if d.strip()]
        hsn_codes = [h.strip() for h in data['hsn_sac_codes'].split(',') if h.strip()]
        quantities = [q.strip() for q in data['quantities'].split(',') if q.strip()]
        values = [v.strip() for v in data['total_values'].split(',') if v.strip()]

        # Validate at least one product
        if not descriptions:
            raise serializers.ValidationError("At least one product is required")

        # Validate array lengths match
        lengths = [len(descriptions), len(hsn_codes), len(quantities), len(values)]
        if len(set(lengths)) != 1:
            raise serializers.ValidationError(
                f"Product fields must have same count. Got: {lengths[0]} descriptions, "
                f"{lengths[1]} HSN codes, {lengths[2]} quantities, {lengths[3]} values"
            )

        # Validate and convert numeric fields
        try:
            quantities_decimal = [Decimal(q) for q in quantities]
            if any(q <= 0 for q in quantities_decimal):
                raise serializers.ValidationError("All quantities must be greater than 0")
        except (ValueError, Exception) as e:
            raise serializers.ValidationError(f"Invalid quantity values: {e}")

        try:
            values_decimal = [Decimal(v) for v in values]
            if any(v <= 0 for v in values_decimal):
                raise serializers.ValidationError("All values must be greater than 0")
        except (ValueError, Exception) as e:
            raise serializers.ValidationError(f"Invalid total values: {e}")

        # Store parsed arrays for downstream processing
        data['_parsed_descriptions'] = descriptions
        data['_parsed_hsn_codes'] = hsn_codes
        data['_parsed_quantities'] = quantities_decimal
        data['_parsed_values'] = values_decimal

        return data


class BulkInvoiceUploadSerializer(serializers.Serializer):
    """Main serializer for bulk invoice upload"""
    csv_file = serializers.FileField()
    invoice_type = serializers.ChoiceField(choices=['topmate', 'user'], default='user')
    user_id = serializers.CharField(max_length=100)
    create_as_draft = serializers.BooleanField(default=False)

    # Email and WhatsApp sending options
    send_email = serializers.BooleanField(default=False)
    send_whatsapp = serializers.BooleanField(default=False)

    # GST rate for all invoices in this batch
    gst_rate = serializers.DecimalField(max_digits=5, decimal_places=2, default=18.00)

    # Seller details (only for user invoices)
    seller_name = serializers.CharField(required=False, allow_blank=True)
    seller_gstin = serializers.CharField(required=False, allow_blank=True)
    seller_address = serializers.CharField(required=False, allow_blank=True)
    seller_pincode = serializers.CharField(required=False, allow_blank=True)
    seller_state = serializers.CharField(required=False, allow_blank=True)
    seller_phone = serializers.CharField(required=False, allow_blank=True)
    seller_email = serializers.EmailField(required=False, allow_blank=True)

    def validate_csv_file(self, value):
        """Validate CSV file"""
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("File must be a CSV")
        if value.size > 5 * 1024 * 1024:  # 5MB limit
            raise serializers.ValidationError("File size cannot exceed 5MB")
        return value

    def validate(self, data):
        """Validate seller details based on invoice type"""
        invoice_type = data.get('invoice_type')

        if invoice_type == 'user':
            required_fields = ['seller_name', 'seller_gstin', 'seller_address',
                             'seller_pincode', 'seller_state']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({
                        field: f"{field} is required for user invoices"
                    })

        # Validate email/WhatsApp sending with draft status
        if (data.get('send_email') or data.get('send_whatsapp')) and data.get('create_as_draft'):
            raise serializers.ValidationError(
                "Cannot send email or WhatsApp for draft invoices. "
                "Set create_as_draft=false to send invoices."
            )

        return data
