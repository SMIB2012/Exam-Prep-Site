#!/usr/bin/env python
"""
Test script to simulate the reset password action and identify the issue
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

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse

def test_reset_password_action():
    """Test the reset password bulk action"""
    print("Testing reset password action...")
    
    try:
        # Create a test user if needed
        user, created = User.objects.get_or_create(
            username='test_reset_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            print(f"Created test user: {user.username}")
        else:
            print(f"Using existing test user: {user.username}")
        
        # Create a client and login as staff
        client = Client()
        
        # Create or get a staff user
        staff_user, created = User.objects.get_or_create(
            username='staff_test',
            defaults={
                'email': 'staff@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        staff_user.set_password('testpass123')
        staff_user.save()
        
        # Login as staff
        client.login(username='staff_test', password='testpass123')
        print("Logged in as staff user")
        
        # Get the user list URL
        user_list_url = reverse('staff:user_list')
        print(f"User list URL: {user_list_url}")
        
        # Test the bulk action
        response = client.post(user_list_url, {
            'action': 'reset_password',
            'user_ids': [user.id]
        })
        
        print(f"Response status: {response.status_code}")
        print(f"Response redirect: {response.get('Location', 'No redirect')}")
        
        # Check messages
        if hasattr(response, 'wsgi_request'):
            messages = list(get_messages(response.wsgi_request))
            for message in messages:
                print(f"Message: {message}")
        
        print("Reset password action completed successfully!")
        
    except Exception as e:
        print(f"Error testing reset password action: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_reset_password_action()
