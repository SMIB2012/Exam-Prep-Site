#!/usr/bin/env python
"""
Comprehensive end-to-end test for the signup form to verify all profile fields are saved correctly.
"""
import os
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')

import django
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from core.models import UserProfile
from core.forms import UserRegistrationForm


def test_signup_form_end_to_end():
    """Test the complete signup process via form submission"""
    print("=== Testing End-to-End Signup Form ===")
    
    # Test data for a new user
    test_data = {
        'username': 'test_student_2024',
        'first_name': 'Test',
        'last_name': 'Student',
        'email': 'test.student.2024@example.com',
        'password1': 'ComplexPassword123!',
        'password2': 'ComplexPassword123!',
        'year_of_study': '4th_year',
        'province': 'Punjab',
        'college_type': 'Public',
        'college_name': 'King Edward Medical University (Lahore)',
        'phone_number': '+92-300-1234567'
    }
    
    # Clean up any existing user with this data
    User.objects.filter(username=test_data['username']).delete()
    User.objects.filter(email=test_data['email']).delete()
    
    print(f"1. Testing form with data: {test_data['username']}, {test_data['email']}")
    
    # Test 1: Form validation
    form = UserRegistrationForm(data=test_data)
    print(f"2. Form is valid: {form.is_valid()}")
    
    if not form.is_valid():
        print(f"   Form errors: {form.errors}")
        return False
    
    # Test 2: Save the form (this should create user and profile)
    try:
        user = form.save()
        print(f"3. User created successfully: {user.username}")
        print(f"   User ID: {user.id}")
        print(f"   User email: {user.email}")
        print(f"   User first name: {user.first_name}")
        print(f"   User last name: {user.last_name}")
    except Exception as e:
        print(f"3. ERROR creating user: {e}")
        return False
    
    # Test 3: Check if profile was created and populated
    try:
        profile = UserProfile.objects.get(user=user)
        print(f"4. Profile found: {profile}")
        print(f"   Year of study: {profile.year_of_study}")
        print(f"   Province: {profile.province}")
        print(f"   College type: {profile.college_type}")
        print(f"   College name: {profile.college_name}")
        print(f"   Phone number: {profile.phone_number}")
        
        # Verify all fields are saved correctly
        assert profile.year_of_study == test_data['year_of_study'], f"Year mismatch: {profile.year_of_study} != {test_data['year_of_study']}"
        assert profile.province == test_data['province'], f"Province mismatch: {profile.province} != {test_data['province']}"
        assert profile.college_type == test_data['college_type'], f"College type mismatch: {profile.college_type} != {test_data['college_type']}"
        assert profile.college_name == test_data['college_name'], f"College name mismatch: {profile.college_name} != {test_data['college_name']}"
        assert profile.phone_number == test_data['phone_number'], f"Phone mismatch: {profile.phone_number} != {test_data['phone_number']}"
        
        print("5. ✅ All profile fields saved correctly!")
        
    except UserProfile.DoesNotExist:
        print("4. ERROR: User profile was not created!")
        return False
    except AssertionError as e:
        print(f"4. ERROR: Profile field mismatch: {e}")
        return False
    except Exception as e:
        print(f"4. ERROR checking profile: {e}")
        return False
    
    # Test 4: Test display methods work correctly
    try:
        print("6. Testing display methods:")
        print(f"   Province display: {profile.get_province_display()}")
        print(f"   College type display: {profile.get_college_type_display()}")
        print(f"   Year display: {profile.get_year_of_study_display()}")
    except Exception as e:
        print(f"6. ERROR testing display methods: {e}")
    
    print("7. ✅ End-to-end signup test PASSED!")
    return True


def test_web_interface_simulation():
    """Simulate the actual web interface submission"""
    print("\n=== Testing Web Interface Simulation ===")
    
    client = Client()
    
    # Test data
    test_data = {
        'username': 'web_test_user_2024',
        'first_name': 'Web',
        'last_name': 'Test',
        'email': 'web.test.2024@example.com',
        'password1': 'ComplexPassword123!',
        'password2': 'ComplexPassword123!',
        'year_of_study': '3rd_year',
        'province': 'Sindh',
        'college_type': 'Private',
        'college_name': 'Aga Khan University',
        'phone_number': '+92-301-9876543'
    }
    
    # Clean up any existing user
    User.objects.filter(username=test_data['username']).delete()
    User.objects.filter(email=test_data['email']).delete()
    
    try:
        # Get the signup URL
        signup_url = reverse('core:signup')
        print(f"1. Signup URL: {signup_url}")
        
        # First get the form to see if it loads
        response = client.get(signup_url)
        print(f"2. GET response status: {response.status_code}")
        
        # Submit the form
        response = client.post(signup_url, test_data)
        print(f"3. POST response status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect after successful signup
            print("4. ✅ Signup appears successful (redirect)")
            redirect_url = response.url
            print(f"   Redirected to: {redirect_url}")
            
            # Check if user was created
            try:
                user = User.objects.get(username=test_data['username'])
                print(f"5. ✅ User created: {user.username}")
                
                # Check profile
                profile = UserProfile.objects.get(user=user)
                print(f"6. ✅ Profile created: {profile}")
                print(f"   Province: {profile.province}")
                print(f"   College: {profile.college_name}")
                print(f"   Year: {profile.year_of_study}")
                
                return True
                
            except (User.DoesNotExist, UserProfile.DoesNotExist) as e:
                print(f"5. ERROR: User or profile not found: {e}")
                return False
                
        else:
            print(f"4. Form submission failed with status: {response.status_code}")
            # Try to extract form errors
            if hasattr(response, 'context') and response.context:
                if 'form' in response.context:
                    form = response.context['form']
                    if hasattr(form, 'errors') and form.errors:
                        print(f"   Form errors: {form.errors}")
                    if hasattr(form, 'non_field_errors'):
                        non_field_errors = form.non_field_errors()
                        if non_field_errors:
                            print(f"   Non-field errors: {non_field_errors}")
            
            # Also try to see if there are any specific college name issues
            from core.forms import UserRegistrationForm
            form = UserRegistrationForm(data=test_data)
            if not form.is_valid():
                print(f"   Direct form validation errors: {form.errors}")
            
            return False
            
    except Exception as e:
        print(f"ERROR in web interface test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("Starting comprehensive signup form testing...")
    
    # Test 1: Direct form testing
    success1 = test_signup_form_end_to_end()
    
    # Test 2: Web interface simulation
    success2 = test_web_interface_simulation()
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Direct form test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Web interface test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("🎉 ALL TESTS PASSED! Signup form is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
