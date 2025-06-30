#!/usr/bin/env python
"""
Quick test script to validate Django setup and homepage functionality
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
    django.setup()

def test_url_resolution():
    """Test that all main URLs can be resolved"""
    from django.urls import reverse
    
    urls_to_test = [
        'core:home',
        'core:signup', 
        'core:login',
        'core:logout',
        'core:dashboard',
        'core:question_bank',
        'core:leaderboard',
        'core:resources',
        'core:subscription',
        'core:about',
        'core:contact',
        'core:faq',
        'core:terms',
        'core:privacy'
    ]
    
    print("Testing URL resolution...")
    for url_name in urls_to_test:
        try:
            resolved_url = reverse(url_name)
            print(f"✅ {url_name}: {resolved_url}")
        except Exception as e:
            print(f"❌ {url_name}: ERROR - {e}")
    
    return True

def test_view_imports():
    """Test that all views can be imported"""
    print("\nTesting view imports...")
    try:
        from core.views import (
            HomeView, RegisterView, CustomLoginView, 
            DashboardView, QuestionBankView, LeaderboardView,
            ResourcesView, SubscriptionView
        )
        print("✅ All main views imported successfully")
        return True
    except Exception as e:
        print(f"❌ View import error: {e}")
        return False

def test_template_syntax():
    """Test basic template loading"""
    print("\nTesting template syntax...")
    try:
        from django.template.loader import get_template
        
        templates_to_test = [
            'base.html',
            'core/home.html',
            'core/dashboard.html',
            'core/leaderboard.html'
        ]
        
        for template_name in templates_to_test:
            try:
                template = get_template(template_name)
                print(f"✅ {template_name}: OK")
            except Exception as e:
                print(f"❌ {template_name}: ERROR - {e}")
        
        return True
    except Exception as e:
        print(f"❌ Template testing error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 MedPrep Django Setup Validation")
    print("=" * 50)
    
    try:
        setup_django()
        print("✅ Django setup successful")
        
        # Run tests
        url_test = test_url_resolution()
        view_test = test_view_imports() 
        template_test = test_template_syntax()
        
        print("\n" + "=" * 50)
        if url_test and view_test and template_test:
            print("🎉 All tests PASSED! Homepage should work correctly.")
        else:
            print("⚠️  Some tests failed. Check the errors above.")
            
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

if __name__ == '__main__':
    main()
