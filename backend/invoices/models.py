from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal


# Indian state choices for GST
INDIAN_STATES = [
    ('AN', 'Andaman and Nicobar Islands'),
    ('AP', 'Andhra Pradesh'),
    ('AR', 'Arunachal Pradesh'),
    ('AS', 'Assam'),
    ('BR', 'Bihar'),
    ('CG', 'Chhattisgarh'),
    ('CH', 'Chandigarh'),
    ('DN', 'Dadra and Nagar Haveli and Daman and Diu'),
    ('DL', 'Delhi'),
    ('GA', 'Goa'),
    ('GJ', 'Gujarat'),
    ('HR', 'Haryana'),
    ('HP', 'Himachal Pradesh'),
    ('JK', 'Jammu and Kashmir'),
    ('JH', 'Jharkhand'),
    ('KA', 'Karnataka'),
    ('KL', 'Kerala'),
    ('LA', 'Ladakh'),
    ('LD', 'Lakshadweep'),
    ('MP', 'Madhya Pradesh'),
    ('MH', 'Maharashtra'),
    ('MN', 'Manipur'),
    ('ML', 'Meghalaya'),
    ('MZ', 'Mizoram'),
    ('NL', 'Nagaland'),
    ('OR', 'Odisha'),
    ('PY', 'Puducherry'),
    ('PB', 'Punjab'),
    ('RJ', 'Rajasthan'),
    ('SK', 'Sikkim'),
    ('TN', 'Tamil Nadu'),
    ('TS', 'Telangana'),
    ('TR', 'Tripura'),
    ('UP', 'Uttar Pradesh'),
    ('UK', 'Uttarakhand'),
    ('WB', 'West Bengal'),
]


class BusinessProfile(models.Model):
    """
    Stores business profile for 'self-use' invoices
    One profile per user
    """
    user_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="User ID from main system"
    )
    business_name = models.CharField(max_length=255)
    gstin = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$',
                message='Invalid GSTIN format'
            )
        ],
        help_text="15-digit GST Identification Number"
    )
    address = models.TextField()
    pincode = models.CharField(max_length=6)
    state = models.CharField(max_length=2, choices=INDIAN_STATES)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'business_profiles'
        verbose_name = 'Business Profile'
        verbose_name_plural = 'Business Profiles'

    def __str__(self):
        return f"{self.business_name} - {self.gstin}"


class InvoiceNumberSequence(models.Model):
    """
    Manages invoice number sequences
    - One sequence for Topmate (global)
    - One sequence per user for self-use invoices
    """
    SEQUENCE_TYPE_CHOICES = [
        ('topmate', 'Topmate Invoice'),
        ('user', 'User Invoice'),
    ]

    sequence_type = models.CharField(max_length=10, choices=SEQUENCE_TYPE_CHOICES)
    user_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="User ID for user-specific sequences"
    )
    current_number = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoice_number_sequences'
        unique_together = [['sequence_type', 'user_id']]
        verbose_name = 'Invoice Number Sequence'
        verbose_name_plural = 'Invoice Number Sequences'

    def get_next_number(self):
        """Atomically increment and return next invoice number"""
        from django.db import transaction
        with transaction.atomic():
            self.current_number += 1
            self.save()
            return self.current_number

    def __str__(self):
        if self.sequence_type == 'topmate':
            return f"Topmate Sequence: {self.current_number}"
        return f"User {self.user_id} Sequence: {self.current_number}"


class Invoice(models.Model):
    """
    Main Invoice model
    Represents a complete invoice (Topmate or User-generated)
    """
    INVOICE_TYPE_CHOICES = [
        ('topmate', 'Topmate Invoice'),
        ('user', 'User Invoice'),
    ]

    # Invoice identification
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_type = models.CharField(max_length=10, choices=INVOICE_TYPE_CHOICES)
    user_id = models.CharField(
        max_length=100,
        help_text="User ID who generated the invoice"
    )

    # Dates
    invoice_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)

    # Seller details (Issued By)
    seller_name = models.CharField(max_length=255)
    seller_gstin = models.CharField(max_length=15)
    seller_address = models.TextField()
    seller_pincode = models.CharField(max_length=6)
    seller_state = models.CharField(max_length=2, choices=INDIAN_STATES)
    seller_phone = models.CharField(max_length=15, blank=True)
    seller_email = models.EmailField(blank=True)

    # Buyer details (Issued To)
    buyer_name = models.CharField(max_length=255)
    buyer_gstin = models.CharField(max_length=15, blank=True, null=True)
    buyer_address = models.TextField()
    buyer_pincode = models.CharField(max_length=6)
    buyer_state = models.CharField(max_length=2, choices=INDIAN_STATES)
    buyer_phone = models.CharField(max_length=15, blank=True)
    buyer_email = models.EmailField(blank=True)

    # Financial details
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    cgst = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    igst = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Tax flags
    is_interstate = models.BooleanField(
        default=False,
        help_text="True if IGST applicable, False if CGST+SGST"
    )
    gst_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=18.00,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="GST rate percentage (e.g., 18.00 for 18%)"
    )

    # Additional fields
    notes = models.TextField(blank=True, help_text="Additional notes/terms")
    payment_terms = models.CharField(max_length=255, blank=True)

    # PDF storage
    pdf_url = models.URLField(blank=True, null=True)
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(default=False)

    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        indexes = [
            models.Index(fields=['user_id', '-created_at']),
            models.Index(fields=['invoice_number']),
            models.Index(fields=['invoice_type']),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.buyer_name}"

    def calculate_taxes(self):
        """
        Calculate GST based on seller and buyer states
        Uses custom gst_rate if set, otherwise uses default from settings
        Updates cgst, sgst, igst, and total fields
        """
        # Use custom GST rate or fall back to settings default
        gst_rate_percent = self.gst_rate if self.gst_rate else Decimal(str(settings.INVOICE_SETTINGS['GST_RATE']))
        gst_rate = gst_rate_percent / 100

        if self.seller_state == self.buyer_state:
            # Same state: CGST + SGST (split GST equally)
            self.is_interstate = False
            half_rate = gst_rate / 2
            self.cgst = (self.subtotal * half_rate).quantize(Decimal('0.01'))
            self.sgst = (self.subtotal * half_rate).quantize(Decimal('0.01'))
            self.igst = Decimal('0.00')
        else:
            # Different states: IGST (full GST rate)
            self.is_interstate = True
            self.igst = (self.subtotal * gst_rate).quantize(Decimal('0.01'))
            self.cgst = Decimal('0.00')
            self.sgst = Decimal('0.00')

        self.total = self.subtotal + self.cgst + self.sgst + self.igst


class InvoiceItem(models.Model):
    """
    Line items for an invoice
    Multiple items per invoice
    """
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items'
    )
    serial_number = models.IntegerField(help_text="S.No. in the invoice")
    description = models.TextField()
    hsn_sac = models.CharField(
        max_length=15,
        help_text="HSN (goods) or SAC (services) code"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'invoice_items'
        ordering = ['serial_number']
        verbose_name = 'Invoice Item'
        verbose_name_plural = 'Invoice Items'

    def __str__(self):
        return f"{self.invoice.invoice_number} - Item {self.serial_number}"

    def save(self, *args, **kwargs):
        # Auto-calculate amount
        self.amount = (self.quantity * self.unit_price).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)
