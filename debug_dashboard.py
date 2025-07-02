#!/usr/bin/env python
"""
Debug script to identify the specific failing dashboard test
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_dashboard_items():
    """Test each dashboard item individually"""
    print("🧪 Testing Dashboard Items Individually...")
    
    try:
        # Create or get staff user
        staff_user, created = User.objects.get_or_create(
            username='debug_staff',
            defaults={
                'email': 'debug@test.com',
                'is_staff': True
            }
        )
        if created:
            staff_user.set_password('testpass123')
            staff_user.save()
        
        # Create client and login
        client = Client()
        client.force_login(staff_user)
        
        # Test dashboard page
        print("\n🌐 Testing Dashboard Page...")
        response = client.get(reverse('staff:dashboard'))
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Test stats cards
            print("\n📊 Testing Stats Cards...")
            stat_cards = [
                ('Total Users Card', 'Total Users'),
                ('Premium Users Card', 'Premium Users'),
                ('Total Questions Card', 'Total Questions'),
                ('Total Revenue Card', 'Total Revenue'),
                ('Total Quiz Attempts Card', 'Total Quiz Attempts'),
            ]
            
            for card_name, search_text in stat_cards:
                found = search_text in content
                status = "✅" if found else "❌"
                print(f"   {status} {card_name}: {'FOUND' if found else 'MISSING'}")
            
            # Test navigation elements
            print("\n🧭 Testing Navigation Elements...")
            nav_elements = [
                ('Users Navigation', 'Users'),
                ('Questions Navigation', 'Questions'),
                ('Subjects Navigation', 'Subjects'),
                ('Quick Actions Section', 'Quick Actions'),
                ('Recent Users Section', 'Recent Users'),
            ]
            
            for nav_name, search_text in nav_elements:
                found = search_text in content
                status = "✅" if found else "❌"
                print(f"   {status} {nav_name}: {'FOUND' if found else 'MISSING'}")
            
            # Test dropdown items
            print("\n📋 Testing Dropdown Items...")
            dropdown_items = [
                ('Profile Menu Item', 'Profile'),
                ('Settings Menu Item', 'Settings'),
                ('Activity Logs Menu', 'Activity Logs'),
                ('Logout Button', 'Logout'),
            ]
            
            for dropdown_name, search_text in dropdown_items:
                found = search_text in content
                status = "✅" if found else "❌"
                print(f"   {status} {dropdown_name}: {'FOUND' if found else 'MISSING'}")
            
            # Test action links
            print("\n🔗 Testing Action Links...")
            action_links = [
                ('staff:user_list', 'User List Link'),
                ('staff:user_add', 'Add User Link'),
                ('staff:question_list', 'Questions Link'),
                ('staff:subject_list', 'Subjects Link'),
            ]
            
            for url_name, description in action_links:
                try:
                    url = reverse(url_name)
                    link_response = client.get(url)
                    success = link_response.status_code == 200
                    status = "✅" if success else "❌"
                    print(f"   {status} {description}: {url} -> HTTP {link_response.status_code}")
                except Exception as e:
                    print(f"   ❌ {description}: ERROR - {str(e)}")
        else:
            print(f"   ❌ Dashboard page failed to load: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_dashboard_items()
