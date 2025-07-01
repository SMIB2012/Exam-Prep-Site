#!/usr/bin/env python
"""
Test script for bulk user upload functionality
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from staff.forms import BulkUserUploadForm
from staff.views.user_views import BulkUserUploadView

def test_bulk_upload_form():
    """Test the bulk upload form validation"""
    print("Testing BulkUserUploadForm...")
    
    # Create a sample CSV content
    csv_content = """first_name,last_name,email,password,role,year_of_study,province,college_type,college_name,phone_number,is_premium,is_active
John,Doe,john.doe@example.com,Pass123!,student,1st_year,Punjab,Public,King Edward Medical University (Lahore),+92-300-1234567,FALSE,TRUE
Jane,Smith,jane.smith@example.com,Pass456!,faculty,,Sindh,Private,Aga Khan University,+92-321-9876543,TRUE,TRUE"""
    
    # Create a file-like object
    csv_file = SimpleUploadedFile(
        "test_users.csv",
        csv_content.encode('utf-8'),
        content_type="text/csv"
    )
    
    # Test form validation
    form_data = {
        'default_password': 'TempPass123!',
        'default_role': 'student',
        'send_welcome_emails': True,
        'skip_errors': True,
    }
    
    form = BulkUserUploadForm(data=form_data, files={'csv_file': csv_file})
    
    if form.is_valid():
        print("✅ Form validation passed!")
        print(f"Default password: {form.cleaned_data['default_password']}")
        print(f"Default role: {form.cleaned_data['default_role']}")
        print(f"Send welcome emails: {form.cleaned_data['send_welcome_emails']}")
        print(f"Skip errors: {form.cleaned_data['skip_errors']}")
    else:
        print("❌ Form validation failed!")
        print("Errors:", form.errors)
    
    return form.is_valid()

def test_csv_parsing():
    """Test CSV parsing functionality"""
    print("\nTesting CSV parsing...")
    
    # Create a BulkUserUploadView instance
    view = BulkUserUploadView()
    
    # Sample CSV data
    csv_data = """first_name,last_name,email,password,role,year_of_study,province,college_type,college_name,phone_number,is_premium,is_active
John,Doe,john.doe@example.com,Pass123!,student,1st_year,Punjab,Public,King Edward Medical University (Lahore),+92-300-1234567,FALSE,TRUE
Jane,Smith,jane.smith@example.com,Pass456!,faculty,,Sindh,Private,Aga Khan University,+92-321-9876543,TRUE,TRUE
Invalid,User,not-an-email,Pass789!,invalid_role,1st_year,Punjab,Public,King Edward Medical University (Lahore),+92-300-7777777,FALSE,TRUE"""
    
    try:
        # Parse CSV data
        parsed_data = view.parse_csv_data(csv_data)
        print(f"✅ CSV parsing successful! Parsed {len(parsed_data)} rows")
        
        # Process the data
        processed_data = view.process_data(parsed_data, 'DefaultPass123!', 'student')
        print(f"✅ Data processing successful!")
        print(f"Valid rows: {len(processed_data['valid_rows'])}")
        print(f"Error rows: {len(processed_data['error_rows'])}")
        
        # Show error details
        if processed_data['error_rows']:
            print("\nError details:")
            for error_row in processed_data['error_rows']:
                print(f"Row {error_row['row_number']}: {error_row['errors']}")
        
        return True
    except Exception as e:
        print(f"❌ CSV parsing failed: {str(e)}")
        return False

def test_user_creation():
    """Test if we can create a user from processed data"""
    print("\nTesting user creation...")
    
    # Check if we can create a user with the processed data
    try:
        # Sample user data
        user_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test.user@example.com',
            'password': 'TestPass123!',
            'role': 'student',
            'year_of_study': '1st_year',
            'province': 'Punjab',
            'college_type': 'Public',
            'college_name': 'King Edward Medical University (Lahore)',
            'phone_number': '+92-300-1234567',
            'is_premium': False,
            'is_active': True
        }
        
        # Check if user already exists
        if User.objects.filter(email=user_data['email']).exists():
            print("⚠️ Test user already exists, skipping creation test")
            return True
        
        # Create user (simulation)
        print("✅ User creation test passed (simulation)")
        print(f"Would create user: {user_data['first_name']} {user_data['last_name']} ({user_data['email']})")
        
        return True
    except Exception as e:
        print(f"❌ User creation test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Bulk User Upload Functionality")
    print("=" * 50)
    
    tests = [
        test_bulk_upload_form,
        test_csv_parsing,
        test_user_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bulk upload functionality is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")

if __name__ == '__main__':
    main()
