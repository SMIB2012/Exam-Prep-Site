#!/usr/bin/env python
"""
Simple manual form test
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

def test_form_fields():
    """Test form field setup"""
    print("Testing form field setup...")
    
    form = UserRegistrationForm()
    
    print("Form fields:")
    for field_name, field in form.fields.items():
        print(f"  {field_name}: {type(field).__name__}")
        if hasattr(field, 'choices'):
            print(f"    Choices: {field.choices[:3]}...")  # Show first 3 choices
    
    print("\nTesting form validation with valid data...")
    
    valid_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'testvalid@example.com',
        'username': 'testvaliduser',
        'password1': 'complexpassword123',
        'password2': 'complexpassword123',
        'year_of_study': '2nd_year',
        'province': 'Punjab',
        'college_type': 'Public',
        'college_name': 'King Edward Medical University (Lahore)',
        'phone_number': '03001234567',
    }
    
    form = UserRegistrationForm(data=valid_data)
    
    print(f"Form is valid: {form.is_valid()}")
    if not form.is_valid():
        print(f"Form errors: {form.errors}")
    
    return form.is_valid()

if __name__ == "__main__":
    test_form_fields()
