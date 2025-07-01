#!/usr/bin/env python
"""
Test script to verify signup form functionality
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile
from core.forms import UserRegistrationForm

def test_year_choices():
    """Test all year of study choices"""
    print("Testing Year of Study choices...")
    
    year_choices = UserProfile.YEAR_CHOICES
    print(f"Available year choices: {year_choices}")
    
    test_data_base = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'username': 'testuser',
        'password1': 'complexpassword123',
        'password2': 'complexpassword123',
        'province': 'Punjab',
        'college_type': 'Public',
        'college_name': 'King Edward Medical University (Lahore)',
        'phone_number': '03001234567',
        'terms': True
    }
    
    test_users = []
    
    for choice_value, choice_label in year_choices:
        test_data = test_data_base.copy()
        test_data['year_of_study'] = choice_value
        test_data['username'] = f'testuser_{choice_value}'
        test_data['email'] = f'test_{choice_value}@example.com'
        
        print(f"\nTesting: {choice_label} ({choice_value})")
        
        form = UserRegistrationForm(data=test_data)
        
        if form.is_valid():
            print(f"✓ Form is valid for {choice_label}")
            try:
                user = form.save()
                test_users.append(user)
                print(f"✓ User created successfully: {user.username}")
                
                # Verify user profile was created
                profile = UserProfile.objects.get(user=user)
                print(f"✓ Profile created: Year={profile.year_of_study}, College={profile.college_name}")
                
            except Exception as e:
                print(f"✗ Error creating user: {e}")
        else:
            print(f"✗ Form validation failed for {choice_label}")
            print(f"Errors: {form.errors}")
    
    return test_users

def test_college_combinations():
    """Test different college combinations"""
    print("\n\nTesting College combinations...")
    
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
    
    test_users = []
    
    for i, (province, college_type, college_name) in enumerate(test_combinations):
        test_data = {
            'first_name': 'Test',
            'last_name': f'College{i}',
            'email': f'testcollege{i}@example.com',
            'username': f'testcollege{i}',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'year_of_study': '2nd_year',
            'province': province,
            'college_type': college_type,
            'college_name': college_name,
            'phone_number': '03001234567',
            'terms': True
        }
        
        print(f"\nTesting: {province} - {college_type} - {college_name}")
        
        form = UserRegistrationForm(data=test_data)
        
        if form.is_valid():
            print(f"✓ Form is valid")
            try:
                user = form.save()
                test_users.append(user)
                print(f"✓ User created: {user.username}")
                
                # Verify user profile
                profile = UserProfile.objects.get(user=user)
                print(f"✓ Profile: {profile.province} - {profile.college_type} - {profile.college_name}")
                
            except Exception as e:
                print(f"✗ Error creating user: {e}")
        else:
            print(f"✗ Form validation failed")
            print(f"Errors: {form.errors}")
    
    return test_users

def cleanup_test_users(test_users):
    """Delete all test users"""
    print(f"\n\nCleaning up {len(test_users)} test users...")
    
    for user in test_users:
        try:
            # Delete user profile first (if exists)
            if hasattr(user, 'userprofile'):
                user.userprofile.delete()
            
            # Delete user
            username = user.username
            user.delete()
            print(f"✓ Deleted user: {username}")
            
        except Exception as e:
            print(f"✗ Error deleting user {user.username}: {e}")
    
    print("Cleanup completed!")

if __name__ == "__main__":
    print("Starting signup form tests...\n")
    
    # Test year choices
    year_test_users = test_year_choices()
    
    # Test college combinations  
    college_test_users = test_college_combinations()
    
    # Combine all test users
    all_test_users = year_test_users + college_test_users
    
    print(f"\n\nTotal test users created: {len(all_test_users)}")
    
    # Cleanup
    cleanup_test_users(all_test_users)
    
    print("\nAll tests completed!")
