#!/usr/bin/env python
"""
Debug script to check user profile data for muhammad.ibrahim.b28@pmc.edu.pk
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile

def check_user_profile():
    """Check the profile data for the specific user"""
    email = 'muhammad.ibrahim.b28@pmc.edu.pk'
    
    try:
        user = User.objects.get(email=email)
        print(f"Found user: {user.get_full_name()} ({user.email})")
        print(f"Username: {user.username}")
        print(f"Active: {user.is_active}")
        print(f"Date joined: {user.date_joined}")
        
        if hasattr(user, 'userprofile'):
            profile = user.userprofile
            print(f"\nProfile Information:")
            print(f"  Year of Study: '{profile.year_of_study}' (choices: {dict(UserProfile.YEAR_CHOICES).get(profile.year_of_study, 'NOT FOUND')})")
            print(f"  Province: '{profile.province}' (choices: {dict(UserProfile.PROVINCE_CHOICES).get(profile.province, 'NOT FOUND')})")
            print(f"  College Type: '{profile.college_type}' (choices: {dict(UserProfile.COLLEGE_TYPE_CHOICES).get(profile.college_type, 'NOT FOUND')})")
            print(f"  College Name: '{profile.college_name}'")
            print(f"  Phone Number: '{profile.phone_number}'")
            print(f"  Is Premium: {profile.is_premium}")
            print(f"  Created: {profile.created_at}")
            print(f"  Updated: {profile.updated_at}")
            
            # Test get_display methods
            print(f"\nDisplay Methods:")
            try:
                print(f"  get_year_of_study_display(): '{profile.get_year_of_study_display()}'")
            except Exception as e:
                print(f"  get_year_of_study_display() ERROR: {e}")
                
            try:
                print(f"  get_province_display(): '{profile.get_province_display()}'")
            except Exception as e:
                print(f"  get_province_display() ERROR: {e}")
                
            try:
                print(f"  get_college_type_display(): '{profile.get_college_type_display()}'")
            except Exception as e:
                print(f"  get_college_type_display() ERROR: {e}")
        else:
            print("\n❌ No profile found for this user!")
            
    except User.DoesNotExist:
        print(f"❌ User with email '{email}' not found!")
        
        # List all users to see what we have
        print("\nAvailable users:")
        for user in User.objects.all()[:10]:
            print(f"  - {user.email} ({user.get_full_name()})")

def check_all_profiles():
    """Check all user profiles for data issues"""
    print("\n" + "="*50)
    print("CHECKING ALL USER PROFILES")
    print("="*50)
    
    profiles = UserProfile.objects.all()
    print(f"Total profiles: {profiles.count()}")
    
    issues = []
    
    for profile in profiles:
        user_issues = []
        
        # Check year_of_study
        if profile.year_of_study and profile.year_of_study not in dict(UserProfile.YEAR_CHOICES):
            user_issues.append(f"Invalid year_of_study: '{profile.year_of_study}'")
            
        # Check province
        if profile.province and profile.province not in dict(UserProfile.PROVINCE_CHOICES):
            user_issues.append(f"Invalid province: '{profile.province}'")
            
        # Check college_type
        if profile.college_type and profile.college_type not in dict(UserProfile.COLLEGE_TYPE_CHOICES):
            user_issues.append(f"Invalid college_type: '{profile.college_type}'")
            
        if user_issues:
            issues.append({
                'user': profile.user,
                'issues': user_issues,
                'profile': profile
            })
    
    if issues:
        print(f"\n❌ Found {len(issues)} profiles with data issues:")
        for item in issues:
            print(f"\nUser: {item['user'].email}")
            for issue in item['issues']:
                print(f"  - {issue}")
            print(f"  Raw data: year='{item['profile'].year_of_study}', province='{item['profile'].province}', college_type='{item['profile'].college_type}'")
    else:
        print("\n✅ All profiles have valid choice data!")

def main():
    """Main function"""
    print("="*60)
    print("USER PROFILE DATA INVESTIGATION")
    print("="*60)
    
    check_user_profile()
    check_all_profiles()
    
    print("\n" + "="*60)
    print("CHOICES REFERENCE")
    print("="*60)
    print("Year choices:", dict(UserProfile.YEAR_CHOICES))
    print("Province choices:", dict(UserProfile.PROVINCE_CHOICES))
    print("College type choices:", dict(UserProfile.COLLEGE_TYPE_CHOICES))

if __name__ == '__main__':
    main()
