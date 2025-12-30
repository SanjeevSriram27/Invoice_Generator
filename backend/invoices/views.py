from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from .models import BusinessProfile, Invoice, InvoiceItem
from .serializers import (
    BusinessProfileSerializer,
    InvoiceSerializer,
    InvoiceCreateSerializer,
    InvoiceListSerializer
)
import json


class BusinessProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user business profiles
    """
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    permission_classes = [AllowAny]  # For development

    def get_queryset(self):
        """Filter by user_id if provided"""
        queryset = BusinessProfile.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get business profile by user_id"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            profile = BusinessProfile.objects.get(user_id=user_id)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except BusinessProfile.DoesNotExist:
            return Response(
                {'error': 'Business profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing invoices
    Supports creating, retrieving, listing, and generating PDFs
    """
    queryset = Invoice.objects.all()
    permission_classes = [AllowAny]  # For development

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return InvoiceCreateSerializer
        elif self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer

    def get_queryset(self):
        """Filter invoices by user_id and other params"""
        queryset = Invoice.objects.prefetch_related('items').all()

        # Filter by user_id
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by invoice_type
        invoice_type = self.request.query_params.get('invoice_type')
        if invoice_type:
            queryset = queryset.filter(invoice_type=invoice_type)

        # Filter by draft status
        is_draft = self.request.query_params.get('is_draft')
        if is_draft is not None:
            queryset = queryset.filter(is_draft=is_draft.lower() == 'true')

        return queryset

    def create(self, request, *args, **kwargs):
        """Create a new invoice"""
        serializer = self.get_serializer(data=request.data)

        # Add debug logging
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        invoice = serializer.save()

        # Return full invoice data
        response_serializer = InvoiceSerializer(invoice)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download invoice as PDF"""
        invoice = self.get_object()

        # Check if PDF exists
        if not invoice.pdf_file:
            # Generate PDF if not exists
            from .services import generate_invoice_pdf
            try:
                generate_invoice_pdf(invoice)
            except Exception as e:
                return Response(
                    {'error': f'Failed to generate PDF: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Return PDF file
        try:
            response = FileResponse(
                invoice.pdf_file.open('rb'),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="{invoice.invoice_number}.pdf"'
            return response
        except Exception as e:
            return Response(
                {'error': f'Failed to serve PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        """Generate/regenerate PDF for invoice"""
        invoice = self.get_object()

        from .services import generate_invoice_pdf
        try:
            pdf_path = generate_invoice_pdf(invoice)
            return Response({
                'message': 'PDF generated successfully',
                'pdf_url': invoice.pdf_url,
                'pdf_file': invoice.pdf_file.url if invoice.pdf_file else None
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to generate PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        """Send invoice PDF via email"""
        invoice = self.get_object()
        email = request.data.get('email')

        if not email:
            return Response(
                {'error': 'email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate PDF if not exists
        if not invoice.pdf_file:
            from .services import generate_invoice_pdf
            try:
                generate_invoice_pdf(invoice)
            except Exception as e:
                return Response(
                    {'error': f'Failed to generate PDF: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Send email with PDF attachment
        from django.core.mail import EmailMessage
        from django.conf import settings

        try:
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
                to=[email],
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

            return Response({
                'message': f'Invoice sent successfully to {email}',
                'invoice_number': invoice.invoice_number
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to send email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def share_whatsapp(self, request, pk=None):
        """Send invoice PDF via WhatsApp using Twilio"""
        invoice = self.get_object()
        phone = request.data.get('phone')

        if not phone:
            return Response(
                {'error': 'phone is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate PDF if not exists
        if not invoice.pdf_file:
            from .services import generate_invoice_pdf
            try:
                generate_invoice_pdf(invoice)
            except Exception as e:
                return Response(
                    {'error': f'Failed to generate PDF: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        from django.conf import settings

        # Check if Twilio is configured
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            # Fallback to wa.me link with PDF URL
            pdf_url = request.build_absolute_uri(invoice.pdf_file.url)
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
            whatsapp_link = f"https://wa.me/{phone}?text={encoded_message}"

            return Response({
                'whatsapp_link': whatsapp_link,
                'message': message,
                'pdf_url': pdf_url,
                'note': 'Twilio not configured. Using fallback method. Configure Twilio to send PDF directly.'
            })

        # Send via Twilio WhatsApp API with PDF attachment
        try:
            from twilio.rest import Client

            # Initialize Twilio client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            # Get the full public URL to the PDF file
            pdf_url = request.build_absolute_uri(invoice.pdf_file.url)

            # Format phone number for WhatsApp
            to_whatsapp = f"whatsapp:+{phone.lstrip('+')}"

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
                media_url=[pdf_url]  # Attach PDF
            )

            return Response({
                'message': 'Invoice sent successfully via WhatsApp',
                'invoice_number': invoice.invoice_number,
                'whatsapp_sid': message.sid,
                'status': message.status
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to send WhatsApp message: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        """Finalize a draft invoice (make it immutable)"""
        invoice = self.get_object()

        if not invoice.is_draft:
            return Response(
                {'error': 'Invoice is already finalized'},
                status=status.HTTP_400_BAD_REQUEST
            )

        invoice.is_draft = False
        invoice.save()

        # Generate PDF
        from .services import generate_invoice_pdf
        try:
            generate_invoice_pdf(invoice)
        except Exception as e:
            pass  # PDF generation failure shouldn't block finalization

        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get invoice summary statistics for a user"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        invoices = Invoice.objects.filter(user_id=user_id)

        summary = {
            'total_invoices': invoices.count(),
            'topmate_invoices': invoices.filter(invoice_type='topmate').count(),
            'user_invoices': invoices.filter(invoice_type='user').count(),
            'draft_invoices': invoices.filter(is_draft=True).count(),
            'total_amount': sum(inv.total for inv in invoices),
        }

        return Response(summary)

    @action(detail=False, methods=['post'], url_path='bulk-upload', url_name='bulk-upload')
    def bulk_upload(self, request):
        """
        Bulk upload invoices via CSV file

        POST /api/invoices/bulk-upload/

        Form data:
        - csv_file: CSV file
        - invoice_type: 'topmate' or 'user'
        - user_id: User ID
        - create_as_draft: Boolean (default: False)
        - send_email: Boolean (default: False) - Send invoice PDFs via email to receivers
        - send_whatsapp: Boolean (default: False) - Send invoice PDFs via WhatsApp to receivers
        - seller_* fields: Required if invoice_type='user'

        Note: send_email and send_whatsapp cannot be used with create_as_draft=true
        """
        from .bulk_upload_serializers import BulkInvoiceUploadSerializer
        from .bulk_upload_service import BulkInvoiceProcessor

        # Set parser classes for this request
        request.parsers = [MultiPartParser(), FormParser()]

        serializer = BulkInvoiceUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        # Extract seller details for user invoices
        seller_details = {
            'seller_name': validated_data.get('seller_name', ''),
            'seller_gstin': validated_data.get('seller_gstin', ''),
            'seller_address': validated_data.get('seller_address', ''),
            'seller_pincode': validated_data.get('seller_pincode', ''),
            'seller_state': validated_data.get('seller_state', ''),
            'seller_phone': validated_data.get('seller_phone', ''),
            'seller_email': validated_data.get('seller_email', ''),
        }

        try:
            processor = BulkInvoiceProcessor(
                csv_file=validated_data['csv_file'],
                user_id=validated_data['user_id'],
                invoice_type=validated_data['invoice_type'],
                seller_details=seller_details,
                create_as_draft=validated_data['create_as_draft'],
                send_email=validated_data.get('send_email', False),
                send_whatsapp=validated_data.get('send_whatsapp', False),
                gst_rate=validated_data.get('gst_rate', 18.00),
                request=request
            )

            result = processor.process()

            # Build response with download links and sending statistics
            email_sent_count = 0
            whatsapp_sent_count = 0

            for success in result['successes']:
                invoice_id = success['invoice_id']
                success['download_url'] = request.build_absolute_uri(
                    f"/api/invoices/{invoice_id}/download_pdf/"
                )

                # Count successful sends
                if success.get('email_sent'):
                    email_sent_count += 1
                if success.get('whatsapp_sent'):
                    whatsapp_sent_count += 1

            # Build summary message
            message_parts = [
                f"Processed {result['total_rows']} rows. "
                f"{result['successful']} successful, {result['failed']} failed."
            ]

            if validated_data.get('send_email'):
                message_parts.append(f"{email_sent_count} emails sent.")
            if validated_data.get('send_whatsapp'):
                message_parts.append(f"{whatsapp_sent_count} WhatsApp messages sent.")

            return Response({
                'message': ' '.join(message_parts),
                'summary': {
                    'total_rows': result['total_rows'],
                    'successful': result['successful'],
                    'failed': result['failed'],
                    'emails_sent': email_sent_count if validated_data.get('send_email') else None,
                    'whatsapp_sent': whatsapp_sent_count if validated_data.get('send_whatsapp') else None
                },
                'successes': result['successes'],
                'failures': result['failures']
            }, status=status.HTTP_200_OK if result['successful'] > 0 else status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {'error': f'Failed to process CSV: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
