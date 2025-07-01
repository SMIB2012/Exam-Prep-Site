#!/usr/bin/env python
"""
Test script to verify the download CSV template button works independently
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

def test_download_button():
    """Test that the download button works without form validation"""
    print("Testing CSV template download button...")
    
    # Create a test client
    client = Client()
    
    # Create a staff user for authentication
    staff_user = User.objects.create_user(
        username='teststaff',
        email='teststaff@example.com',
        password='testpass123',
        is_staff=True
    )
    
    # Login as staff
    login_success = client.login(username='teststaff', password='testpass123')
    print(f"Login successful: {login_success}")
    
    if not login_success:
        print("❌ Failed to login as staff user")
        return False
    
    # Test the download button (POST request with action=download_template)
    response = client.post('/staff/users/bulk-upload/', {
        'action': 'download_template'
    })
    
    print(f"Response status code: {response.status_code}")
    print(f"Response content type: {response.get('Content-Type', 'Not set')}")
    
    # Check if it's a file download response
    if response.status_code == 200:
        content_disposition = response.get('Content-Disposition', '')
        print(f"Content-Disposition: {content_disposition}")
        
        if 'attachment' in content_disposition and 'user_upload_template.csv' in content_disposition:
            print("✅ Download button works correctly!")
            print(f"File size: {len(response.content)} bytes")
            
            # Check if content looks like CSV
            content_str = response.content.decode('utf-8')
            if 'first_name,last_name,email' in content_str:
                print("✅ CSV content is correct!")
                return True
            else:
                print("❌ CSV content is incorrect")
                print(f"First 200 characters: {content_str[:200]}")
                return False
        else:
            print("❌ Response doesn't look like a file download")
            return False
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"Response content: {response.content.decode('utf-8')[:500]}")
        return False

def test_form_validation_independence():
    """Test that download button works even with invalid form data"""
    print("\nTesting download button with invalid form data...")
    
    client = Client()
    
    # Login as staff
    staff_user, created = User.objects.get_or_create(
        username='teststaff',
        defaults={'email': 'teststaff@example.com', 'is_staff': True}
    )
    if created:
        staff_user.set_password('testpass123')
        staff_user.save()
    
    client.login(username='teststaff', password='testpass123')
    
    # Try download with some invalid form data that would normally cause errors
    response = client.post('/staff/users/bulk-upload/', {
        'action': 'download_template',
        'csv_file': '',  # Empty file field
        'default_password': '',  # Empty password
        # Missing required fields
    })
    
    print(f"Response status code with invalid data: {response.status_code}")
    
    if response.status_code == 200:
        content_disposition = response.get('Content-Disposition', '')
        if 'attachment' in content_disposition and 'user_upload_template.csv' in content_disposition:
            print("✅ Download button works independently of form validation!")
            return True
        else:
            print("❌ Response is not a file download")
            return False
    else:
        print(f"❌ Download failed with invalid form data")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Testing CSV Template Download Button")
    print("=" * 60)
    
    try:
        # Clean up any existing test users
        User.objects.filter(username='teststaff').delete()
        
        success1 = test_download_button()
        success2 = test_form_validation_independence()
        
        print("\n" + "=" * 60)
        if success1 and success2:
            print("✅ All tests passed! Download button works correctly.")
        else:
            print("❌ Some tests failed. Check the output above.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test user
        try:
            User.objects.filter(username='teststaff').delete()
        except:
            pass
