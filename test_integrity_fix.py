#!/usr/bin/env python
"""
Test script to verify the UserProfile IntegrityError fix
"""

import os
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')

import django
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.messages.storage.fallback import FallbackStorage
from staff.views.user_views import UserCreateView
from staff.forms import UserCreateForm
from core.models import UserProfile

def test_user_creation_fix():
    """Test that user creation doesn't cause IntegrityError"""
    print("🔍 Testing UserProfile IntegrityError fix...")
    
    # Clean up any existing test users
    User.objects.filter(email='test.integrity@example.com').delete()
    
    # Create a request factory
    factory = RequestFactory()
    
    # Create a staff user for the request
    staff_user = User.objects.create_user(
        username='teststaff',
        email='teststaff@example.com',
        password='testpass123',
        is_staff=True
    )
    
    # Create POST request with form data
    form_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test.integrity@example.com',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!',  # Required field
        'user_role': 'student',
        'year_of_study': '1st_year',
        'province': 'Punjab',
        'college_type': 'Public',
        'college_name': 'King Edward Medical University (Lahore)',  # Valid choice
        'phone_number': '+92-300-1234567',
        'is_premium': False,
        'is_active': True,
        'send_welcome_email': False
    }
    
    request = factory.post('/staff/users/add/', form_data)
    request.user = staff_user
    
    # Add session and messages
    session = SessionStore()
    session.create()
    request.session = session
    request._messages = FallbackStorage(request)
    
    try:
        # Create form and test validation
        form = UserCreateForm(data=form_data)
        print(f"   Form is valid: {form.is_valid()}")
        
        if not form.is_valid():
            print(f"   Form errors: {form.errors}")
            return False
        
        # Create view and test form_valid method
        view = UserCreateView()
        view.request = request
        
        print("   Testing form_valid method...")
        response = view.form_valid(form)
        
        print("   ✅ User creation successful!")
        
        # Verify user was created
        user = User.objects.get(email='test.integrity@example.com')
        print(f"   User created: {user.first_name} {user.last_name}")
        
        # Verify profile was created/updated
        profile = user.userprofile
        print(f"   Profile exists: {profile is not None}")
        print(f"   Profile college: {profile.college_name}")
        print(f"   Profile year: {profile.year_of_study}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error during user creation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        try:
            User.objects.filter(email='test.integrity@example.com').delete()
            User.objects.filter(username='teststaff').delete()
        except:
            pass

def test_signal_behavior():
    """Test that the signal automatically creates UserProfile"""
    print("\n🔍 Testing UserProfile signal behavior...")
    
    # Clean up
    User.objects.filter(email='signal.test@example.com').delete()
    
    try:
        # Create a user
        user = User.objects.create_user(
            username='signaltest',
            email='signal.test@example.com',
            password='testpass123'
        )
        
        print("   User created")
        
        # Check if profile was automatically created
        try:
            profile = user.userprofile
            print("   ✅ UserProfile was automatically created by signal")
            print(f"   Profile ID: {profile.id}")
            return True
        except UserProfile.DoesNotExist:
            print("   ❌ UserProfile was NOT automatically created")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing signal: {e}")
        return False
    
    finally:
        # Clean up
        try:
            User.objects.filter(email='signal.test@example.com').delete()
        except:
            pass

def test_multiple_profile_creation():
    """Test that we can't create multiple profiles for the same user"""
    print("\n🔍 Testing multiple profile creation prevention...")
    
    # Clean up
    User.objects.filter(email='multi.test@example.com').delete()
    
    try:
        # Create a user (profile will be created automatically)
        user = User.objects.create_user(
            username='multitest',
            email='multi.test@example.com',
            password='testpass123'
        )
        
        # Verify one profile exists
        profile_count = UserProfile.objects.filter(user=user).count()
        print(f"   Profiles after user creation: {profile_count}")
        
        if profile_count != 1:
            print("   ❌ Expected exactly 1 profile")
            return False
        
        # Try to create another profile (this should fail)
        try:
            UserProfile.objects.create(user=user)
            print("   ❌ ERROR: Second profile creation should have failed!")
            return False
        except Exception as e:
            print("   ✅ Second profile creation correctly failed")
            print(f"   Error: {type(e).__name__}")
            return True
            
    except Exception as e:
        print(f"   ❌ Error during test: {e}")
        return False
    
    finally:
        # Clean up
        try:
            User.objects.filter(email='multi.test@example.com').delete()
        except:
            pass

if __name__ == '__main__':
    print("🛠️ USERPROFILE INTEGRITYERROR FIX TEST")
    print("=" * 50)
    
    test1 = test_signal_behavior()
    test2 = test_multiple_profile_creation()
    test3 = test_user_creation_fix()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"   Signal creates profile: {'✅' if test1 else '❌'}")
    print(f"   Multiple profile prevention: {'✅' if test2 else '❌'}")
    print(f"   User creation fix: {'✅' if test3 else '❌'}")
    
    if test1 and test2 and test3:
        print("\n🎉 ALL TESTS PASSED!")
        print("   The IntegrityError fix is working correctly.")
        print("   User creation should now work without errors.")
    else:
        print("\n⚠️ SOME TESTS FAILED!")
        print("   The fix may need additional work.")
    
    print("=" * 50)
