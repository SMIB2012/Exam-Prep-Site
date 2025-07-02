#!/usr/bin/env python
"""
Test bulk actions with live debugging
"""
import os
import django
import sys
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import UserProfile

def test_with_live_server():
    """Test bulk actions with server running"""
    print("=== Live Server Test ===\n")
    
    # Clean up and create test users
    User.objects.filter(username__startswith='testuser').delete()
    User.objects.filter(username='testadmin').delete()
    
    # Create admin user
    admin_user = User.objects.create_user(
        username='testadmin',
        email='admin@test.com',
        password='testpass123',
        is_staff=True,
        is_superuser=True
    )
    
    # Create test users
    test_users = []
    for i in range(3):
        user = User.objects.create_user(
            username=f'testuser{i}',
            email=f'user{i}@test.com',
            password='testpass123',
            first_name=f'Test{i}',
            last_name=f'User{i}',
            is_active=True
        )
        test_users.append(user)
    
    print(f"Created admin and {len(test_users)} test users")
    
    # Test with live POST request
    client = Client()
    login_success = client.login(username='testadmin', password='testpass123')
    print(f"Admin login: {'✓' if login_success else '✗'}")
    
    if login_success:
        user_ids = [str(u.id) for u in test_users[:2]]
        
        print(f"Testing make_premium action on users: {user_ids}")
        
        response = client.post('/staff/users/', {
            'action': 'make_premium',
            'user_ids': user_ids,
        }, follow=True)
        
        print(f"Response status: {response.status_code}")
        print(f"Final URL: {response.request['PATH_INFO']}")
        
        # Check if users were made premium
        for user_id in user_ids:
            user = User.objects.get(id=user_id)
            profile = user.userprofile
            premium_status = "Premium" if profile.is_premium else "Free"
            print(f"User {user.username}: {premium_status}")
        
        print("\nNow test through actual form submission...")
        
        # Get the user list page to see the actual form
        response = client.get('/staff/users/')
        print(f"User list page status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            csrf_token_start = content.find('name="csrfmiddlewaretoken" value="')
            if csrf_token_start != -1:
                csrf_token_start += len('name="csrfmiddlewaretoken" value="')
                csrf_token_end = content.find('"', csrf_token_start)
                csrf_token = content[csrf_token_start:csrf_token_end]
                print(f"Found CSRF token: {csrf_token[:20]}...")
                
                # Test with the actual CSRF token
                response = client.post('/staff/users/', {
                    'csrfmiddlewaretoken': csrf_token,
                    'action': 'activate',
                    'user_ids': user_ids,
                })
                
                print(f"POST with CSRF token status: {response.status_code}")
            else:
                print("❌ CSRF token not found in page")
    
    # Clean up
    User.objects.filter(username__startswith='testuser').delete()
    User.objects.filter(username='testadmin').delete()
    print("\n✅ Test complete, cleaned up")

if __name__ == '__main__':
    test_with_live_server()
