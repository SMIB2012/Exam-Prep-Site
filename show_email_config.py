#!/usr/bin/env python
"""
Email Configuration Summary and Test for MedPrep
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.core.mail import send_mail
from django.contrib.auth.models import User

def show_email_configuration():
    """Display current email configuration"""
    print("📧 MedPrep Email Configuration")
    print("=" * 50)
    
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    print(f"Email Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"Email Port: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"Use TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    print(f"Host User: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    print(f"Default From Email: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
    print(f"Server Email: {getattr(settings, 'SERVER_EMAIL', 'Not set')}")
    
    print("\n📝 Current Status:")
    if 'console' in settings.EMAIL_BACKEND:
        print("✅ DEVELOPMENT MODE - Emails printed to console")
        print("   → Safe for testing, no real emails sent")
        print("   → Password reset emails appear in terminal")
    else:
        print("📤 PRODUCTION MODE - Real emails will be sent")
        print("   → Emails sent via SMTP server")
        print("   → Make sure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are set")
    
    print("\n🔧 To Enable Real Email Sending:")
    print("1. Create a .env file based on .env.example")
    print("2. Set your Gmail address and app password")
    print("3. Change EMAIL_BACKEND to 'django.core.mail.backends.smtp.EmailBackend'")
    print("4. Restart the server")
    
    print("\n📋 Gmail Setup for Production:")
    print("1. Enable 2-Factor Authentication on Gmail")
    print("2. Generate an App Password (not your regular password)")
    print("3. Use the App Password in EMAIL_HOST_PASSWORD")
    print("4. Set EMAIL_HOST_USER to your Gmail address")

def test_email_sending():
    """Test email sending with current configuration"""
    print("\n🧪 Testing Email Functionality...")
    
    try:
        # Try to send a test email
        result = send_mail(
            subject='MedPrep Test Email',
            message='This is a test email from MedPrep platform.',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@medprep.com'),
            recipient_list=['test@example.com'],
            fail_silently=False,
        )
        
        if 'console' in settings.EMAIL_BACKEND:
            print("✅ Email function works (printed above in console)")
        else:
            print(f"✅ Email sent successfully! Result: {result}")
            
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")

if __name__ == '__main__':
    show_email_configuration()
    test_email_sending()
