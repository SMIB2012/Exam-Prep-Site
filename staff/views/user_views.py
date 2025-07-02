from django.views.generic import ListView, DetailView, UpdateView, CreateView, View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg, Max
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from core.models import UserProfile
from staff.forms import UserSearchForm, UserCreateForm, BulkUserUploadForm, UserEditForm
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
    
    def get(self, request, *args, **kwargs):
        """Override get to handle pagination errors gracefully"""
        try:
            return super().get(request, *args, **kwargs)
        except (EmptyPage, PageNotAnInteger):
            # Redirect to page 1 if invalid page requested
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            
            # Build query string without page parameter
            query_dict = request.GET.copy()
            if 'page' in query_dict:
                del query_dict['page']
            
            url = reverse('staff:user_list')
            if query_dict:
                url += f'?{query_dict.urlencode()}'
            
            # Add a message to inform user
            messages.warning(request, 'Invalid page number. Redirected to page 1.')
            return HttpResponseRedirect(url)
    
    def paginate_queryset(self, queryset, page_size):
        """Override to handle invalid page numbers gracefully"""
        paginator = self.get_paginator(
            queryset, page_size, orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty())
        
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        
        try:
            page_number = int(page)
        except ValueError:
            page_number = 1
            
        # Ensure page number is within valid range
        if page_number < 1:
            page_number = 1
        elif page_number > paginator.num_pages and paginator.num_pages > 0:
            page_number = paginator.num_pages
            
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except (EmptyPage, PageNotAnInteger):
            # Fallback to page 1
            page = paginator.page(1)
            return (paginator, page, page.object_list, page.has_other_pages())
    
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
    
    def post(self, request, *args, **kwargs):
        """Handle bulk actions on users"""
        action = request.POST.get('action')
        user_ids = request.POST.getlist('user_ids')
        
        if not action or not user_ids:
            messages.error(request, 'Please select an action and at least one user.')
            return redirect('staff:user_list')
        
        try:
            user_ids = [int(uid) for uid in user_ids]
            users = User.objects.filter(id__in=user_ids)
            count = users.count()
            
            if action == 'activate':
                users.update(is_active=True)
                messages.success(request, f'Successfully activated {count} user(s).')
                
            elif action == 'deactivate':
                users.update(is_active=False)
                messages.success(request, f'Successfully deactivated {count} user(s).')
                
            elif action == 'make_premium':
                from django.utils import timezone
                from datetime import timedelta
                
                # Update users to premium with 1 year expiration
                expiry_date = timezone.now() + timedelta(days=365)
                for user in users:
                    profile = user.userprofile
                    profile.is_premium = True
                    profile.premium_expires_at = expiry_date
                    profile.save()
                
                messages.success(request, f'Successfully made {count} user(s) premium.')
                
            elif action == 'remove_premium':
                for user in users:
                    profile = user.userprofile
                    profile.is_premium = False
                    profile.premium_expires_at = None
                    profile.save()
                
                messages.success(request, f'Successfully removed premium from {count} user(s).')
                
            elif action == 'reset_password':
                # Send password reset emails to selected users
                from django.contrib.auth.forms import PasswordResetForm
                from django.contrib.sites.shortcuts import get_current_site
                
                success_count = 0
                for user in users:
                    if user.email:
                        # Use Django's built-in password reset functionality
                        form = PasswordResetForm({'email': user.email})
                        if form.is_valid():
                            form.save(
                                request=request,
                                use_https=request.is_secure(),
                                email_template_name='registration/password_reset_email.html',
                                subject_template_name='registration/password_reset_subject.txt'
                            )
                            success_count += 1
                
                if success_count > 0:
                    messages.success(request, f'Password reset emails sent to {success_count} user(s).')
                else:
                    messages.warning(request, 'No password reset emails were sent. Users may not have valid email addresses.')
                
            elif action == 'export':
                # Implement CSV export
                return self.export_users(users)
                
            else:
                messages.error(request, f'Unknown action: {action}')
                
        except (ValueError, TypeError) as e:
            messages.error(request, f'Invalid user selection: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error performing bulk action: {str(e)}')
            
        return redirect('staff:user_list')
    
    def export_users(self, users):
        """Export selected users to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'ID', 'Username', 'Email', 'First Name', 'Last Name', 'Is Active', 'Is Staff',
            'Date Joined', 'Year of Study', 'Province', 'College Type', 'College Name',
            'Phone Number', 'Is Premium', 'Premium Expires At'
        ])
        
        # Write user data
        for user in users:
            profile = getattr(user, 'userprofile', None)
            writer.writerow([
                user.id,
                user.username,
                user.email,
                user.first_name,
                user.last_name,
                user.is_active,
                user.is_staff,
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                profile.year_of_study if profile else '',
                profile.province if profile else '',
                profile.college_type if profile else '',
                profile.college_name if profile else '',
                profile.phone_number if profile else '',
                profile.is_premium if profile else False,
                profile.premium_expires_at.strftime('%Y-%m-%d %H:%M:%S') if profile and profile.premium_expires_at else ''
            ])
        
        return response


class UserDetailView(StaffRequiredMixin, DetailView):
    """View user details with action handling"""
    model = User
    template_name = 'staff/users/user_detail.html'
    context_object_name = 'user'
    
    def post(self, request, *args, **kwargs):
        """Handle AJAX actions for user detail page"""
        user = self.get_object()
        action = request.POST.get('action')
        
        try:
            if action == 'toggle_status':
                status = request.POST.get('status') == 'true'
                user.is_active = status
                user.save()
                return JsonResponse({
                    'success': True,
                    'message': f'User {"activated" if status else "suspended"} successfully.',
                    'new_status': status
                })
                
            elif action == 'toggle_premium':
                is_premium = request.POST.get('is_premium') == 'true'
                profile = user.userprofile
                profile.is_premium = is_premium
                
                if is_premium:
                    # Set premium expiration to 1 year from now
                    from django.utils import timezone
                    from datetime import timedelta
                    profile.premium_expires_at = timezone.now() + timedelta(days=365)
                else:
                    profile.premium_expires_at = None
                    
                profile.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Premium status {"enabled" if is_premium else "removed"} successfully.',
                    'is_premium': is_premium
                })
                
            elif action == 'send_welcome_email':
                # Use the same welcome email logic from UserCreateView
                self._send_welcome_email(user)
                return JsonResponse({
                    'success': True,
                    'message': 'Welcome email sent successfully!'
                })
                
            elif action == 'reset_password':
                # Use Django's built-in password reset
                from django.contrib.auth.forms import PasswordResetForm
                if user.email:
                    form = PasswordResetForm({'email': user.email})
                    if form.is_valid():
                        form.save(
                            request=request,
                            use_https=request.is_secure(),
                            email_template_name='registration/password_reset_email.html',
                            subject_template_name='registration/password_reset_subject.txt'
                        )
                        return JsonResponse({
                            'success': True,
                            'message': 'Password reset email sent successfully!'
                        })
                    else:
                        return JsonResponse({
                            'success': False,
                            'message': 'Failed to send password reset email.'
                        })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'User has no email address.'
                    })
                    
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Unknown action.'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    def _send_welcome_email(self, user):
        """Send welcome email to user"""
        try:
            subject = f'Welcome to MedPrep, {user.first_name}!'
            message = f'''
            Dear {user.first_name},

            Welcome to MedPrep - Your Medical Education Platform!

            Your account has been created successfully. You can now:
            - Take practice quizzes
            - Access study materials
            - Track your progress
            - Compete with fellow medical students

            Get started by taking your first quiz or exploring our study resources.

            Best of luck with your medical studies!

            The MedPrep Team
            '''
            
            html_message = render_to_string('emails/welcome_user.html', {
                'user': user,
                'site_name': 'MedPrep'
            })
            
            send_mail(
                subject=subject,
                message=message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
        except Exception as e:
            # Log error but don't fail the action
            pass
    
    def get_context_data(self, **kwargs):
        """Add additional context data"""
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        # Add today's date for template comparisons
        from django.utils import timezone
        context['today'] = timezone.now()
        
        # Add quiz statistics
        try:
            from core.models import QuizSession
            quiz_attempts = QuizSession.objects.filter(user=user, status='completed').order_by('-completed_at')
            
            if quiz_attempts.exists():
                from django.db.models import Avg, Max
                stats = quiz_attempts.aggregate(
                    avg_score=Avg('score'),
                    max_score=Max('score')
                )
                context['quiz_stats'] = {
                    'total_attempts': quiz_attempts.count(),
                    'avg_score': stats['avg_score'] or 0,
                    'max_score': stats['max_score'] or 0,
                    'latest_attempt': quiz_attempts.first()
                }
            else:
                context['quiz_stats'] = {
                    'total_attempts': 0,
                    'avg_score': 0,
                    'max_score': 0,
                    'latest_attempt': None
                }
            
            # Add recent quiz attempts (last 5)
            context['recent_attempts'] = quiz_attempts[:5]
            
        except ImportError:
            # Handle case where QuizSession model doesn't exist yet
            context['quiz_stats'] = {
                'total_attempts': 0,
                'avg_score': 0,
                'max_score': 0,
                'latest_attempt': None
            }
            context['recent_attempts'] = []
        
        return context


class UserEditView(StaffRequiredMixin, UpdateView):
    """Edit user details"""
    model = User
    form_class = UserEditForm
    template_name = 'staff/users/user_edit.html'
    
    def get_context_data(self, **kwargs):
        """Add additional context for user edit page"""
        context = super().get_context_data(**kwargs)
        user = self.object
        
        # Add quiz statistics
        from core.models import QuizSession
        attempts = QuizSession.objects.filter(user=user, status='completed')
        if attempts.exists():
            total_attempts = attempts.count()
            avg_score = attempts.aggregate(avg_score=Avg('score'))['avg_score'] or 0
            max_score = attempts.aggregate(max_score=Max('score'))['max_score'] or 0
            latest_attempt = attempts.order_by('-completed_at').first()
            
            context['quiz_stats'] = {
                'total_attempts': total_attempts,
                'avg_score': avg_score,
                'max_score': max_score,
                'latest_attempt': latest_attempt,
            }
        else:
            context['quiz_stats'] = {
                'total_attempts': 0,
                'avg_score': 0,
                'max_score': 0,
                'latest_attempt': None,
            }
        
        return context
    
    def get_success_url(self):
        """Redirect to user detail page after successful edit"""
        messages.success(self.request, f'User "{self.object.get_full_name()}" has been updated successfully!')
        return reverse_lazy('staff:user_detail', kwargs={'pk': self.object.pk})

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


class UserExportView(StaffRequiredMixin, View):
    """Export a single user's data to CSV"""
    
    def get(self, request, pk):
        """Export user data as CSV download"""
        try:
            user = User.objects.select_related('userprofile').get(pk=pk)
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('staff:user_list')
        
        # Create the CSV response
        response = HttpResponse(content_type='text/csv')
        filename = f"user_{user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'Field', 'Value'
        ])
        
        # Write user basic info
        writer.writerow(['User ID', user.id])
        writer.writerow(['Username', user.username])
        writer.writerow(['Email', user.email])
        writer.writerow(['First Name', user.first_name])
        writer.writerow(['Last Name', user.last_name])
        writer.writerow(['Is Active', user.is_active])
        writer.writerow(['Is Staff', user.is_staff])
        writer.writerow(['Is Superuser', user.is_superuser])
        writer.writerow(['Date Joined', user.date_joined.strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow(['Last Login', user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'])
        
        # Write profile info if exists
        profile = getattr(user, 'userprofile', None)
        if profile:
            writer.writerow(['--- Profile Information ---', ''])
            writer.writerow(['Year of Study', profile.year_of_study])
            writer.writerow(['Province', profile.province])
            writer.writerow(['College Type', profile.college_type])
            writer.writerow(['College Name', profile.college_name])
            writer.writerow(['Phone Number', profile.phone_number])
            writer.writerow(['Is Premium', profile.is_premium])
            writer.writerow(['Premium Expires At', profile.premium_expires_at.strftime('%Y-%m-%d %H:%M:%S') if profile.premium_expires_at else 'N/A'])
            writer.writerow(['Profile Created', profile.created_at.strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow(['Profile Updated', profile.updated_at.strftime('%Y-%m-%d %H:%M:%S')])
        
        # Add quiz statistics if available
        try:
            from core.models import QuizSession
            quiz_sessions = QuizSession.objects.filter(user=user)
            if quiz_sessions.exists():
                writer.writerow(['--- Quiz Statistics ---', ''])
                writer.writerow(['Total Quiz Sessions', quiz_sessions.count()])
                writer.writerow(['Completed Sessions', quiz_sessions.filter(completed=True).count()])
                
                completed_sessions = quiz_sessions.filter(completed=True, score__isnull=False)
                if completed_sessions.exists():
                    avg_score = completed_sessions.aggregate(avg_score=Avg('score'))['avg_score']
                    best_score = completed_sessions.aggregate(best_score=Max('score'))['best_score']
                    writer.writerow(['Average Score', f"{avg_score:.2f}%" if avg_score else 'N/A'])
                    writer.writerow(['Best Score', f"{best_score:.2f}%" if best_score else 'N/A'])
                    
        except ImportError:
            # QuizSession model might not exist
            pass
        
        return response
