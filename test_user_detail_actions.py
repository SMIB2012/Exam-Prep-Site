#!/usr/bin/env python
"""
Test script to verify all user detail page actions work correctly
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
import json

def test_user_detail_actions():
    """Test all user detail page actions"""
    print("🔧 Testing User Detail Page Actions")
    print("=" * 50)
    
    try:
        # Create a test user
        test_user, created = User.objects.get_or_create(
            username='test_detail_user',
            defaults={
                'email': 'test_detail@example.com',
                'first_name': 'Test',
                'last_name': 'Detail',
                'is_active': True
            }
        )
        
        if created:
            print(f"✓ Created test user: {test_user.username}")
        else:
            print(f"✓ Using existing test user: {test_user.username}")
        
        # Create staff user
        staff_user, created = User.objects.get_or_create(
            username='staff_detail_test',
            defaults={
                'email': 'staff_detail@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        staff_user.set_password('testpass123')
        staff_user.save()
        
        # Test client
        client = Client()
        client.login(username='staff_detail_test', password='testpass123')
        print("✓ Logged in as staff user")
        
        # Get detail page URL
        detail_url = reverse('staff:user_detail', kwargs={'pk': test_user.id})
        print(f"✓ Detail URL: {detail_url}")
        
        # Test 1: Toggle User Status
        print("\n🔄 Testing Toggle User Status...")
        response = client.post(detail_url, {
            'action': 'toggle_status',
            'status': 'false'
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Suspend user: {data.get('message')}")
            else:
                print(f"❌ Suspend failed: {data.get('message')}")
        else:
            print(f"❌ Suspend failed: HTTP {response.status_code}")
        
        # Test 2: Toggle Premium Status
        print("\n👑 Testing Toggle Premium Status...")
        response = client.post(detail_url, {
            'action': 'toggle_premium',
            'is_premium': 'true'
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Make premium: {data.get('message')}")
            else:
                print(f"❌ Make premium failed: {data.get('message')}")
        else:
            print(f"❌ Make premium failed: HTTP {response.status_code}")
        
        # Test 3: Send Welcome Email
        print("\n📧 Testing Send Welcome Email...")
        response = client.post(detail_url, {
            'action': 'send_welcome_email'
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Welcome email: {data.get('message')}")
            else:
                print(f"❌ Welcome email failed: {data.get('message')}")
        else:
            print(f"❌ Welcome email failed: HTTP {response.status_code}")
        
        # Test 4: Reset Password
        print("\n🔑 Testing Reset Password...")
        response = client.post(detail_url, {
            'action': 'reset_password'
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Reset password: {data.get('message')}")
            else:
                print(f"❌ Reset password failed: {data.get('message')}")
        else:
            print(f"❌ Reset password failed: HTTP {response.status_code}")
        
        # Test 5: Export User Data
        print("\n📊 Testing Export User Data...")
        export_url = reverse('staff:user_export', kwargs={'pk': test_user.id})
        response = client.get(export_url)
        
        if response.status_code == 200:
            content_type = response.get('Content-Type', '')
            if 'csv' in content_type:
                print("✅ Export user data: CSV file generated successfully")
                disposition = response.get('Content-Disposition', '')
                print(f"   File: {disposition}")
            else:
                print(f"⚠ Export unexpected content type: {content_type}")
        else:
            print(f"❌ Export failed: HTTP {response.status_code}")
        
        # Test 6: Detail Page GET
        print("\n📄 Testing Detail Page Load...")
        response = client.get(detail_url)
        
        if response.status_code == 200:
            print("✅ Detail page loads successfully")
            
            # Check if action buttons are present
            content = response.content.decode()
            if 'toggleUserStatus' in content:
                print("✅ Toggle status button present")
            if 'togglePremiumStatus' in content:
                print("✅ Toggle premium button present")
            if 'sendWelcomeEmail' in content:
                print("✅ Send welcome email button present")
            if 'resetPassword' in content:
                print("✅ Reset password button present")
            if 'exportUserData' in content:
                print("✅ Export user data button present")
        else:
            print(f"❌ Detail page failed: HTTP {response.status_code}")
        
        print("\n🎉 User Detail Actions Test Complete!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error testing user detail actions: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_user_detail_actions()
