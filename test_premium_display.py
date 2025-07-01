#!/usr/bin/env python
"""
Test the premium user display fix
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
from django.utils import timezone
from datetime import timedelta

def test_premium_user_display():
    """Test that premium users display correctly in the user list"""
    print("🧪 Testing Premium User Display Fix")
    print("=" * 40)
    
    # Clean up any existing test users
    User.objects.filter(email='premium.test@example.com').delete()
    User.objects.filter(email='free.test@example.com').delete()
    
    try:
        # Create a premium user
        print("1. Creating premium user...")
        premium_user = User.objects.create_user(
            username='premiumtest',
            email='premium.test@example.com',
            password='test123',
            first_name='Premium',
            last_name='User'
        )
        
        # Update profile to be premium with expiration
        premium_profile = premium_user.userprofile
        premium_profile.is_premium = True
        premium_profile.premium_expires_at = timezone.now() + timedelta(days=365)
        premium_profile.save()
        
        print(f"   ✅ Premium user created: {premium_user.get_full_name()}")
        print(f"   is_premium: {premium_profile.is_premium}")
        print(f"   premium_expires_at: {premium_profile.premium_expires_at}")
        print(f"   is_premium_active: {premium_profile.is_premium_active}")
        
        # Create a free user
        print("\n2. Creating free user...")
        free_user = User.objects.create_user(
            username='freetest',
            email='free.test@example.com',
            password='test123',
            first_name='Free',
            last_name='User'
        )
        
        free_profile = free_user.userprofile
        print(f"   ✅ Free user created: {free_user.get_full_name()}")
        print(f"   is_premium: {free_profile.is_premium}")
        print(f"   premium_expires_at: {free_profile.premium_expires_at}")
        print(f"   is_premium_active: {free_profile.is_premium_active}")
        
        # Test the template logic
        print("\n3. Testing template display logic...")
        
        # Premium user should show as Premium
        if premium_profile.is_premium_active:
            print("   ✅ Premium user will show 'Premium' badge")
        else:
            print("   ❌ Premium user will show 'Free' badge (PROBLEM!)")
        
        # Free user should show as Free
        if not free_profile.is_premium_active:
            print("   ✅ Free user will show 'Free' badge")
        else:
            print("   ❌ Free user will show 'Premium' badge (PROBLEM!)")
        
        return premium_profile.is_premium_active and not free_profile.is_premium_active
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        try:
            User.objects.filter(email='premium.test@example.com').delete()
            User.objects.filter(email='free.test@example.com').delete()
        except:
            pass

def test_premium_user_creation():
    """Test creating a premium user through the view"""
    print("\n🧪 Testing Premium User Creation via Form")
    print("=" * 40)
    
    from staff.forms import UserCreateForm
    from django.utils import timezone
    from datetime import timedelta
    
    # Clean up
    User.objects.filter(email='formtest@example.com').delete()
    
    try:
        # Test form data
        future_date = timezone.now() + timedelta(days=30)
        form_data = {
            'first_name': 'Form',
            'last_name': 'Test',
            'email': 'formtest@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'user_role': 'student',
            'year_of_study': '1st_year',
            'province': 'Punjab',
            'college_type': 'Public',
            'college_name': 'King Edward Medical University (Lahore)',
            'phone_number': '+92-300-1234567',
            'is_premium': True,
            'premium_expires_at': future_date,
            'is_active': True,
            'send_welcome_email': False
        }
        
        print("1. Testing form validation...")
        form = UserCreateForm(data=form_data)
        
        if form.is_valid():
            print("   ✅ Form validation passed")
            
            print("2. Simulating user creation...")
            # Simulate what the view does
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            user.is_active = form.cleaned_data.get('is_active', True)
            user.save()
            
            # Update profile
            profile_data = {
                'year_of_study': form.cleaned_data.get('year_of_study', ''),
                'province': form.cleaned_data.get('province', ''),
                'college_type': form.cleaned_data.get('college_type', ''),
                'college_name': form.cleaned_data.get('college_name', ''),
                'phone_number': form.cleaned_data.get('phone_number', ''),
                'is_premium': form.cleaned_data.get('is_premium', False),
            }
            
            profile = user.userprofile
            for field, value in profile_data.items():
                setattr(profile, field, value)
            
            # Handle premium expiration
            if profile_data.get('is_premium', False):
                custom_expiry = form.cleaned_data.get('premium_expires_at')
                if custom_expiry:
                    profile.premium_expires_at = custom_expiry
                else:
                    profile.premium_expires_at = timezone.now() + timedelta(days=365)
            
            profile.save()
            
            print("   ✅ User created successfully")
            print(f"   User: {user.get_full_name()}")
            print(f"   is_premium: {profile.is_premium}")
            print(f"   premium_expires_at: {profile.premium_expires_at}")
            print(f"   is_premium_active: {profile.is_premium_active}")
            
            return profile.is_premium_active
            
        else:
            print("   ❌ Form validation failed")
            print(f"   Errors: {form.errors}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        try:
            User.objects.filter(email='formtest@example.com').delete()
        except:
            pass

if __name__ == '__main__':
    print("🔧 PREMIUM USER DISPLAY FIX TEST")
    print("=" * 50)
    
    test1 = test_premium_user_display()
    test2 = test_premium_user_creation()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    print(f"   Premium display logic: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"   Premium user creation: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n🎉 SUCCESS!")
        print("   Premium users should now display correctly in the user list.")
        print("   The subscription status should show 'Premium' for active premium users.")
    else:
        print("\n⚠️ ISSUES DETECTED!")
        print("   There may still be problems with premium user display.")
    
    print("=" * 50)
