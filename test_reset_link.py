#!/usr/bin/env python
"""
Test script to verify password reset link functionality
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

from django.test import Client
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse

def test_password_reset_link():
    """Test if password reset links work correctly"""
    print("Testing password reset link functionality...")
    
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='test_reset_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Generate password reset token and uid
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        print(f"Generated UID: {uid}")
        print(f"Generated Token: {token}")
        
        # Test the password reset confirm URL
        reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        print(f"Reset URL: {reset_url}")
        
        # Test with client
        client = Client()
        response = client.get(reset_url)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Password reset confirm page loads successfully")
            
            # Check if it's the set password form
            content = response.content.decode()
            if 'new_password1' in content:
                print("✓ Password reset form is displayed")
            else:
                print("✗ Password reset form not found in response")
                
        elif response.status_code == 302:
            print(f"Redirect to: {response.get('Location', 'Unknown')}")
        else:
            print(f"✗ Unexpected response status: {response.status_code}")
            
        # Test token validation
        if default_token_generator.check_token(user, token):
            print("✓ Token is valid")
        else:
            print("✗ Token is invalid")
            
    except Exception as e:
        print(f"Error testing password reset link: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_password_reset_link()
