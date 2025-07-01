#!/usr/bin/env python
"""
Test script to simulate the exact user creation scenario that was failing
"""

import os
import sys

# Setup Django
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')

import django
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile
from staff.forms import UserCreateForm

def test_user_add_scenario():
    """Test the exact scenario that was causing IntegrityError"""
    print("🧪 Testing Add User Scenario")
    print("=" * 40)
    
    # Clean up any existing test data
    User.objects.filter(email='testuser@example.com').delete()
    
    # Form data similar to what would be submitted from the add user form
    form_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'testuser@example.com',
        'password': 'TestPassword123!',
        'confirm_password': 'TestPassword123!',
        'user_role': 'student',
        'year_of_study': '2nd_year',
        'province': 'Punjab',
        'college_type': 'Public',
        'college_name': 'King Edward Medical University (Lahore)',
        'phone_number': '+92-300-1234567',
        'is_premium': False,
        'is_active': True,
        'send_welcome_email': True
    }
    
    try:
        print("1. Creating form with data...")
        form = UserCreateForm(data=form_data)
        
        print("2. Validating form...")
        if form.is_valid():
            print("   ✅ Form validation passed")
            
            print("3. Creating user...")
            # Simulate what happens in the view
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            
            # Set admin fields
            user_role = form.cleaned_data.get('user_role', 'student')
            if user_role == 'admin':
                user.is_staff = True
                user.is_superuser = True
            elif user_role == 'faculty':
                user.is_staff = True
            
            user.is_active = form.cleaned_data.get('is_active', True)
            user.save()
            
            print("   ✅ User saved successfully")
            
            print("4. Updating profile...")
            # Update profile (profile is automatically created by signals)
            profile_data = {
                'year_of_study': form.cleaned_data.get('year_of_study', ''),
                'province': form.cleaned_data.get('province', ''),
                'college_type': form.cleaned_data.get('college_type', ''),
                'college_name': form.cleaned_data.get('college_name', ''),
                'phone_number': form.cleaned_data.get('phone_number', ''),
                'is_premium': form.cleaned_data.get('is_premium', False),
            }
            
            # Get the profile that was automatically created by the signal
            profile = user.userprofile
            for field, value in profile_data.items():
                setattr(profile, field, value)
            profile.save()
            
            print("   ✅ Profile updated successfully")
            
            print("\n📊 Results:")
            print(f"   User ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Full Name: {user.get_full_name()}")
            print(f"   Profile ID: {profile.id}")
            print(f"   College: {profile.college_name}")
            print(f"   Year: {profile.year_of_study}")
            
            print("\n🎉 SUCCESS! User creation completed without IntegrityError!")
            return True
            
        else:
            print("   ❌ Form validation failed")
            print(f"   Errors: {form.errors}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"   Error type: {type(e).__name__}")
        if "UNIQUE constraint failed" in str(e):
            print("   This is the IntegrityError that was supposed to be fixed!")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        try:
            User.objects.filter(email='testuser@example.com').delete()
        except:
            pass

if __name__ == '__main__':
    success = test_user_add_scenario()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ FIX VERIFIED: The IntegrityError issue is resolved!")
        print("   You can now use the Add User form without errors.")
    else:
        print("❌ FIX FAILED: The IntegrityError issue still exists.")
    print("=" * 40)
