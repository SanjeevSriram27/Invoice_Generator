"""
SuprSend Integration Service for Invoice Notifications
Uses httpx for async HTTP requests
Implements SuprSend's HMAC-SHA256 signature authentication
"""
import httpx
import json
import base64
import hashlib
import hmac
import logging
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Dict, Any, Literal

from app.config import settings
from app.core.validators import validate_and_format_phone
from app.core.exceptions import EmailSendException, WhatsAppSendException


logger = logging.getLogger(__name__)


class SuprSendService:
    """Service for sending invoice notifications via SuprSend"""

    def __init__(self):
        """Initialize SuprSend HTTP client"""
        self.workspace_key = settings.suprsend_workspace_key
        self.workspace_secret = settings.suprsend_workspace_secret
        self.base_url = settings.suprsend_workspace_url

        if not self.workspace_key or not self.workspace_secret:
            logger.warning("SuprSend credentials not configured")
            self.api_url = None
        else:
            # SuprSend URL format: {base_url}/{workspace_key}/trigger/
            self.api_url = f"{self.base_url}/{self.workspace_key}/trigger/"
            logger.info("SuprSend HTTP client initialized successfully")

    def _calculate_signature(
        self,
        url: str,
        http_method: str,
        body: dict,
        headers: dict
    ) -> tuple:
        """
        Calculate HMAC-SHA256 signature for SuprSend authentication

        CRITICAL: This algorithm must match Django implementation exactly
        Based on SuprSend SDK signature algorithm

        Returns:
            tuple: (content_txt, signature)
        """
        # Convert body to JSON string and calculate MD5
        content_txt = json.dumps(body, ensure_ascii=False)
        content_md5 = hashlib.md5(content_txt.encode()).hexdigest()

        # Get request URI (path + query)
        parsed_url = urlparse(url)
        request_uri = parsed_url.path
        if parsed_url.query:
            request_uri = f"{request_uri}?{parsed_url.query}"

        # Create string to sign
        string_to_sign = (
            f"{http_method}\n"
            f"{content_md5}\n"
            f"{headers['Content-Type']}\n"
            f"{headers['Date']}\n"
            f"{request_uri}"
        )

        # Calculate HMAC-SHA256 signature
        sig_bytes = hmac.HMAC(
            self.workspace_secret.encode(),
            msg=string_to_sign.encode(),
            digestmod=hashlib.sha256
        ).digest()

        # Base64 encode the signature
        signature = base64.b64encode(sig_bytes).decode()

        return content_txt, signature

    async def send_invoice_notification(
        self,
        invoice,
        channel: Literal['email', 'whatsapp'] = 'email'
    ) -> Dict[str, Any]:
        """
        Send invoice notification via SuprSend

        Args:
            invoice: Invoice model instance
            channel: Notification channel ('email' or 'whatsapp')

        Returns:
            dict: Result with success status and details
        """
        if not self.api_url:
            error_msg = 'SuprSend not configured. Please set SUPRSEND_WORKSPACE_KEY and SUPRSEND_WORKSPACE_SECRET'
            return {
                'success': False,
                'error': error_msg
            }

        try:
            # Prepare recipient identifier
            if channel == 'email':
                if not invoice.buyer_email:
                    return {'success': False, 'error': 'Buyer email not available'}
                recipient_id = invoice.buyer_email
            elif channel == 'whatsapp':
                if not invoice.buyer_phone:
                    return {'success': False, 'error': 'Buyer phone not available'}
                # Validate and format phone for WhatsApp with proper country code
                is_valid, formatted_phone, error_msg = validate_and_format_phone(invoice.buyer_phone)
                if not is_valid:
                    return {'success': False, 'error': f'Invalid phone number: {error_msg}'}
                recipient_id = formatted_phone
            else:
                return {'success': False, 'error': f'Invalid channel: {channel}'}

            # Get PDF URL
            pdf_url = None
            if invoice.pdf_file:
                # Build absolute URL for PDF
                # In production, use actual domain
                pdf_url = f"http://localhost:8000{invoice.pdf_url or ''}"

            # Prepare workflow data with ALL required template variables
            # The template expects these variables
            workflow_data = {
                # Core invoice data
                'consumer_name': invoice.buyer_name,
                'service_title': f"Invoice {invoice.invoice_number}",
                'testimonial_link': pdf_url or '',

                # Required template variables (populated with invoice seller data)
                'whatsapp_cta': pdf_url or '',
                'reply_to': invoice.seller_email or 'invoices@example.com',
                're_request': False,
                'expert_name': invoice.seller_name,
                'expert_page': invoice.seller_website or 'example.com',
                'call_end_url': pdf_url or '',
                'expert_username': invoice.seller_name.lower().replace(' ', '_'),
                'videocall_info_id_follower_param': f"invoice_{invoice.invoice_number}",
            }

            # Prepare user object (Topmate format)
            user = {
                "distinct_id": recipient_id,
                "$email": [invoice.buyer_email] if invoice.buyer_email else []
            }

            # Add WhatsApp if available (with validation)
            if invoice.buyer_phone:
                is_valid_phone, whatsapp_phone, _ = validate_and_format_phone(invoice.buyer_phone)
                if is_valid_phone:
                    user["$whatsapp"] = [whatsapp_phone]

            # Create workflow trigger payload (Topmate format)
            payload = {
                "name": f"Invoice {invoice.invoice_number} - {channel}",
                "template": settings.suprsend_invoice_template,
                "notification_category": "transactional",
                "users": [user],
                "data": workflow_data
            }

            # Debug logging
            logger.info(f"=== SuprSend Debug ===")
            logger.info(f"Workspace Key: {self.workspace_key}")
            logger.info(f"Invoice: {invoice.invoice_number}")
            logger.info(f"Channel: {channel}")
            logger.info(f"Recipient: {recipient_id}")
            logger.info(f"Workflow: {settings.suprsend_invoice_template}")
            logger.info(f"API URL: {self.api_url}")
            logger.info(f"=== End Debug ===")

            logger.info(f"Triggering SuprSend workflow for invoice {invoice.invoice_number} via {channel}")

            # Prepare headers (SuprSend requires specific format)
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'Date': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
                'User-Agent': 'suprsend/invoice-generator-python'
            }

            # Calculate signature and get JSON content
            content_txt, signature = self._calculate_signature(
                self.api_url,
                'POST',
                payload,
                headers
            )

            # Add Authorization header with workspace_key:signature format
            headers['Authorization'] = f"{self.workspace_key}:{signature}"

            logger.info(f"Authorization: {headers['Authorization'][:30]}...")
            logger.info(f"Date: {headers['Date']}")

            # Send request with httpx (async)
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    content=content_txt.encode('utf-8'),
                    headers=headers
                )

            logger.info(f"=== SuprSend Response ===")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            logger.info(f"Response Body: {response.text}")
            logger.info(f"=== End Response ===")

            # Check if request was successful
            if response.status_code not in [200, 201, 202]:
                error_msg = f'SuprSend API error: {response.status_code} - {response.text}'
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }

            logger.info(f"SuprSend notification sent for invoice {invoice.invoice_number} via {channel}")

            return {
                'success': True,
                'channel': channel,
                'recipient': recipient_id,
                'workflow': settings.suprsend_invoice_template,
                'status_code': response.status_code,
                'response': response.text
            }

        except httpx.HTTPError as e:
            logger.error(f"SuprSend HTTP error for invoice {invoice.invoice_number}: {str(e)}")
            return {
                'success': False,
                'error': f'HTTP error: {str(e)}',
                'channel': channel
            }
        except Exception as e:
            logger.error(f"SuprSend notification failed for invoice {invoice.invoice_number}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'channel': channel
            }

    async def send_invoice_email(self, invoice) -> Dict[str, Any]:
        """
        Send invoice via email using SuprSend

        Args:
            invoice: Invoice model instance

        Returns:
            dict: Result with success status

        Raises:
            EmailSendException: If sending fails
        """
        result = await self.send_invoice_notification(invoice, channel='email')

        if not result.get('success'):
            raise EmailSendException(result.get('error', 'Failed to send email via SuprSend'))

        return result

    async def send_invoice_whatsapp(self, invoice) -> Dict[str, Any]:
        """
        Send invoice via WhatsApp using SuprSend

        Args:
            invoice: Invoice model instance

        Returns:
            dict: Result with success status

        Raises:
            WhatsAppSendException: If sending fails
        """
        result = await self.send_invoice_notification(invoice, channel='whatsapp')

        if not result.get('success'):
            raise WhatsAppSendException(result.get('error', 'Failed to send WhatsApp via SuprSend'))

        return result
