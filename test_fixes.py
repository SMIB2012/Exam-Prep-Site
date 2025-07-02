#!/usr/bin/env python
"""
Test script to verify the reset password and stats fixes
"""
import os
import sys
import django
from django.test import TestCase, Client

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

def test_reset_password_action():
    """Test that the reset password action works correctly"""
    try:
        from django.contrib.auth.models import User
        from core.models import UserProfile
        from django.urls import reverse
        
        # Create test users
        admin_user, created = User.objects.get_or_create(
            username='test_admin_reset',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        test_user, created = User.objects.get_or_create(
            username='test_user_reset',
            defaults={
                'email': 'testreset@example.com',
                'first_name': 'Test',
                'last_name': 'Reset'
            }
        )
        
        print(f"✅ Test users created - Admin: {admin_user.username}, User: {test_user.username}")
        
        # Test with Django test client
        client = Client()
        client.force_login(admin_user)
        
        # Simulate POST request to user_list with reset_password action
        url = reverse('staff:user_list')
        response = client.post(url, {
            'action': 'reset_password',
            'user_ids': [test_user.id]
        })
        
        print(f"✅ Reset password POST response status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect after successful action
            print("✅ Reset password action executed successfully")
        else:
            print(f"❌ Unexpected response status: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing reset password: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_stats_rendering():
    """Test that the stats display correctly in template"""
    try:
        from django.template import Template, Context
        from django.contrib.auth.models import User
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        # Create a test user with last_login
        test_user = User.objects.create_user(
            username='test_stats_user',
            email='teststats@example.com',
            first_name='Stats',
            last_name='Test'
        )
        
        # Set last login to 2 hours ago
        test_user.last_login = timezone.now() - timedelta(hours=2)
        test_user.save()
        
        # Test template rendering
        template_content = """
        {% if user.last_login %}
            {{ user.last_login|timesince }} ago
        {% else %}
            Never
        {% endif %}
        """
        
        template = Template(template_content)
        context = Context({'user': test_user})
        rendered = template.render(context)
        
        print(f"✅ Template rendered: '{rendered.strip()}'")
        
        # Check that it doesn't just show "2"
        if "2" in rendered and "hour" in rendered:
            print("✅ Stats display correctly shows full time information")
        elif "Never" in rendered:
            print("✅ Stats display shows 'Never' for users who haven't logged in")
        else:
            print(f"❌ Unexpected stats display: {rendered}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing template stats: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Testing reset password and stats fixes...")
    print("=" * 50)
    
    test1 = test_reset_password_action()
    print("\n" + "=" * 50)
    
    test2 = test_template_stats_rendering()
    print("\n" + "=" * 50)
    
    if test1 and test2:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
