#!/usr/bin/env python
"""
FOCUSED TEST for identified issues
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

def test_remaining_issues():
    """Test the few remaining issues identified"""
    print("🔍 TESTING REMAINING ISSUES")
    print("=" * 40)
    
    # Setup
    client = Client()
    staff_user, created = User.objects.get_or_create(
        username='issue_test_staff',
        defaults={
            'email': 'issue_test@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    staff_user.set_password('testpass123')
    staff_user.save()
    
    client.login(username='issue_test_staff', password='testpass123')
    
    # Test 1: Dashboard content analysis
    print("\n📊 Dashboard Content Analysis:")
    response = client.get(reverse('staff:dashboard'))
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check for dashboard cards
        checks = [
            ('Total Users', 'Total Users'),
            ('Premium Users', 'Premium Users'),
            ('Quiz Attempts', 'Quiz Attempts'),
            ('Total Revenue', 'Revenue'),
            ('Profile Menu', 'Profile'),
        ]
        
        for check_name, search_term in checks:
            variations = [
                search_term,
                search_term.lower(),
                search_term.replace(' ', '_'),
                search_term.replace(' ', ''),
            ]
            
            found = any(var in content.lower() for var in variations)
            status = "✅" if found else "❌"
            print(f"  {status} {check_name}: {search_term}")
            
            if not found:
                # Look for similar terms
                similar_terms = []
                if 'user' in search_term.lower():
                    if 'user' in content.lower():
                        similar_terms.append('user (found)')
                if 'premium' in search_term.lower():
                    if 'premium' in content.lower():
                        similar_terms.append('premium (found)')
                if similar_terms:
                    print(f"    Similar terms found: {', '.join(similar_terms)}")
    
    # Test 2: User Detail Quiz Stats
    print("\n👤 User Detail Quiz Stats:")
    test_user = User.objects.filter(is_staff=False).first()
    if test_user:
        detail_url = reverse('staff:user_detail', kwargs={'pk': test_user.id})
        response = client.get(detail_url)
        if response.status_code == 200:
            content = response.content.decode()
            
            quiz_terms = ['Quiz Statistics', 'quiz', 'Quiz', 'statistics', 'attempts']
            for term in quiz_terms:
                found = term in content
                status = "✅" if found else "❌"
                print(f"  {status} '{term}' in content")
    
    # Test 3: User Edit JavaScript
    print("\n✏️ User Edit JavaScript Analysis:")
    if test_user:
        edit_url = reverse('staff:user_edit', kwargs={'pk': test_user.id})
        response = client.get(edit_url)
        if response.status_code == 200:
            content = response.content.decode()
            
            js_checks = [
                ('exportUserData function', 'exportUserData'),
                ('sendWelcomeEmail function', 'sendWelcomeEmail'),
                ('showNotification function', 'showNotification'),
                ('college dropdown logic', 'college'),
                ('province change', 'province'),
                ('college_type change', 'college_type'),
            ]
            
            for check_name, search_term in js_checks:
                found = search_term in content
                status = "✅" if found else "❌"
                print(f"  {status} {check_name}")
    
    # Test 4: URL resolution check
    print("\n🔗 URL Resolution Check:")
    urls_to_check = [
        ('staff:user_add', 'Add User URL'),
        ('staff:dashboard', 'Dashboard URL'),
        ('staff:user_list', 'User List URL'),
    ]
    
    for url_name, description in urls_to_check:
        try:
            url = reverse(url_name)
            response = client.get(url)
            status = "✅" if response.status_code == 200 else f"❌ ({response.status_code})"
            print(f"  {status} {description}: {url}")
        except Exception as e:
            print(f"  ❌ {description}: Error - {str(e)}")

if __name__ == '__main__':
    test_remaining_issues()
