from django.contrib import admin
from .models import BusinessProfile, InvoiceNumberSequence, Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['serial_number', 'description', 'hsn_sac', 'quantity', 'unit_price', 'amount']
    readonly_fields = ['amount']


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'gstin', 'state', 'user_id', 'created_at']
    list_filter = ['state', 'created_at']
    search_fields = ['business_name', 'gstin', 'user_id', 'email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Business Information', {
            'fields': ('user_id', 'business_name', 'gstin')
        }),
        ('Contact Details', {
            'fields': ('address', 'pincode', 'state', 'phone', 'email')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InvoiceNumberSequence)
class InvoiceNumberSequenceAdmin(admin.ModelAdmin):
    list_display = ['sequence_type', 'user_id', 'current_number', 'updated_at']
    list_filter = ['sequence_type']
    search_fields = ['user_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'invoice_type', 'buyer_name',
        'total', 'invoice_date', 'is_draft', 'created_at'
    ]
    list_filter = ['invoice_type', 'is_draft', 'is_interstate', 'invoice_date', 'created_at']
    search_fields = ['invoice_number', 'buyer_name', 'seller_name', 'user_id']
    readonly_fields = ['created_at', 'updated_at', 'invoice_number']
    date_hierarchy = 'invoice_date'
    inlines = [InvoiceItemInline]

    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'invoice_type', 'user_id', 'invoice_date', 'due_date', 'is_draft')
        }),
        ('Seller Details (Issued By)', {
            'fields': ('seller_name', 'seller_gstin', 'seller_address', 'seller_pincode',
                      'seller_state', 'seller_phone', 'seller_email')
        }),
        ('Buyer Details (Issued To)', {
            'fields': ('buyer_name', 'buyer_gstin', 'buyer_address', 'buyer_pincode',
                      'buyer_state', 'buyer_phone', 'buyer_email')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'cgst', 'sgst', 'igst', 'total', 'is_interstate')
        }),
        ('Additional Information', {
            'fields': ('notes', 'payment_terms', 'pdf_url', 'pdf_file'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Only for new objects
            obj.calculate_taxes()
        super().save_model(request, obj, form, change)


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'serial_number', 'description', 'quantity', 'unit_price', 'amount']
    list_filter = ['invoice__invoice_type', 'created_at']
    search_fields = ['invoice__invoice_number', 'description', 'hsn_sac']
    readonly_fields = ['amount', 'created_at']
