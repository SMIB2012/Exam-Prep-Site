#!/usr/bin/env python
"""
Test the template download fix
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from staff.views.user_views import BulkUserUploadView

def test_template_download_fix():
    """Test that template download works without form validation"""
    print("🔧 Testing Template Download Fix...")
    
    try:
        # Create test user
        test_user, created = User.objects.get_or_create(
            username='template_fix_test',
            defaults={
                'email': 'templatefix@test.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
        
        # Create request factory
        factory = RequestFactory()
        
        # Test POST request with only download action (no file upload)
        request = factory.post('/staff/users/bulk-upload/', {
            'action': 'download_template'
        })
        request.user = test_user
        
        # Create view and call post method
        view = BulkUserUploadView()
        view.request = request
        response = view.post(request)
        
        if hasattr(response, 'status_code'):
            print(f"✅ Response generated with status: {response.status_code}")
        
        # Check if it's a file download response
        content_disposition = response.get('Content-Disposition', '')
        if 'attachment' in content_disposition and 'csv' in content_disposition:
            print("✅ Template download response generated correctly!")
            print(f"   Content-Disposition: {content_disposition}")
            
            # Check content
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                if 'first_name,last_name,email' in content:
                    print("✅ CSV content is correct")
                else:
                    print("⚠️ CSV content may be incomplete")
            
            return True
        else:
            print("❌ Response is not a file download")
            print(f"   Content-Disposition: {content_disposition}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_form_validation_still_works():
    """Test that form validation still works for upload action"""
    print("\n🔧 Testing Form Validation Still Works...")
    
    try:
        # Create test user
        test_user = User.objects.get(username='template_fix_test')
        
        # Create request factory
        factory = RequestFactory()
        
        # Test POST request with upload action but no file (should fail validation)
        request = factory.post('/staff/users/bulk-upload/', {
            'action': 'upload',
            'default_password': 'TempPass123!',
            'default_role': 'student'
            # Note: no csv_file - should trigger validation error
        })
        request.user = test_user
        
        # Create view and call post method
        view = BulkUserUploadView()
        view.request = request
        response = view.post(request)
        
        # Should render template with form errors, not download
        if hasattr(response, 'status_code') and response.status_code == 200:
            print("✅ Form validation triggered correctly")
            
            # Check that it's not a download response
            content_disposition = response.get('Content-Disposition', '')
            if 'attachment' not in content_disposition:
                print("✅ Not a download response (correct)")
                return True
            else:
                print("❌ Unexpected download response")
                return False
        else:
            print(f"❌ Unexpected response: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def main():
    """Run template download fix tests"""
    print("🧪 Template Download Fix Tests")
    print("=" * 40)
    
    tests = [
        test_template_download_fix,
        test_form_validation_still_works
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Template download fix is working!")
        print("\n✅ What was fixed:")
        print("1. Download button now uses separate form")
        print("2. Download action bypasses form validation")
        print("3. Upload/confirm actions still validate properly")
        print("\n🚀 The download button should now work correctly!")
    else:
        print("⚠️ Some tests failed, fix may need adjustment")

if __name__ == '__main__':
    main()
