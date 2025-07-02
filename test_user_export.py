#!/usr/bin/env python
"""
Test script to verify the user export functionality
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

def test_user_export():
    """Test the user export functionality"""
    print("🔄 Testing User Export Functionality")
    print("=" * 50)
    
    try:
        # Create a test user if needed
        user, created = User.objects.get_or_create(
            username='test_export_user',
            defaults={
                'email': 'test_export@example.com',
                'first_name': 'Test',
                'last_name': 'Export',
                'is_active': True
            }
        )
        
        if created:
            print(f"✓ Created test user: {user.username}")
        else:
            print(f"✓ Using existing test user: {user.username}")
        
        # Create or get a staff user
        staff_user, created = User.objects.get_or_create(
            username='staff_export_test',
            defaults={
                'email': 'staff_export@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        staff_user.set_password('testpass123')
        staff_user.save()
        
        # Test the export URL
        client = Client()
        client.login(username='staff_export_test', password='testpass123')
        print("✓ Logged in as staff user")
        
        # Test export URL resolution
        export_url = reverse('staff:user_export', kwargs={'pk': user.id})
        print(f"✓ Export URL: {export_url}")
        
        # Test the export functionality
        response = client.get(export_url)
        
        print(f"📊 Export Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Export successful!")
            
            # Check content type
            content_type = response.get('Content-Type', '')
            print(f"   Content Type: {content_type}")
            
            # Check content disposition
            disposition = response.get('Content-Disposition', '')
            print(f"   Content Disposition: {disposition}")
            
            # Check if response contains CSV data
            content = response.content.decode('utf-8')
            lines = content.split('\n')
            print(f"   CSV Lines: {len(lines)}")
            
            if len(lines) > 5:
                print("   First few lines:")
                for i, line in enumerate(lines[:5]):
                    if line.strip():
                        print(f"     {i+1}: {line}")
                        
        elif response.status_code == 302:
            print(f"⚠ Redirected to: {response.get('Location', 'Unknown')}")
        else:
            print(f"❌ Export failed with status: {response.status_code}")
            print(f"   Response content: {response.content[:200]}")
        
        # Test with non-existent user
        print("\n🔍 Testing with non-existent user...")
        response = client.get(reverse('staff:user_export', kwargs={'pk': 99999}))
        if response.status_code == 302:
            print("✓ Properly handles non-existent user (redirects)")
        else:
            print(f"⚠ Unexpected response for non-existent user: {response.status_code}")
            
        print("\n🎉 User Export Test Complete!")
        
    except Exception as e:
        print(f"❌ Error testing user export: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_user_export()
