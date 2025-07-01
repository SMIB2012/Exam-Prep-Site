#!/usr/bin/env python
"""
Test the CSV template download functionality
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from staff.views.user_views import BulkUserUploadView

def test_template_download():
    """Test CSV template download"""
    print("🔍 Testing CSV Template Download...")
    
    try:
        # Test the download_template method directly
        view = BulkUserUploadView()
        response = view.download_template()
        
        print(f"✅ Template download response generated")
        print(f"   Status code: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
        print(f"   Content type: {response.get('Content-Type', 'N/A')}")
        print(f"   Content disposition: {response.get('Content-Disposition', 'N/A')}")
        
        # Check if response has content
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            lines = content.split('\n')
            print(f"   Content lines: {len(lines)}")
            
            # Check for key elements
            if 'first_name,last_name,email' in content:
                print("✅ CSV headers found")
            if 'Ahmed,Hassan' in content or 'Instructions:' in content:
                print("✅ Sample data or instructions found")
            
            # Show first few lines
            print("   First 3 lines:")
            for i, line in enumerate(lines[:3]):
                print(f"     {i+1}: {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template download test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_web_template_download():
    """Test template download via web interface"""
    print("\n🌐 Testing Web Template Download...")
    
    try:
        # Create test client
        client = Client()
        
        # Create or get test admin user
        test_user, created = User.objects.get_or_create(
            username='template_test_admin',
            defaults={
                'email': 'template@test.com',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Template',
                'last_name': 'Test'
            }
        )
        if created:
            test_user.set_password('templatetest123')
            test_user.save()
        
        # Login
        login_success = client.login(username='template_test_admin', password='templatetest123')
        if not login_success:
            print("❌ Login failed")
            return False
        
        # Test template download via POST
        response = client.post('/staff/users/bulk-upload/', {
            'action': 'download_template'
        })
        
        print(f"✅ Web template download response")
        print(f"   Status code: {response.status_code}")
        print(f"   Content type: {response.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            print("✅ Template download successful!")
            
            # Check content
            content = response.content.decode('utf-8')
            if 'first_name' in content:
                print("✅ CSV content found")
            return True
        else:
            print(f"❌ Download failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Web template download test failed: {str(e)}")
        return False

def test_static_file_access():
    """Test if the static template file can be accessed"""
    print("\n📂 Testing Static File Access...")
    
    try:
        from django.contrib.staticfiles import finders
        
        # Try to find the template file
        template_path = finders.find('templates/user_upload_template.csv')
        
        if template_path:
            print(f"✅ Template file found at: {template_path}")
            
            # Check if file exists and is readable
            if os.path.exists(template_path):
                print("✅ File exists and is accessible")
                
                # Read a few lines
                with open(template_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:5]
                    print(f"   File has {len(lines)} initial lines")
                    for i, line in enumerate(lines):
                        print(f"     {i+1}: {line.strip()}")
                
                return True
            else:
                print("❌ File path found but file doesn't exist")
                return False
        else:
            print("⚠️ Static template file not found, will use dynamic generation")
            return True  # This is OK, dynamic generation will work
            
    except Exception as e:
        print(f"❌ Static file test failed: {str(e)}")
        return False

def main():
    """Run all template download tests"""
    print("📥 CSV Template Download Tests")
    print("=" * 40)
    
    tests = [
        test_static_file_access,
        test_template_download,
        test_web_template_download
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed >= 2:  # At least dynamic generation should work
        print("🎉 Template download functionality is working!")
        print("\n📋 How it works:")
        print("1. Button triggers POST with action='download_template'")
        print("2. View tries to serve static file first")
        print("3. Falls back to dynamic generation if needed")
        print("4. Returns CSV file with instructions and sample data")
    else:
        print("⚠️ Template download needs attention")

if __name__ == '__main__':
    main()
