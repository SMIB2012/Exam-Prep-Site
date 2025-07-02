#!/usr/bin/env python
"""
Test script to verify password reset URL patterns are working
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

from django.urls import reverse, resolve
from django.test import RequestFactory
from django.contrib.auth.models import User

def test_password_reset_urls():
    """Test all password reset related URLs"""
    print("Testing password reset URL patterns...")
    
    try:
        # Test password reset URLs
        urls_to_test = [
            ('password_reset', {}),
            ('password_reset_done', {}),
            ('password_reset_confirm', {'uidb64': 'test', 'token': 'test'}),
            ('password_reset_complete', {}),
        ]
        
        for url_name, kwargs in urls_to_test:
            try:
                url = reverse(url_name, kwargs=kwargs)
                print(f"✓ {url_name}: {url}")
            except Exception as e:
                print(f"✗ {url_name}: {str(e)}")
        
        # Test if the URLs resolve correctly
        print("\nTesting URL resolution...")
        test_urls = [
            '/accounts/password_reset/',
            '/accounts/password_reset/done/',
            '/accounts/reset/test/test/',
            '/accounts/reset/done/',
        ]
        
        for url in test_urls:
            try:
                resolved = resolve(url)
                print(f"✓ {url}: {resolved.url_name}")
            except Exception as e:
                print(f"✗ {url}: {str(e)}")
                
    except Exception as e:
        print(f"Error testing URLs: {str(e)}")

if __name__ == '__main__':
    test_password_reset_urls()
