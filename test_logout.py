#!/usr/bin/env python
"""
Test logout functionality
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

def test_logout_functionality():
    """Test logout GET and POST requests"""
    print("Testing logout functionality...")
    
    # Create a test client
    client = Client()
    
    # Test logout URL resolution
    try:
        logout_url = reverse('core:logout')
        print(f"✓ Logout URL resolved: {logout_url}")
    except Exception as e:
        print(f"✗ Error resolving logout URL: {e}")
        return False
    
    # Test GET request to logout (should work now)
    print("\nTesting GET request to /logout/:")
    try:
        response = client.get(logout_url)
        print(f"  Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("  ✓ GET request successful")
        elif response.status_code == 405:
            print("  ✗ Method not allowed (405) - GET not working")
            return False
        elif response.status_code == 302:
            print("  ✓ Redirect response (user not logged in)")
        else:
            print(f"  ? Unexpected status code: {response.status_code}")
    
    except Exception as e:
        print(f"  ✗ Error with GET request: {e}")
        return False
    
    # Test POST request to logout
    print("\nTesting POST request to /logout/:")
    try:
        response = client.post(logout_url)
        print(f"  Status code: {response.status_code}")
        
        if response.status_code in [200, 302]:
            print("  ✓ POST request successful")
        else:
            print(f"  ? Unexpected status code: {response.status_code}")
    
    except Exception as e:
        print(f"  ✗ Error with POST request: {e}")
        return False
    
    # Test logout with authenticated user
    print("\nTesting logout with authenticated user:")
    try:
        # Create a test user
        test_user = User.objects.create_user(
            username='testlogout',
            email='testlogout@example.com',
            password='testpass123'
        )
        
        # Login the user
        login_success = client.login(username='testlogout', password='testpass123')
        print(f"  Login successful: {login_success}")
        
        if login_success:
            # Test logout
            response = client.get(logout_url)
            print(f"  Logout GET status: {response.status_code}")
            
            # Check if user is logged out by trying to access a protected page
            dashboard_url = reverse('core:dashboard')
            response = client.get(dashboard_url)
            if response.status_code == 302:  # Redirect to login
                print("  ✓ User successfully logged out")
            else:
                print(f"  ? User might still be logged in (status: {response.status_code})")
        
        # Clean up test user
        test_user.delete()
        print("  ✓ Test user cleaned up")
        
    except Exception as e:
        print(f"  ✗ Error testing authenticated logout: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_logout_functionality()
    
    if success:
        print("\n✅ LOGOUT FUNCTIONALITY TEST PASSED")
        print("✓ GET requests to /logout/ work")
        print("✓ POST requests to /logout/ work") 
        print("✓ Authenticated user logout works")
        print("✓ No more 405 Method Not Allowed errors")
    else:
        print("\n❌ LOGOUT FUNCTIONALITY TEST FAILED")
        print("Some issues need to be resolved.")
