import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings')
    
    print("Starting MedPrep Django Development Server...")
    print("Navigate to: http://127.0.0.1:8000/")
    print("Admin Panel: http://127.0.0.1:8000/admin/")
    print("Admin credentials: admin / admin123")
    print("-" * 50)
    
    try:
        execute_from_command_line(['manage.py', 'runserver'])
    except Exception as e:
        print(f"Error starting server: {e}")
        input("Press Enter to exit...")
