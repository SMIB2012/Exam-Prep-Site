#!/usr/bin/env python
"""
Quick test to check pagination and Add User button issues
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_pagination_and_add_user():
    """Test pagination handling and Add User button"""
    print("🧪 Testing Pagination and Add User Button...")
    
    try:
        # Create or get staff user
        staff_user, created = User.objects.get_or_create(
            username='test_staff',
            defaults={
                'email': 'staff@test.com',
                'is_staff': True
            }
        )
        if created:
            staff_user.set_password('testpass123')
            staff_user.save()
        
        # Create client and login
        client = Client()
        client.force_login(staff_user)
        
        # Test invalid page number
        print("\n🔢 Testing invalid page number...")
        response = client.get('/staff/users/?page=999')
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 302]:
            print("   ✅ Invalid page handled gracefully")
        else:
            print("   ❌ Invalid page not handled properly")
        
        # Test user list page for Add User button
        print("\n🔗 Testing Add User button presence...")
        response = client.get('/staff/users/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check various ways the Add User button might appear
            checks = [
                ('Add User' in content, 'Text "Add User"'),
                ('user_add' in content, 'URL name "user_add"'),
                ('btn-admin-primary' in content, 'Primary button class'),
                ('fas fa-plus' in content, 'Plus icon'),
            ]
            
            print("   Button detection checks:")
            for found, description in checks:
                status = "✅" if found else "❌"
                print(f"     {status} {description}: {'FOUND' if found else 'NOT FOUND'}")
                
            # Also check for the URL
            add_url = reverse('staff:user_add')
            print(f"   Add User URL should be: {add_url}")
            if add_url in content:
                print("   ✅ Add User URL found in page")
            else:
                print("   ❌ Add User URL not found in page")
                
        else:
            print(f"   ❌ Failed to load user list page: {response.status_code}")
            
        # Test Add User page directly
        print("\n📝 Testing Add User page directly...")
        add_url = reverse('staff:user_add')
        response = client.get(add_url)
        print(f"   Add User page ({add_url}): {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Add User page loads successfully")
        else:
            print("   ❌ Add User page failed to load")
            
    except Exception as e:
        print(f"❌ Error testing pagination and Add User: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_pagination_and_add_user()
