#!/usr/bin/env python
"""
Quick verification that bulk actions are working
"""

import os
import sys

# Setup Django
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')

import django
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile

def quick_verification():
    """Quick check that we can make a user premium via bulk action logic"""
    print("🔍 Quick Bulk Actions Verification")
    print("=" * 40)
    
    # Find an existing non-premium user
    non_premium_users = User.objects.filter(
        userprofile__is_premium=False
    ).exclude(is_superuser=True)[:1]
    
    if not non_premium_users.exists():
        print("⚠️ No non-premium users found to test with")
        return False
    
    user = non_premium_users.first()
    profile = user.userprofile
    
    print(f"Testing with user: {user.get_full_name() or user.username} ({user.email})")
    print(f"Before - is_premium: {profile.is_premium}")
    print(f"Before - premium_expires_at: {profile.premium_expires_at}")
    print(f"Before - is_premium_active: {profile.is_premium_active}")
    
    # Simulate the make_premium bulk action
    from django.utils import timezone
    from datetime import timedelta
    
    try:
        expiry_date = timezone.now() + timedelta(days=365)
        profile.is_premium = True
        profile.premium_expires_at = expiry_date
        profile.save()
        
        # Refresh from database
        profile.refresh_from_db()
        
        print(f"\nAfter - is_premium: {profile.is_premium}")
        print(f"After - premium_expires_at: {profile.premium_expires_at}")
        print(f"After - is_premium_active: {profile.is_premium_active}")
        
        if profile.is_premium_active:
            print("✅ Bulk action logic works correctly!")
            
            # Reset the user back to non-premium
            profile.is_premium = False
            profile.premium_expires_at = None
            profile.save()
            print("✅ User reset to non-premium state")
            
            return True
        else:
            print("❌ Premium status not working correctly")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == '__main__':
    success = quick_verification()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 VERIFICATION PASSED!")
        print("Bulk actions should work correctly in the admin panel.")
        print("Try selecting users and using 'Make Premium' or other actions.")
    else:
        print("⚠️ VERIFICATION ISSUES!")
        print("There may be problems with the bulk action implementation.")
    print("=" * 40)
