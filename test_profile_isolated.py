#!/usr/bin/env python
"""
Very specific test to isolate the profile saving issue
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
from django.db import transaction

def test_direct_profile_creation():
    """Test creating a profile directly without the form"""
    print("="*60)
    print("DIRECT PROFILE CREATION TEST")
    print("="*60)
    
    # Create user first
    user = User.objects.create_user(
        username='directtest@example.com',
        email='directtest@example.com',
        first_name='Direct',
        last_name='Test',
        password='TestPassword123!'
    )
    
    print(f"1. User created: {user}")
    
    # Check if profile was auto-created
    try:
        profile = user.userprofile
        print(f"2. Auto-created profile found: {profile}")
        print(f"   Initial values: year='{profile.year_of_study}', province='{profile.province}'")
        
        # Update the profile
        profile.year_of_study = '4th_year'
        profile.province = 'Balochistan'
        profile.college_type = 'Private'
        profile.college_name = 'Direct Test College'
        profile.save()
        
        print(f"3. Profile updated and saved")
        
        # Refresh from database
        profile.refresh_from_db()
        print(f"4. After refresh from DB:")
        print(f"   year='{profile.year_of_study}' -> {profile.get_year_of_study_display()}")
        print(f"   province='{profile.province}' -> {profile.get_province_display()}")
        print(f"   college_type='{profile.college_type}' -> {profile.get_college_type_display()}")
        print(f"   college_name='{profile.college_name}'")
        
        # Test if values persist
        user2 = User.objects.get(pk=user.pk)
        profile2 = user2.userprofile
        print(f"5. Re-fetched user and profile:")
        print(f"   year='{profile2.year_of_study}'")
        print(f"   province='{profile2.province}'")
        
        success = (profile2.year_of_study == '4th_year' and profile2.province == 'Balochistan')
        
    except UserProfile.DoesNotExist:
        print("2. No auto-created profile found")
        success = False
    
    # Clean up
    user.delete()
    print("6. ✅ Test user cleaned up")
    
    return success

def test_form_step_by_step():
    """Test form processing step by step"""
    print("\n" + "="*60)
    print("FORM STEP-BY-STEP TEST")
    print("="*60)
    
    from core.forms import UserRegistrationForm
    
    form_data = {
        'username': 'steptest@example.com',
        'first_name': 'Step',
        'last_name': 'Test', 
        'email': 'steptest@example.com',
        'password1': 'TestPassword123!',
        'password2': 'TestPassword123!',
        'year_of_study': '1st_year',
        'province': 'Khyber Pakhtunkhwa',
        'college_type': 'Public',
        'college_name': 'Step Test College',
        'phone_number': '+92-333-7777777',
    }
    
    print("1. Creating form with data...")
    form = UserRegistrationForm(data=form_data)
    
    if form.is_valid():
        print("2. ✅ Form is valid")
        
        # Step-by-step save process
        print("3. Calling super().save(commit=False)...")
        user = form.__class__.__bases__[0].save(form, commit=False)
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.email = form.cleaned_data['email']
        
        print("4. Saving user...")
        user.save()
        print(f"   User saved: {user}")
        
        print("5. Checking if profile was auto-created...")
        try:
            profile = user.userprofile
            print(f"   Profile found: {profile}")
            print(f"   Initial values: year='{profile.year_of_study}', province='{profile.province}'")
        except UserProfile.DoesNotExist:
            print("   No profile found, creating one...")
            profile = UserProfile.objects.create(user=user)
        
        print("6. Updating profile with form data...")
        profile.year_of_study = form.cleaned_data['year_of_study']
        profile.province = form.cleaned_data['province']
        profile.college_type = form.cleaned_data['college_type']
        profile.college_name = form.cleaned_data['college_name']
        profile.phone_number = form.cleaned_data.get('phone_number', '')
        
        print(f"   Assigned values: year='{profile.year_of_study}', province='{profile.province}'")
        
        print("7. Saving profile...")
        profile.save()
        
        print("8. Verifying profile after save...")
        profile.refresh_from_db()
        print(f"   Final values: year='{profile.year_of_study}', province='{profile.province}'")
        
        success = (profile.year_of_study == '1st_year' and profile.province == 'Khyber Pakhtunkhwa')
        
        # Clean up
        user.delete()
        print("9. ✅ Test user cleaned up")
        
        return success
    else:
        print("2. ❌ Form validation failed")
        for field, errors in form.errors.items():
            print(f"   {field}: {errors}")
        return False

def main():
    success1 = test_direct_profile_creation()
    success2 = test_form_step_by_step()
    
    print("\n" + "="*60)
    print("DIAGNOSTIC RESULTS")
    print("="*60)
    
    if success1:
        print("✅ Direct profile creation works")
    else:
        print("❌ Direct profile creation failed")
    
    if success2:
        print("✅ Step-by-step form processing works")
        print("\n🎉 The issue is fixed! Form should now work correctly.")
    else:
        print("❌ Step-by-step form processing failed")
        print("\n❌ There's still an issue with the form processing.")

if __name__ == '__main__':
    main()
