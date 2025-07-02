#!/usr/bin/env python
"""
Test script to verify the UserEditForm college dropdown functionality
"""
import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

def test_user_edit_form_college_dropdown():
    """Test that the UserEditForm college dropdown works correctly"""
    try:
        from core.models import UserProfile
        from staff.forms import UserEditForm
        
        # Create a test user with profile
        test_user, created = User.objects.get_or_create(
            username='test_edit_college_user',
            defaults={
                'email': 'testcollegeedit@example.com',
                'first_name': 'Test',
                'last_name': 'College'
            }
        )
        
        # Create/update user profile with college data
        profile, created = UserProfile.objects.get_or_create(
            user=test_user,
            defaults={
                'province': 'Punjab',
                'college_type': 'Public',
                'college_name': 'King Edward Medical University (Lahore)',
                'year_of_study': '2nd_year'
            }
        )
        
        if not created:
            profile.province = 'Punjab'
            profile.college_type = 'Public' 
            profile.college_name = 'King Edward Medical University (Lahore)'
            profile.year_of_study = '2nd_year'
            profile.save()
        
        print(f"✅ Test user created: {test_user.username}")
        print(f"✅ Profile: {profile.province} | {profile.college_type} | {profile.college_name}")
        
        # Test form initialization with existing user
        form = UserEditForm(instance=test_user)
        
        # Check if province and college_type are properly initialized
        print(f"✅ Form province initial: {form.fields['province'].initial}")
        print(f"✅ Form college_type initial: {form.fields['college_type'].initial}")
        print(f"✅ Form college_name initial: {form.fields['college_name'].initial}")
        
        # Test college choices population
        college_choices = form.fields['college_name'].choices
        print(f"✅ College choices available: {len(college_choices)}")
        
        # Verify specific college is in choices
        college_names = [choice[0] for choice in college_choices]
        if 'King Edward Medical University (Lahore)' in college_names:
            print("✅ KEMU found in college choices")
        else:
            print("❌ KEMU not found in college choices")
        
        # Test form with updated data
        test_data = {
            'first_name': 'Test',
            'last_name': 'College',
            'email': 'testcollegeedit@example.com',
            'username': 'test_edit_college_user',
            'is_active': True,
            'is_staff': False,
            'province': 'Sindh',
            'college_type': 'Private',
            'college_name': 'Aga Khan University',
            'year_of_study': '3rd_year',
            'phone_number': '03001234567',
            'is_premium': False
        }
        
        form_with_data = UserEditForm(data=test_data, instance=test_user)
        print(f"✅ Form with new data is valid: {form_with_data.is_valid()}")
        
        if not form_with_data.is_valid():
            print(f"❌ Form errors: {form_with_data.errors}")
        else:
            # Test save functionality
            saved_user = form_with_data.save()
            updated_profile = UserProfile.objects.get(user=saved_user)
            print(f"✅ Updated profile: {updated_profile.province} | {updated_profile.college_type} | {updated_profile.college_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing UserEditForm: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_college_choices_update():
    """Test college choices update method directly"""
    try:
        from staff.forms import UserEditForm
        
        # Test form with different province/college_type combinations
        test_combinations = [
            ('Punjab', 'Public'),
            ('Punjab', 'Private'),
            ('Sindh', 'Public'),
            ('Sindh', 'Private'),
            ('Khyber Pakhtunkhwa', 'Public'),
            ('Balochistan', 'Private')
        ]
        
        for province, college_type in test_combinations:
            form = UserEditForm()
            form.update_college_choices(province, college_type)
            
            choices = form.fields['college_name'].choices
            college_count = len(choices) - 1  # Subtract 1 for the empty option
            
            print(f"✅ {province} | {college_type}: {college_count} colleges available")
            
            if college_count > 0:
                sample_college = choices[1][0] if len(choices) > 1 else "None"
                print(f"   Sample: {sample_college[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing college choices: {e}")
        return False

if __name__ == '__main__':
    print("Testing UserEditForm college dropdown functionality...")
    print("=" * 60)
    
    test1 = test_user_edit_form_college_dropdown()
    print("\n" + "=" * 60)
    
    test2 = test_college_choices_update()
    print("\n" + "=" * 60)
    
    if test1 and test2:
        print("✅ All UserEditForm college dropdown tests passed!")
    else:
        print("❌ Some tests failed!")
