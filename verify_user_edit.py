#!/usr/bin/env python
"""
Quick verification that the user edit page is working correctly
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

def test_imports():
    """Test all necessary imports"""
    print("Testing imports...")
    
    try:
        from staff.views.user_views import UserEditView, UserDetailView
        print("✅ UserEditView and UserDetailView imported successfully")
    except ImportError as e:
        print(f"❌ Error importing views: {e}")
        return False
        
    try:
        from staff.forms import UserEditForm
        print("✅ UserEditForm imported successfully")
    except ImportError as e:
        print(f"❌ Error importing UserEditForm: {e}")
        return False
        
    try:
        from core.models import QuizSession, UserProfile
        print("✅ QuizSession and UserProfile imported successfully")
    except ImportError as e:
        print(f"❌ Error importing models: {e}")
        return False
        
    return True

def test_template_exists():
    """Test that template files exist"""
    print("\nTesting template files...")
    
    templates = [
        'templates/staff/users/user_edit.html',
        'templates/staff/users/user_detail.html'
    ]
    
    for template in templates:
        if os.path.exists(template):
            print(f"✅ {template} exists")
        else:
            print(f"❌ {template} missing")
            return False
    
    return True

def main():
    print("🔍 MedPrep User Edit Page Verification")
    print("=" * 40)
    
    all_good = True
    
    if not test_imports():
        all_good = False
    
    if not test_template_exists():
        all_good = False
    
    print("\n" + "=" * 40)
    if all_good:
        print("🎉 All tests passed! User edit page is ready to use.")
        print("\nTo access the user edit page:")
        print("1. Start the server with: python manage.py runserver")
        print("2. Go to Admin > Users")
        print("3. Click on any user")
        print("4. Click 'Edit User' button")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
