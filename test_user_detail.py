#!/usr/bin/env python
"""
Test script to verify the user detail page functionality
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
from django.test import RequestFactory
from staff.views.user_views import UserDetailView

def test_user_detail_view():
    """Test the UserDetailView functionality"""
    print("Testing User Detail View...")
    
    # Create a test user if one doesn't exist
    test_user, created = User.objects.get_or_create(
        username='testuser@example.com',
        defaults={
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True
        }
    )
    
    if created:
        print(f"Created test user: {test_user.username}")
    else:
        print(f"Using existing test user: {test_user.username}")
    
    # Ensure user has a profile
    profile, profile_created = UserProfile.objects.get_or_create(
        user=test_user,
        defaults={
            'year_of_study': '2nd_year',
            'province': 'Punjab',
            'college_type': 'Public',
            'college_name': 'Test Medical College',
            'phone_number': '+92-300-1234567',
            'is_premium': True
        }
    )
    
    if profile_created:
        print(f"Created profile for test user")
    else:
        print(f"Using existing profile for test user")
    
    # Test the view
    factory = RequestFactory()
    request = factory.get(f'/staff/users/{test_user.pk}/')
    
    # Create a mock staff user for the request
    staff_user = User.objects.filter(is_staff=True).first()
    if not staff_user:
        staff_user, _ = User.objects.get_or_create(
            username='admin@example.com',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        staff_user.set_password('admin123')
        staff_user.save()
        print(f"Created admin user: {staff_user.username}")
    
    request.user = staff_user
    
    try:
        view = UserDetailView()
        view.setup(request, pk=test_user.pk)
        context = view.get_context_data()
        
        print("\n✅ User Detail View Test Results:")
        print(f"   User: {context['user'].get_full_name()}")
        print(f"   Quiz Stats: {context.get('quiz_stats', 'Not available')}")
        print(f"   Recent Attempts: {len(context.get('recent_attempts', []))}")
        print(f"   Today: {context.get('today', 'Not set')}")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_templates_exist():
    """Test that all required templates exist"""
    print("\nTesting Template Files...")
    
    templates = [
        'templates/staff/users/user_detail.html',
        'templates/staff/users/user_edit.html',
        'static/staff/css/user_detail.css'
    ]
    
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    for template in templates:
        full_path = os.path.join(base_path, template)
        if os.path.exists(full_path):
            print(f"✅ {template} exists")
        else:
            print(f"❌ {template} missing")
            return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("MEDPREP ADMIN USER DETAIL PAGE TESTS")
    print("=" * 50)
    
    success = True
    
    # Test template files
    success &= test_templates_exist()
    
    # Test view functionality
    success &= test_user_detail_view()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("\nTo test the user detail page:")
        print("1. Run: python manage.py runserver")
        print("2. Visit: http://127.0.0.1:8000/staff/")
        print("3. Login as admin and navigate to Users")
        print("4. Click 'View Details' on any user")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
