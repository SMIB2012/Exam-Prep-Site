#!/usr/bin/env python
"""
Simple verification script to test the bulk upload view directly
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from staff.views.user_views import BulkUserUploadView
from staff.forms import BulkUserUploadForm

def test_bulk_upload_page():
    """Test if the bulk upload page loads without errors"""
    print("Testing Bulk Upload Page Loading...")
    
    try:
        # Create a test superuser
        test_user, created = User.objects.get_or_create(
            username='test_admin',
            defaults={
                'email': 'admin@test.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            print("✅ Test admin user created")
        else:
            print("✅ Test admin user already exists")
        
        # Create a request factory
        factory = RequestFactory()
        
        # Test GET request
        request = factory.get('/staff/users/bulk-upload/')
        request.user = test_user
        
        view = BulkUserUploadView()
        response = view.get(request)
        
        if response.status_code == 200:
            print("✅ GET request successful - Page loads correctly!")
        else:
            print(f"❌ GET request failed with status code: {response.status_code}")
            return False
        
        # Test form instantiation
        form = BulkUserUploadForm()
        print("✅ Form instantiation successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Page loading test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_form_submission():
    """Test form submission with valid data"""
    print("\nTesting Form Submission...")
    
    try:
        # Create a test superuser
        test_user = User.objects.get(username='test_admin')
        
        # Create sample CSV content
        csv_content = """first_name,last_name,email,password,role,year_of_study,province,college_type,college_name,phone_number,is_premium,is_active
TestUser1,LastName1,testuser1@example.com,Pass123!,student,1st_year,Punjab,Public,King Edward Medical University (Lahore),+92-300-1111111,FALSE,TRUE
TestUser2,LastName2,testuser2@example.com,Pass456!,faculty,,Sindh,Private,Aga Khan University,+92-321-2222222,TRUE,TRUE"""
        
        # Create a file-like object
        csv_file = SimpleUploadedFile(
            "test_upload.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        # Test form validation
        form_data = {
            'default_password': 'TempPass123!',
            'default_role': 'student',
            'send_welcome_emails': False,  # Don't send emails in test
            'skip_errors': True,
        }
        
        form = BulkUserUploadForm(data=form_data, files={'csv_file': csv_file})
        
        if form.is_valid():
            print("✅ Form validation passed!")
            
            # Test CSV processing
            view = BulkUserUploadView()
            parsed_data = view.parse_csv_data(csv_content)
            processed_data = view.process_data(parsed_data, 'TempPass123!', 'student')
            
            print(f"✅ CSV processing successful!")
            print(f"   Valid rows: {len(processed_data['valid_rows'])}")
            print(f"   Error rows: {len(processed_data['error_rows'])}")
            
            return True
        else:
            print("❌ Form validation failed!")
            print("Errors:", form.errors)
            return False
            
    except Exception as e:
        print(f"❌ Form submission test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_template_download():
    """Test template download functionality"""
    print("\nTesting Template Download...")
    
    try:
        # Create a request factory
        factory = RequestFactory()
        test_user = User.objects.get(username='test_admin')
        
        # Create POST request for template download
        request = factory.post('/staff/users/bulk-upload/', {'action': 'download_template'})
        request.user = test_user
        
        view = BulkUserUploadView()
        response = view.download_template()
        
        if response.status_code == 200:
            print("✅ Template download successful!")
            print(f"   Content type: {response.get('Content-Type')}")
            print(f"   Content disposition: {response.get('Content-Disposition')}")
            return True
        else:
            print(f"❌ Template download failed with status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Template download test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification tests"""
    print("🔍 Bulk Upload Page Verification")
    print("=" * 50)
    
    tests = [
        test_bulk_upload_page,
        test_form_submission,
        test_template_download
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Verification Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All verification tests passed! The bulk upload page is working correctly.")
        print("\n📋 Next Steps:")
        print("1. Start the Django server: python manage.py runserver")
        print("2. Login as staff/admin user")
        print("3. Navigate to: /staff/users/bulk-upload/")
        print("4. Test the functionality with the sample CSV files")
    else:
        print("⚠️ Some verification tests failed. Please check the implementation.")

if __name__ == '__main__':
    main()
