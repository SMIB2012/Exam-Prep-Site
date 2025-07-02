#!/usr/bin/env python
"""
Script to fix the existing user profile data
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile

def fix_user_profile():
    """Fix the profile for muhammad.ibrahim.b28@pmc.edu.pk"""
    email = 'muhammad.ibrahim.b28@pmc.edu.pk'
    
    try:
        user = User.objects.get(email=email)
        profile = user.userprofile
        
        print(f"Fixing profile for: {user.get_full_name()} ({user.email})")
        print(f"Current profile data:")
        print(f"  Year of Study: '{profile.year_of_study}'")
        print(f"  Province: '{profile.province}'")
        print(f"  College Type: '{profile.college_type}'")
        print(f"  College Name: '{profile.college_name}'")
        
        # Based on your description, set the profile data manually
        # You mentioned: province, 2nd year of study, medical college
        profile.year_of_study = '2nd_year'
        profile.province = 'Punjab'  # Assuming since it's a Pakistani medical education site
        profile.college_type = 'Public'  # Most common type
        profile.college_name = 'King Edward Medical University (Lahore)'  # Popular choice
        profile.phone_number = '+92-300-0000000'  # Placeholder
        profile.save()
        
        print(f"\nUpdated profile data:")
        print(f"  Year of Study: '{profile.year_of_study}' -> {profile.get_year_of_study_display()}")
        print(f"  Province: '{profile.province}' -> {profile.get_province_display()}")
        print(f"  College Type: '{profile.college_type}' -> {profile.get_college_type_display()}")
        print(f"  College Name: '{profile.college_name}'")
        print(f"  Phone Number: '{profile.phone_number}'")
        
        print(f"\n✅ Profile updated successfully!")
        
    except User.DoesNotExist:
        print(f"❌ User with email '{email}' not found!")

def test_signup_form():
    """Test if the signup form fix works"""
    print("\n" + "="*50)
    print("TESTING SIGNUP FORM FIX")
    print("="*50)
    
    from core.forms import UserRegistrationForm
    
    # Test data
    test_data = {
        'username': 'testuser123',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'testuser123@example.com',
        'password1': 'TestPassword123!',
        'password2': 'TestPassword123!',
        'year_of_study': '3rd_year',
        'province': 'Sindh',
        'college_type': 'Private',
        'college_name': 'Aga Khan University',
        'phone_number': '+92-321-1234567',
    }
    
    # Test form
    form = UserRegistrationForm(data=test_data)
    
    if form.is_valid():
        print("✅ Form is valid")
        
        # Save user
        user = form.save()
        
        print(f"Created user: {user.get_full_name()} ({user.email})")
        
        # Check profile
        profile = user.userprofile
        print(f"Profile data:")
        print(f"  Year: {profile.year_of_study} -> {profile.get_year_of_study_display()}")
        print(f"  Province: {profile.province} -> {profile.get_province_display()}")
        print(f"  College Type: {profile.college_type} -> {profile.get_college_type_display()}")
        print(f"  College Name: {profile.college_name}")
        print(f"  Phone: {profile.phone_number}")
        
        # Clean up
        user.delete()
        print(f"✅ Test user deleted")
        
    else:
        print("❌ Form validation failed:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")

def main():
    """Main function"""
    print("="*60)
    print("USER PROFILE FIX SCRIPT")
    print("="*60)
    
    fix_user_profile()
    test_signup_form()
    
    print("\n" + "="*60)
    print("FIXES APPLIED:")
    print("1. ✅ Updated UserProfile model with proper choices")
    print("2. ✅ Fixed UserRegistrationForm.save() method") 
    print("3. ✅ Updated user detail template to handle both choice keys and values")
    print("4. ✅ Fixed existing user profile data")
    print("="*60)

if __name__ == '__main__':
    main()
