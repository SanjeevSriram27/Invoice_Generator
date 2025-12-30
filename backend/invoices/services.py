"""
Invoice PDF Generation Service
"""
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings
import os


def generate_invoice_pdf(invoice):
    """
    Generate PDF for an invoice using HTML template
    Args:
        invoice: Invoice model instance
    Returns:
        str: Path to generated PDF file
    """
    try:
        # Try importing pdfkit (requires wkhtmltopdf)
        import pdfkit
        use_pdfkit = True
    except (ImportError, OSError):
        # Fallback to reportlab if pdfkit not available
        use_pdfkit = False

    # Prepare context data
    context = {
        'invoice': invoice,
        'items': invoice.items.all().order_by('serial_number'),
        'settings': settings.INVOICE_SETTINGS,
    }

    # Render HTML template
    html_string = render_to_string('invoices/invoice_template.html', context)

    if use_pdfkit:
        # Generate PDF using pdfkit
        try:
            pdf_content = pdfkit.from_string(html_string, False)
            filename = f"{invoice.invoice_number}.pdf"

            # Save PDF to model
            invoice.pdf_file.save(filename, ContentFile(pdf_content), save=True)

            return invoice.pdf_file.path
        except Exception as e:
            print(f"pdfkit error: {e}")
            # Fall through to reportlab

    # Fallback: Generate professional PDF using reportlab
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    from io import BytesIO
    from decimal import Decimal

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 1.2*cm

    # Helper function to format currency (avoiding Unicode rupee symbol)
    def format_currency(amount):
        return f"Rs. {amount}"

    # Helper function to draw text
    def draw_text(x, y, text, font="Helvetica", size=10, bold=False, align='left'):
        if bold:
            p.setFont(f"{font}-Bold", size)
        else:
            p.setFont(font, size)
        if align == 'right':
            text_width = p.stringWidth(str(text), f"{font}-Bold" if bold else font, size)
            p.drawString(x - text_width, y, str(text))
        else:
            p.drawString(x, y, str(text))

    # Header - INVOICE title and number
    p.setFillColorRGB(0.2, 0.2, 0.2)
    p.rect(margin, height - 3.5*cm, width - 2*margin, 2.5*cm, fill=1, stroke=0)
    p.setFillColorRGB(1, 1, 1)
    draw_text(margin + 0.7*cm, height - 2.2*cm, "TAX INVOICE", "Helvetica", 26, bold=True)
    draw_text(width - margin - 8*cm, height - 2*cm, f"Invoice #: {invoice.invoice_number}", "Helvetica", 13, bold=True)
    draw_text(width - margin - 8*cm, height - 2.7*cm, f"Date: {invoice.invoice_date.strftime('%d/%m/%Y')}", "Helvetica", 11)

    p.setFillColorRGB(0, 0, 0)

    # Seller and Buyer boxes
    y_pos = height - 5*cm
    box_height = 6.5*cm  # Increased height for bank details

    # Seller box (with bank details)
    p.setStrokeColorRGB(0.7, 0.7, 0.7)
    p.setLineWidth(1)
    p.rect(margin, y_pos - box_height, (width - 2*margin) / 2 - 0.4*cm, box_height, stroke=1, fill=0)

    draw_text(margin + 0.6*cm, y_pos - 0.7*cm, "SELLER DETAILS", "Helvetica", 11, bold=True)
    draw_text(margin + 0.6*cm, y_pos - 1.3*cm, invoice.seller_name, "Helvetica", 10, bold=True)
    draw_text(margin + 0.6*cm, y_pos - 1.8*cm, f"GSTIN: {invoice.seller_gstin}", "Helvetica", 9)
    if invoice.seller_phone:
        # Align phone to right edge of seller box
        seller_box_right = margin + (width - 2*margin) / 2 - 0.8*cm
        draw_text(seller_box_right, y_pos - 1.8*cm, f"Ph: {invoice.seller_phone}", "Helvetica", 8, align='right')

    # Multi-line address for seller
    address_lines = []
    if invoice.seller_address:
        # Split address into lines of max 40 characters
        words = invoice.seller_address.split()
        line = ""
        for word in words:
            if len(line + word) < 40:
                line += word + " "
            else:
                address_lines.append(line.strip())
                line = word + " "
        if line:
            address_lines.append(line.strip())

    y_addr = y_pos - 2.3*cm
    for line in address_lines[:2]:  # Max 2 lines
        draw_text(margin + 0.6*cm, y_addr, line, "Helvetica", 9)
        y_addr -= 0.45*cm

    if invoice.seller_pincode:
        draw_text(margin + 0.6*cm, y_addr, f"PIN: {invoice.seller_pincode}", "Helvetica", 9)
        y_addr -= 0.6*cm

    # Bank details within seller box
    draw_text(margin + 0.6*cm, y_addr, "BANK DETAILS", "Helvetica", 10, bold=True)
    y_addr -= 0.5*cm
    draw_text(margin + 0.6*cm, y_addr, "Bank: HDFC Bank", "Helvetica", 8)
    y_addr -= 0.4*cm
    draw_text(margin + 0.6*cm, y_addr, "A/c: 50200012345678", "Helvetica", 8)
    y_addr -= 0.4*cm
    draw_text(margin + 0.6*cm, y_addr, "IFSC: HDFC0001234", "Helvetica", 8)

    # Buyer box (same height as seller box)
    p.rect(margin + (width - 2*margin) / 2 + 0.4*cm, y_pos - box_height, (width - 2*margin) / 2 - 0.4*cm, box_height, stroke=1, fill=0)

    buyer_x = margin + (width - 2*margin) / 2 + 1*cm
    draw_text(buyer_x, y_pos - 0.7*cm, "BUYER DETAILS", "Helvetica", 11, bold=True)
    # Truncate buyer name if too long (max 30 characters for better fit)
    buyer_name_display = invoice.buyer_name[:30] + "..." if len(invoice.buyer_name) > 30 else invoice.buyer_name
    draw_text(buyer_x, y_pos - 1.3*cm, buyer_name_display, "Helvetica", 10, bold=True)

    current_y = y_pos - 1.8*cm
    if invoice.buyer_gstin:
        draw_text(buyer_x, current_y, f"GSTIN: {invoice.buyer_gstin}", "Helvetica", 9)
        current_y -= 0.5*cm

    if invoice.buyer_phone:
        draw_text(buyer_x, current_y, f"Ph: {invoice.buyer_phone}", "Helvetica", 9)
        current_y -= 0.5*cm

    # Buyer address - starts after GSTIN and phone
    buyer_address_lines = []
    if invoice.buyer_address:
        words = invoice.buyer_address.split()
        line = ""
        for word in words:
            if len(line + word) < 40:
                line += word + " "
            else:
                buyer_address_lines.append(line.strip())
                line = word + " "
        if line:
            buyer_address_lines.append(line.strip())

    y_addr = current_y
    for line in buyer_address_lines[:3]:  # Allow 3 lines
        draw_text(buyer_x, y_addr, line, "Helvetica", 9)
        y_addr -= 0.45*cm

    if invoice.buyer_pincode:
        draw_text(buyer_x, y_addr, f"PIN: {invoice.buyer_pincode}", "Helvetica", 9)
        y_addr -= 0.4*cm
        draw_text(buyer_x, y_addr, f"State: {invoice.buyer_state}", "Helvetica", 9)

    # Items table
    y_pos = y_pos - box_height - 1.2*cm

    # Table header
    table_data = [
        ['#', 'Description', 'HSN/SAC', 'Qty', 'Rate', 'Amount']
    ]

    # Table rows
    for item in invoice.items.all():
        table_data.append([
            str(item.serial_number),
            item.description[:50],
            item.hsn_sac,
            str(item.quantity),
            format_currency(item.unit_price),
            format_currency(item.amount)
        ])

    # Create table with wider columns
    col_widths = [1.2*cm, 7.5*cm, 2.5*cm, 1.8*cm, 2.8*cm, 2.8*cm]
    table = Table(table_data, colWidths=col_widths)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D3748')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('ALIGN', (4, 1), (5, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.75, colors.HexColor('#A0AEC0')),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#2D3748')),
    ]))

    # Draw table
    table.wrapOn(p, width, height)
    table_height = table._height
    table.drawOn(p, margin, y_pos - table_height)

    # Totals section - Fixed alignment
    y_pos = y_pos - table_height - 1.5*cm
    totals_x = width - margin - 7.5*cm

    # Draw totals box with better styling
    p.setStrokeColorRGB(0.7, 0.7, 0.7)
    p.setLineWidth(1)
    totals_box_height = 3.5*cm if invoice.is_interstate else 4*cm

    # Ensure totals section doesn't go below minimum margin (4cm from bottom for footer)
    min_y_position = 4*cm
    if (y_pos - totals_box_height) < min_y_position:
        # Add new page if not enough space
        p.showPage()
        y_pos = height - 3*cm  # Start near top of new page
        totals_x = width - margin - 7.5*cm

    p.rect(totals_x - 0.4*cm, y_pos - totals_box_height, 7.9*cm, totals_box_height, stroke=1, fill=0)

    # Subtotal row
    y_totals = y_pos - 0.8*cm
    draw_text(totals_x, y_totals, "Subtotal:", "Helvetica", 11)
    draw_text(totals_x + 6.5*cm, y_totals, format_currency(invoice.subtotal), "Helvetica", 11, align='right')

    # GST rows - Calculate percentages dynamically
    y_totals -= 0.8*cm
    gst_rate = float(invoice.gst_rate) if invoice.gst_rate else 18.0
    # Format rate to remove .0 if it's a whole number
    gst_rate_display = f"{gst_rate:.0f}" if gst_rate % 1 == 0 else f"{gst_rate:.1f}"

    if invoice.is_interstate:
        draw_text(totals_x, y_totals, f"IGST ({gst_rate_display}%):", "Helvetica", 10)
        draw_text(totals_x + 6.5*cm, y_totals, format_currency(invoice.igst), "Helvetica", 10, align='right')
        y_totals -= 0.8*cm
    else:
        half_rate = gst_rate / 2
        half_rate_display = f"{half_rate:.0f}" if half_rate % 1 == 0 else f"{half_rate:.1f}"
        draw_text(totals_x, y_totals, f"CGST ({half_rate_display}%):", "Helvetica", 10)
        draw_text(totals_x + 6.5*cm, y_totals, format_currency(invoice.cgst), "Helvetica", 10, align='right')
        y_totals -= 0.7*cm
        draw_text(totals_x, y_totals, f"SGST ({half_rate_display}%):", "Helvetica", 10)
        draw_text(totals_x + 6.5*cm, y_totals, format_currency(invoice.sgst), "Helvetica", 10, align='right')
        y_totals -= 0.8*cm

    # Total line with background
    p.setFillColorRGB(0.95, 0.95, 0.95)
    p.rect(totals_x - 0.35*cm, y_totals - 0.3*cm, 7.8*cm, 0.9*cm, fill=1, stroke=0)
    p.setFillColorRGB(0.1, 0.3, 0.7)
    # Center text vertically in the grey background (adjust y-position for better alignment)
    draw_text(totals_x, y_totals + 0.1*cm, "Total Amount:", "Helvetica", 13, bold=True)
    draw_text(totals_x + 6.5*cm, y_totals + 0.1*cm, format_currency(invoice.total), "Helvetica", 13, bold=True, align='right')
    p.setFillColorRGB(0, 0, 0)

    # Footer
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColorRGB(0.4, 0.4, 0.4)
    p.drawString(margin, 2.5*cm, "This is a computer-generated invoice and does not require a signature.")
    if invoice.notes:
        p.setFont("Helvetica", 9)
        p.setFillColorRGB(0, 0, 0)
        p.drawString(margin, 2*cm, f"Notes: {invoice.notes[:90]}")

    # Thank you message
    p.setFont("Helvetica-Bold", 10)
    p.setFillColorRGB(0.2, 0.4, 0.7)
    thank_you_text = "Thank you for your business!"
    text_width = p.stringWidth(thank_you_text, "Helvetica-Bold", 10)
    p.drawString((width - text_width) / 2, 1.2*cm, thank_you_text)

    p.showPage()
    p.save()

    # Save PDF to model
    buffer.seek(0)
    filename = f"{invoice.invoice_number}.pdf"
    invoice.pdf_file.save(filename, ContentFile(buffer.read()), save=True)

    return invoice.pdf_file.path
