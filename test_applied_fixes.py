#!/usr/bin/env python
"""
Test the fixes for the remaining issues
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_fixes():
    """Test all the fixes applied"""
    print("🔧 TESTING APPLIED FIXES")
    print("=" * 40)
    
    # Setup
    client = Client()
    staff_user, created = User.objects.get_or_create(
        username='fix_test_staff',
        defaults={
            'email': 'fix_test@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    staff_user.set_password('testpass123')
    staff_user.save()
    
    client.login(username='fix_test_staff', password='testpass123')
    
    # Test 1: Dashboard fixes
    print("\n📊 Testing Dashboard Fixes:")
    response = client.get(reverse('staff:dashboard'))
    if response.status_code == 200:
        content = response.content.decode()
        
        fixes = [
            ('Premium Users card', 'Premium Users'),
            ('Total Revenue card', 'Total Revenue'),
            ('Profile dropdown menu', 'Profile'),
            ('Total Quiz Attempts', 'Total Quiz Attempts'),
            ('Users navigation', 'Users'),
        ]
        
        for fix_name, search_term in fixes:
            found = search_term in content
            status = "✅" if found else "❌"
            print(f"  {status} {fix_name}: {search_term}")
    
    # Test 2: User Detail Quiz Statistics
    print("\n👤 Testing User Detail Quiz Statistics:")
    test_user = User.objects.filter(is_staff=False).first()
    if not test_user:
        # Create a test user
        test_user = User.objects.create_user(
            username='stats_test_user',
            email='stats@test.com',
            password='testpass123'
        )
    
    detail_url = reverse('staff:user_detail', kwargs={'pk': test_user.id})
    response = client.get(detail_url)
    if response.status_code == 200:
        content = response.content.decode()
        
        quiz_terms = [
            ('Quiz Statistics header', 'Quiz Statistics'),
            ('Quiz Performance section', 'Quiz Performance'),
            ('Total attempts stat', 'Total Attempts'),
            ('Average score stat', 'Average Score'),
        ]
        
        for term_name, search_term in quiz_terms:
            found = search_term in content
            status = "✅" if found else "❌"
            print(f"  {status} {term_name}: {search_term}")
    
    # Test 3: User Edit JavaScript (should already be working)
    print("\n✏️ Testing User Edit JavaScript:")
    if test_user:
        edit_url = reverse('staff:user_edit', kwargs={'pk': test_user.id})
        response = client.get(edit_url)
        if response.status_code == 200:
            content = response.content.decode()
            
            js_functions = [
                ('exportUserData', 'Export function'),
                ('sendWelcomeEmail', 'Welcome email function'),
                ('showNotification', 'Notification function'),
                ('college dropdown', 'College dropdown logic'),
            ]
            
            for js_func, description in js_functions:
                found = js_func in content
                status = "✅" if found else "❌"
                print(f"  {status} {description}: {js_func}")
    
    print("\n🎉 Fix Testing Complete!")

if __name__ == '__main__':
    test_fixes()
