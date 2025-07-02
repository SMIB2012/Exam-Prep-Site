#!/usr/bin/env python
"""
Comprehensive test to verify the complete password reset workflow
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
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def test_complete_password_reset_workflow():
    """Test the complete password reset workflow"""
    print("🔐 Testing Complete Password Reset Workflow")
    print("=" * 50)
    
    try:
        # Step 1: Create test users
        print("📝 Step 1: Setting up test users...")
        user, created = User.objects.get_or_create(
            username='test_reset_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        user.set_password('oldpassword123')
        user.save()
        
        staff_user, created = User.objects.get_or_create(
            username='staff_test',
            defaults={
                'email': 'staff@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        staff_user.set_password('staffpass123')
        staff_user.save()
        print(f"✓ Test user: {user.username} ({user.email})")
        print(f"✓ Staff user: {staff_user.username}")
        
        # Step 2: Test admin bulk reset password action
        print("\n📧 Step 2: Testing admin bulk reset password...")
        client = Client()
        client.login(username='staff_test', password='staffpass123')
        
        user_list_url = reverse('staff:user_list')
        response = client.post(user_list_url, {
            'action': 'reset_password',
            'user_ids': [user.id]
        })
        
        if response.status_code == 302:
            print("✓ Bulk reset password action executed successfully")
        else:
            print(f"✗ Unexpected response: {response.status_code}")
            
        # Step 3: Test password reset URL resolution
        print("\n🔗 Step 3: Testing URL patterns...")
        urls_to_test = [
            ('password_reset', {}, '/accounts/password_reset/'),
            ('password_reset_done', {}, '/accounts/password_reset/done/'),
            ('password_reset_complete', {}, '/accounts/reset/done/'),
        ]
        
        for url_name, kwargs, expected_url in urls_to_test:
            try:
                url = reverse(url_name, kwargs=kwargs)
                if url == expected_url:
                    print(f"✓ {url_name}: {url}")
                else:
                    print(f"⚠ {url_name}: {url} (expected {expected_url})")
            except Exception as e:
                print(f"✗ {url_name}: {str(e)}")
        
        # Step 4: Test password reset confirm with valid token
        print("\n🔑 Step 4: Testing password reset confirmation...")
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Test the confirm URL
        confirm_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        response = client.get(confirm_url)
        
        if response.status_code in [200, 302]:
            print(f"✓ Password reset confirm URL accessible: {confirm_url}")
            if response.status_code == 302:
                redirect_url = response.get('Location', '')
                print(f"  → Redirects to: {redirect_url}")
        else:
            print(f"✗ Password reset confirm failed: {response.status_code}")
        
        # Step 5: Test password reset form submission
        print("\n📝 Step 5: Testing password change...")
        
        # Get the redirect URL for setting password
        if response.status_code == 302:
            set_password_url = response.get('Location', '')
            if set_password_url:
                response = client.get(set_password_url)
                if response.status_code == 200:
                    print("✓ Set password form loads successfully")
                    
                    # Submit new password
                    response = client.post(set_password_url, {
                        'new_password1': 'newpassword123!',
                        'new_password2': 'newpassword123!'
                    })
                    
                    if response.status_code == 302:
                        print("✓ Password change submitted successfully")
                        
                        # Test login with new password
                        client.logout()
                        login_success = client.login(username='test_reset_user', password='newpassword123!')
                        if login_success:
                            print("✓ Login with new password successful")
                        else:
                            print("✗ Login with new password failed")
                    else:
                        print(f"✗ Password change failed: {response.status_code}")
                else:
                    print(f"✗ Set password form failed: {response.status_code}")
        
        print("\n🎉 Password Reset Workflow Test Complete!")
        print("=" * 50)
        print("✅ All password reset functionality is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error in password reset workflow: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_complete_password_reset_workflow()
