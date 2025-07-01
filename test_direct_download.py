#!/usr/bin/env python
"""
Direct test of the view logic without HTTP client
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

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from staff.views.user_views import BulkUserUploadView

def test_download_logic():
    """Test the download logic directly"""
    print("🔍 Testing download logic directly...")
    
    # Setup
    factory = RequestFactory()
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass',
        is_staff=True
    )
    
    # Create request
    request = factory.post('/staff/users/bulk-upload/', {
        'action': 'download_template'
    })
    request.user = user
    
    # Add session and messages (required by Django)
    session = SessionStore()
    session.create()
    request.session = session
    
    # Add messages framework
    messages = FallbackStorage(request)
    request._messages = messages
    
    # Test the view
    view = BulkUserUploadView()
    
    try:
        # Call the post method
        response = view.post(request)
        
        print(f"✅ Response received")
        print(f"   Status code: {response.status_code}")
        print(f"   Content-Type: {response.get('Content-Type', 'Not set')}")
        print(f"   Content-Disposition: {response.get('Content-Disposition', 'Not set')}")
        
        # Check if it's a file download
        if response.status_code == 200:
            content_disposition = response.get('Content-Disposition', '')
            if 'attachment' in content_disposition and 'csv' in content_disposition:
                print("✅ SUCCESS: Download response is correct!")
                
                # Verify content
                content = response.content.decode('utf-8')
                if 'first_name,last_name,email' in content:
                    print("✅ CSV content is valid")
                    print(f"   Content length: {len(content)} characters")
                    print(f"   First line: {content.split('\\n')[0]}")
                    return True
                else:
                    print("❌ CSV content is invalid")
                    return False
            else:
                print("❌ Response is not a file download")
                print(f"   Content-Disposition: {content_disposition}")
                return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        user.delete()

def test_form_bypass():
    """Test that download action bypasses form validation"""
    print("\n🔍 Testing form validation bypass...")
    
    factory = RequestFactory()
    user = User.objects.create_user(
        username='testuser2',
        email='test2@example.com', 
        password='testpass',
        is_staff=True
    )
    
    # Create request with invalid form data but download action
    request = factory.post('/staff/users/bulk-upload/', {
        'action': 'download_template',
        'csv_file': '',  # This would cause validation error
        'default_password': '',  # This would cause validation error
    })
    request.user = user
    
    # Add session and messages
    session = SessionStore()
    session.create()
    request.session = session
    request._messages = FallbackStorage(request)
    
    view = BulkUserUploadView()
    
    try:
        # This should NOT validate the form since action is download_template
        response = view.post(request)
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            content_disposition = response.get('Content-Disposition', '')
            if 'attachment' in content_disposition:
                print("✅ SUCCESS: Form validation was bypassed!")
                return True
            else:
                # Check if we got an HTML response with form errors
                if hasattr(response, 'content'):
                    content = response.content.decode('utf-8')
                    if 'please select a file' in content.lower() or 'form' in content.lower():
                        print("❌ FAILURE: Form validation was NOT bypassed!")
                        print("   The view is still processing the form instead of downloading")
                        return False
                    else:
                        print("❌ Unknown response type")
                        return False
                else:
                    print("❌ No response content")
                    return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        user.delete()

if __name__ == '__main__':
    print("🎯 DIRECT DOWNLOAD LOGIC TEST")
    print("=" * 40)
    
    test1 = test_download_logic()
    test2 = test_form_bypass()
    
    print("\n" + "=" * 40)
    print("📊 RESULTS:")
    print(f"   Download logic: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"   Form bypass: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n🎉 SUCCESS!")
        print("The download button logic is working correctly.")
        print("If you're still seeing issues in the browser,")
        print("try clearing your browser cache or hard refresh.")
    else:
        print("\n⚠️ ISSUES DETECTED!")
        print("The download button logic has problems.")
    
    print("=" * 40)
