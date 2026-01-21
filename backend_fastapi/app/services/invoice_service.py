"""
Invoice Service - Core business logic for invoice operations
Handles atomic invoice numbering, GST calculations, CRUD operations
"""
import hashlib
import base64
import os
from decimal import Decimal
from typing import Optional, List, Dict, Any
from datetime import date
from pathlib import Path

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Invoice, InvoiceItem, InvoiceNumberSequence
from app.config import settings
from app.core.exceptions import (
    InvoiceNotFoundException,
    InvoiceNotDraftException,
    InvalidInvoiceDataException
)


class InvoiceService:
    """
    Service for invoice operations
    Handles invoice creation, updates, GST calculations, and atomic numbering
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    def _save_base64_image(self, base64_data: str, prefix: str = "logo") -> Optional[str]:
        """
        Convert base64 image to file and save it

        Args:
            base64_data: Base64 encoded image (with or without data URL prefix)
            prefix: Filename prefix

        Returns:
            str: Relative path to saved image or None
        """
        if not base64_data or not base64_data.strip():
            return None

        try:
            # Check if it's a data URL (data:image/png;base64,...)
            if base64_data.startswith('data:image'):
                # Extract base64 part
                base64_data = base64_data.split(',', 1)[1]

            # Decode base64
            image_data = base64.b64decode(base64_data)

            # Generate unique filename
            file_hash = hashlib.md5(image_data).hexdigest()[:12]
            filename = f"{prefix}_{file_hash}.png"

            # Create logos directory
            logos_dir = Path(settings.media_root) / "logos"
            logos_dir.mkdir(parents=True, exist_ok=True)

            # Save file
            file_path = logos_dir / filename
            with open(file_path, 'wb') as f:
                f.write(image_data)

            # Return relative path
            return f"logos/{filename}"

        except Exception as e:
            print(f"Error saving base64 image: {e}")
            return None

    async def _generate_invoice_number(
        self,
        invoice_type: str,
        user_id: str
    ) -> str:
        """
        Atomically generate next invoice number
        CRITICAL: Uses row-level locking to prevent duplicate numbers

        Args:
            invoice_type: 'topmate' or 'user'
            user_id: User ID for user-specific sequences

        Returns:
            str: Generated invoice number (e.g., 'TM-INV-000001' or 'INV-ABC123-0001')
        """
        async with self.db.begin_nested():  # Savepoint for isolation
            # Row-level lock (SELECT FOR UPDATE) - prevents concurrent duplicates
            query = select(InvoiceNumberSequence).where(
                InvoiceNumberSequence.sequence_type == invoice_type,
            )

            if invoice_type == 'topmate':
                # Global Topmate sequence (user_id is NULL)
                query = query.where(InvoiceNumberSequence.user_id.is_(None))
            else:
                # User-specific sequence
                query = query.where(InvoiceNumberSequence.user_id == user_id)

            # CRITICAL: with_for_update() locks the row until transaction commits
            query = query.with_for_update()

            result = await self.db.execute(query)
            sequence = result.scalar_one_or_none()

            if not sequence:
                # Create new sequence
                sequence = InvoiceNumberSequence(
                    sequence_type=invoice_type,
                    user_id=None if invoice_type == 'topmate' else user_id,
                    current_number=0
                )
                self.db.add(sequence)
                await self.db.flush()

            # Atomic increment
            sequence.current_number += 1
            await self.db.flush()

            # Generate invoice number
            if invoice_type == 'topmate':
                return f"{settings.topmate_invoice_prefix}-{sequence.current_number:06d}"
            else:
                # User invoice: INV-{6-char-hash}-{4-digit-number}
                user_hash = hashlib.md5(user_id.encode()).hexdigest()[:6].upper()
                return f"INV-{user_hash}-{sequence.current_number:04d}"

    def _extract_base_price_from_gst_inclusive(
        self,
        price_with_gst: Decimal,
        gst_rate_percent: Decimal
    ) -> Decimal:
        """
        Extract base price from GST-inclusive price

        Formula:
            base_price = price_with_gst / (1 + gst_rate)

        Example:
            price_with_gst = ₹11,800, gst_rate = 18%
            gst_multiplier = 1.18
            base_price = 11,800 / 1.18 = ₹10,000

        Args:
            price_with_gst: Price including GST
            gst_rate_percent: GST rate as percentage (e.g., 18.00)

        Returns:
            Decimal: Base price without GST
        """
        gst_rate = gst_rate_percent / Decimal('100')  # Convert to decimal (0.18)
        gst_multiplier = Decimal('1') + gst_rate  # 1.18
        base_price = (price_with_gst / gst_multiplier).quantize(Decimal('0.01'))
        return base_price

    def _calculate_taxes(
        self,
        subtotal: Decimal,
        gst_rate_percent: Decimal,
        seller_state: str,
        buyer_state: str
    ) -> Dict[str, Any]:
        """
        Calculate GST based on seller and buyer states

        Business Rules:
        - Intrastate (same state): CGST + SGST (split equally)
        - Interstate (different states): IGST (full rate)

        Args:
            subtotal: Taxable amount
            gst_rate_percent: GST rate as percentage (e.g., 18.00)
            seller_state: Seller state code (e.g., 'KA')
            buyer_state: Buyer state code (e.g., 'DL')

        Returns:
            Dict with cgst, sgst, igst, total, is_interstate
        """
        gst_rate = gst_rate_percent / Decimal('100')

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

        total = subtotal + cgst + sgst + igst

        return {
            'cgst': cgst,
            'sgst': sgst,
            'igst': igst,
            'total': total,
            'is_interstate': is_interstate
        }

    async def create_invoice(self, invoice_data: Dict[str, Any]) -> Invoice:
        """
        Create new invoice with all business logic

        Steps:
        1. Generate unique invoice number (atomic)
        2. Extract base prices from GST-inclusive prices
        3. Calculate subtotal
        4. Calculate taxes (CGST+SGST or IGST)
        5. Create invoice and items
        6. Generate PDF if not draft

        Args:
            invoice_data: Dict with invoice details

        Returns:
            Invoice: Created invoice instance
        """
        # Generate unique invoice number
        invoice_number = await self._generate_invoice_number(
            invoice_data['invoice_type'],
            invoice_data['user_id']
        )

        # Process items: extract base price from GST-inclusive unit_price
        gst_rate_percent = Decimal(str(invoice_data.get('gst_rate', 18.0)))
        items_data = invoice_data['items']
        processed_items = []
        subtotal = Decimal('0.00')

        for idx, item_data in enumerate(items_data):
            # Unit price from frontend is GST-inclusive
            unit_price_with_gst = Decimal(str(item_data['unit_price']))
            quantity = Decimal(str(item_data['quantity']))

            # Extract base unit price
            base_unit_price = self._extract_base_price_from_gst_inclusive(
                unit_price_with_gst,
                gst_rate_percent
            )

            # Calculate amount
            amount = (quantity * base_unit_price).quantize(Decimal('0.01'))
            subtotal += amount

            processed_items.append({
                'serial_number': idx + 1,
                'description': item_data['description'],
                'hsn_sac': item_data['hsn_sac'],
                'quantity': quantity,
                'unit_price': base_unit_price,  # Store base price
                'amount': amount
            })

        # Auto-fill seller details for Topmate invoices
        if invoice_data['invoice_type'] == 'topmate':
            from app.config import settings
            seller_name = settings.topmate_company_name
            seller_gstin = settings.topmate_gstin
            seller_address = settings.topmate_address
            seller_pincode = settings.topmate_pincode
            seller_state = settings.topmate_state_code
            seller_phone = settings.topmate_phone
            seller_email = settings.topmate_email
            seller_website = settings.topmate_website
            seller_logo = None
            # Bank details (not used for Topmate invoices)
            seller_bank_name = None
            seller_account_number = None
            seller_ifsc_code = None
            seller_account_holder_name = None
            seller_branch = None
        else:
            # User invoice - use provided seller details
            seller_name = invoice_data['seller_name']
            seller_gstin = invoice_data['seller_gstin']
            seller_address = invoice_data['seller_address']
            seller_pincode = invoice_data['seller_pincode']
            seller_state = invoice_data['seller_state']
            seller_phone = invoice_data.get('seller_phone')
            seller_email = invoice_data.get('seller_email')
            seller_website = invoice_data.get('seller_website')
            # Convert base64 logo to file
            seller_logo_base64 = invoice_data.get('seller_logo')
            seller_logo = self._save_base64_image(seller_logo_base64, 'seller_logo') if seller_logo_base64 else None
            # Bank details
            seller_bank_name = invoice_data.get('seller_bank_name')
            seller_account_number = invoice_data.get('seller_account_number')
            seller_ifsc_code = invoice_data.get('seller_ifsc_code')
            seller_account_holder_name = invoice_data.get('seller_account_holder_name')
            seller_branch = invoice_data.get('seller_branch')

        # Convert buyer logo if provided
        buyer_logo_base64 = invoice_data.get('buyer_logo')
        buyer_logo = self._save_base64_image(buyer_logo_base64, 'buyer_logo') if buyer_logo_base64 else None

        # Calculate taxes
        tax_result = self._calculate_taxes(
            subtotal,
            gst_rate_percent,
            seller_state,
            invoice_data['buyer_state']
        )

        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            invoice_type=invoice_data['invoice_type'],
            user_id=invoice_data['user_id'],
            invoice_date=invoice_data['invoice_date'],
            due_date=invoice_data.get('due_date'),
            # Seller (auto-filled for Topmate, provided for user)
            seller_name=seller_name,
            seller_gstin=seller_gstin,
            seller_address=seller_address,
            seller_pincode=seller_pincode,
            seller_state=seller_state,
            seller_phone=seller_phone,
            seller_email=seller_email,
            seller_logo=seller_logo,
            seller_website=seller_website,
            # Seller bank details
            seller_bank_name=seller_bank_name,
            seller_account_number=seller_account_number,
            seller_ifsc_code=seller_ifsc_code,
            seller_account_holder_name=seller_account_holder_name,
            seller_branch=seller_branch,
            # Buyer
            buyer_name=invoice_data['buyer_name'],
            buyer_gstin=invoice_data.get('buyer_gstin'),
            buyer_address=invoice_data['buyer_address'],
            buyer_pincode=invoice_data['buyer_pincode'],
            buyer_state=invoice_data['buyer_state'],
            buyer_phone=invoice_data.get('buyer_phone'),
            buyer_email=invoice_data.get('buyer_email'),
            buyer_logo=buyer_logo,
            # Financial
            subtotal=subtotal,
            cgst=tax_result['cgst'],
            sgst=tax_result['sgst'],
            igst=tax_result['igst'],
            total=tax_result['total'],
            is_interstate=tax_result['is_interstate'],
            gst_rate=gst_rate_percent,
            # Additional
            notes=invoice_data.get('notes'),
            payment_terms=invoice_data.get('payment_terms'),
            is_draft=invoice_data.get('is_draft', False)
        )

        self.db.add(invoice)
        await self.db.flush()  # Get invoice.id

        # Create items
        for item_data in processed_items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                **item_data
            )
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def get_invoice(self, invoice_id: int) -> Optional[Invoice]:
        """
        Get invoice by ID with items

        Args:
            invoice_id: Invoice ID

        Returns:
            Invoice or None if not found
        """
        query = select(Invoice).where(Invoice.id == invoice_id)
        result = await self.db.execute(query)
        invoice = result.scalar_one_or_none()
        return invoice

    async def get_invoice_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """
        Get invoice by invoice number

        Args:
            invoice_number: Invoice number

        Returns:
            Invoice or None if not found
        """
        query = select(Invoice).where(Invoice.invoice_number == invoice_number)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_invoices(
        self,
        user_id: Optional[str] = None,
        invoice_type: Optional[str] = None,
        is_draft: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Invoice]:
        """
        List invoices with filters

        Args:
            user_id: Filter by user ID
            invoice_type: Filter by invoice type
            is_draft: Filter by draft status
            skip: Offset for pagination
            limit: Limit for pagination

        Returns:
            List of invoices
        """
        query = select(Invoice)

        # Apply filters
        conditions = []
        if user_id:
            conditions.append(Invoice.user_id == user_id)
        if invoice_type:
            conditions.append(Invoice.invoice_type == invoice_type)
        if is_draft is not None:
            conditions.append(Invoice.is_draft == is_draft)

        if conditions:
            query = query.where(and_(*conditions))

        # Order by created_at descending
        query = query.order_by(Invoice.created_at.desc())

        # Pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_invoices(
        self,
        user_id: Optional[str] = None,
        invoice_type: Optional[str] = None,
        is_draft: Optional[bool] = None
    ) -> int:
        """
        Count invoices with filters

        Args:
            user_id: Filter by user ID
            invoice_type: Filter by invoice type
            is_draft: Filter by draft status

        Returns:
            Count of invoices
        """
        query = select(func.count()).select_from(Invoice)

        # Apply filters
        conditions = []
        if user_id:
            conditions.append(Invoice.user_id == user_id)
        if invoice_type:
            conditions.append(Invoice.invoice_type == invoice_type)
        if is_draft is not None:
            conditions.append(Invoice.is_draft == is_draft)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar()

    async def update_invoice(
        self,
        invoice_id: int,
        invoice_data: Dict[str, Any]
    ) -> Invoice:
        """
        Update invoice (only if draft)

        Args:
            invoice_id: Invoice ID
            invoice_data: Updated invoice data

        Returns:
            Updated invoice

        Raises:
            InvoiceNotFoundException: If invoice not found
            InvoiceNotDraftException: If invoice is finalized
        """
        invoice = await self.get_invoice(invoice_id)
        if not invoice:
            raise InvoiceNotFoundException(invoice_id)

        if not invoice.is_draft:
            raise InvoiceNotDraftException(invoice.invoice_number)

        # Delete existing items
        for item in invoice.items:
            await self.db.delete(item)

        # Process new items
        gst_rate_percent = Decimal(str(invoice_data.get('gst_rate', 18.0)))
        items_data = invoice_data['items']
        processed_items = []
        subtotal = Decimal('0.00')

        for idx, item_data in enumerate(items_data):
            unit_price_with_gst = Decimal(str(item_data['unit_price']))
            quantity = Decimal(str(item_data['quantity']))

            base_unit_price = self._extract_base_price_from_gst_inclusive(
                unit_price_with_gst,
                gst_rate_percent
            )

            amount = (quantity * base_unit_price).quantize(Decimal('0.01'))
            subtotal += amount

            processed_items.append({
                'serial_number': idx + 1,
                'description': item_data['description'],
                'hsn_sac': item_data['hsn_sac'],
                'quantity': quantity,
                'unit_price': base_unit_price,
                'amount': amount
            })

        # Calculate taxes
        tax_result = self._calculate_taxes(
            subtotal,
            gst_rate_percent,
            invoice_data['seller_state'],
            invoice_data['buyer_state']
        )

        # Update invoice fields
        invoice.invoice_date = invoice_data['invoice_date']
        invoice.due_date = invoice_data.get('due_date')
        invoice.buyer_name = invoice_data['buyer_name']
        invoice.buyer_address = invoice_data['buyer_address']
        invoice.buyer_pincode = invoice_data['buyer_pincode']
        invoice.buyer_state = invoice_data['buyer_state']
        invoice.buyer_phone = invoice_data.get('buyer_phone')
        invoice.buyer_email = invoice_data.get('buyer_email')
        invoice.buyer_gstin = invoice_data.get('buyer_gstin')
        invoice.subtotal = subtotal
        invoice.cgst = tax_result['cgst']
        invoice.sgst = tax_result['sgst']
        invoice.igst = tax_result['igst']
        invoice.total = tax_result['total']
        invoice.is_interstate = tax_result['is_interstate']
        invoice.gst_rate = gst_rate_percent
        invoice.notes = invoice_data.get('notes')
        invoice.payment_terms = invoice_data.get('payment_terms')

        # Create new items
        for item_data in processed_items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                **item_data
            )
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def delete_invoice(self, invoice_id: int) -> None:
        """
        Delete invoice

        Args:
            invoice_id: Invoice ID

        Raises:
            InvoiceNotFoundException: If invoice not found
        """
        invoice = await self.get_invoice(invoice_id)
        if not invoice:
            raise InvoiceNotFoundException(invoice_id)

        await self.db.delete(invoice)
        await self.db.commit()

    async def finalize_invoice(self, invoice_id: int) -> Invoice:
        """
        Finalize draft invoice (make immutable + generate PDF)

        Args:
            invoice_id: Invoice ID

        Returns:
            Finalized invoice

        Raises:
            InvoiceNotFoundException: If invoice not found
            InvalidInvoiceDataException: If already finalized
        """
        invoice = await self.get_invoice(invoice_id)
        if not invoice:
            raise InvoiceNotFoundException(invoice_id)

        if not invoice.is_draft:
            raise InvalidInvoiceDataException(
                f"Invoice {invoice.invoice_number} is already finalized"
            )

        # Mark as finalized
        invoice.is_draft = False

        # Generate PDF
        from app.services.pdf_service import PDFService
        pdf_service = PDFService()
        await pdf_service.generate_pdf(invoice)

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def get_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get invoice summary statistics for user

        Args:
            user_id: User ID

        Returns:
            Dict with invoice counts and totals
        """
        # Total count
        total_invoices = await self.count_invoices(user_id=user_id)

        # Draft count
        draft_invoices = await self.count_invoices(user_id=user_id, is_draft=True)

        # Finalized count
        finalized_invoices = await self.count_invoices(user_id=user_id, is_draft=False)

        # Topmate invoices count
        topmate_invoices = await self.count_invoices(user_id=user_id, invoice_type='topmate')

        # User invoices count
        user_invoices = await self.count_invoices(user_id=user_id, invoice_type='user')

        # Total amount (finalized invoices only)
        query = select(func.sum(Invoice.total)).where(
            and_(
                Invoice.user_id == user_id,
                Invoice.is_draft == False
            )
        )
        result = await self.db.execute(query)
        total_amount = result.scalar() or Decimal('0.00')

        return {
            'total_invoices': total_invoices,
            'draft_invoices': draft_invoices,
            'finalized_invoices': finalized_invoices,
            'total_amount': total_amount,
            'topmate_invoices': topmate_invoices,
            'user_invoices': user_invoices
        }
