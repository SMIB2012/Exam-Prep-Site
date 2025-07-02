#!/usr/bin/env python
"""
Test script to debug UserEditForm save functionality
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile
from staff.forms import UserEditForm

def test_user_edit_form_save():
    """Test that UserEditForm saves data correctly"""
    print("🧪 Testing UserEditForm save functionality...")
    
    try:
        # Create or get a test user
        user, created = User.objects.get_or_create(
            username='test_edit_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Create profile if needed
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        print(f"📝 Testing form with user: {user.username}")
        print(f"   Original data:")
        print(f"   - First name: {user.first_name}")
        print(f"   - Last name: {user.last_name}")
        print(f"   - Email: {user.email}")
        print(f"   - Province: {profile.province}")
        print(f"   - College type: {profile.college_type}")
        print(f"   - Phone: {profile.phone_number}")
        
        # Test form data
        form_data = {
            'username': user.username,
            'email': 'updated@example.com',
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
            'is_active': True,
            'is_staff': False,
            'year_of_study': '2nd_year',
            'province': 'Punjab',
            'college_type': 'Public',
            'college_name': 'Allama Iqbal Medical College (Lahore)',
            'phone_number': '+92-300-1234567',
            'is_premium': True,
        }
        
        print(f"\n📥 Submitting form with updated data:")
        for key, value in form_data.items():
            print(f"   - {key}: {value}")
        
        # Create and validate form
        form = UserEditForm(data=form_data, instance=user)
        
        if form.is_valid():
            print("\n✅ Form is valid!")
            
            # Save the form
            saved_user = form.save()
            
            # Reload from database
            saved_user.refresh_from_db()
            saved_profile = saved_user.userprofile
            
            print(f"\n📤 Checking saved data:")
            print(f"   - First name: {saved_user.first_name} (expected: UpdatedFirst)")
            print(f"   - Last name: {saved_user.last_name} (expected: UpdatedLast)")
            print(f"   - Email: {saved_user.email} (expected: updated@example.com)")
            print(f"   - Year of study: {saved_profile.year_of_study} (expected: 2nd_year)")
            print(f"   - College type: {saved_profile.college_type} (expected: Public)")
            print(f"   - Phone: {saved_profile.phone_number} (expected: +92-300-1234567)")
            print(f"   - Is premium: {saved_profile.is_premium} (expected: True)")
            
            # Verify data was saved correctly
            checks = [
                (saved_user.first_name == 'UpdatedFirst', 'First name'),
                (saved_user.last_name == 'UpdatedLast', 'Last name'),
                (saved_user.email == 'updated@example.com', 'Email'),
                (saved_profile.year_of_study == '2nd_year', 'Year of study'),
                (saved_profile.province == 'Punjab', 'Province'),
                (saved_profile.college_type == 'Public', 'College type'),
                (saved_profile.phone_number == '+92-300-1234567', 'Phone'),
                (saved_profile.is_premium == True, 'Premium status'),
            ]
            
            print(f"\n📊 Verification results:")
            all_passed = True
            for passed, field in checks:
                status = "✅" if passed else "❌"
                print(f"   {status} {field}: {'PASS' if passed else 'FAIL'}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                print(f"\n🎉 All checks passed! UserEditForm is working correctly.")
            else:
                print(f"\n⚠️ Some checks failed! There may be an issue with the form save.")
                
        else:
            print("\n❌ Form validation failed!")
            print("Form errors:")
            for field, errors in form.errors.items():
                print(f"   - {field}: {errors}")
                
    except Exception as e:
        print(f"❌ Error testing UserEditForm: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_user_edit_form_save()
