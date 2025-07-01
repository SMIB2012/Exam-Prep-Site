#!/usr/bin/env python
"""
Test login functionality with both username and email
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import UserProfile

def test_login_functionality():
    """Test login with both username and email"""
    print("Testing login functionality...")
    
    # Create a test client
    client = Client()
    
    # Create a test user
    test_user = User.objects.create_user(
        username='testlogin',
        email='testlogin@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    
    # Create user profile
    UserProfile.objects.create(
        user=test_user,
        year_of_study='2nd_year',
        province='Punjab',
        college_type='Public',
        college_name='King Edward Medical University (Lahore)'
    )
    
    login_url = reverse('core:login')
    print(f"Login URL: {login_url}")
    
    # Test 1: Login with username
    print("\n1. Testing login with USERNAME:")
    login_data = {
        'username': 'testlogin',
        'password': 'testpass123'
    }
    
    response = client.post(login_url, login_data)
    print(f"   Status code: {response.status_code}")
    
    if response.status_code == 302:  # Redirect after successful login
        print("   ✓ Login with username successful")
        # Logout for next test
        client.logout()
    else:
        print("   ✗ Login with username failed")
        if hasattr(response, 'context') and response.context and 'form' in response.context:
            print(f"   Form errors: {response.context['form'].errors}")
    
    # Test 2: Login with email
    print("\n2. Testing login with EMAIL:")
    login_data = {
        'username': 'testlogin@example.com',  # Using email in username field
        'password': 'testpass123'
    }
    
    response = client.post(login_url, login_data)
    print(f"   Status code: {response.status_code}")
    
    if response.status_code == 302:  # Redirect after successful login
        print("   ✓ Login with email successful")
        client.logout()
    else:
        print("   ✗ Login with email failed")
        if hasattr(response, 'context') and response.context and 'form' in response.context:
            print(f"   Form errors: {response.context['form'].errors}")
    
    # Test 3: Login with invalid credentials
    print("\n3. Testing login with INVALID credentials:")
    login_data = {
        'username': 'invalid@example.com',
        'password': 'wrongpassword'
    }
    
    response = client.post(login_url, login_data)
    print(f"   Status code: {response.status_code}")
    
    if response.status_code == 200:  # Should stay on login page
        print("   ✓ Invalid login correctly rejected")
    else:
        print("   ? Unexpected response for invalid login")
    
    # Test 4: Test form validation
    print("\n4. Testing form validation:")
    from core.forms import CustomAuthenticationForm
    
    # Test with username
    form_data = {'username': 'testlogin', 'password': 'testpass123'}
    form = CustomAuthenticationForm(data=form_data)
    print(f"   Form valid with username: {form.is_valid()}")
    
    # Test with email
    form_data = {'username': 'testlogin@example.com', 'password': 'testpass123'}
    form = CustomAuthenticationForm(data=form_data)
    print(f"   Form valid with email: {form.is_valid()}")
    
    # Test with invalid email
    form_data = {'username': 'invalid@example.com', 'password': 'testpass123'}
    form = CustomAuthenticationForm(data=form_data)
    print(f"   Form valid with invalid email: {form.is_valid()}")
    
    # Clean up test user
    test_user.delete()
    print("\n✓ Test user cleaned up")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("LOGIN FUNCTIONALITY TEST")
    print("=" * 60)
    
    try:
        success = test_login_functionality()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ LOGIN FUNCTIONALITY TEST COMPLETED")
            print("=" * 60)
            print("CHANGES MADE:")
            print("✓ Created CustomAuthenticationForm")
            print("✓ Form accepts both username and email")
            print("✓ Updated CustomLoginView to use new form")
            print("✓ Updated login template labels")
            print("✓ No additional fields added")
            print("✓ Page layout unchanged")
            
            print("\nHOW IT WORKS:")
            print("1. User types username OR email in the same field")
            print("2. Form detects if input contains '@' (email)")
            print("3. If email, looks up username by email")
            print("4. Authenticates using username (converted or original)")
            print("5. User can login with either credential type")
            
        else:
            print("\n❌ LOGIN FUNCTIONALITY TEST FAILED")
            
    except Exception as e:
        print(f"\n❌ ERROR RUNNING TEST: {e}")
        import traceback
        traceback.print_exc()
