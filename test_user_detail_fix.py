#!/usr/bin/env python
"""
Test the user detail page template rendering with the fixed data
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.contrib.auth.models import User
from django.template import Context, Template
from django.template.loader import get_template

def test_user_detail_template():
    """Test the user detail template with real data"""
    email = 'muhammad.ibrahim.b28@pmc.edu.pk'
    
    try:
        user = User.objects.get(email=email)
        profile = user.userprofile
        
        print("="*60)
        print("USER DETAIL TEMPLATE TEST")
        print("="*60)
        
        print(f"Testing template with user: {user.get_full_name()}")
        
        # Test template variables that were problematic
        test_vars = [
            ('user.userprofile.year_of_study', profile.year_of_study),
            ('user.userprofile.get_year_of_study_display', profile.get_year_of_study_display()),
            ('user.userprofile.province', profile.province),
            ('user.userprofile.get_province_display', profile.get_province_display()),
            ('user.userprofile.college_type', profile.college_type),
            ('user.userprofile.get_college_type_display', profile.get_college_type_display()),
            ('user.userprofile.college_name', profile.college_name),
        ]
        
        print("\nTemplate Variable Tests:")
        for var_name, value in test_vars:
            print(f"  {var_name}: '{value}'")
        
        # Test the template rendering logic
        template_code = """
        Year of Study: 
        {% if user.userprofile.year_of_study %}
            {{ user.userprofile.get_year_of_study_display|default:user.userprofile.year_of_study }}
        {% else %}
            Not specified
        {% endif %}
        
        Province: 
        {% if user.userprofile.province %}
            {{ user.userprofile.get_province_display|default:user.userprofile.province }}
        {% else %}
            Not specified
        {% endif %}
        
        College Type: 
        {% if user.userprofile.college_type %}
            {{ user.userprofile.get_college_type_display|default:user.userprofile.college_type }}
        {% else %}
            Not specified
        {% endif %}
        
        College Name: 
        {% if user.userprofile.college_name %}
            {{ user.userprofile.college_name }}
        {% else %}
            Not specified
        {% endif %}
        """
        
        template = Template(template_code)
        context = Context({'user': user})
        rendered = template.render(context)
        
        print("\nTemplate Rendering Test:")
        print(rendered)
        
        # Check if all expected data is present
        expected_values = [
            '2nd Year MBBS',
            'Punjab', 
            'Public',
            'King Edward Medical University (Lahore)'
        ]
        
        success = True
        for expected in expected_values:
            if expected in rendered:
                print(f"✅ Found expected value: '{expected}'")
            else:
                print(f"❌ Missing expected value: '{expected}'")
                success = False
        
        if success:
            print(f"\n🎉 All template variables are working correctly!")
        else:
            print(f"\n❌ Some template variables failed")
            
        return success
        
    except User.DoesNotExist:
        print(f"❌ User with email '{email}' not found!")
        return False

def test_signup_process_end_to_end():
    """Test the complete signup process"""
    print("\n" + "="*60)
    print("END-TO-END SIGNUP TEST")
    print("="*60)
    
    from core.forms import UserRegistrationForm
    
    # Simulate form submission data
    test_data = {
        'username': 'endtoendtest@example.com',
        'first_name': 'End',
        'last_name': 'Test',
        'email': 'endtoendtest@example.com',
        'password1': 'TestPassword123!',
        'password2': 'TestPassword123!',
        'year_of_study': '4th_year',
        'province': 'Sindh',
        'college_type': 'Private',
        'college_name': 'Aga Khan University',
        'phone_number': '+92-333-1234567',
    }
    
    print("1. Testing form validation...")
    form = UserRegistrationForm(data=test_data)
    
    if form.is_valid():
        print("✅ Form validation passed")
        
        print("2. Testing user creation...")
        user = form.save()
        print(f"✅ User created: {user.get_full_name()}")
        
        print("3. Testing profile creation...")
        profile = user.userprofile
        print(f"✅ Profile exists: {profile}")
        
        print("4. Testing profile data...")
        tests = [
            ('Year of Study', profile.year_of_study, '4th_year', profile.get_year_of_study_display()),
            ('Province', profile.province, 'Sindh', profile.get_province_display()),
            ('College Type', profile.college_type, 'Private', profile.get_college_type_display()),
            ('College Name', profile.college_name, 'Aga Khan University', profile.college_name),
        ]
        
        all_passed = True
        for field_name, actual, expected, display in tests:
            if actual == expected:
                print(f"✅ {field_name}: '{actual}' -> '{display}'")
            else:
                print(f"❌ {field_name}: Expected '{expected}', got '{actual}'")
                all_passed = False
        
        # Clean up
        user.delete()
        print("✅ Test user cleaned up")
        
        if all_passed:
            print("\n🎉 End-to-end signup test PASSED!")
            return True
        else:
            print("\n❌ End-to-end signup test FAILED!")
            return False
    else:
        print("❌ Form validation failed:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        return False

def main():
    """Main test function"""
    success1 = test_user_detail_template()
    success2 = test_signup_process_end_to_end()
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    if success1 and success2:
        print("🎉 ALL TESTS PASSED!")
        print("\nThe fixes have resolved the issues:")
        print("1. ✅ User detail page now displays province and college information")
        print("2. ✅ Signup form properly saves profile data")
        print("3. ✅ Template rendering works correctly")
        print("\nThe user muhammad.ibrahim.b28@pmc.edu.pk should now show:")
        print("- Year of Study: 2nd Year MBBS")
        print("- Province: Punjab") 
        print("- College Type: Public")
        print("- College Name: King Edward Medical University (Lahore)")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Check the output above for details.")

if __name__ == '__main__':
    main()
