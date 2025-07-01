from django.views.generic import ListView, DetailView, UpdateView, CreateView, View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.staticfiles import finders
from core.models import UserProfile
from staff.forms import UserSearchForm, UserCreateForm, BulkUserUploadForm
import csv
import io
import os
from datetime import datetime


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require staff permissions"""
    def test_func(self):
        return self.request.user.is_staff


class UserListView(StaffRequiredMixin, ListView):
    """List all users with search and filter capabilities"""
    model = User
    template_name = 'staff/users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        """Filter users based on search and filter parameters"""
        queryset = User.objects.select_related('userprofile').prefetch_related('groups')
        
        # Get search parameters
        search = self.request.GET.get('search', '').strip()
        subscription_status = self.request.GET.get('subscription_status', '')
        is_active = self.request.GET.get('is_active', '')
        year_filter = self.request.GET.get('year_filter', '')
        
        # Apply search filter
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(username__icontains=search)
            )
        
        # Apply subscription status filter
        if subscription_status == 'premium':
            queryset = queryset.filter(userprofile__is_premium=True)
        elif subscription_status == 'free':
            queryset = queryset.filter(
                Q(userprofile__is_premium=False) | 
                Q(userprofile__isnull=True)
            )
        
        # Apply active status filter
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
        
        # Apply year filter
        if year_filter:
            queryset = queryset.filter(userprofile__year_of_study=year_filter)
        
        return queryset.order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        """Add additional context data"""
        context = super().get_context_data(**kwargs)
        
        # Initialize search form with current GET parameters
        context['search_form'] = UserSearchForm(self.request.GET or None)
        
        # Add filter choices for year
        context['year_choices'] = UserProfile.YEAR_CHOICES
        
        # Add summary statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        premium_users = User.objects.filter(userprofile__is_premium=True).count()
        
        context.update({
            'total_users': total_users,
            'active_users': active_users,
            'premium_users': premium_users,
            'inactive_users': total_users - active_users,
        })
        
        return context


class UserDetailView(StaffRequiredMixin, DetailView):
    """View user details"""
    model = User
    template_name = 'staff/users/user_detail.html'
    context_object_name = 'user'


class UserEditView(StaffRequiredMixin, UpdateView):
    """Edit user details"""
    model = User
    template_name = 'staff/users/user_edit.html'
    fields = ['first_name', 'last_name', 'email', 'is_active']

class UserCreateView(StaffRequiredMixin, CreateView):
    """Create new user with profile"""
    model = User
    form_class = UserCreateForm
    template_name = 'staff/users/user_add.html'
    success_url = reverse_lazy('staff:user_list')
    
    def form_valid(self, form):
        """Create user and profile"""
        # Create the user
        user = form.save(commit=False)
        user.username = form.cleaned_data['email']  # Use email as username
        user.set_password(form.cleaned_data['password'])
        
        # Set admin fields
        user_role = form.cleaned_data.get('user_role', 'student')
        if user_role == 'admin':
            user.is_staff = True
            user.is_superuser = True
        elif user_role == 'faculty':
            user.is_staff = True
        
        user.is_active = form.cleaned_data.get('is_active', True)
        user.save()
        
        # Update or create profile (profile is automatically created by signals)
        profile_data = {
            'year_of_study': form.cleaned_data.get('year_of_study', ''),
            'province': form.cleaned_data.get('province', ''),
            'college_type': form.cleaned_data.get('college_type', ''),
            'college_name': form.cleaned_data.get('college_name', ''),
            'phone_number': form.cleaned_data.get('phone_number', ''),
            'is_premium': form.cleaned_data.get('is_premium', False),
        }
        
        # Get the profile that was automatically created by the signal
        profile = user.userprofile
        for field, value in profile_data.items():
            setattr(profile, field, value)
        
        # If user is marked as premium, set expiration date
        if profile_data.get('is_premium', False):
            from django.utils import timezone
            from datetime import timedelta
            
            # Use custom expiration date if provided, otherwise default to 1 year
            custom_expiry = form.cleaned_data.get('premium_expires_at')
            if custom_expiry:
                profile.premium_expires_at = custom_expiry
            else:
                # Default premium expiration: 1 year from now
                profile.premium_expires_at = timezone.now() + timedelta(days=365)
        
        profile.save()
        
        messages.success(
            self.request, 
            f'User "{user.get_full_name()}" has been created successfully!'
        )
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        """Handle form errors"""
        messages.error(
            self.request,
            'Please correct the errors below and try again.'
        )
        return super().form_invalid(form)


class BulkUserUploadView(StaffRequiredMixin, View):
    """Bulk upload users from CSV/Excel file"""
    template_name = 'staff/users/bulk_upload.html'
    success_url = reverse_lazy('staff:user_list')
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests"""
        form = BulkUserUploadForm()
        context = {
            'form': form,
            'preview_data': request.session.get('bulk_upload_preview', None)
        }
        return render(request, self.template_name, context)
    
    def get_form(self):
        """Get form instance"""
        return BulkUserUploadForm(self.request.POST or None, self.request.FILES or None)
    
    def post(self, request, *args, **kwargs):
        """Handle form submission and file processing"""
        action = request.POST.get('action', 'upload')
        
        # Handle template download first (doesn't require form validation)
        if action == 'download_template':
            return self.download_template()
        
        # For other actions, validate the form
        form = self.get_form()
        
        if form.is_valid():
            if action == 'upload':
                return self.handle_file_upload(form)
            elif action == 'confirm':
                return self.handle_confirm_import(form)
        
        # Form is invalid, render with errors
        context = {
            'form': form,
            'preview_data': request.session.get('bulk_upload_preview', None)
        }
        return render(request, self.template_name, context)
    
    def handle_file_upload(self, form):
        """Process uploaded file and show preview"""
        csv_file = form.cleaned_data['csv_file']
        default_password = form.cleaned_data['default_password']
        default_role = form.cleaned_data['default_role']
        
        try:
            # Read the file
            if csv_file.name.endswith('.csv'):
                file_data = csv_file.read().decode('utf-8')
                df = self.parse_csv_data(file_data)
            else:
                # Handle Excel files
                df = self.parse_excel_data(csv_file)
            
            # Validate and prepare data
            processed_data = self.process_data(df, default_password, default_role)
            
            # Store in session for confirmation
            self.request.session['bulk_upload_preview'] = processed_data
            self.request.session['bulk_upload_defaults'] = {
                'default_password': default_password,
                'default_role': default_role,
                'send_welcome_emails': form.cleaned_data.get('send_welcome_emails', True),
                'skip_errors': form.cleaned_data.get('skip_errors', True)
            }
            
            messages.success(
                self.request,
                f"File processed successfully! {len(processed_data['valid_rows'])} valid rows, "
                f"{len(processed_data['error_rows'])} errors found."
            )
            
        except Exception as e:
            messages.error(self.request, f"Error processing file: {str(e)}")
        
        # Return to the same page with updated context
        context = {
            'form': BulkUserUploadForm(),
            'preview_data': self.request.session.get('bulk_upload_preview', None)
        }
        return render(self.request, self.template_name, context)
    
    def handle_confirm_import(self, form):
        """Actually create the users from validated data"""
        preview_data = self.request.session.get('bulk_upload_preview')
        defaults = self.request.session.get('bulk_upload_defaults', {})
        
        if not preview_data:
            messages.error(self.request, "No data to import. Please upload a file first.")
            return redirect('staff:user_bulk_upload')
        
        created_count = 0
        skipped_count = 0
        
        # Process valid rows
        for row_data in preview_data['valid_rows']:
            try:
                # Create user
                user = User.objects.create_user(
                    username=row_data['email'],
                    email=row_data['email'],
                    first_name=row_data['first_name'],
                    last_name=row_data['last_name'],
                    password=row_data.get('password', defaults.get('default_password', 'TempPass123!')),
                    is_active=row_data.get('is_active', True)
                )
                
                # Set staff permissions based on role
                role = row_data.get('role', defaults.get('default_role', 'student'))
                if role == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                elif role == 'faculty':
                    user.is_staff = True
                user.save()
                
                # Update user profile (profile is automatically created by signals)
                profile = user.userprofile
                profile.year_of_study = row_data.get('year_of_study', '')
                profile.province = row_data.get('province', '')
                profile.college_type = row_data.get('college_type', '')
                profile.college_name = row_data.get('college_name', '')
                profile.phone_number = row_data.get('phone_number', '')
                profile.is_premium = row_data.get('is_premium', False)
                
                # If user is marked as premium, set a default expiration date
                if row_data.get('is_premium', False):
                    from django.utils import timezone
                    from datetime import timedelta
                    # Default premium expiration: 1 year from now
                    profile.premium_expires_at = timezone.now() + timedelta(days=365)
                
                profile.save()
                
                # Send welcome email if requested
                if defaults.get('send_welcome_emails', False):
                    self.send_welcome_email(user, row_data.get('password', defaults.get('default_password')))
                
                created_count += 1
                
            except Exception as e:
                skipped_count += 1
                if not defaults.get('skip_errors', True):
                    messages.error(self.request, f"Error creating user {row_data['email']}: {str(e)}")
                    break
        
        # Clear session data
        self.request.session.pop('bulk_upload_preview', None)
        self.request.session.pop('bulk_upload_defaults', None)
        
        messages.success(
            self.request,
            f"Bulk import completed! {created_count} users created, {skipped_count} skipped."
        )
        
        return redirect(self.success_url)
    
    def download_template(self):
        """Download CSV template file"""
        try:
            # Try to find the template file in static files
            template_path = finders.find('templates/user_upload_template.csv')
            
            if template_path and os.path.exists(template_path):
                # Serve the existing template file
                response = FileResponse(
                    open(template_path, 'rb'),
                    content_type='text/csv',
                    as_attachment=True,
                    filename='user_upload_template.csv'
                )
                return response
            else:
                # Fallback: Generate template dynamically
                return self.generate_dynamic_template()
                
        except Exception as e:
            # If file serving fails, generate dynamically
            return self.generate_dynamic_template()
    
    def generate_dynamic_template(self):
        """Generate CSV template dynamically as fallback"""
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="user_upload_template.csv"'
        
        # Add BOM for proper Excel encoding
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        # Write instructions as comments
        writer.writerow(['# MedAce Bulk User Upload Template'])
        writer.writerow(['# Instructions:'])
        writer.writerow(['# 1. Fill in the user data below the header row'])
        writer.writerow(['# 2. Required fields: first_name, last_name, email'])
        writer.writerow(['# 3. Optional fields can be left empty - defaults will be used'])
        writer.writerow(['# 4. For role: use student, faculty, or admin'])
        writer.writerow(['# 5. For year_of_study: use 1st_year, 2nd_year, 3rd_year, 4th_year, final_year, graduate'])
        writer.writerow(['# 6. For is_premium and is_active: use TRUE or FALSE'])
        writer.writerow(['# 7. Delete these instruction lines before uploading'])
        writer.writerow(['#'])
        
        # Write header
        writer.writerow([
            'first_name', 'last_name', 'email', 'password', 'role',
            'year_of_study', 'province', 'college_type', 'college_name',
            'phone_number', 'is_premium', 'is_active'
        ])
        
        # Write sample data
        writer.writerow([
            'Ahmed', 'Hassan', 'ahmed.hassan@example.com', 'SecurePass123!', 'student',
            '1st_year', 'Punjab', 'Public', 'King Edward Medical University (Lahore)',
            '+92-300-1234567', 'FALSE', 'TRUE'
        ])
        
        writer.writerow([
            'Fatima', 'Ali', 'fatima.ali@example.com', 'StudentPass456!', 'student',
            '2nd_year', 'Sindh', 'Private', 'Aga Khan University',
            '+92-321-9876543', 'TRUE', 'TRUE'
        ])
        
        writer.writerow([
            'Dr. Muhammad', 'Khan', 'dr.khan@example.com', 'FacultyPass789!', 'faculty',
            '', 'Khyber Pakhtunkhwa', 'Public', 'Khyber Medical College (Peshawar)',
            '+92-333-5555555', 'FALSE', 'TRUE'
        ])
        
        writer.writerow([
            'Dr. Sarah', 'Ahmed', 'dr.sarah@example.com', '', 'faculty',
            '', 'Punjab', 'Private', 'Lahore Medical & Dental College',
            '+92-300-7777777', 'TRUE', 'TRUE'
        ])
        
        writer.writerow([
            'Admin', 'User', 'admin@example.com', 'AdminPass999!', 'admin',
            '', 'Sindh', 'Public', 'Dow Medical College',
            '+92-321-8888888', 'TRUE', 'TRUE'
        ])
        
        return response
    
    def parse_csv_data(self, file_data):
        """Parse CSV data into a structured format"""
        lines = file_data.strip().split('\n')
        if not lines:
            raise ValueError("CSV file is empty")
        
        # Get headers
        headers = [h.strip().lower() for h in lines[0].split(',')]
        
        # Parse rows
        data = []
        for line in lines[1:]:
            if line.strip():
                values = [v.strip() for v in line.split(',')]
                row_dict = dict(zip(headers, values))
                data.append(row_dict)
        
        return data
    
    def parse_excel_data(self, file):
        """Parse Excel data - fallback to manual parsing if pandas not available"""
        try:
            import pandas as pd
            df = pd.read_excel(file)
            return df.to_dict('records')
        except ImportError:
            raise ValueError("Excel file support requires pandas. Please use CSV format instead.")
    
    def process_data(self, data, default_password, default_role):
        """Validate and process uploaded data"""
        valid_rows = []
        error_rows = []
        
        for i, row in enumerate(data, 1):
            errors = []
            processed_row = {}
            
            # Required fields validation
            required_fields = ['first_name', 'last_name', 'email']
            for field in required_fields:
                value = row.get(field, '').strip()
                if not value:
                    errors.append(f"Missing {field}")
                else:
                    processed_row[field] = value
            
            # Email validation
            email = row.get('email', '').strip()
            if email:
                if User.objects.filter(email=email).exists():
                    errors.append("Email already exists")
                else:
                    processed_row['email'] = email
            
            # Optional fields with defaults
            processed_row['password'] = row.get('password', '').strip() or default_password
            processed_row['role'] = row.get('role', '').strip() or default_role
            processed_row['year_of_study'] = row.get('year_of_study', '').strip()
            processed_row['province'] = row.get('province', '').strip()
            processed_row['college_type'] = row.get('college_type', '').strip()
            processed_row['college_name'] = row.get('college_name', '').strip()
            processed_row['phone_number'] = row.get('phone_number', '').strip()
            
            # Boolean fields
            processed_row['is_premium'] = str(row.get('is_premium', 'FALSE')).upper() == 'TRUE'
            processed_row['is_active'] = str(row.get('is_active', 'TRUE')).upper() == 'TRUE'
            
            # Role validation
            if processed_row['role'] not in ['student', 'faculty', 'admin']:
                errors.append("Invalid role (must be: student, faculty, or admin)")
            
            # Add to appropriate list
            if errors:
                error_rows.append({
                    'row_number': i,
                    'data': row,
                    'errors': errors
                })
            else:
                valid_rows.append(processed_row)
        
        return {
            'valid_rows': valid_rows,
            'error_rows': error_rows
        }
    
    def send_welcome_email(self, user, password):
        """Send welcome email to new user"""
        try:
            subject = 'Welcome to MedAce - Your Account Details'
            context = {
                'user': user,
                'password': password,
                'login_url': self.request.build_absolute_uri('/login/')
            }
            message = render_to_string('emails/welcome_user.txt', context)
            html_message = render_to_string('emails/welcome_user.html', context)
            
            send_mail(
                subject=subject,
                message=message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
        except Exception as e:
            # Log error but don't fail the user creation
            pass
