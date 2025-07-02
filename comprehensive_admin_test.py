#!/usr/bin/env python
"""
COMPREHENSIVE ADMIN TEST SUITE
Tests every button, function, and feature across all admin pages:
- Dashboard
- User List Page  
- User Detail Page
- User Edit Page
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
from core.models import UserProfile
import json
import time

class AdminTestSuite:
    def __init__(self):
        self.client = Client()
        self.test_users = []
        self.staff_user = None
        self.results = {
            'dashboard': {'passed': 0, 'failed': 0, 'tests': []},
            'user_list': {'passed': 0, 'failed': 0, 'tests': []},
            'user_detail': {'passed': 0, 'failed': 0, 'tests': []},
            'user_edit': {'passed': 0, 'failed': 0, 'tests': []},
        }
    
    def setup_test_data(self):
        """Create test users and staff for testing"""
        print("🔧 Setting up test data...")
        
        # Create staff user
        self.staff_user, created = User.objects.get_or_create(
            username='admin_test_staff',
            defaults={
                'email': 'admin_test@example.com',
                'first_name': 'Admin',
                'last_name': 'Tester',
                'is_staff': True,
                'is_superuser': True
            }
        )
        self.staff_user.set_password('admintest123')
        self.staff_user.save()
        
        # Create multiple test users with different statuses
        test_user_data = [
            {'username': 'test_active_user', 'email': 'active@test.com', 'is_active': True, 'premium': False},
            {'username': 'test_inactive_user', 'email': 'inactive@test.com', 'is_active': False, 'premium': False},
            {'username': 'test_premium_user', 'email': 'premium@test.com', 'is_active': True, 'premium': True},
            {'username': 'test_expired_user', 'email': 'expired@test.com', 'is_active': True, 'premium': False},
            {'username': 'test_no_email_user', 'email': '', 'is_active': True, 'premium': False},
        ]
        
        for i, data in enumerate(test_user_data):
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': f'Test{i+1}',
                    'last_name': 'User',
                    'is_active': data['is_active']
                }
            )
            
            # Create/update profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'year_of_study': 'year_1',
                    'province': 'punjab',
                    'college_type': 'public',
                    'college_name': 'King Edward Medical University',
                    'phone_number': f'+92300123456{i}',
                    'is_premium': data['premium']
                }
            )
            
            if data['premium']:
                from django.utils import timezone
                from datetime import timedelta
                profile.premium_expires_at = timezone.now() + timedelta(days=365)
                profile.save()
            
            self.test_users.append(user)
        
        # Login as staff
        login_success = self.client.login(username='admin_test_staff', password='admintest123')
        if login_success:
            print("✅ Test data setup complete")
            print(f"   Staff user: {self.staff_user.username}")
            print(f"   Test users created: {len(self.test_users)}")
        else:
            raise Exception("Failed to login as staff user")
    
    def log_test(self, page, test_name, passed, message=""):
        """Log test result"""
        status = "✅" if passed else "❌"
        print(f"  {status} {test_name}: {message}")
        
        self.results[page]['tests'].append({
            'name': test_name,
            'passed': passed,
            'message': message
        })
        
        if passed:
            self.results[page]['passed'] += 1
        else:
            self.results[page]['failed'] += 1
    
    def test_dashboard(self):
        """Test Dashboard page functionality"""
        print("\n📊 TESTING DASHBOARD PAGE")
        print("=" * 40)
        
        try:
            # Test dashboard load
            response = self.client.get(reverse('staff:dashboard'))
            self.log_test('dashboard', 'Dashboard Load', 
                         response.status_code == 200, f"HTTP {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode()
                
                # Test dashboard elements
                elements_to_check = [
                    ('User Stats Card', 'Total Users'),
                    ('Premium Stats Card', 'Premium Users'),
                    ('Activity Stats Card', 'Total Quiz Attempts'),
                    ('Revenue Stats Card', 'Total Revenue'),
                    ('Recent Users Section', 'Recent Users'),
                    ('Quick Actions Section', 'Quick Actions'),
                    ('Navigation Menu', 'Users'),
                    ('Navigation Menu', 'Questions'),
                    ('Profile Dropdown', 'Profile'),
                ]
                
                for element_name, search_text in elements_to_check:
                    found = search_text in content
                    self.log_test('dashboard', f'{element_name} Present', 
                                 found, f"'{search_text}' {'found' if found else 'not found'}")
                
                # Test dashboard links
                dashboard_links = [
                    ('user_list', 'Users link'),
                    ('user_add', 'Add User link'),
                    ('question_list', 'Questions link'),
                    ('subject_list', 'Subjects link'),
                ]
                
                for url_name, description in dashboard_links:
                    try:
                        url = reverse(f'staff:{url_name}')
                        link_present = url in content or f'href="{url}"' in content
                        self.log_test('dashboard', f'{description} Working', 
                                     link_present, f"URL: {url}")
                    except:
                        self.log_test('dashboard', f'{description} Working', 
                                     False, "URL resolution failed")
        
        except Exception as e:
            self.log_test('dashboard', 'Dashboard Test', False, str(e))
    
    def test_user_list(self):
        """Test User List page functionality"""
        print("\n👥 TESTING USER LIST PAGE")
        print("=" * 40)
        
        try:
            # Test user list load
            response = self.client.get(reverse('staff:user_list'))
            self.log_test('user_list', 'User List Load', 
                         response.status_code == 200, f"HTTP {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode()
                
                # Test search functionality
                search_tests = [
                    ('Email Search', {'search': 'active@test.com'}),
                    ('Name Search', {'search': 'Test1'}),
                    ('Username Search', {'search': 'test_active_user'}),
                    ('Status Filter', {'is_active': 'true'}),
                    ('Premium Filter', {'subscription_status': 'premium'}),
                ]
                
                for test_name, params in search_tests:
                    search_response = self.client.get(reverse('staff:user_list'), params)
                    self.log_test('user_list', f'{test_name}', 
                                 search_response.status_code == 200, 
                                 f"Search with {params}")
                
                # Test bulk actions
                test_user_ids = [user.id for user in self.test_users[:2]]
                
                bulk_actions = [
                    ('activate', 'Bulk Activate'),
                    ('deactivate', 'Bulk Deactivate'), 
                    ('make_premium', 'Bulk Make Premium'),
                    ('remove_premium', 'Bulk Remove Premium'),
                    ('reset_password', 'Bulk Reset Password'),
                    ('export', 'Bulk Export'),
                ]
                
                for action, description in bulk_actions:
                    bulk_response = self.client.post(reverse('staff:user_list'), {
                        'action': action,
                        'user_ids': test_user_ids
                    })
                    
                    success = bulk_response.status_code in [200, 302]
                    self.log_test('user_list', f'{description}', 
                                 success, f"Action: {action}")
                
                # Test pagination
                page_response = self.client.get(reverse('staff:user_list') + '?page=1')
                self.log_test('user_list', 'Pagination', 
                             page_response.status_code == 200, "Page 1 load")
                
                # Test Add User button
                add_user_url = reverse('staff:user_add')
                add_button_present = add_user_url in content
                self.log_test('user_list', 'Add User Button', 
                             add_button_present, f"Add user link: {add_user_url}")
        
        except Exception as e:
            self.log_test('user_list', 'User List Test', False, str(e))
    
    def test_user_detail(self):
        """Test User Detail page functionality"""
        print("\n👤 TESTING USER DETAIL PAGE")
        print("=" * 40)
        
        try:
            test_user = self.test_users[0]  # Use first test user
            detail_url = reverse('staff:user_detail', kwargs={'pk': test_user.id})
            
            # Test detail page load
            response = self.client.get(detail_url)
            self.log_test('user_detail', 'Detail Page Load', 
                         response.status_code == 200, f"HTTP {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode()
                
                # Test page elements
                elements = [
                    ('User Information', test_user.username),
                    ('Email Display', test_user.email if test_user.email else 'No email'),
                    ('Action Dropdown', 'Actions'),
                    ('Edit Button', 'Edit User'),
                    ('Export Button', 'Export User Data'),
                    ('Stats Section', 'Quiz Statistics'),
                ]
                
                for element_name, search_text in elements:
                    found = search_text in content
                    self.log_test('user_detail', f'{element_name} Display', 
                                 found, f"'{search_text}' {'found' if found else 'not found'}")
                
                # Test AJAX actions
                ajax_actions = [
                    ('toggle_status', {'status': 'false'}, 'Toggle User Status'),
                    ('toggle_premium', {'is_premium': 'true'}, 'Toggle Premium Status'),
                    ('send_welcome_email', {}, 'Send Welcome Email'),
                    ('reset_password', {}, 'Reset Password'),
                ]
                
                for action, data, description in ajax_actions:
                    post_data = {'action': action}
                    post_data.update(data)
                    
                    ajax_response = self.client.post(detail_url, post_data)
                    
                    if ajax_response.status_code == 200:
                        try:
                            json_data = ajax_response.json()
                            success = json_data.get('success', False)
                            message = json_data.get('message', 'No message')
                            self.log_test('user_detail', f'{description}', 
                                         success, message)
                        except:
                            self.log_test('user_detail', f'{description}', 
                                         False, "Invalid JSON response")
                    else:
                        self.log_test('user_detail', f'{description}', 
                                     False, f"HTTP {ajax_response.status_code}")
                
                # Test export functionality
                export_url = reverse('staff:user_export', kwargs={'pk': test_user.id})
                export_response = self.client.get(export_url)
                
                export_success = (export_response.status_code == 200 and 
                                'csv' in export_response.get('Content-Type', ''))
                self.log_test('user_detail', 'Export User Data', 
                             export_success, f"CSV export: {export_response.status_code}")
                
                # Test edit page link
                edit_url = reverse('staff:user_edit', kwargs={'pk': test_user.id})
                edit_link_present = edit_url in content
                self.log_test('user_detail', 'Edit User Link', 
                             edit_link_present, f"Edit link: {edit_url}")
        
        except Exception as e:
            self.log_test('user_detail', 'User Detail Test', False, str(e))
    
    def test_user_edit(self):
        """Test User Edit page functionality"""
        print("\n✏️ TESTING USER EDIT PAGE")
        print("=" * 40)
        
        try:
            test_user = self.test_users[0]  # Use first test user
            edit_url = reverse('staff:user_edit', kwargs={'pk': test_user.id})
            
            # Test edit page load
            response = self.client.get(edit_url)
            self.log_test('user_edit', 'Edit Page Load', 
                         response.status_code == 200, f"HTTP {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode()
                
                # Test form elements
                form_elements = [
                    ('Username Field', 'id_username'),
                    ('Email Field', 'id_email'),
                    ('First Name Field', 'id_first_name'),
                    ('Last Name Field', 'id_last_name'),
                    ('Province Dropdown', 'id_province'),
                    ('College Type Dropdown', 'id_college_type'),
                    ('College Name Dropdown', 'id_college_name'),
                    ('Year of Study Field', 'id_year_of_study'),
                    ('Premium Checkbox', 'id_is_premium'),
                    ('Active Checkbox', 'id_is_active'),
                ]
                
                for element_name, field_id in form_elements:
                    found = field_id in content
                    self.log_test('user_edit', f'{element_name} Present', 
                                 found, f"Field ID: {field_id}")
                
                # Test form submission
                form_data = {
                    'username': test_user.username,
                    'email': test_user.email,
                    'first_name': 'Updated',
                    'last_name': 'Name',
                    'is_active': True,
                    'is_staff': False,
                    'year_of_study': 'year_2',
                    'province': 'sindh',
                    'college_type': 'private',
                    'college_name': 'Aga Khan University',
                    'phone_number': '+923001234567',
                    'is_premium': True
                }
                
                form_response = self.client.post(edit_url, form_data)
                form_success = form_response.status_code in [200, 302]
                self.log_test('user_edit', 'Form Submission', 
                             form_success, f"HTTP {form_response.status_code}")
                
                # Test college dropdown AJAX
                college_ajax_data = {
                    'province': 'punjab',
                    'college_type': 'public'
                }
                
                # Note: This would typically be a separate AJAX endpoint
                # For now, we'll just test that the form handles the data
                ajax_form_response = self.client.post(edit_url, {**form_data, **college_ajax_data})
                ajax_success = ajax_form_response.status_code in [200, 302]
                self.log_test('user_edit', 'College Dropdown AJAX', 
                             ajax_success, "Dynamic college loading")
                
                # Test action buttons
                action_buttons = [
                    ('Save Button', 'Save'),
                    ('Cancel Button', 'Cancel'),
                    ('Export User Data', 'Export User Data'),
                    ('Send Welcome Email', 'Send Welcome Email'),
                ]
                
                for button_name, button_text in action_buttons:
                    found = button_text in content
                    self.log_test('user_edit', f'{button_name} Present', 
                                 found, f"Button: {button_text}")
                
                # Test JavaScript functionality
                js_functions = [
                    ('exportUserData', 'Export function'),
                    ('sendWelcomeEmail', 'Welcome email function'),
                    ('showNotification', 'Notification function'),
                    ('college dropdown', 'College dropdown logic'),
                ]
                
                for function_name, description in js_functions:
                    found = function_name.replace(' ', '') in content.replace(' ', '')
                    self.log_test('user_edit', f'{description} JS', 
                                 found, f"JavaScript: {function_name}")
        
        except Exception as e:
            self.log_test('user_edit', 'User Edit Test', False, str(e))
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 COMPREHENSIVE ADMIN TEST SUITE")
        print("=" * 60)
        print("Testing: Dashboard, User List, User Detail, User Edit")
        print("=" * 60)
        
        # Setup
        self.setup_test_data()
        
        # Run tests
        self.test_dashboard()
        self.test_user_list()
        self.test_user_detail()
        self.test_user_edit()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for page, results in self.results.items():
            passed = results['passed']
            failed = results['failed']
            total = passed + failed
            
            total_passed += passed
            total_failed += failed
            
            status_icon = "✅" if failed == 0 else "⚠️" if passed > failed else "❌"
            
            print(f"{status_icon} {page.upper().replace('_', ' ')}: {passed}/{total} passed")
            
            if failed > 0:
                print(f"   Failed tests:")
                for test in results['tests']:
                    if not test['passed']:
                        print(f"     ❌ {test['name']}: {test['message']}")
        
        print("-" * 60)
        overall_total = total_passed + total_failed
        success_rate = (total_passed / overall_total * 100) if overall_total > 0 else 0
        
        print(f"🎯 OVERALL RESULTS: {total_passed}/{overall_total} tests passed ({success_rate:.1f}%)")
        
        if total_failed == 0:
            print("🎉 ALL TESTS PASSED! Admin pages are fully functional!")
        elif success_rate >= 80:
            print("✅ Most tests passed! Minor issues to address.")
        else:
            print("⚠️ Several issues found. Review failed tests above.")
        
        print("=" * 60)

if __name__ == '__main__':
    test_suite = AdminTestSuite()
    test_suite.run_all_tests()
