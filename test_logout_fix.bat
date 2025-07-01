@echo off
echo Testing logout fix...
echo.

cd /d "d:\PMC\Exam-Prep-Site"

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Running Django check...
python manage.py check

echo.
echo Testing URL resolution...
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medprep.settings'); import django; django.setup(); from django.urls import reverse; print('Logout URL:', reverse('core:logout'))"

echo.
echo Starting Django server for manual testing...
echo Navigate to: http://127.0.0.1:8000/logout/
echo.
python manage.py runserver
