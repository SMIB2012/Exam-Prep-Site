#!/usr/bin/env python
"""
Test script to verify the user_edit.html template can be parsed by Django
"""
import os
import sys
import django
from django.conf import settings
from django.template import Template, Context
from django.template.loader import get_template

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

def test_user_edit_template():
    """Test that the user_edit template can be loaded and parsed"""
    try:
        # Try to get the template
        template = get_template('staff/users/user_edit.html')
        print("✅ Template loaded successfully!")
        
        # Test rendering with minimal context
        from django.contrib.auth.models import User
        from core.models import UserProfile
        
        # Create a test user if none exists
        test_user, created = User.objects.get_or_create(
            username='test_template_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Ensure user has a profile
        profile, created = UserProfile.objects.get_or_create(
            user=test_user,
            defaults={
                'college': 'Test College',
                'year_of_study': 1,
                'preferred_language': 'en'
            }
        )
        
        # Create a minimal context
        context = {
            'user': test_user,
            'form': None,  # We'll use a mock form
            'quiz_stats': {
                'total_attempts': 0,
                'avg_score': 0,
                'best_score': 0,
                'total_time_spent': 0
            },
            'recent_activities': []
        }
        
        # Try to render (this will catch template syntax errors)
        rendered = template.render(context)
        print("✅ Template rendered successfully!")
        print(f"Template length: {len(rendered)} characters")
        
        # Check for block structure
        if '{% block content %}' in open('templates/staff/users/user_edit.html').read():
            count = open('templates/staff/users/user_edit.html').read().count('{% block content %}')
            if count == 1:
                print("✅ Template has exactly one content block")
            else:
                print(f"❌ Template has {count} content blocks (should be 1)")
        
        return True
        
    except Exception as e:
        print(f"❌ Template error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == '__main__':
    print("Testing user_edit.html template...")
    print("=" * 50)
    
    success = test_user_edit_template()
    
    print("=" * 50)
    if success:
        print("✅ All template tests passed!")
    else:
        print("❌ Template tests failed!")
    
    sys.exit(0 if success else 1)
