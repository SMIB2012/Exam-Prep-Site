#!/usr/bin/env python
"""
Test script to verify the user edit view works properly
"""
import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

def test_user_edit_view():
    """Test that the user edit view works"""
    try:
        from core.models import UserProfile
        
        # Create a test user
        test_user, created = User.objects.get_or_create(
            username='test_edit_user',
            defaults={
                'email': 'testedit@example.com',
                'first_name': 'Test',
                'last_name': 'Edit'
            }
        )
        
        # Create profile
        profile, created = UserProfile.objects.get_or_create(
            user=test_user,
            defaults={
                'college': 'Edit Test College',
                'year_of_study': 2,
                'preferred_language': 'en'
            }
        )
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='test_admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        print(f"✅ Test user created: {test_user.username}")
        print(f"✅ Admin user created: {admin_user.username}")
        
        # Test with Django test client
        client = Client()
        
        # Login as admin
        client.force_login(admin_user)
        print("✅ Logged in as admin")
        
        # Try to access user edit page
        url = reverse('staff:user_edit', kwargs={'pk': test_user.pk})
        print(f"Testing URL: {url}")
        
        response = client.get(url)
        print(f"✅ GET response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ User edit page loads successfully!")
            
            # Check if important elements are in the response
            content = response.content.decode('utf-8', errors='ignore')
            
            if 'Edit User' in content:
                print("✅ Page title found")
            if test_user.username in content:
                print("✅ User data displayed")
            if 'form' in content.lower():
                print("✅ Form elements found")
                
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing user edit view: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Testing user edit view...")
    print("=" * 50)
    
    success = test_user_edit_view()
    
    print("=" * 50)
    if success:
        print("✅ User edit view test passed!")
    else:
        print("❌ User edit view test failed!")
