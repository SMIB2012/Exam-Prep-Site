#!/usr/bin/env python
"""
Final verification that the premium user fix is working
"""

import os
import sys

# Setup Django
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')

import django
django.setup()

from core.models import UserProfile

def verify_premium_users():
    """Verify all premium users have proper setup"""
    print("🔍 FINAL VERIFICATION: Premium User Display")
    print("=" * 50)
    
    # Get all users
    all_profiles = UserProfile.objects.all()
    
    total_users = all_profiles.count()
    premium_users = all_profiles.filter(is_premium=True)
    premium_count = premium_users.count()
    
    print(f"Total users: {total_users}")
    print(f"Premium users (is_premium=True): {premium_count}")
    
    if premium_count == 0:
        print("✅ No premium users to check")
        return True
    
    # Check each premium user
    print(f"\nChecking {premium_count} premium users:")
    all_good = True
    
    for profile in premium_users:
        user = profile.user
        status = "✅" if profile.is_premium_active else "❌"
        
        print(f"{status} {user.get_full_name() or user.username} ({user.email})")
        print(f"   is_premium: {profile.is_premium}")
        print(f"   premium_expires_at: {profile.premium_expires_at}")
        print(f"   is_premium_active: {profile.is_premium_active}")
        
        if profile.is_premium and not profile.is_premium_active:
            print(f"   ⚠️ ISSUE: User is marked premium but not showing as active!")
            if not profile.premium_expires_at:
                print(f"   ⚠️ CAUSE: Missing premium_expires_at date")
            all_good = False
        print()
    
    return all_good

if __name__ == '__main__':
    success = verify_premium_users()
    
    print("=" * 50)
    if success:
        print("🎉 VERIFICATION PASSED!")
        print("All premium users are properly configured.")
        print("The user list should now show accurate subscription status.")
    else:
        print("⚠️ VERIFICATION FAILED!")
        print("Some premium users may still have issues.")
        print("Run fix_premium_users.py to resolve remaining issues.")
    print("=" * 50)
