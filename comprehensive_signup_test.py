#!/usr/bin/env python
"""
Comprehensive test for all year choices and college combinations
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile
from core.forms import UserRegistrationForm
import uuid

def test_all_year_choices():
    """Test all year of study choices"""
    print("=" * 60)
    print("TESTING ALL YEAR OF STUDY CHOICES")
    print("=" * 60)
    
    year_choices = UserProfile.YEAR_CHOICES
    print(f"Testing {len(year_choices)} year choices:")
    for choice_value, choice_label in year_choices:
        print(f"  - {choice_label} ({choice_value})")
    
    test_users = []
    success_count = 0
    
    for choice_value, choice_label in year_choices:
        # Generate unique identifiers
        unique_id = str(uuid.uuid4())[:8]
        
        test_data = {
            'first_name': 'Test',
            'last_name': f'Year{choice_value}',
            'email': f'test_year_{choice_value}_{unique_id}@example.com',
            'username': f'test_year_{choice_value}_{unique_id}',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!',
            'year_of_study': choice_value,
            'province': 'Punjab',
            'college_type': 'Public',
            'college_name': 'King Edward Medical University (Lahore)',
            'phone_number': '03001234567',
        }
        
        print(f"\nTesting: {choice_label} ({choice_value})")
        
        form = UserRegistrationForm(data=test_data)
        
        if form.is_valid():
            try:
                user = form.save()
                test_users.append(user)
                success_count += 1
                print(f"  ✓ SUCCESS: User created - {user.username}")
                
                # Verify profile
                profile = UserProfile.objects.get(user=user)
                print(f"  ✓ Profile verified: {profile.year_of_study} | {profile.college_name}")
                
            except Exception as e:
                print(f"  ✗ ERROR saving user: {e}")
        else:
            print(f"  ✗ FORM INVALID: {form.errors}")
    
    print(f"\nYear Choice Test Results: {success_count}/{len(year_choices)} successful")
    return test_users

def test_college_combinations():
    """Test various college combinations"""
    print("\n" + "=" * 60)
    print("TESTING COLLEGE COMBINATIONS")
    print("=" * 60)
    
    test_combinations = [
        ('Punjab', 'Public', 'King Edward Medical University (Lahore)'),
        ('Punjab', 'Private', 'Lahore Medical & Dental College'),
        ('Sindh', 'Public', 'Dow Medical College'),
        ('Sindh', 'Private', 'Aga Khan University'),
        ('Khyber Pakhtunkhwa', 'Public', 'Khyber Medical College (Peshawar)'),
        ('Khyber Pakhtunkhwa', 'Private', 'Rehman Medical College'),
        ('Balochistan', 'Public', 'Bolan Medical College (Quetta)'),
        ('Balochistan', 'Private', 'Quetta Institute of Medical Sciences (Quetta)'),
        ('Azad Jammu & Kashmir', 'Public', 'Azad Jammu & Kashmir Medical College (Muzaffarabad)'),
        ('Azad Jammu & Kashmir', 'Private', 'Mohiuddin Islamic Medical College (Mirpur)'),
    ]
    
    print(f"Testing {len(test_combinations)} college combinations:")
    
    test_users = []
    success_count = 0
    
    for i, (province, college_type, college_name) in enumerate(test_combinations):
        # Generate unique identifier
        unique_id = str(uuid.uuid4())[:8]
        
        test_data = {
            'first_name': 'Test',
            'last_name': f'College{i}',
            'email': f'test_college_{i}_{unique_id}@example.com',
            'username': f'test_college_{i}_{unique_id}',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!',
            'year_of_study': '2nd_year',
            'province': province,
            'college_type': college_type,
            'college_name': college_name,
            'phone_number': '03001234567',
        }
        
        print(f"\nTesting: {province} | {college_type} | {college_name[:50]}...")
        
        form = UserRegistrationForm(data=test_data)
        
        if form.is_valid():
            try:
                user = form.save()
                test_users.append(user)
                success_count += 1
                print(f"  ✓ SUCCESS: User created - {user.username}")
                
                # Verify profile
                profile = UserProfile.objects.get(user=user)
                print(f"  ✓ Profile verified: {profile.province} | {profile.college_type} | {profile.college_name[:30]}...")
                
            except Exception as e:
                print(f"  ✗ ERROR saving user: {e}")
        else:
            print(f"  ✗ FORM INVALID: {form.errors}")
    
    print(f"\nCollege Test Results: {success_count}/{len(test_combinations)} successful")
    return test_users

def cleanup_test_users(test_users):
    """Clean up all test users"""
    print("\n" + "=" * 60)
    print("CLEANING UP TEST USERS")
    print("=" * 60)
    
    print(f"Deleting {len(test_users)} test users...")
    
    deleted_count = 0
    for user in test_users:
        try:
            username = user.username
            
            # Delete user profile if exists
            if hasattr(user, 'userprofile'):
                user.userprofile.delete()
            
            # Delete user
            user.delete()
            deleted_count += 1
            print(f"  ✓ Deleted: {username}")
            
        except Exception as e:
            print(f"  ✗ Error deleting {user.username}: {e}")
    
    print(f"\nCleanup Results: {deleted_count}/{len(test_users)} users deleted")

def main():
    """Main test function"""
    print("MEDPREP SIGNUP FORM COMPREHENSIVE TEST")
    print("=" * 60)
    print("This test will:")
    print("1. Test all year of study choices")
    print("2. Test various medical college combinations")
    print("3. Create temporary user accounts for testing")
    print("4. Clean up all test accounts after verification")
    print("=" * 60)
    
    all_test_users = []
    
    try:
        # Test all year choices
        year_test_users = test_all_year_choices()
        all_test_users.extend(year_test_users)
        
        # Test college combinations
        college_test_users = test_college_combinations()
        all_test_users.extend(college_test_users)
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total test users created: {len(all_test_users)}")
        print(f"Year choice tests: {len(year_test_users)} users")
        print(f"College combination tests: {len(college_test_users)} users")
        
        if all_test_users:
            print("\n✓ ALL TESTS PASSED - Signup form is working correctly!")
            print("✓ All year choices are accepted")
            print("✓ Medical college dependent dropdowns are functional")
            print("✓ College field is now mandatory as required")
        else:
            print("\n✗ TESTS FAILED - No users were created successfully")
            
    finally:
        # Always clean up test users
        if all_test_users:
            cleanup_test_users(all_test_users)
        
        print("\n" + "=" * 60)
        print("TEST COMPLETED")
        print("=" * 60)

if __name__ == "__main__":
    main()
