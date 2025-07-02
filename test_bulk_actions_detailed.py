#!/usr/bin/env python
"""
Detailed test for bulk actions functionality
"""
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import UserProfile
from django.utils import timezone
from datetime import timedelta

def test_bulk_actions():
    """Test all bulk actions functionality"""
    print("=== Testing Bulk Actions Functionality ===\n")
    
    # Create test client
    client = Client()
    
    # Clean up any existing test users first
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
    
    print(f"Created {len(test_users)} test users")
    
    # Login as admin
    login_success = client.login(username='testadmin', password='testpass123')
    print(f"Admin login successful: {login_success}")
    
    if not login_success:
        print("❌ Failed to login as admin")
        return
    
    # Test GET request to user list page
    print("\n1. Testing GET request to user list page...")
    response = client.get(reverse('staff:user_list'))
    print(f"   Status code: {response.status_code}")
    print(f"   Template used: {response.templates[0].name if response.templates else 'None'}")
    
    if response.status_code != 200:
        print("❌ Failed to load user list page")
        return
    
    # Test bulk activate action
    print("\n2. Testing bulk activate action...")
    user_ids = [str(user.id) for user in test_users[:2]]  # First 2 users
    
    # First deactivate them
    for user in test_users[:2]:
        user.is_active = False
        user.save()
    
    response = client.post(reverse('staff:user_list'), {
        'action': 'activate',
        'user_ids': user_ids,
    })
    
    print(f"   Response status: {response.status_code}")
    print(f"   Response location: {response.get('Location', 'No redirect')}")
    
    # Check if users were activated
    activated_users = User.objects.filter(id__in=user_ids, is_active=True).count()
    print(f"   Users activated: {activated_users}/{len(user_ids)}")
    
    # Test bulk deactivate action
    print("\n3. Testing bulk deactivate action...")
    response = client.post(reverse('staff:user_list'), {
        'action': 'deactivate',
        'user_ids': user_ids,
    })
    
    print(f"   Response status: {response.status_code}")
    deactivated_users = User.objects.filter(id__in=user_ids, is_active=False).count()
    print(f"   Users deactivated: {deactivated_users}/{len(user_ids)}")
    
    # Test bulk make premium action
    print("\n4. Testing bulk make premium action...")
    response = client.post(reverse('staff:user_list'), {
        'action': 'make_premium',
        'user_ids': user_ids,
    })
    
    print(f"   Response status: {response.status_code}")
    premium_users = UserProfile.objects.filter(user_id__in=user_ids, is_premium=True).count()
    print(f"   Users made premium: {premium_users}/{len(user_ids)}")
    
    # Test bulk remove premium action
    print("\n5. Testing bulk remove premium action...")
    response = client.post(reverse('staff:user_list'), {
        'action': 'remove_premium',
        'user_ids': user_ids,
    })
    
    print(f"   Response status: {response.status_code}")
    non_premium_users = UserProfile.objects.filter(user_id__in=user_ids, is_premium=False).count()
    print(f"   Users premium removed: {non_premium_users}/{len(user_ids)}")
    
    # Test export action
    print("\n6. Testing export action...")
    response = client.post(reverse('staff:user_list'), {
        'action': 'export',
        'user_ids': user_ids,
    })
    
    print(f"   Response status: {response.status_code}")
    print(f"   Content type: {response.get('Content-Type', 'Unknown')}")
    
    if response.status_code == 200 and 'text/csv' in response.get('Content-Type', ''):
        print("   ✅ Export working correctly")
    else:
        print("   ❌ Export failed")
    
    # Test invalid action
    print("\n7. Testing invalid action...")
    response = client.post(reverse('staff:user_list'), {
        'action': 'invalid_action',
        'user_ids': user_ids,
    })
    
    print(f"   Response status: {response.status_code}")
    print("   Should redirect with error message")
    
    # Test empty user_ids
    print("\n8. Testing empty user_ids...")
    response = client.post(reverse('staff:user_list'), {
        'action': 'activate',
        'user_ids': [],
    })
    
    print(f"   Response status: {response.status_code}")
    print("   Should redirect with error message")
    
    print("\n=== Test Complete ===")
    
    # Clean up
    User.objects.filter(username__startswith='testuser').delete()
    User.objects.filter(username='testadmin').delete()
    
    print("✅ Test users cleaned up")

if __name__ == '__main__':
    test_bulk_actions()
