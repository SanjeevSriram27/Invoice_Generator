"""
Business logic for processing bulk CSV uploads with async support
"""
import csv
import io
import asyncio
import time
from decimal import Decimal
from datetime import date
from typing import Dict, List, Any, Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice, InvoiceItem
from app.models.invoice_sequence import InvoiceNumberSequence
from app.services.pdf_service import PDFService
from app.services.email_service import EmailService
from app.services.whatsapp_service import WhatsAppService
from app.config import settings
from app.core.validators import validate_and_format_phone


class BulkUploadService:
    """
    Handles bulk invoice creation from CSV with async support

    Features:
    - Async CSV processing
    - Savepoint transactions for partial success
    - Optional email/WhatsApp sending
    - PDF generation
    """

    def __init__(
        self,
        db: AsyncSession,
        csv_file: UploadFile,
        user_id: str,
        invoice_type: str,
        create_as_draft: bool = False,
        send_email: bool = False,
        send_whatsapp: bool = False,
        gst_rate: float = 18.0,
        seller_details: Optional[Dict[str, Any]] = None
    ):
        self.db = db
        self.csv_file = csv_file
        self.user_id = user_id
        self.invoice_type = invoice_type
        self.create_as_draft = create_as_draft
        self.send_email = send_email
        self.send_whatsapp = send_whatsapp
        self.gst_rate = gst_rate
        self.seller_details = seller_details or {}

        self.successes = []
        self.failures = []

    async def process(self) -> Dict[str, Any]:
        """
        Main processing method with partial success support

        Returns:
            Dict with processing results including successes and failures
        """
        start_time = time.time()

        # Read CSV content
        csv_content = await self.csv_file.read()
        csv_text = csv_content.decode('utf-8-sig')  # Handle BOM
        csv_reader = csv.DictReader(io.StringIO(csv_text))

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
                await self._process_single_invoice(cleaned_row, row_number)
            except Exception as e:
                import traceback
                import logging
                logger = logging.getLogger(__name__)
                error_details = traceback.format_exc()
                logger.error(f"Row {row_number} failed for {cleaned_row.get('receiver_name', 'Unknown')}: {str(e)}")
                logger.error(f"Full traceback: {error_details}")
                logger.error(f"Row data: {cleaned_row}")
                self.failures.append({
                    'row_number': row_number,
                    'buyer_name': cleaned_row.get('receiver_name', 'Unknown'),
                    'error': str(e),
                    'details': {'data': cleaned_row}
                })

        processing_time = time.time() - start_time

        return {
            'total_rows': row_number - 1,
            'successful': len(self.successes),
            'failed': len(self.failures),
            'successes': self.successes,
            'failures': self.failures,
            'processing_time_seconds': round(processing_time, 2)
        }

    async def _process_single_invoice(self, row_data: Dict[str, str], row_number: int):
        """
        Process a single invoice with savepoint for isolation

        CRITICAL: Uses begin_nested() for savepoint transaction.
        If this invoice fails, it won't affect other invoices.
        """
        # Validate row data
        validated_row = self._validate_row(row_data)

        # Use savepoint for transaction isolation
        async with self.db.begin_nested():  # Creates SAVEPOINT
            try:
                # Create invoice
                invoice = await self._create_invoice(validated_row)

                # Always generate PDF (drafts need PDFs for review)
                pdf_url = None
                try:
                    pdf_service = PDFService()
                    await pdf_service.generate_pdf(invoice)
                    pdf_url = invoice.pdf_url
                except Exception as pdf_error:
                    # Log but don't fail invoice creation
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"PDF generation failed for row {row_number}: {pdf_error}")

                # Savepoint auto-committed on context exit

                # Prepare success result
                result = {
                    'row_number': row_number,
                    'invoice_id': invoice.id,
                    'invoice_number': invoice.invoice_number,
                    'buyer_name': invoice.buyer_name,
                    'total': str(invoice.total),
                    'pdf_url': pdf_url,
                    'is_draft': invoice.is_draft,
                    'email_sent': False,
                    'whatsapp_sent': False,
                    'email_error': None,
                    'whatsapp_error': None
                }

                # Send email if enabled and email exists
                if self.send_email and invoice.buyer_email:
                    email_result = await self._send_email(invoice)
                    result['email_sent'] = email_result.get('success', False)
                    result['email_error'] = email_result.get('error')

                # Send WhatsApp if enabled and phone exists
                if self.send_whatsapp and invoice.buyer_phone:
                    whatsapp_result = await self._send_whatsapp(invoice)
                    result['whatsapp_sent'] = whatsapp_result.get('success', False)
                    result['whatsapp_error'] = whatsapp_result.get('error')

                self.successes.append(result)

            except Exception as e:
                # Savepoint auto-rolled back on exception
                # Other rows unaffected
                raise

    def _validate_row(self, row_data: Dict[str, str]) -> Dict[str, Any]:
        """Validate and parse CSV row data"""
        # Validate required fields
        required_fields = ['receiver_name', 'receiver_address', 'pincode']
        for field in required_fields:
            if not row_data.get(field):
                raise ValueError(f"Missing required field: {field}")

        # Parse pipe-separated or comma-separated fields
        # Try pipe first, fall back to comma if no pipes found
        separator = '|' if '|' in row_data['product_descriptions'] else ','
        descriptions = [d.strip() for d in row_data['product_descriptions'].split(separator) if d.strip()]
        hsn_codes = [h.strip() for h in row_data['hsn_sac_codes'].split(separator) if h.strip()]
        quantities_str = [q.strip() for q in row_data['quantities'].split(separator) if q.strip()]
        values_str = [v.strip() for v in row_data['total_values'].split(separator) if v.strip()]

        # Validate arrays have same length
        if not (len(descriptions) == len(hsn_codes) == len(quantities_str) == len(values_str)):
            raise ValueError("Product descriptions, HSN codes, quantities, and values must have same number of items")

        if len(descriptions) == 0:
            raise ValueError("At least one product is required")

        # Convert to proper types
        try:
            quantities = []
            for q in quantities_str:
                # Remove any non-numeric characters except decimal point
                clean_q = ''.join(c for c in q if c.isdigit() or c == '.')
                if clean_q:
                    quantities.append(Decimal(clean_q))
                else:
                    raise ValueError(f"Empty or invalid quantity: '{q}'")

            total_values = []
            for v in values_str:
                # Remove any non-numeric characters except decimal point
                clean_v = ''.join(c for c in v if c.isdigit() or c == '.')
                if clean_v:
                    total_values.append(Decimal(clean_v))
                else:
                    raise ValueError(f"Empty or invalid value: '{v}'")
        except Exception as e:
            raise ValueError(f"Invalid number format in quantities={quantities_str} or values={values_str}: {str(e)}")

        # Validate phone if provided
        phone = row_data.get('phone', '').strip()
        if phone:
            # Handle scientific notation (Excel exports phone numbers as 9.19877E+11)
            try:
                # Try to convert from scientific notation
                if 'E' in phone.upper() or 'e' in phone:
                    phone = str(int(float(phone)))
            except:
                pass  # Keep original if conversion fails

            is_valid, formatted_phone, error = validate_and_format_phone(phone)
            if not is_valid:
                raise ValueError(f"Invalid phone number: {error}")
            row_data['phone'] = formatted_phone

        return {
            'receiver_name': row_data['receiver_name'],
            'receiver_address': row_data['receiver_address'],
            'pincode': row_data['pincode'],
            'phone': row_data.get('phone', ''),
            'email': row_data.get('email', ''),
            'gstin': row_data.get('gstin', ''),
            'descriptions': descriptions,
            'hsn_codes': hsn_codes,
            'quantities': quantities,
            'total_values': total_values,
            'notes': row_data.get('notes', ''),
            'payment_terms': row_data.get('payment_terms', '')
        }

    async def _create_invoice(self, validated_row: Dict[str, Any]) -> Invoice:
        """Create invoice from validated CSV row"""
        # Extract parsed arrays
        descriptions = validated_row['descriptions']
        hsn_codes = validated_row['hsn_codes']
        quantities = validated_row['quantities']
        total_values = validated_row['total_values']

        # Determine buyer state code from pincode
        buyer_pincode = validated_row['pincode']
        buyer_state = self._infer_state_from_pincode(buyer_pincode)

        # Prepare seller details
        if self.invoice_type == 'topmate':
            seller_name = settings.topmate_company_name
            seller_gstin = settings.topmate_gstin
            seller_address = settings.topmate_address
            seller_pincode = settings.topmate_pincode
            seller_state = settings.topmate_state_code
            seller_phone = settings.topmate_phone
            seller_email = settings.topmate_email
            seller_logo = None  # TODO: Handle logo
            seller_website = settings.topmate_website
        else:
            seller_name = self.seller_details.get('name', '')
            seller_gstin = self.seller_details.get('gstin', '')
            seller_address = self.seller_details.get('address', '')
            seller_pincode = self.seller_details.get('pincode', '')
            seller_state = self.seller_details.get('state', '')
            seller_phone = self.seller_details.get('phone', '')
            seller_email = self.seller_details.get('email', '')
            seller_logo = self.seller_details.get('logo')
            seller_website = self.seller_details.get('website', '')

        # Generate invoice number atomically
        invoice_number = await self._generate_invoice_number()

        # Calculate financials with GST extraction
        gst_rate_percent = Decimal(str(self.gst_rate))
        gst_rate = gst_rate_percent / Decimal('100')
        gst_multiplier = Decimal('1') + gst_rate

        # Extract base prices from GST-inclusive values
        subtotal = Decimal('0.00')
        items_data = []

        for i, (desc, hsn, qty, value_with_gst) in enumerate(zip(
            descriptions, hsn_codes, quantities, total_values
        )):
            # value_with_gst is the total value for this item (GST-inclusive)
            unit_price_with_gst = value_with_gst / qty
            base_unit_price = (unit_price_with_gst / gst_multiplier).quantize(Decimal('0.01'))

            item_subtotal = (qty * base_unit_price).quantize(Decimal('0.01'))
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
            # Intrastate: CGST + SGST
            is_interstate = False
            half_rate = gst_rate / Decimal('2')
            cgst = (subtotal * half_rate).quantize(Decimal('0.01'))
            sgst = (subtotal * half_rate).quantize(Decimal('0.01'))
            igst = Decimal('0.00')
        else:
            # Interstate: IGST
            is_interstate = True
            igst = (subtotal * gst_rate).quantize(Decimal('0.01'))
            cgst = Decimal('0.00')
            sgst = Decimal('0.00')

        total = (subtotal + cgst + sgst + igst).quantize(Decimal('0.01'))

        # Create invoice
        invoice = Invoice(
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
            seller_logo=seller_logo,
            seller_website=seller_website,
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
            is_draft=self.create_as_draft,
            notes=validated_row.get('notes'),
            payment_terms=validated_row.get('payment_terms')
        )

        self.db.add(invoice)
        await self.db.flush()  # Flush to get invoice ID

        # Create items
        for item_data in items_data:
            item = InvoiceItem(invoice_id=invoice.id, **item_data)
            self.db.add(item)

        await self.db.flush()

        return invoice

    async def _generate_invoice_number(self) -> str:
        """
        Generate unique invoice number atomically

        CRITICAL: Uses same logic as InvoiceService
        """
        from sqlalchemy import select
        import hashlib

        async with self.db.begin_nested():
            # Row-level lock
            query = select(InvoiceNumberSequence).where(
                InvoiceNumberSequence.sequence_type == self.invoice_type,
            )

            if self.invoice_type == 'topmate':
                query = query.where(InvoiceNumberSequence.user_id.is_(None))
            else:
                query = query.where(InvoiceNumberSequence.user_id == self.user_id)

            query = query.with_for_update()

            result = await self.db.execute(query)
            sequence = result.scalar_one_or_none()

            if not sequence:
                sequence = InvoiceNumberSequence(
                    sequence_type=self.invoice_type,
                    user_id=None if self.invoice_type == 'topmate' else self.user_id,
                    current_number=0
                )
                self.db.add(sequence)
                await self.db.flush()

            # Atomic increment
            sequence.current_number += 1
            await self.db.flush()

            if self.invoice_type == 'topmate':
                return f"{settings.topmate_invoice_prefix}-{sequence.current_number:06d}"
            else:
                user_hash = hashlib.md5(self.user_id.encode()).hexdigest()[:6].upper()
                return f"INV-{user_hash}-{sequence.current_number:04d}"

    def _infer_state_from_pincode(self, pincode: str) -> str:
        """
        Infer state code from pincode (first digit maps to region)
        Based on Indian postal code system
        """
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

    async def _send_email(self, invoice: Invoice) -> Dict[str, Any]:
        """Send invoice PDF via email"""
        try:
            if not invoice.pdf_file:
                return {'success': False, 'error': 'PDF not generated'}

            email_service = EmailService()
            await email_service.send_invoice_email(invoice)

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _send_whatsapp(self, invoice: Invoice) -> Dict[str, Any]:
        """Send invoice via WhatsApp"""
        try:
            if not invoice.pdf_file:
                return {'success': False, 'error': 'PDF not generated'}

            whatsapp_service = WhatsAppService()
            result = await whatsapp_service.send_invoice_whatsapp(invoice)

            return result

        except Exception as e:
            return {'success': False, 'error': str(e)}
