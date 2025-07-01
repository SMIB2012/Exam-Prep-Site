#!/usr/bin/env python
"""
Test college field population
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from core.forms import UserRegistrationForm

def test_college_population():
    """Test college field population"""
    print("Testing college field population...")
    
    # Test data with province and college_type
    test_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'testcollege@example.com',
        'username': 'testcollegeuser',
        'password1': 'complexpassword123',
        'password2': 'complexpassword123',
        'year_of_study': '2nd_year',
        'province': 'Punjab',
        'college_type': 'Public',
        'college_name': 'King Edward Medical University (Lahore)',
        'phone_number': '03001234567',
    }
    
    form = UserRegistrationForm(data=test_data)
    
    print(f"Form is valid: {form.is_valid()}")
    
    # Check college choices
    college_choices = form.fields['college_name'].choices
    print(f"Number of college choices: {len(college_choices)}")
    print("First few college choices:")
    for i, choice in enumerate(college_choices[:5]):
        print(f"  {i+1}. {choice}")
    
    # Test different province combinations
    test_combinations = [
        ('Punjab', 'Public'),
        ('Punjab', 'Private'),
        ('Sindh', 'Public'),
        ('Sindh', 'Private'),
        ('Khyber Pakhtunkhwa', 'Public'),
        ('Balochistan', 'Public'),
        ('Azad Jammu & Kashmir', 'Public'),
    ]
    
    print("\nTesting different province/type combinations:")
    for province, college_type in test_combinations:
        test_data_copy = test_data.copy()
        test_data_copy['province'] = province
        test_data_copy['college_type'] = college_type
        test_data_copy['username'] = f'test_{province.replace(" ", "").lower()}_{college_type.lower()}'
        test_data_copy['email'] = f'test_{province.replace(" ", "").lower()}_{college_type.lower()}@example.com'
        
        # Get first college from the expected list
        form_test = UserRegistrationForm(data=test_data_copy)
        college_choices = form_test.fields['college_name'].choices
        
        if len(college_choices) > 1:  # More than just the default option
            # Use the first actual college choice
            test_data_copy['college_name'] = college_choices[1][0]  # [1] to skip the empty option
            
            form_final = UserRegistrationForm(data=test_data_copy)
            is_valid = form_final.is_valid()
            
            print(f"  {province} - {college_type}: {is_valid} ({len(college_choices)-1} colleges available)")
            if not is_valid:
                print(f"    Errors: {form_final.errors}")
        else:
            print(f"  {province} - {college_type}: No colleges available")

if __name__ == "__main__":
    test_college_population()
