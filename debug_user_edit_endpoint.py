#!/usr/bin/env python
"""
Debug script to identify why comprehensive test is failing for user edit
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
from core.models import UserProfile
from django.urls import reverse

def test_user_edit_endpoint():
    """Test the user edit endpoint directly"""
    print("🧪 Testing User Edit Endpoint...")
    
    try:
        # Create test users
        staff_user = User.objects.create_user(
            username='test_staff',
            email='staff@test.com',
            password='testpass123',
            is_staff=True
        )
        
        test_user = User.objects.create_user(
            username='test_target',
            email='target@test.com',
            password='testpass123',
            first_name='Original',
            last_name='Name'
        )
        
        # Create profile
        profile, _ = UserProfile.objects.get_or_create(user=test_user)
        
        print(f"📝 Created test users:")
        print(f"   Staff user: {staff_user.username}")
        print(f"   Target user: {test_user.username}")
        print(f"   Original name: {test_user.first_name} {test_user.last_name}")
        
        # Create client and login
        client = Client()
        client.force_login(staff_user)
        
        # Test GET request to edit page
        edit_url = reverse('staff:user_edit', kwargs={'pk': test_user.pk})
        print(f"\n🌐 Testing GET {edit_url}")
        
        response = client.get(edit_url)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ GET request successful")
            
            # Test POST request with form data
            form_data = {
                'username': test_user.username,
                'email': test_user.email,
                'first_name': 'Updated',
                'last_name': 'Name',
                'is_active': True,
                'is_staff': False,
                'year_of_study': '2nd_year',
                'province': 'Punjab',
                'college_type': 'Public',
                'college_name': 'Allama Iqbal Medical College (Lahore)',
                'phone_number': '+92-300-1234567',
                'is_premium': True,
            }
            
            print(f"\n📤 Testing POST with data:")
            for key, value in form_data.items():
                print(f"   - {key}: {value}")
            
            post_response = client.post(edit_url, form_data, follow=True)
            print(f"\n   POST Status: {post_response.status_code}")
            
            if post_response.status_code == 200:
                print("   ✅ POST request successful")
                
                # Check if user was updated
                test_user.refresh_from_db()
                profile.refresh_from_db()
                
                print(f"\n📊 Checking updated data:")
                print(f"   - First name: '{test_user.first_name}' (expected: 'Updated')")
                print(f"   - Province: '{profile.province}' (expected: 'Punjab')")
                print(f"   - Phone: '{profile.phone_number}' (expected: '+92-300-1234567')")
                
                # Verify changes
                if test_user.first_name == 'Updated':
                    print("   ✅ First name updated correctly")
                else:
                    print("   ❌ First name NOT updated")
                    
                if profile.province == 'Punjab':
                    print("   ✅ Province updated correctly")
                else:
                    print("   ❌ Province NOT updated")
                    
                if profile.phone_number == '+92-300-1234567':
                    print("   ✅ Phone updated correctly")  
                else:
                    print("   ❌ Phone NOT updated")
                    
                # Check if there were any form errors in response
                if hasattr(post_response, 'context') and post_response.context:
                    form = post_response.context.get('form')
                    if form and hasattr(form, 'errors') and form.errors:
                        print(f"\n⚠️ Form errors in response:")
                        for field, errors in form.errors.items():
                            print(f"   - {field}: {errors}")
                else:
                    print("\n✅ No form errors detected")
                    
            else:
                print(f"   ❌ POST request failed with status {post_response.status_code}")
                print(f"   Response content: {post_response.content[:200]}")
        else:
            print(f"   ❌ GET request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing user edit endpoint: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_user_edit_endpoint()
