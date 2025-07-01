from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth import logout
from ..forms import StaffLoginForm


class AdminLoginView(LoginView):
    """Custom login view for admin/staff users"""
    form_class = StaffLoginForm
    template_name = 'staff/auth/login.html'
    success_url = reverse_lazy('staff:dashboard')
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Check if user is staff before allowing login"""
        user = form.get_user()
        if not user.is_staff:
            messages.error(self.request, 'You do not have permission to access the admin area.')
            return self.form_invalid(form)
        
        messages.success(self.request, f'Welcome back, {user.get_full_name() or user.username}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Add custom error message for invalid login"""
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)

    def get_success_url(self):
        """Redirect to dashboard after successful login"""
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('staff:dashboard')


class AdminLogoutView(View):
    """Custom logout view for admin/staff users"""
    
    def get(self, request, *args, **kwargs):
        """Handle logout on GET request"""
        if request.user.is_authenticated:
            if request.user.is_staff:
                messages.success(request, 'You have been successfully logged out from MedPrep Admin.')
            logout(request)
        else:
            messages.info(request, 'You were not logged in.')
        
        return redirect('staff:login')
    
    def post(self, request, *args, **kwargs):
        """Handle logout on POST request"""
        return self.get(request, *args, **kwargs)
