"""
Test script to verify email configuration
Run this from the backend directory: python test_email.py
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoice_api.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email():
    """Send a test email to verify configuration"""
    print("=" * 60)
    print("Testing Email Configuration")
    print("=" * 60)
    print(f"From: {settings.DEFAULT_FROM_EMAIL}")
    print(f"Host: {settings.EMAIL_HOST}")
    print(f"Port: {settings.EMAIL_PORT}")
    print(f"User: {settings.EMAIL_HOST_USER}")
    print("=" * 60)

    # Get recipient email
    recipient = input("\nEnter recipient email address (or press Enter to send to yourself): ").strip()

    if not recipient:
        recipient = settings.EMAIL_HOST_USER
        print(f"Sending test email to: {recipient}")

    try:
        # Send test email
        send_mail(
            subject='Test Email from Django Invoice App',
            message='Hello!\n\nThis is a test email from your Django Invoice application.\n\nIf you received this, your email configuration is working correctly!\n\nBest regards,\nInvoice App',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )

        print("\n" + "=" * 60)
        print("✅ SUCCESS! Email sent successfully!")
        print("=" * 60)
        print(f"Check the inbox of: {recipient}")
        print("If you don't see it, check your spam folder.")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ERROR! Failed to send email")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print("\nPossible issues:")
        print("1. App Password might be incorrect")
        print("2. Gmail account might need additional verification")
        print("3. Internet connection issue")
        print("=" * 60)

if __name__ == "__main__":
    test_email()
