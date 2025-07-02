#!/usr/bin/env python
"""
Comprehensive test to verify bulk actions and check the actual user interface
"""
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile
from django.test import Client
from django.urls import reverse

def comprehensive_test():
    """Test bulk actions comprehensively"""
    print("=== Comprehensive Bulk Actions Test ===\n")
    
    # Clean up
    User.objects.filter(username__startswith='testuser').delete()
    User.objects.filter(username='testadmin').delete()
    
    # Create admin
    admin = User.objects.create_user(
        username='testadmin',
        email='admin@test.com',
        password='testpass123',
        is_staff=True,
        is_superuser=True
    )
    
    # Create test users
    users = []
    for i in range(5):
        user = User.objects.create_user(
            username=f'testuser{i}',
            email=f'user{i}@test.com',
            password='testpass123',
            first_name=f'Test{i}',
            last_name=f'User{i}',
            is_active=True
        )
        users.append(user)
        print(f"Created user: {user.username} (ID: {user.id})")
    
    client = Client()
    client.login(username='testadmin', password='testpass123')
    
    print("\n--- Test 1: Make Premium ---")
    user_ids = [users[0].id, users[1].id]
    response = client.post('/staff/users/', {
        'action': 'make_premium',
        'user_ids': user_ids,
    })
    
    print(f"Response: {response.status_code}")
    
    # Check results
    for user_id in user_ids:
        user = User.objects.get(id=user_id)
        profile = user.userprofile
        status = "✓ Premium" if profile.is_premium else "✗ Not Premium"
        expiry = profile.premium_expires_at.strftime('%Y-%m-%d') if profile.premium_expires_at else "No expiry"
        print(f"  {user.username}: {status} (expires: {expiry})")
    
    print("\n--- Test 2: Remove Premium ---")
    response = client.post('/staff/users/', {
        'action': 'remove_premium',
        'user_ids': user_ids,
    })
    
    print(f"Response: {response.status_code}")
    
    # Check results
    for user_id in user_ids:
        user = User.objects.get(id=user_id)
        profile = user.userprofile
        status = "✗ Not Premium" if not profile.is_premium else "✓ Still Premium"
        print(f"  {user.username}: {status}")
    
    print("\n--- Test 3: Deactivate Users ---")
    response = client.post('/staff/users/', {
        'action': 'deactivate',
        'user_ids': user_ids,
    })
    
    print(f"Response: {response.status_code}")
    
    # Check results
    for user_id in user_ids:
        user = User.objects.get(id=user_id)
        status = "✗ Inactive" if not user.is_active else "✓ Still Active"
        print(f"  {user.username}: {status}")
    
    print("\n--- Test 4: Activate Users ---")
    response = client.post('/staff/users/', {
        'action': 'activate',
        'user_ids': user_ids,
    })
    
    print(f"Response: {response.status_code}")
    
    # Check results
    for user_id in user_ids:
        user = User.objects.get(id=user_id)
        status = "✓ Active" if user.is_active else "✗ Still Inactive"
        print(f"  {user.username}: {status}")
    
    print("\n--- Test 5: Check User List Page ---")
    response = client.get('/staff/users/')
    print(f"User list page status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check if our test users appear in the list
        print("Users found in HTML:")
        for user in users[:3]:  # Check first 3
            if user.username in content:
                # Check for premium status
                user_start = content.find(user.username)
                user_section = content[user_start:user_start+500]  # Get section around username
                
                is_premium = 'Premium' in user_section
                is_active = 'Active' in user_section and 'Inactive' not in user_section
                
                print(f"  {user.username}: Premium={is_premium}, Active={is_active}")
            else:
                print(f"  {user.username}: NOT FOUND IN HTML")
        
        # Check for CSRF token
        has_csrf = 'csrfmiddlewaretoken' in content
        print(f"\nCSRF token present: {has_csrf}")
        
        # Check for bulk action elements
        has_bulk_select = 'bulkActionSelect' in content
        has_bulk_button = 'applyBulkAction' in content
        print(f"Bulk action select: {has_bulk_select}")
        print(f"Bulk action button: {has_bulk_button}")
    
    print("\n--- Current Database State ---")
    all_users = User.objects.all().order_by('username')
    for user in all_users:
        if hasattr(user, 'userprofile'):
            profile = user.userprofile
            premium = "Premium" if profile.is_premium else "Free"
            active = "Active" if user.is_active else "Inactive"
            print(f"  {user.username:15s} | {active:8s} | {premium:7s} | Staff: {user.is_staff}")
    
    # Clean up
    User.objects.filter(username__startswith='testuser').delete()
    User.objects.filter(username='testadmin').delete()
    print("\n✅ Test complete, cleaned up")

if __name__ == '__main__':
    comprehensive_test()
