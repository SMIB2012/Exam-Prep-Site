#!/usr/bin/env python
"""
Debug the form save method directly
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from core.forms import UserRegistrationForm

def debug_form_save():
    """Debug the form save method"""
    test_data = {
        'username': 'debugtest@example.com',
        'first_name': 'Debug',
        'last_name': 'Test',
        'email': 'debugtest@example.com',
        'password1': 'TestPassword123!',
        'password2': 'TestPassword123!',
        'year_of_study': '3rd_year',
        'province': 'Sindh',
        'college_type': 'Private',
        'college_name': 'Aga Khan University',
        'phone_number': '+92-321-9999999',
    }
    
    print("="*60)
    print("FORM DEBUG TEST")
    print("="*60)
    
    form = UserRegistrationForm(data=test_data)
    
    print("1. Form validation...")
    if form.is_valid():
        print("✅ Form is valid")
        
        print("\n2. Checking cleaned_data...")
        for field in ['year_of_study', 'province', 'college_type', 'college_name', 'phone_number']:
            value = form.cleaned_data.get(field, 'NOT_FOUND')
            print(f"   {field}: '{value}'")
        
        print("\n3. Saving form...")
        user = form.save(commit=False)
        print(f"   User created (not committed): {user}")
        
        print("\n4. Committing save...")
        user = form.save(commit=True)
        print(f"   User saved: {user}")
        
        print("\n5. Checking profile...")
        try:
            profile = user.userprofile
            print(f"   Profile exists: {profile}")
            print(f"   Year: '{profile.year_of_study}'")
            print(f"   Province: '{profile.province}'")
            print(f"   College Type: '{profile.college_type}'")
            print(f"   College Name: '{profile.college_name}'")
            print(f"   Phone: '{profile.phone_number}'")
        except Exception as e:
            print(f"   ❌ Profile error: {e}")
        
        # Clean up
        user.delete()
        print("\n6. ✅ Test user cleaned up")
        
    else:
        print("❌ Form validation failed:")
        for field, errors in form.errors.items():
            print(f"   {field}: {errors}")

def debug_manual_save():
    """Test manual profile creation"""
    from django.contrib.auth.models import User
    from core.models import UserProfile
    
    print("\n" + "="*60)
    print("MANUAL SAVE TEST")
    print("="*60)
    
    # Create user manually
    user = User.objects.create_user(
        username='manualtest@example.com',
        email='manualtest@example.com',
        first_name='Manual',
        last_name='Test',
        password='TestPassword123!'
    )
    
    print(f"1. User created: {user}")
    
    # Check if profile was auto-created by signal
    try:
        profile = user.userprofile
        print(f"2. Auto-created profile: {profile}")
        print(f"   Initial data: year='{profile.year_of_study}', province='{profile.province}'")
    except:
        print("2. No auto-created profile")
        profile = UserProfile.objects.create(user=user)
        print(f"   Manually created profile: {profile}")
    
    # Update profile
    profile.year_of_study = '2nd_year'
    profile.province = 'Punjab'
    profile.college_type = 'Public'
    profile.college_name = 'Test College'
    profile.phone_number = '+92-300-1111111'
    profile.save()
    
    print(f"3. Updated profile:")
    print(f"   Year: '{profile.year_of_study}' -> {profile.get_year_of_study_display()}")
    print(f"   Province: '{profile.province}' -> {profile.get_province_display()}")
    print(f"   College Type: '{profile.college_type}' -> {profile.get_college_type_display()}")
    print(f"   College Name: '{profile.college_name}'")
    
    # Clean up
    user.delete()
    print("4. ✅ Test user cleaned up")

if __name__ == '__main__':
    debug_form_save()
    debug_manual_save()
