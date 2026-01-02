# WhatsApp Integration Setup Guide

This guide explains how to set up WhatsApp integration to send invoice PDFs directly to clients.

## Important Note

**WhatsApp Web API (`wa.me` links) CANNOT send files directly.** They can only open WhatsApp with pre-filled text messages.

To send PDF files directly via WhatsApp, you need to use **Twilio WhatsApp API** or **WhatsApp Business API**.

## Current Implementation

The system has TWO modes:

### 1. **Fallback Mode** (Default - No Twilio Setup Required)
- Opens WhatsApp with a message containing a PDF download link
- **Limitation**: PDF link shows `http://localhost:8000` which won't work for recipients
- **Solution**: Deploy backend to a public server OR use Twilio

### 2. **Twilio Mode** (Recommended - Sends PDF Directly)
- Sends PDF file directly as WhatsApp attachment
- No manual chat opening required
- Professional delivery

---

## Setup Twilio WhatsApp API (Recommended)

### Step 1: Create Twilio Account
1. Go to https://www.twilio.com/try-twilio
2. Sign up for a free account
3. Complete phone verification

### Step 2: Get Credentials
1. Go to https://console.twilio.com/
2. Find your **Account SID** and **Auth Token** on the dashboard
3. Copy these values

### Step 3: Setup WhatsApp Sandbox (For Testing)
1. In Twilio Console, go to **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Follow instructions to connect your WhatsApp number to the sandbox
3. Send the join code (e.g., "join <code>") to the Twilio WhatsApp number
4. Note the **Sandbox WhatsApp Number** (e.g., `whatsapp:+14155238886`)

### Step 4: Configure Your Application

Edit `backend/invoice_api/settings.py`:

```python
# Twilio Configuration for WhatsApp
TWILIO_ACCOUNT_SID = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxx'  # Your Account SID
TWILIO_AUTH_TOKEN = 'your_auth_token_here'          # Your Auth Token
TWILIO_WHATSAPP_FROM = 'whatsapp:+14155238886'      # Twilio Sandbox number
```

### Step 5: Deploy Backend to Public Server

**The PDF file must be accessible from the internet.**

Options:
- Deploy to **Heroku**, **Railway**, **Render**, **DigitalOcean**, or **AWS**
- Use **ngrok** for temporary testing: `ngrok http 8000`

Update Django settings:
```python
ALLOWED_HOSTS = ['your-domain.com', 'your-app.herokuapp.com']
MEDIA_URL = 'https://your-domain.com/media/'
```

### Step 6: Test
1. Restart Django server
2. Generate an invoice
3. Click "WhatsApp" button
4. PDF should be sent directly to the client's WhatsApp

---

## Production Setup (After Testing)

### Get Approved WhatsApp Number
1. In Twilio Console, go to **Messaging** → **Senders** → **WhatsApp senders**
2. Click **Request to use your Twilio number with WhatsApp**
3. Complete the application process
4. Update `TWILIO_WHATSAPP_FROM` with your approved number

### Phone Number Format
Client phone numbers should be in international format:
- **Correct**: `919876543210` (country code + number, no spaces/symbols)
- **Correct**: `+919876543210`
- **Incorrect**: `9876543210` (missing country code)
- **Incorrect**: `+91 98765 43210` (has spaces)

---

## Email Alternative (Works Out of the Box)

Email integration **sends PDF attachments directly** without any external service:

### For Development (Console Backend - Current Setup)
- Emails print to Django console
- No SMTP configuration needed

### For Production (SMTP)
Edit `backend/invoice_api/settings.py`:

```python
# Uncomment and configure:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Get from Gmail App Passwords
```

**Gmail App Password Setup:**
1. Go to https://myaccount.google.com/apppasswords
2. Generate an app password for "Mail"
3. Use that password in settings

---

## Troubleshooting

### WhatsApp shows localhost URL
- **Problem**: PDF link is `http://localhost:8000/media/...`
- **Solution**: Deploy backend to public server or use ngrok

### Twilio Error: "Unable to create record"
- **Problem**: Twilio credentials not configured
- **Solution**: Set `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` in settings

### WhatsApp not received
- **Problem**: Phone number format incorrect
- **Solution**: Use format `919876543210` (country code + number)

### PDF not accessible
- **Problem**: Media files not served correctly
- **Solution**: Configure `MEDIA_URL` and `MEDIA_ROOT` properly, ensure server serves media files

---

## Cost

### Twilio WhatsApp Messaging
- **Sandbox**: Free for testing
- **Production**: ~$0.005 per message (₹0.40 per message)
- Free trial credit: $15 (3000 messages)

### Email (SMTP)
- **Gmail**: Free (up to 500 emails/day)
- **SendGrid**: Free (up to 100 emails/day)

---

## Alternative: WhatsApp Cloud API (Meta)

If you don't want to use Twilio, you can use Meta's WhatsApp Cloud API:
- https://developers.facebook.com/docs/whatsapp/cloud-api/

**Pros**: Official Meta API, similar pricing
**Cons**: More complex setup, requires business verification

---

## Summary

✅ **Email**: Works immediately, sends PDF attachments
⚠️ **WhatsApp (No Twilio)**: Opens chat with localhost link (won't work for recipients)
✅ **WhatsApp (With Twilio)**: Sends PDF directly to client's WhatsApp

**Recommended Setup:**
1. Use **Email** for immediate PDF delivery
2. Setup **Twilio WhatsApp** for professional WhatsApp delivery
3. Deploy backend to public server for either method to work properly
