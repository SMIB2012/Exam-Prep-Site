from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from core.models import UserProfile
from staff.forms import UserSearchForm, UserCreateForm


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
        
        # Create profile
        profile_data = {
            'year_of_study': form.cleaned_data.get('year_of_study', ''),
            'province': form.cleaned_data.get('province', ''),
            'college_type': form.cleaned_data.get('college_type', ''),
            'college_name': form.cleaned_data.get('college_name', ''),
            'phone_number': form.cleaned_data.get('phone_number', ''),
            'is_premium': form.cleaned_data.get('is_premium', False),
        }
        
        profile = UserProfile.objects.create(user=user, **profile_data)
        
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
