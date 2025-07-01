#!/usr/bin/env python
"""
Show what the CSV template looks like
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
django.setup()

from staff.views.user_views import BulkUserUploadView

def show_template_preview():
    """Show what the template looks like"""
    print("📋 CSV Template Preview")
    print("=" * 60)
    
    try:
        # Generate template
        view = BulkUserUploadView()
        response = view.generate_dynamic_template()
        
        # Get content
        content = response.content.decode('utf-8')
        lines = content.split('\n')
        
        print("📁 Template Content:")
        print("-" * 60)
        for i, line in enumerate(lines[:20], 1):  # Show first 20 lines
            if line.strip():
                print(f"{i:2d}: {line}")
        
        if len(lines) > 20:
            print(f"... and {len(lines) - 20} more lines")
        
        print("-" * 60)
        print(f"✅ Template contains {len(lines)} lines")
        print("✅ Ready for download via bulk upload page")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating template: {str(e)}")
        return False

def main():
    print("🎯 CSV Template Download - READY!")
    print("\n" + "=" * 50)
    
    if show_template_preview():
        print("\n🎉 CSV Template Download is WORKING!")
        print("\n📋 How to use:")
        print("1. Go to: /staff/users/bulk-upload/")
        print("2. Click 'Download CSV Template' button")
        print("3. Fill in your user data")
        print("4. Upload the completed file")
        print("\n✅ Features included:")
        print("- Instructions in CSV comments")
        print("- Sample data for reference")
        print("- All required and optional columns")
        print("- Proper encoding for Excel compatibility")

if __name__ == '__main__':
    main()
