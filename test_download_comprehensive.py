#!/usr/bin/env python
"""
Test to simulate actual browser behavior for download button
"""

import os
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def create_staff_user():
    """Create a staff user for testing"""
    user, created = User.objects.get_or_create(
        username='teststaff',
        defaults={
            'email': 'teststaff@example.com',
            'is_staff': True,
            'first_name': 'Test',
            'last_name': 'Staff'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    return user

def test_page_loads():
    """Test that the bulk upload page loads correctly"""
    print("🔍 Testing if bulk upload page loads...")
    
    client = Client()
    user = create_staff_user()
    
    # Login
    login_success = client.login(username='teststaff', password='testpass123')
    if not login_success:
        print("❌ Failed to login")
        return False
    
    # Get the page
    try:
        response = client.get('/staff/users/bulk-upload/')
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check if download button exists
            if 'Download CSV Template' in content:
                print("✅ Page loads and contains download button")
                
                # Check if it's in a separate form
                if 'name="action" value="download_template"' in content:
                    print("✅ Download button has correct action value")
                    return True
                else:
                    print("❌ Download button missing action value")
                    return False
            else:
                print("❌ Download button not found on page")
                return False
        else:
            print(f"❌ Page failed to load: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading page: {e}")
        return False

def test_download_request():
    """Test the actual download request"""
    print("\n🔍 Testing download button request...")
    
    client = Client()
    user = create_staff_user()
    
    # Login
    client.login(username='teststaff', password='testpass123')
    
    # Test download request
    try:
        response = client.post('/staff/users/bulk-upload/', {
            'action': 'download_template'
        })
        
        print(f"   Response status: {response.status_code}")
        print(f"   Content-Type: {response.get('Content-Type', 'Not set')}")
        print(f"   Content-Disposition: {response.get('Content-Disposition', 'Not set')}")
        
        if response.status_code == 200:
            content_disposition = response.get('Content-Disposition', '')
            content_type = response.get('Content-Type', '')
            
            if 'attachment' in content_disposition and 'csv' in content_type:
                print("✅ Download request returns proper file response")
                
                # Check content
                if hasattr(response, 'content'):
                    content = response.content.decode('utf-8')
                    if 'first_name,last_name,email' in content:
                        print("✅ CSV content is correct")
                        return True
                    else:
                        print("❌ CSV content is incorrect")
                        print(f"   First 200 chars: {content[:200]}")
                        return False
                else:
                    print("❌ Response has no content")
                    return False
            else:
                print("❌ Response is not a file download")
                print(f"   Expected: attachment + csv content type")
                print(f"   Got: {content_disposition} + {content_type}")
                return False
        else:
            print(f"❌ Download request failed: {response.status_code}")
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                print(f"   Response content (first 500 chars): {content[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error during download request: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_invalid_form_with_download():
    """Test that download works even when form would be invalid"""
    print("\n🔍 Testing download with invalid form data...")
    
    client = Client()
    user = create_staff_user()
    client.login(username='teststaff', password='testpass123')
    
    # Send request with invalid form data but download action
    try:
        response = client.post('/staff/users/bulk-upload/', {
            'action': 'download_template',
            'csv_file': '',  # Missing file
            'default_password': '',  # Invalid password
            # Other invalid/missing fields
        })
        
        print(f"   Response status with invalid data: {response.status_code}")
        
        if response.status_code == 200:
            content_disposition = response.get('Content-Disposition', '')
            if 'attachment' in content_disposition:
                print("✅ Download works even with invalid form data")
                return True
            else:
                print("❌ Download failed - not a file response")
                content = response.content.decode('utf-8')
                if 'please select a file' in content.lower():
                    print("❌ ERROR: Still showing 'please select a file' error!")
                    print("   This means form validation is still running for download action")
                return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def cleanup():
    """Clean up test data"""
    try:
        User.objects.filter(username='teststaff').delete()
    except:
        pass

if __name__ == '__main__':
    print("🧪 COMPREHENSIVE DOWNLOAD BUTTON TEST")
    print("=" * 50)
    
    try:
        test1 = test_page_loads()
        test2 = test_download_request()
        test3 = test_invalid_form_with_download()
        
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS:")
        print(f"   Page loads: {'✅' if test1 else '❌'}")
        print(f"   Download works: {'✅' if test2 else '❌'}")
        print(f"   Independent of form: {'✅' if test3 else '❌'}")
        
        if test1 and test2 and test3:
            print("\n🎉 ALL TESTS PASSED!")
            print("   The download button should work correctly now.")
        else:
            print("\n⚠️ SOME TESTS FAILED!")
            print("   The download button may still have issues.")
            
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cleanup()
