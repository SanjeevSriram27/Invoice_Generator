"""
Email service using AWS SES (boto3) for async email sending
"""
import aioboto3
import aiofiles
import os
from typing import Optional

from app.config import settings
from app.core.exceptions import EmailSendException


class EmailService:
    """
    Service for sending emails via AWS SES

    Uses AWS SDK (boto3) instead of SMTP for better reliability
    """

    def __init__(self):
        self.aws_access_key_id = settings.aws_access_key_id
        self.aws_secret_access_key = settings.aws_secret_access_key
        self.aws_region = settings.aws_region
        self.sender_email = settings.ses_sender_email
        self.email_from_name = settings.email_from_name

    async def send_invoice_email(
        self,
        invoice,
        recipient_email: Optional[str] = None,
        subject: Optional[str] = None,
        message: Optional[str] = None
    ):
        """
        Send invoice PDF via email using AWS SES

        Args:
            invoice: Invoice model instance
            recipient_email: Override buyer email (optional)
            subject: Custom email subject (optional)
            message: Custom email message (optional)

        Raises:
            EmailSendException: If email sending fails
        """
        try:
            # Determine recipient
            to_email = recipient_email or invoice.buyer_email

            if not to_email:
                raise EmailSendException("No recipient email provided")

            # Build email subject
            if not subject:
                subject = f"Invoice {invoice.invoice_number} from {invoice.seller_name}"

            # Build email body
            if not message:
                html_body = self._build_default_message(invoice)
            else:
                html_body = message

            # Generate PDF if it doesn't exist
            if not invoice.pdf_file:
                from app.services.pdf_service import PDFService
                pdf_service = PDFService()
                await pdf_service.generate_pdf(invoice)

            # Read PDF file
            pdf_data = None
            pdf_filename = None
            if invoice.pdf_file:
                pdf_filename = invoice.pdf_file.split('/')[-1]
                pdf_path = os.path.join("media", "invoices", pdf_filename)

                if os.path.exists(pdf_path):
                    async with aiofiles.open(pdf_path, 'rb') as f:
                        pdf_data = await f.read()
                else:
                    raise EmailSendException(f"PDF file not found: {pdf_path}")

            # Send email via SES
            await self._send_ses_email(
                to_email=to_email,
                subject=subject,
                html_body=html_body,
                pdf_data=pdf_data,
                pdf_filename=f"{invoice.invoice_number}.pdf" if pdf_data else None
            )

        except Exception as e:
            raise EmailSendException(f"Failed to send email: {str(e)}")

    def _build_default_message(self, invoice) -> str:
        """Build default HTML email message"""
        return f"""
        <html>
            <body>
                <h2>Invoice {invoice.invoice_number}</h2>
                <p>Dear {invoice.buyer_name},</p>
                <p>Please find attached your invoice from {invoice.seller_name}.</p>

                <h3>Invoice Details:</h3>
                <table style="border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Invoice Number:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{invoice.invoice_number}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Date:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{invoice.invoice_date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Total Amount:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">₹{invoice.total}</td>
                    </tr>
                </table>

                {f'<p><strong>Payment Terms:</strong> {invoice.payment_terms}</p>' if invoice.payment_terms else ''}
                {f'<p><strong>Notes:</strong> {invoice.notes}</p>' if invoice.notes else ''}

                <p>Thank you for your business!</p>

                <p>Best regards,<br>
                {invoice.seller_name}</p>

                {f'<p><a href="{invoice.seller_website}">{invoice.seller_website}</a></p>' if invoice.seller_website else ''}
            </body>
        </html>
        """

    async def _send_ses_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        pdf_data: Optional[bytes] = None,
        pdf_filename: Optional[str] = None
    ):
        """
        Send email via AWS SES using boto3

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            pdf_data: PDF file bytes (optional)
            pdf_filename: PDF filename (optional)
        """
        try:
            # Create async boto3 session
            session = aioboto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )

            async with session.client('ses') as ses:
                if pdf_data:
                    # Send email with attachment using raw email
                    from email.mime.multipart import MIMEMultipart
                    from email.mime.text import MIMEText
                    from email.mime.application import MIMEApplication

                    msg = MIMEMultipart()
                    msg['Subject'] = subject
                    msg['From'] = f"{self.email_from_name} <{self.sender_email}>"
                    msg['To'] = to_email

                    # Add HTML body
                    msg.attach(MIMEText(html_body, 'html'))

                    # Add PDF attachment
                    pdf_attachment = MIMEApplication(pdf_data, _subtype='pdf')
                    pdf_attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=pdf_filename
                    )
                    msg.attach(pdf_attachment)

                    # Send raw email
                    response = await ses.send_raw_email(
                        Source=self.sender_email,
                        Destinations=[to_email],
                        RawMessage={'Data': msg.as_string()}
                    )
                else:
                    # Send simple email without attachment
                    response = await ses.send_email(
                        Source=f"{self.email_from_name} <{self.sender_email}>",
                        Destination={'ToAddresses': [to_email]},
                        Message={
                            'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                            'Body': {
                                'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                            }
                        }
                    )

                return response

        except Exception as e:
            raise EmailSendException(f"SES error: {str(e)}")

    async def send_simple_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False
    ):
        """
        Send a simple email without attachments

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            html: Whether body is HTML (default False)
        """
        try:
            session = aioboto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )

            async with session.client('ses') as ses:
                message = {
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {}
                }

                if html:
                    message['Body']['Html'] = {'Data': body, 'Charset': 'UTF-8'}
                else:
                    message['Body']['Text'] = {'Data': body, 'Charset': 'UTF-8'}

                response = await ses.send_email(
                    Source=f"{self.email_from_name} <{self.sender_email}>",
                    Destination={'ToAddresses': [to_email]},
                    Message=message
                )

                return response

        except Exception as e:
            raise EmailSendException(f"Failed to send email: {str(e)}")
