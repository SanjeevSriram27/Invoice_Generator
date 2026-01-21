"""
WhatsApp service using Twilio
"""
from typing import Optional, Dict, Any
import os

from app.config import settings
from app.core.exceptions import WhatsAppSendException


class WhatsAppService:
    """
    Service for sending WhatsApp messages via Twilio

    Supports:
    - Twilio WhatsApp Business API
    - Fallback to wa.me link if Twilio not configured
    """

    def __init__(self):
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.whatsapp_number = settings.twilio_whatsapp_number
        self.twilio_configured = bool(self.account_sid and self.auth_token)

    async def send_invoice_whatsapp(
        self,
        invoice,
        recipient_phone: Optional[str] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send invoice via WhatsApp

        Args:
            invoice: Invoice model instance
            recipient_phone: Override buyer phone (optional)
            message: Custom WhatsApp message (optional)

        Returns:
            Dict with result info (message_sid if sent, or wa.me link)

        Raises:
            WhatsAppSendException: If sending fails
        """
        try:
            # Determine recipient
            to_phone = recipient_phone or invoice.buyer_phone

            if not to_phone:
                raise WhatsAppSendException("No recipient phone number provided")

            # Ensure phone starts with whatsapp: prefix for Twilio
            if not to_phone.startswith('whatsapp:'):
                to_phone = f"whatsapp:{to_phone}"

            # Build message
            if not message:
                message = self._build_default_message(invoice)

            # Check if Twilio is configured
            if self.twilio_configured:
                # Send via Twilio
                result = await self._send_via_twilio(to_phone, message, invoice)
                return {
                    "method": "twilio",
                    "status": "sent",
                    **result
                }
            else:
                # Fallback to wa.me link
                wa_link = self._generate_wa_link(to_phone, message)
                return {
                    "method": "wa_link",
                    "status": "link_generated",
                    "link": wa_link,
                    "message": "Twilio not configured. Use the provided link to send via WhatsApp Web."
                }

        except Exception as e:
            raise WhatsAppSendException(f"Failed to send WhatsApp: {str(e)}")

    def _build_default_message(self, invoice) -> str:
        """Build default WhatsApp message"""
        message_lines = [
            f"*Invoice {invoice.invoice_number}*",
            "",
            f"Dear {invoice.buyer_name},",
            "",
            f"Your invoice from {invoice.seller_name}:",
            "",
            f"Date: {invoice.invoice_date}",
            f"Amount: ₹{invoice.total}",
            "",
        ]

        if invoice.payment_terms:
            message_lines.append(f"Payment Terms: {invoice.payment_terms}")
            message_lines.append("")

        if invoice.notes:
            message_lines.append(f"Notes: {invoice.notes}")
            message_lines.append("")

        # Add PDF download info if available
        if invoice.pdf_url:
            message_lines.append(f"Download PDF: {invoice.pdf_url}")
            message_lines.append("")

        message_lines.extend([
            "Thank you for your business!",
            "",
            f"Best regards,",
            f"{invoice.seller_name}"
        ])

        if invoice.seller_website:
            message_lines.append(f"{invoice.seller_website}")

        return "\n".join(message_lines)

    async def _send_via_twilio(
        self,
        to_phone: str,
        message: str,
        invoice
    ) -> Dict[str, Any]:
        """
        Send WhatsApp message via Twilio

        Uses Twilio's Python SDK in async context
        """
        try:
            # Import Twilio client
            from twilio.rest import Client
            import asyncio

            # Create Twilio client
            client = Client(self.account_sid, self.auth_token)

            # Send message in executor (Twilio SDK is sync)
            loop = asyncio.get_event_loop()
            twilio_message = await loop.run_in_executor(
                None,
                lambda: client.messages.create(
                    from_=self.whatsapp_number,
                    body=message,
                    to=to_phone
                )
            )

            # TODO: Attach PDF if Twilio supports media
            # Note: Twilio WhatsApp supports media attachments
            # You can add media_url parameter if you have a public PDF URL

            return {
                "message_sid": twilio_message.sid,
                "status": twilio_message.status,
                "to": twilio_message.to,
                "from": twilio_message.from_
            }

        except Exception as e:
            raise WhatsAppSendException(f"Twilio error: {str(e)}")

    def _generate_wa_link(self, to_phone: str, message: str) -> str:
        """
        Generate wa.me link for manual WhatsApp sending

        Args:
            to_phone: Phone number (with or without whatsapp: prefix)
            message: Message text

        Returns:
            wa.me URL
        """
        # Remove whatsapp: prefix if present
        phone = to_phone.replace('whatsapp:', '')

        # Remove + if present (wa.me doesn't need it)
        phone = phone.replace('+', '')

        # URL encode message
        from urllib.parse import quote
        encoded_message = quote(message)

        # Build wa.me link
        wa_link = f"https://wa.me/{phone}?text={encoded_message}"

        return wa_link

    async def send_simple_whatsapp(
        self,
        to_phone: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send a simple WhatsApp message

        Args:
            to_phone: Recipient phone number (E.164 format recommended)
            message: Message text

        Returns:
            Dict with result info
        """
        # Ensure phone starts with whatsapp: prefix
        if not to_phone.startswith('whatsapp:'):
            to_phone = f"whatsapp:{to_phone}"

        if self.twilio_configured:
            # Import Twilio client
            from twilio.rest import Client
            import asyncio

            client = Client(self.account_sid, self.auth_token)

            # Send message
            loop = asyncio.get_event_loop()
            twilio_message = await loop.run_in_executor(
                None,
                lambda: client.messages.create(
                    from_=self.whatsapp_number,
                    body=message,
                    to=to_phone
                )
            )

            return {
                "method": "twilio",
                "status": "sent",
                "message_sid": twilio_message.sid,
                "to": twilio_message.to
            }
        else:
            # Generate wa.me link
            wa_link = self._generate_wa_link(to_phone, message)
            return {
                "method": "wa_link",
                "status": "link_generated",
                "link": wa_link
            }
