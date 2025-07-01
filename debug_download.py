#!/usr/bin/env python
"""
Debug the download_template method
"""

import os
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')

import django
django.setup()

from django.contrib.staticfiles import finders
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.messages.storage.fallback import FallbackStorage
from staff.views.user_views import BulkUserUploadView

def debug_template_path():
    """Debug the template path finding"""
    print("🔍 Debugging template path...")
    
    # Check what finders.find returns
    template_path = finders.find('templates/user_upload_template.csv')
    print(f"   finders.find result: {template_path}")
    
    if template_path:
        print(f"   Path exists: {os.path.exists(template_path)}")
        if os.path.exists(template_path):
            print(f"   File size: {os.path.getsize(template_path)} bytes")
    
    # Check direct path
    direct_path = os.path.join(project_dir, 'static', 'templates', 'user_upload_template.csv')
    print(f"   Direct path: {direct_path}")
    print(f"   Direct path exists: {os.path.exists(direct_path)}")
    
    if os.path.exists(direct_path):
        print(f"   Direct file size: {os.path.getsize(direct_path)} bytes")
        
        # Try to read it
        try:
            with open(direct_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"   Content length: {len(content)} characters")
                print(f"   First line: {content.split(chr(10))[0]}")
        except Exception as e:
            print(f"   Error reading file: {e}")

def debug_download_method():
    """Debug the download_template method"""
    print("\n🔍 Debugging download_template method...")
    
    # Setup
    factory = RequestFactory()
    user = User.objects.create_user(
        username='debuguser',
        email='debug@example.com',
        password='testpass',
        is_staff=True
    )
    
    request = factory.post('/staff/users/bulk-upload/', {
        'action': 'download_template'
    })
    request.user = user
    
    session = SessionStore()
    session.create()
    request.session = session
    request._messages = FallbackStorage(request)
    
    view = BulkUserUploadView()
    view.request = request
    
    try:
        print("   Calling download_template()...")
        response = view.download_template()
        
        print(f"   Response type: {type(response)}")
        print(f"   Response status: {response.status_code}")
        print(f"   Content-Type: {response.get('Content-Type', 'Not set')}")
        print(f"   Content-Disposition: {response.get('Content-Disposition', 'Not set')}")
        
        if hasattr(response, 'content'):
            print(f"   Has content: Yes")
            print(f"   Content length: {len(response.content)}")
        else:
            print(f"   Has content: No")
            
        return response
        
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        user.delete()

def debug_dynamic_template():
    """Debug the dynamic template generation"""
    print("\n🔍 Testing dynamic template generation...")
    
    view = BulkUserUploadView()
    
    try:
        response = view.generate_dynamic_template()
        
        print(f"   Response type: {type(response)}")
        print(f"   Response status: {response.status_code}")
        print(f"   Content-Type: {response.get('Content-Type', 'Not set')}")
        print(f"   Content-Disposition: {response.get('Content-Disposition', 'Not set')}")
        
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            print(f"   Content length: {len(content)}")
            print(f"   First 100 chars: {content[:100]}")
            
            if 'first_name,last_name,email' in content:
                print("   ✅ Dynamic template content is correct")
            else:
                print("   ❌ Dynamic template content is incorrect")
        
        return response
        
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    print("🐛 DOWNLOAD DEBUG SESSION")
    print("=" * 40)
    
    debug_template_path()
    response1 = debug_download_method()
    response2 = debug_dynamic_template()
    
    print("\n" + "=" * 40)
    print("📋 SUMMARY:")
    
    if response1 and response1.status_code == 200:
        print("✅ download_template() works")
    else:
        print("❌ download_template() has issues")
    
    if response2 and response2.status_code == 200:
        print("✅ generate_dynamic_template() works")
    else:
        print("❌ generate_dynamic_template() has issues")
    
    print("=" * 40)
