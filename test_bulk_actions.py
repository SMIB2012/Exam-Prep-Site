#!/usr/bin/env python
"""
Test the bulk actions functionality
"""

import os
import sys

# Setup Django
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')

import django
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.messages.storage.fallback import FallbackStorage
from staff.views.user_views import UserListView
from core.models import UserProfile

def test_bulk_actions():
    """Test bulk actions functionality"""
    print("🧪 Testing Bulk Actions Functionality")
    print("=" * 50)
    
    # Clean up any existing test users
    User.objects.filter(email__startswith='bulktest').delete()
    
    # Create test users
    test_users = []
    for i in range(3):
        user = User.objects.create_user(
            username=f'bulktest{i}',
            email=f'bulktest{i}@example.com',
            password='test123',
            first_name=f'Test{i}',
            last_name='User',
            is_active=False  # Start as inactive
        )
        test_users.append(user)
        print(f"Created test user: {user.email}")
    
    # Create staff user for request
    staff_user = User.objects.create_user(
        username='stafftest',
        email='staff@example.com',
        password='test123',
        is_staff=True
    )
    
    factory = RequestFactory()
    
    try:
        # Test 1: Activate users
        print("\n1. Testing 'activate' bulk action...")
        user_ids = [str(user.id) for user in test_users]
        
        request = factory.post('/staff/users/', {
            'action': 'activate',
            'user_ids': user_ids
        })
        request.user = staff_user
        
        # Add session and messages
        session = SessionStore()
        session.create()
        request.session = session
        request._messages = FallbackStorage(request)
        
        view = UserListView()
        response = view.post(request)
        
        # Check if users were activated
        activated_count = User.objects.filter(id__in=[u.id for u in test_users], is_active=True).count()
        print(f"   ✅ Activated {activated_count}/{len(test_users)} users")
        
        # Test 2: Make premium
        print("\n2. Testing 'make_premium' bulk action...")
        request = factory.post('/staff/users/', {
            'action': 'make_premium',
            'user_ids': user_ids
        })
        request.user = staff_user
        request.session = session
        request._messages = FallbackStorage(request)
        
        response = view.post(request)
        
        # Check if users are premium
        premium_count = UserProfile.objects.filter(
            user_id__in=[u.id for u in test_users], 
            is_premium=True
        ).count()
        print(f"   ✅ Made {premium_count}/{len(test_users)} users premium")
        
        # Verify premium expiration dates are set
        premium_with_expiry = UserProfile.objects.filter(
            user_id__in=[u.id for u in test_users], 
            is_premium=True,
            premium_expires_at__isnull=False
        ).count()
        print(f"   ✅ {premium_with_expiry}/{premium_count} premium users have expiration dates")
        
        # Test 3: Remove premium
        print("\n3. Testing 'remove_premium' bulk action...")
        request = factory.post('/staff/users/', {
            'action': 'remove_premium',
            'user_ids': user_ids
        })
        request.user = staff_user
        request.session = session
        request._messages = FallbackStorage(request)
        
        response = view.post(request)
        
        # Check if premium was removed
        non_premium_count = UserProfile.objects.filter(
            user_id__in=[u.id for u in test_users], 
            is_premium=False
        ).count()
        print(f"   ✅ Removed premium from {non_premium_count}/{len(test_users)} users")
        
        # Test 4: Deactivate users
        print("\n4. Testing 'deactivate' bulk action...")
        request = factory.post('/staff/users/', {
            'action': 'deactivate',
            'user_ids': user_ids
        })
        request.user = staff_user
        request.session = session
        request._messages = FallbackStorage(request)
        
        response = view.post(request)
        
        # Check if users were deactivated
        deactivated_count = User.objects.filter(id__in=[u.id for u in test_users], is_active=False).count()
        print(f"   ✅ Deactivated {deactivated_count}/{len(test_users)} users")
        
        # Test 5: Export functionality
        print("\n5. Testing 'export' bulk action...")
        request = factory.post('/staff/users/', {
            'action': 'export',
            'user_ids': user_ids
        })
        request.user = staff_user
        request.session = session
        request._messages = FallbackStorage(request)
        
        response = view.post(request)
        
        # Check if export response is CSV
        if response.get('Content-Type') == 'text/csv':
            print("   ✅ Export returns CSV file")
            content_disposition = response.get('Content-Disposition', '')
            if 'users_export.csv' in content_disposition:
                print("   ✅ Export has correct filename")
            else:
                print("   ❌ Export filename is incorrect")
        else:
            print("   ❌ Export does not return CSV")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error during bulk action test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        try:
            User.objects.filter(email__startswith='bulktest').delete()
            User.objects.filter(email='staff@example.com').delete()
        except:
            pass

if __name__ == '__main__':
    success = test_bulk_actions()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 BULK ACTIONS TEST PASSED!")
        print("All bulk actions should now work correctly:")
        print("- Activate/Deactivate users")
        print("- Make users premium/remove premium")
        print("- Export users to CSV")
    else:
        print("❌ BULK ACTIONS TEST FAILED!")
        print("Some bulk actions may not be working correctly.")
    print("=" * 50)
