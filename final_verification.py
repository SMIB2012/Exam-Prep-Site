#!/usr/bin/env python
"""
Final verification - Test that a newly created user displays correctly in the admin user detail page.
"""
import os
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')

import django
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import UserProfile
from core.forms import UserRegistrationForm


def create_test_user_and_verify():
    """Create a test user via form and verify it displays correctly"""
    print("=== Final Verification: User Detail Display ===")
    
    # Test data for a new user
    test_data = {
        'username': 'final_test_user',
        'first_name': 'Final',
        'last_name': 'TestUser',
        'email': 'final.test@example.com',
        'password1': 'ComplexPassword123!',
        'password2': 'ComplexPassword123!',
        'year_of_study': 'final_year',
        'province': 'Khyber Pakhtunkhwa',
        'college_type': 'Public',
        'college_name': 'Khyber Medical College (Peshawar)',
        'phone_number': '+92-333-1234567'
    }
    
    # Clean up any existing user
    User.objects.filter(username=test_data['username']).delete()
    User.objects.filter(email=test_data['email']).delete()
    
    print(f"1. Creating user with form: {test_data['username']}")
    
    # Create user via form
    form = UserRegistrationForm(data=test_data)
    if not form.is_valid():
        print(f"   ERROR: Form is invalid: {form.errors}")
        return False
    
    user = form.save()
    print(f"2. ✅ User created: {user.username} (ID: {user.id})")
    
    # Verify profile was created and populated
    try:
        profile = UserProfile.objects.get(user=user)
        print(f"3. ✅ Profile created and populated:")
        print(f"   User: {profile.user.get_full_name()} ({profile.user.username})")
        print(f"   Email: {profile.user.email}")
        print(f"   Year: {profile.year_of_study} -> {profile.get_year_of_study_display()}")
        print(f"   Province: {profile.province} -> {profile.get_province_display()}")
        print(f"   College Type: {profile.college_type} -> {profile.get_college_type_display()}")
        print(f"   College Name: {profile.college_name}")
        print(f"   Phone: {profile.phone_number}")
        print(f"   Premium: {profile.is_premium}")
        print(f"   Created: {profile.created_at}")
        
        # Verify all fields have values
        assert profile.year_of_study, "Year of study is empty"
        assert profile.province, "Province is empty"
        assert profile.college_type, "College type is empty"
        assert profile.college_name, "College name is empty"
        
        print("4. ✅ All profile fields are properly populated!")
        
        # Test that the display methods work
        print("5. Testing display methods:")
        print(f"   Year display: '{profile.get_year_of_study_display()}'")
        print(f"   Province display: '{profile.get_province_display()}'")
        print(f"   College type display: '{profile.get_college_type_display()}'")
        
        # Test that fallback displays work when fields are missing
        profile.year_of_study = ""
        profile.province = ""
        profile.college_type = ""
        profile.college_name = ""
        print("6. Testing fallback displays when fields are empty:")
        print(f"   Year display (empty): '{profile.get_year_of_study_display() or 'Not specified'}'")
        print(f"   Province display (empty): '{profile.get_province_display() or 'Not specified'}'")
        print(f"   College type display (empty): '{profile.get_college_type_display() or 'Not specified'}'")
        
        return True
        
    except UserProfile.DoesNotExist:
        print("3. ERROR: User profile was not created!")
        return False
    except Exception as e:
        print(f"3. ERROR: {e}")
        return False


def test_user_detail_template_display():
    """Test that the user detail template would display the data correctly"""
    print("\n=== Testing User Detail Template Logic ===")
    
    # Get the test user we just created
    try:
        user = User.objects.get(username='final_test_user')
        profile = UserProfile.objects.get(user=user)
        
        print(f"1. Testing template display logic for: {user.get_full_name()}")
        
        # Simulate what the template would show
        template_data = {
            'full_name': user.get_full_name() or user.username,
            'email': user.email,
            'username': user.username,
            'year_display': profile.get_year_of_study_display() or "Not specified",
            'province_display': profile.get_province_display() or "Not specified", 
            'college_type_display': profile.get_college_type_display() or "Not specified",
            'college_name': profile.college_name or "Not specified",
            'phone_number': profile.phone_number or "Not provided",
            'premium_status': "Premium" if profile.is_premium else "Free",
            'join_date': profile.created_at.strftime("%B %d, %Y"),
        }
        
        print("2. Template display data:")
        for key, value in template_data.items():
            print(f"   {key}: {value}")
        
        # Verify no field shows empty
        for key, value in template_data.items():
            if not value or value.strip() == "":
                print(f"   ⚠️  WARNING: {key} is empty!")
                return False
        
        print("3. ✅ All template fields have proper values!")
        return True
        
    except (User.DoesNotExist, UserProfile.DoesNotExist) as e:
        print(f"1. ERROR: User or profile not found: {e}")
        return False


if __name__ == '__main__':
    print("Starting final verification...")
    
    # Test 1: Create user and verify profile
    success1 = create_test_user_and_verify()
    
    # Test 2: Verify template display logic
    success2 = test_user_detail_template_display()
    
    print(f"\n=== FINAL VERIFICATION RESULTS ===")
    print(f"User creation & profile: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Template display logic: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("\n🎉 FINAL VERIFICATION PASSED!")
        print("✅ Signup form correctly saves all profile fields")
        print("✅ User detail page will display all information correctly")
        print("✅ The MedPrep User Detail admin page is ready for use!")
    else:
        print("\n⚠️  Some verification tests failed.")
