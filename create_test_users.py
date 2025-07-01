#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')

django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile
from django.utils import timezone
from datetime import timedelta

# Create test users
test_users = [
    {
        'username': 'john_doe',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'is_active': True,
        'profile': {
            'year_of_study': '2nd_year',
            'province': 'Punjab',
            'college_type': 'Public',
            'college_name': 'King Edward Medical University',
            'phone_number': '+92-300-1234567',
            'is_premium': True,
            'premium_expires_at': timezone.now() + timedelta(days=30)
        }
    },
    {
        'username': 'sarah_khan',
        'first_name': 'Sarah',
        'last_name': 'Khan',
        'email': 'sarah.khan@example.com',
        'is_active': True,
        'profile': {
            'year_of_study': '3rd_year',
            'province': 'Sindh',
            'college_type': 'Private',
            'college_name': 'Aga Khan University',
            'phone_number': '+92-321-9876543',
            'is_premium': False,
        }
    },
    {
        'username': 'ahmed_ali',
        'first_name': 'Ahmed',
        'last_name': 'Ali',
        'email': 'ahmed.ali@example.com',
        'is_active': False,
        'profile': {
            'year_of_study': '1st_year',
            'province': 'KPK',
            'college_type': 'Public',
            'college_name': 'Khyber Medical University',
            'phone_number': '+92-333-5555555',
            'is_premium': False,
        }
    },
    {
        'username': 'fatima_shah',
        'first_name': 'Fatima',
        'last_name': 'Shah',
        'email': 'fatima.shah@example.com',
        'is_active': True,
        'profile': {
            'year_of_study': 'final_year',
            'province': 'Balochistan',
            'college_type': 'Public',
            'college_name': 'Bolan University of Medical Sciences',
            'phone_number': '+92-345-7777777',
            'is_premium': True,
            'premium_expires_at': timezone.now() + timedelta(days=60)
        }
    },
    {
        'username': 'hassan_malik',
        'first_name': 'Hassan',
        'last_name': 'Malik',
        'email': 'hassan.malik@example.com',
        'is_active': True,
        'profile': {
            'year_of_study': '4th_year',
            'province': 'Punjab',
            'college_type': 'Private',
            'college_name': 'Shifa College of Medicine',
            'phone_number': '+92-301-8888888',
            'is_premium': False,
        }
    }
]

def create_test_users():
    print("Creating test users...")
    
    for user_data in test_users:
        # Check if user already exists
        if User.objects.filter(username=user_data['username']).exists():
            print(f"User {user_data['username']} already exists, skipping...")
            continue
            
        # Create user
        user = User.objects.create_user(
            username=user_data['username'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            password='testpass123',
            is_active=user_data['is_active']
        )
        
        # Create profile
        profile_data = user_data['profile']
        profile = UserProfile.objects.create(
            user=user,
            year_of_study=profile_data['year_of_study'],
            province=profile_data['province'],
            college_type=profile_data['college_type'],
            college_name=profile_data['college_name'],
            phone_number=profile_data['phone_number'],
            is_premium=profile_data['is_premium'],
            premium_expires_at=profile_data.get('premium_expires_at'),
            total_quiz_score=0,
            total_quizzes_taken=0,
        )
        
        print(f"Created user: {user.username} ({user.get_full_name()})")
    
    print(f"\nTotal users in database: {User.objects.count()}")
    print(f"Active users: {User.objects.filter(is_active=True).count()}")
    print(f"Premium users: {User.objects.filter(userprofile__is_premium=True).count()}")

if __name__ == '__main__':
    create_test_users()
