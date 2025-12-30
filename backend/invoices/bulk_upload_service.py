"""
Business logic for processing bulk CSV uploads
"""
import csv
import io
from decimal import Decimal
from datetime import date
from django.db import transaction
from django.conf import settings
from .models import Invoice, InvoiceItem, InvoiceNumberSequence
from .services import generate_invoice_pdf
from .bulk_upload_serializers import BulkInvoiceCSVRowSerializer


class BulkInvoiceProcessor:
    """Handles bulk invoice creation from CSV"""

    def __init__(self, csv_file, user_id, invoice_type, seller_details, create_as_draft=False,
                 send_email=False, send_whatsapp=False, gst_rate=18.00, request=None):
        self.csv_file = csv_file
        self.user_id = user_id
        self.invoice_type = invoice_type
        self.seller_details = seller_details
        self.create_as_draft = create_as_draft
        self.send_email = send_email
        self.send_whatsapp = send_whatsapp
        self.gst_rate = gst_rate
        self.request = request

        self.successes = []
        self.failures = []

    def process(self):
        """Main processing method with partial success support"""
        # Read and parse CSV
        csv_content = self.csv_file.read().decode('utf-8-sig')  # Handle BOM
        csv_reader = csv.DictReader(io.StringIO(csv_content))

        # Validate CSV headers
        expected_headers = {
            'receiver_name', 'receiver_address', 'pincode', 'phone',
            'email', 'gstin', 'product_descriptions', 'hsn_sac_codes',
            'quantities', 'total_values'
        }

        actual_headers = set(h.strip().lower() for h in csv_reader.fieldnames or [])
        missing_headers = expected_headers - actual_headers

        if missing_headers:
            raise ValueError(f"Missing CSV columns: {', '.join(missing_headers)}")

        # Process each row
        row_number = 1
        for row in csv_reader:
            row_number += 1

            # Clean row data (strip whitespace from keys and values)
            cleaned_row = {k.strip().lower(): v.strip() for k, v in row.items()}

            try:
                self._process_single_invoice(cleaned_row, row_number)
            except Exception as e:
                self.failures.append({
                    'row': row_number,
                    'data': cleaned_row,
                    'errors': str(e)
                })

        return {
            'total_rows': row_number - 1,
            'successful': len(self.successes),
            'failed': len(self.failures),
            'successes': self.successes,
            'failures': self.failures
        }

    def _process_single_invoice(self, row_data, row_number):
        """Process a single invoice with savepoint for isolation"""
        # Validate row
        row_serializer = BulkInvoiceCSVRowSerializer(data=row_data)
        if not row_serializer.is_valid():
            raise ValueError(f"Validation errors: {row_serializer.errors}")

        validated_row = row_serializer.validated_data

        # Use savepoint for transaction isolation
        with transaction.atomic():
            sid = transaction.savepoint()

            try:
                invoice = self._create_invoice(validated_row)

                # Generate PDF if not draft
                pdf_url = None
                if not self.create_as_draft:
                    try:
                        generate_invoice_pdf(invoice)
                        pdf_url = invoice.pdf_file.url if invoice.pdf_file else None
                    except Exception as pdf_error:
                        # Log but don't fail invoice creation
                        print(f"PDF generation failed for row {row_number}: {pdf_error}")

                transaction.savepoint_commit(sid)

                # Prepare success result
                result = {
                    'row': row_number,
                    'invoice_number': invoice.invoice_number,
                    'invoice_id': invoice.id,
                    'buyer_name': invoice.buyer_name,
                    'total': float(invoice.total),
                    'pdf_url': pdf_url,
                    'is_draft': invoice.is_draft,
                    'email_sent': False,
                    'whatsapp_sent': False,
                    'email_error': None,
                    'whatsapp_error': None
                }

                # Send email if enabled and email exists
                if self.send_email and invoice.buyer_email:
                    email_result = self._send_email(invoice)
                    result['email_sent'] = email_result['success']
                    result['email_error'] = email_result.get('error')

                # Send WhatsApp if enabled and phone exists
                if self.send_whatsapp and invoice.buyer_phone:
                    whatsapp_result = self._send_whatsapp(invoice)
                    result['whatsapp_sent'] = whatsapp_result['success']
                    result['whatsapp_error'] = whatsapp_result.get('error')

                self.successes.append(result)

            except Exception as e:
                transaction.savepoint_rollback(sid)
                raise

    def _create_invoice(self, validated_row):
        """Create invoice from validated CSV row"""
        # Extract parsed product arrays
        descriptions = validated_row['_parsed_descriptions']
        hsn_codes = validated_row['_parsed_hsn_codes']
        quantities = validated_row['_parsed_quantities']
        total_values = validated_row['_parsed_values']

        # Determine buyer state code from pincode
        buyer_pincode = validated_row['pincode']
        buyer_state = self._infer_state_from_pincode(buyer_pincode)

        # Prepare seller details
        if self.invoice_type == 'topmate':
            topmate_settings = settings.INVOICE_SETTINGS
            seller_name = topmate_settings['TOPMATE_COMPANY_NAME']
            seller_gstin = topmate_settings['TOPMATE_GSTIN']
            seller_address = topmate_settings['TOPMATE_ADDRESS']
            seller_pincode = topmate_settings['TOPMATE_PINCODE']
            seller_state = topmate_settings['TOPMATE_STATE_CODE']
            seller_phone = topmate_settings.get('TOPMATE_PHONE', '')
            seller_email = topmate_settings.get('TOPMATE_EMAIL', '')
        else:
            seller_name = self.seller_details['seller_name']
            seller_gstin = self.seller_details['seller_gstin']
            seller_address = self.seller_details['seller_address']
            seller_pincode = self.seller_details['seller_pincode']
            seller_state = self.seller_details['seller_state']
            seller_phone = self.seller_details.get('seller_phone', '')
            seller_email = self.seller_details.get('seller_email', '')

        # Generate invoice number
        invoice_number = self._generate_invoice_number()

        # Calculate financials with GST extraction
        gst_rate_percent = Decimal(str(self.gst_rate))
        gst_rate = gst_rate_percent / 100
        gst_multiplier = Decimal('1') + gst_rate

        # Extract base prices from GST-inclusive values
        subtotal = Decimal('0.00')
        items_data = []

        for i, (desc, hsn, qty, value_with_gst) in enumerate(zip(
            descriptions, hsn_codes, quantities, total_values
        )):
            # value_with_gst is the total value for this item (GST-inclusive)
            # Need to extract unit price
            unit_price_with_gst = value_with_gst / qty
            base_unit_price = (unit_price_with_gst / gst_multiplier).quantize(Decimal('0.01'))

            item_subtotal = qty * base_unit_price
            subtotal += item_subtotal

            items_data.append({
                'serial_number': i + 1,
                'description': desc,
                'hsn_sac': hsn,
                'quantity': qty,
                'unit_price': base_unit_price,
                'amount': item_subtotal
            })

        # Calculate taxes based on state
        if seller_state == buyer_state:
            is_interstate = False
            half_rate = gst_rate / 2
            cgst = (subtotal * half_rate).quantize(Decimal('0.01'))
            sgst = (subtotal * half_rate).quantize(Decimal('0.01'))
            igst = Decimal('0.00')
        else:
            is_interstate = True
            igst = (subtotal * gst_rate).quantize(Decimal('0.01'))
            cgst = Decimal('0.00')
            sgst = Decimal('0.00')

        total = (subtotal + cgst + sgst + igst).quantize(Decimal('0.01'))

        # Create invoice
        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            invoice_type=self.invoice_type,
            user_id=self.user_id,
            invoice_date=date.today(),
            seller_name=seller_name,
            seller_gstin=seller_gstin,
            seller_address=seller_address,
            seller_pincode=seller_pincode,
            seller_state=seller_state,
            seller_phone=seller_phone,
            seller_email=seller_email,
            buyer_name=validated_row['receiver_name'],
            buyer_gstin=validated_row.get('gstin'),
            buyer_address=validated_row['receiver_address'],
            buyer_pincode=buyer_pincode,
            buyer_state=buyer_state,
            buyer_phone=validated_row.get('phone', ''),
            buyer_email=validated_row.get('email', ''),
            subtotal=subtotal,
            cgst=cgst,
            sgst=sgst,
            igst=igst,
            total=total,
            gst_rate=gst_rate_percent,
            is_interstate=is_interstate,
            is_draft=self.create_as_draft
        )

        # Create items
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)

        return invoice

    def _generate_invoice_number(self):
        """Generate unique invoice number atomically"""
        if self.invoice_type == 'topmate':
            sequence, _ = InvoiceNumberSequence.objects.get_or_create(
                sequence_type='topmate',
                user_id=None,
                defaults={'current_number': 0}
            )
            prefix = settings.INVOICE_SETTINGS['TOPMATE_INVOICE_PREFIX']
            number = sequence.get_next_number()
            return f"{prefix}-{number:06d}"
        else:
            sequence, _ = InvoiceNumberSequence.objects.get_or_create(
                sequence_type='user',
                user_id=self.user_id,
                defaults={'current_number': 0}
            )
            import hashlib
            user_hash = hashlib.md5(self.user_id.encode()).hexdigest()[:6].upper()
            number = sequence.get_next_number()
            return f"INV-{user_hash}-{number:04d}"

    def _infer_state_from_pincode(self, pincode):
        """Infer state code from pincode (first 2 digits map to state)"""
        # Simplified mapping - first digit indicates region
        # Based on Indian postal code system
        pincode_state_map = {
            '1': 'DL',  # Delhi
            '2': 'HR',  # Haryana
            '3': 'PB',  # Punjab/HP
            '4': 'RJ',  # Rajasthan
            '5': 'UP',  # Uttar Pradesh
            '6': 'TN',  # Tamil Nadu
            '7': 'AP',  # Andhra Pradesh
            '8': 'KA',  # Karnataka
            '9': 'GJ',  # Gujarat
        }

        first_digit = pincode[0] if pincode else '0'
        return pincode_state_map.get(first_digit, 'KA')  # Default to Karnataka

    def _send_email(self, invoice):
        """Send invoice PDF via email"""
        try:
            from django.core.mail import EmailMessage

            # Ensure PDF exists
            if not invoice.pdf_file:
                return {'success': False, 'error': 'PDF not generated'}

            subject = f'Invoice {invoice.invoice_number} - Rs.{invoice.total}'
            body = f"""Dear {invoice.buyer_name},

Please find attached your invoice {invoice.invoice_number}.

Invoice Details:
- Invoice Number: {invoice.invoice_number}
- Date: {invoice.invoice_date.strftime('%d/%m/%Y')}
- Total Amount: Rs.{invoice.total}

Thank you for your business!

Best regards,
{invoice.seller_name}"""

            email_message = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@invoice.com',
                to=[invoice.buyer_email],
            )

            # Attach PDF
            invoice.pdf_file.open('rb')
            email_message.attach(
                f'{invoice.invoice_number}.pdf',
                invoice.pdf_file.read(),
                'application/pdf'
            )
            invoice.pdf_file.close()

            email_message.send(fail_silently=False)

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _send_whatsapp(self, invoice):
        """Send invoice PDF via WhatsApp"""
        try:
            # Ensure PDF exists
            if not invoice.pdf_file:
                return {'success': False, 'error': 'PDF not generated'}

            # Check if Twilio is configured
            if not hasattr(settings, 'TWILIO_ACCOUNT_SID') or not settings.TWILIO_ACCOUNT_SID:
                # Fallback: return WhatsApp link (not actually sending)
                if self.request:
                    pdf_url = self.request.build_absolute_uri(invoice.pdf_file.url)
                    message = f"""Hello {invoice.buyer_name},

Here is your invoice:

*Invoice #{invoice.invoice_number}*
Date: {invoice.invoice_date.strftime('%d/%m/%Y')}
Amount: ₹{invoice.total}

Download PDF: {pdf_url}

Thank you for your business!
- {invoice.seller_name}"""

                    import urllib.parse
                    encoded_message = urllib.parse.quote(message)
                    whatsapp_link = f"https://wa.me/{invoice.buyer_phone}?text={encoded_message}"

                    return {
                        'success': False,
                        'error': 'Twilio not configured. WhatsApp link generated instead.',
                        'whatsapp_link': whatsapp_link
                    }
                else:
                    return {'success': False, 'error': 'Twilio not configured and no request context'}

            # Send via Twilio WhatsApp API
            from twilio.rest import Client

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            # Get the full public URL to the PDF file
            if self.request:
                pdf_url = self.request.build_absolute_uri(invoice.pdf_file.url)
            else:
                pdf_url = invoice.pdf_file.url

            # Format phone number for WhatsApp
            phone = invoice.buyer_phone.strip()
            if not phone.startswith('+'):
                phone = '+' + phone
            to_whatsapp = f"whatsapp:{phone}"

            # Create message body
            message_body = f"""Hello {invoice.buyer_name},

Your invoice is ready!

Invoice #: {invoice.invoice_number}
Date: {invoice.invoice_date.strftime('%d/%m/%Y')}
Amount: ₹{invoice.total}

Thank you for your business!
- {invoice.seller_name}"""

            # Send WhatsApp message with PDF attachment
            message = client.messages.create(
                from_=settings.TWILIO_WHATSAPP_FROM,
                body=message_body,
                to=to_whatsapp,
                media_url=[pdf_url]
            )

            return {'success': True, 'message_sid': message.sid}

        except Exception as e:
            return {'success': False, 'error': str(e)}
