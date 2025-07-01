#!/usr/bin/env python
"""
Final comprehensive test to identify any remaining issues
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
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.messages.storage.fallback import FallbackStorage
from staff.views.user_views import BulkUserUploadView
from django.template.loader import render_to_string

def test_template_rendering():
    """Test that the template renders correctly with separate forms"""
    print("🔍 Testing template rendering...")
    
    factory = RequestFactory()
    user = User.objects.create_user(
        username='templatetest',
        email='template@example.com',
        password='testpass',
        is_staff=True
    )
    
    request = factory.get('/staff/users/bulk-upload/')
    request.user = user
    
    session = SessionStore()
    session.create()
    request.session = session
    request._messages = FallbackStorage(request)
    
    view = BulkUserUploadView()
    
    try:
        response = view.get(request)
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            print("   ✅ Template renders successfully")
            
            # Check for download button
            if 'Download CSV Template' in content:
                print("   ✅ Download button is present")
            else:
                print("   ❌ Download button is missing")
                return False
            
            # Check for separate form
            if 'name="action" value="download_template"' in content:
                print("   ✅ Download action is present")
            else:
                print("   ❌ Download action is missing")
                return False
            
            # Check form structure - look for nested forms
            form_count = content.count('<form')
            closing_form_count = content.count('</form>')
            
            print(f"   Form tags: {form_count} opening, {closing_form_count} closing")
            
            if form_count == closing_form_count and form_count >= 2:
                print("   ✅ Form structure looks correct")
                
                # Check that download form comes before main form
                download_pos = content.find('name="action" value="download_template"')
                main_form_pos = content.find('enctype="multipart/form-data"')
                
                if download_pos < main_form_pos and download_pos > 0:
                    print("   ✅ Download form comes before main form")
                    return True
                else:
                    print("   ❌ Form order is incorrect")
                    print(f"      Download button at position: {download_pos}")
                    print(f"      Main form at position: {main_form_pos}")
                    return False
            else:
                print("   ❌ Form structure is incorrect")
                return False
        else:
            print(f"   ❌ Template failed to render: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        user.delete()

def test_complete_flow():
    """Test the complete request flow"""
    print("\n🔍 Testing complete request flow...")
    
    factory = RequestFactory()
    user = User.objects.create_user(
        username='flowtest',
        email='flow@example.com',
        password='testpass',
        is_staff=True
    )
    
    # Test POST request with download action
    request = factory.post('/staff/users/bulk-upload/', {
        'action': 'download_template',
        'csrfmiddlewaretoken': 'test-token'
    })
    request.user = user
    
    session = SessionStore()
    session.create()
    request.session = session
    request._messages = FallbackStorage(request)
    
    view = BulkUserUploadView()
    
    try:
        print("   Sending POST request with download action...")
        response = view.post(request)
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response type: {type(response)}")
        
        if response.status_code == 200:
            content_type = response.get('Content-Type', '')
            content_disposition = response.get('Content-Disposition', '')
            
            print(f"   Content-Type: {content_type}")
            print(f"   Content-Disposition: {content_disposition}")
            
            if 'csv' in content_type and 'attachment' in content_disposition:
                print("   ✅ SUCCESS: Proper file download response!")
                
                # Verify content
                if hasattr(response, 'content'):
                    content = response.content.decode('utf-8')
                    if 'first_name,last_name,email' in content:
                        print("   ✅ CSV content is correct")
                        return True
                    else:
                        print("   ❌ CSV content is wrong")
                        return False
                else:
                    print("   ❌ No content in response")
                    return False
            else:
                print("   ❌ PROBLEM: Not a file download response")
                
                # Check if it's an HTML response (indicates form processing)
                if hasattr(response, 'content'):
                    content = response.content.decode('utf-8')
                    if '<html' in content or '<form' in content:
                        print("   ❌ ERROR: Got HTML response instead of file download!")
                        print("           This means the form is still being processed.")
                        if 'please select a file' in content.lower():
                            print("   ❌ CONFIRMED: 'Please select a file' error found!")
                        return False
                
                return False
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        user.delete()

if __name__ == '__main__':
    print("🔬 FINAL DIAGNOSTIC TEST")
    print("=" * 50)
    
    test1 = test_template_rendering()
    test2 = test_complete_flow()
    
    print("\n" + "=" * 50)
    print("🎯 FINAL DIAGNOSIS:")
    
    if test1 and test2:
        print("✅ ALL SYSTEMS WORKING!")
        print("   The download button should work correctly.")
        print("   If you're still having issues, try:")
        print("   1. Hard refresh your browser (Ctrl+F5)")
        print("   2. Clear browser cache")
        print("   3. Check browser developer tools for errors")
    else:
        print("❌ ISSUES FOUND:")
        if not test1:
            print("   - Template rendering has problems")
        if not test2:
            print("   - Request flow has problems")
        print("   The download button needs more fixing.")
    
    print("=" * 50)
