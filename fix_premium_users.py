#!/usr/bin/env python
"""
Fix existing premium users who don't have premium_expires_at set
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
from django.utils import timezone
from datetime import timedelta

def fix_premium_users():
    """Fix premium users without expiration date"""
    print("🔧 Fixing Premium Users Without Expiration Date")
    print("=" * 50)
    
    # Find premium users without expiration date
    premium_users_without_expiry = UserProfile.objects.filter(
        is_premium=True,
        premium_expires_at__isnull=True
    )
    
    count = premium_users_without_expiry.count()
    print(f"Found {count} premium users without expiration date")
    
    if count == 0:
        print("✅ All premium users already have expiration dates!")
        return
    
    # Set default expiration date (1 year from now)
    default_expiry = timezone.now() + timedelta(days=365)
    
    print(f"Setting expiration date to: {default_expiry}")
    
    updated_count = 0
    for profile in premium_users_without_expiry:
        profile.premium_expires_at = default_expiry
        profile.save()
        updated_count += 1
        print(f"✅ Updated {profile.user.get_full_name() or profile.user.username} ({profile.user.email})")
    
    print(f"\n🎉 Successfully updated {updated_count} premium users!")
    
    # Verify the fix
    print("\n🔍 Verifying fix...")
    remaining_users = UserProfile.objects.filter(
        is_premium=True,
        premium_expires_at__isnull=True
    ).count()
    
    if remaining_users == 0:
        print("✅ All premium users now have expiration dates!")
    else:
        print(f"⚠️ Still {remaining_users} users without expiration dates")

def check_premium_status():
    """Check premium status of all users"""
    print("\n📊 Premium User Status Report")
    print("=" * 30)
    
    all_users = UserProfile.objects.all()
    
    total_users = all_users.count()
    premium_users = all_users.filter(is_premium=True).count()
    active_premium_users = sum(1 for profile in all_users if profile.is_premium_active)
    
    print(f"Total users: {total_users}")
    print(f"Premium users (is_premium=True): {premium_users}")
    print(f"Active premium users (is_premium_active=True): {active_premium_users}")
    
    if premium_users > active_premium_users:
        inactive_premium = premium_users - active_premium_users
        print(f"⚠️ {inactive_premium} premium users are not showing as active!")
        
        # Show details of inactive premium users
        print("\nInactive premium users:")
        for profile in all_users.filter(is_premium=True):
            if not profile.is_premium_active:
                user = profile.user
                print(f"  - {user.get_full_name() or user.username} ({user.email})")
                print(f"    is_premium: {profile.is_premium}")
                print(f"    premium_expires_at: {profile.premium_expires_at}")
                print(f"    is_premium_active: {profile.is_premium_active}")
                print()

if __name__ == '__main__':
    try:
        check_premium_status()
        fix_premium_users()
        print("\n" + "=" * 50)
        check_premium_status()
        print("=" * 50)
        print("✅ Premium user fix completed!")
        print("   The user list should now show accurate subscription status.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
