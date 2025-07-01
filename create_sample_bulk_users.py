#!/usr/bin/env python
"""
Script to test the bulk user upload functionality
Creates sample CSV files for testing
"""

import csv
import os

def create_sample_csv():
    """Create a sample CSV file for testing bulk user upload"""
    
    # Sample data
    sample_users = [
        {
            'first_name': 'Ahmed',
            'last_name': 'Hassan',
            'email': 'ahmed.hassan@example.com',
            'password': 'SecurePass123!',
            'role': 'student',
            'year_of_study': '1st_year',
            'province': 'Punjab',
            'college_type': 'Public',
            'college_name': 'King Edward Medical University (Lahore)',
            'phone_number': '+92-300-1234567',
            'is_premium': 'FALSE',
            'is_active': 'TRUE'
        },
        {
            'first_name': 'Fatima',
            'last_name': 'Ali',
            'email': 'fatima.ali@example.com',
            'password': 'StudentPass456!',
            'role': 'student',
            'year_of_study': '2nd_year',
            'province': 'Sindh',
            'college_type': 'Private',
            'college_name': 'Aga Khan University',
            'phone_number': '+92-321-9876543',
            'is_premium': 'TRUE',
            'is_active': 'TRUE'
        },
        {
            'first_name': 'Muhammad',
            'last_name': 'Khan',
            'email': 'muhammad.khan@example.com',
            'password': '',  # Will use default password
            'role': 'faculty',
            'year_of_study': '',
            'province': 'Khyber Pakhtunkhwa',
            'college_type': 'Public',
            'college_name': 'Khyber Medical College (Peshawar)',
            'phone_number': '+92-333-5555555',
            'is_premium': 'FALSE',
            'is_active': 'TRUE'
        },
        {
            'first_name': 'Sarah',
            'last_name': 'Ahmed',
            'email': 'sarah.ahmed@example.com',
            'password': 'FacultyPass789!',
            'role': 'faculty',
            'year_of_study': '',
            'province': 'Punjab',
            'college_type': 'Private',
            'college_name': 'Lahore Medical & Dental College',
            'phone_number': '+92-300-7777777',
            'is_premium': 'TRUE',
            'is_active': 'TRUE'
        },
        {
            'first_name': 'Zain',
            'last_name': 'Malik',
            'email': 'zain.malik@example.com',
            'password': 'AdminPass999!',
            'role': 'admin',
            'year_of_study': '',
            'province': 'Sindh',
            'college_type': 'Public',
            'college_name': 'Dow Medical College',
            'phone_number': '+92-321-8888888',
            'is_premium': 'TRUE',
            'is_active': 'TRUE'
        }
    ]
    
    # Create CSV file
    filename = 'sample_users.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'first_name', 'last_name', 'email', 'password', 'role',
            'year_of_study', 'province', 'college_type', 'college_name',
            'phone_number', 'is_premium', 'is_active'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for user in sample_users:
            writer.writerow(user)
    
    print(f"Sample CSV file created: {filename}")
    print("You can use this file to test the bulk upload functionality.")
    
    # Also create a file with errors for testing error handling
    error_filename = 'sample_users_with_errors.csv'
    error_users = [
        {
            'first_name': 'Valid',
            'last_name': 'User',
            'email': 'valid.user@example.com',
            'password': 'ValidPass123!',
            'role': 'student',
            'year_of_study': '1st_year',
            'province': 'Punjab',
            'college_type': 'Public',
            'college_name': 'King Edward Medical University (Lahore)',
            'phone_number': '+92-300-1111111',
            'is_premium': 'FALSE',
            'is_active': 'TRUE'
        },
        {
            'first_name': '',  # Missing first name - ERROR
            'last_name': 'NoFirstName',
            'email': 'no.firstname@example.com',
            'password': 'Pass123!',
            'role': 'student',
            'year_of_study': '1st_year',
            'province': 'Punjab',
            'college_type': 'Public',
            'college_name': 'King Edward Medical University (Lahore)',
            'phone_number': '+92-300-2222222',
            'is_premium': 'FALSE',
            'is_active': 'TRUE'
        },
        {
            'first_name': 'Invalid',
            'last_name': 'Email',
            'email': 'not-an-email',  # Invalid email - ERROR
            'password': 'Pass123!',
            'role': 'student',
            'year_of_study': '1st_year',
            'province': 'Punjab',
            'college_type': 'Public',
            'college_name': 'King Edward Medical University (Lahore)',
            'phone_number': '+92-300-3333333',
            'is_premium': 'FALSE',
            'is_active': 'TRUE'
        },
        {
            'first_name': 'Invalid',
            'last_name': 'Role',
            'email': 'invalid.role@example.com',
            'password': 'Pass123!',
            'role': 'invalid_role',  # Invalid role - ERROR
            'year_of_study': '1st_year',
            'province': 'Punjab',
            'college_type': 'Public',
            'college_name': 'King Edward Medical University (Lahore)',
            'phone_number': '+92-300-4444444',
            'is_premium': 'FALSE',
            'is_active': 'TRUE'
        }
    ]
    
    with open(error_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'first_name', 'last_name', 'email', 'password', 'role',
            'year_of_study', 'province', 'college_type', 'college_name',
            'phone_number', 'is_premium', 'is_active'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for user in error_users:
            writer.writerow(user)
    
    print(f"Sample CSV with errors created: {error_filename}")
    print("You can use this file to test error handling in bulk upload.")

if __name__ == '__main__':
    create_sample_csv()
