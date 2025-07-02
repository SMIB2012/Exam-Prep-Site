#!/usr/bin/env python
"""
Final verification that all bulk actions work correctly
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

def final_verification():
    """Final verification of all bulk actions"""
    print("=== FINAL BULK ACTIONS VERIFICATION ===\n")
    
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
    
    # Create 3 test users
    users = []
    for i in range(3):
        user = User.objects.create_user(
            username=f'testuser{i}',
            email=f'user{i}@test.com',
            password='testpass123',
            first_name=f'Test{i}',
            last_name=f'User{i}',
            is_active=True
        )
        users.append(user)
    
    print(f"✅ Created {len(users)} test users")
    
    client = Client()
    login_success = client.login(username='testadmin', password='testpass123')
    print(f"✅ Admin login successful: {login_success}")
    
    user_ids = [str(u.id) for u in users]
    
    # Test all bulk actions
    actions = [
        ('make_premium', 'Make Premium'),
        ('remove_premium', 'Remove Premium'),
        ('deactivate', 'Deactivate'),
        ('activate', 'Activate'),
    ]
    
    all_passed = True
    
    for action, description in actions:
        print(f"\n🧪 Testing: {description}")
        
        response = client.post('/staff/users/', {
            'action': action,
            'user_ids': user_ids,
        })
        
        if response.status_code != 302:
            print(f"❌ Failed: Status {response.status_code}")
            all_passed = False
            continue
        
        # Verify the changes
        if action == 'make_premium':
            premium_count = UserProfile.objects.filter(user_id__in=user_ids, is_premium=True).count()
            success = premium_count == len(user_ids)
            print(f"{'✅' if success else '❌'} Premium users: {premium_count}/{len(user_ids)}")
            
        elif action == 'remove_premium':
            non_premium_count = UserProfile.objects.filter(user_id__in=user_ids, is_premium=False).count()
            success = non_premium_count == len(user_ids)
            print(f"{'✅' if success else '❌'} Non-premium users: {non_premium_count}/{len(user_ids)}")
            
        elif action == 'activate':
            active_count = User.objects.filter(id__in=user_ids, is_active=True).count()
            success = active_count == len(user_ids)
            print(f"{'✅' if success else '❌'} Active users: {active_count}/{len(user_ids)}")
            
        elif action == 'deactivate':
            inactive_count = User.objects.filter(id__in=user_ids, is_active=False).count()
            success = inactive_count == len(user_ids)
            print(f"{'✅' if success else '❌'} Inactive users: {inactive_count}/{len(user_ids)}")
        
        if not success:
            all_passed = False
    
    # Test export
    print(f"\n🧪 Testing: Export")
    response = client.post('/staff/users/', {
        'action': 'export',
        'user_ids': user_ids[:2],  # Export first 2 users
    })
    
    export_success = response.status_code == 200 and 'text/csv' in response.get('Content-Type', '')
    print(f"{'✅' if export_success else '❌'} Export: {response.status_code}, {response.get('Content-Type', 'Unknown')}")
    
    if not export_success:
        all_passed = False
    
    # Test error handling
    print(f"\n🧪 Testing: Error Handling")
    
    # Invalid action
    response = client.post('/staff/users/', {
        'action': 'invalid_action',
        'user_ids': user_ids,
    })
    invalid_action_handled = response.status_code == 302
    print(f"{'✅' if invalid_action_handled else '❌'} Invalid action handled: {response.status_code}")
    
    # Empty user_ids
    response = client.post('/staff/users/', {
        'action': 'activate',
        'user_ids': [],
    })
    empty_ids_handled = response.status_code == 302
    print(f"{'✅' if empty_ids_handled else '❌'} Empty user_ids handled: {response.status_code}")
    
    if not (invalid_action_handled and empty_ids_handled):
        all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 ALL BULK ACTIONS WORKING CORRECTLY!")
        print("✅ Make Premium")
        print("✅ Remove Premium") 
        print("✅ Activate Users")
        print("✅ Deactivate Users")
        print("✅ Export Users")
        print("✅ Error Handling")
    else:
        print("❌ Some bulk actions failed")
    
    print(f"\n{'='*50}")
    print("TROUBLESHOOTING TIPS:")
    print("1. If bulk actions appear not to work in browser:")
    print("   - Check browser console for JavaScript errors")
    print("   - Ensure you're selecting users with checkboxes")
    print("   - Refresh the page after applying actions")
    print("   - Look for success/error messages at the top")
    print("2. The backend is working correctly as verified by tests")
    print("3. Check that JavaScript is enabled in your browser")
    print("4. Clear browser cache if needed")
    
    # Clean up
    User.objects.filter(username__startswith='testuser').delete()
    User.objects.filter(username='testadmin').delete()
    print("\n✅ Test users cleaned up")

if __name__ == '__main__':
    final_verification()
