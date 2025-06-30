"""
Authentication views for MedPrep application
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy

from ..forms import UserRegistrationForm, UserProfileForm
from ..models import UserProfile


class CustomLoginView(LoginView):
    """Custom login view"""
    template_name = 'core/auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('core:dashboard')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """Custom logout view"""
    next_page = 'core:home'
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    """User registration view"""
    form_class = UserRegistrationForm
    template_name = 'core/auth/register.html'
    success_url = reverse_lazy('core:dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create user profile
        UserProfile.objects.create(
            user=self.object,
            year_of_study=form.cleaned_data['year_of_study'],
            college_name=form.cleaned_data['college_name'],
            phone_number=form.cleaned_data.get('phone_number', '')
        )
        
        # Log in the user
        login(self.request, self.object)
        messages.success(self.request, 'Registration successful! Welcome to MedPrep.')
        
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'core/auth/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = UserProfile.objects.create(
                user=user,
                year_of_study='1st',
                college_name='Not specified'
            )
        
        # Get user's quiz statistics
        from ..models import QuizSession
        quiz_sessions = QuizSession.objects.filter(user=user, status='completed')
        recent_quizzes = quiz_sessions.order_by('-completed_at')[:10]
        
        # Calculate subject-wise performance
        subject_performance = {}
        for quiz in quiz_sessions:
            subject = quiz.topic.subject
            if subject.name not in subject_performance:
                subject_performance[subject.name] = {
                    'total_score': 0,
                    'total_questions': 0,
                    'quiz_count': 0
                }
            
            subject_performance[subject.name]['total_score'] += quiz.score
            subject_performance[subject.name]['total_questions'] += quiz.total_questions
            subject_performance[subject.name]['quiz_count'] += 1
        
        # Calculate percentages
        for subject_data in subject_performance.values():
            if subject_data['total_questions'] > 0:
                subject_data['percentage'] = round(
                    (subject_data['total_score'] / subject_data['total_questions']) * 100, 2
                )
            else:
                subject_data['percentage'] = 0
        
        context.update({
            'profile': profile,
            'recent_quizzes': recent_quizzes,
            'subject_performance': subject_performance,
            'total_quizzes': quiz_sessions.count(),
        })
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user profile"""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'core/auth/profile_edit.html'
    success_url = reverse_lazy('core:profile')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'year_of_study': '1st',
                'college_name': 'Not specified'
            }
        )
        return profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
