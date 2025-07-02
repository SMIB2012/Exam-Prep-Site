#!/usr/bin/env python
"""
Check the user list page and debug bulk actions
"""
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile

def check_users():
    """Check current users and their status"""
    print("=== Current Users Status ===\n")
    
    users = User.objects.all().order_by('-date_joined')[:10]
    
    print(f"Total users: {User.objects.count()}")
    print(f"Active users: {User.objects.filter(is_active=True).count()}")
    print(f"Premium users: {UserProfile.objects.filter(is_premium=True).count()}")
    print()
    
    print("Recent users:")
    for user in users:
        profile = getattr(user, 'userprofile', None)
        premium_status = "Premium" if profile and profile.is_premium else "Free"
        active_status = "Active" if user.is_active else "Inactive"
        
        print(f"ID: {user.id:3d} | {user.username:15s} | {user.email:25s} | {active_status:8s} | {premium_status}")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    check_users()
