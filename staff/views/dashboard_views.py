from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from core.models import Question, PaymentProof, QuizSession
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta


class DashboardView(UserPassesTestMixin, TemplateView):
    """Admin dashboard with overview statistics"""
    template_name = 'staff/dashboard.html'
    
    def test_func(self):
        """Only allow staff users"""
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # User statistics
        total_users = User.objects.count()
        new_users_today = User.objects.filter(date_joined__date=today).count()
        new_users_week = User.objects.filter(date_joined__date__gte=week_ago).count()
        
        # Premium user statistics
        premium_users = User.objects.filter(userprofile__is_premium=True).count()
        premium_percentage = (premium_users / total_users * 100) if total_users > 0 else 0
        
        # Question statistics
        total_questions = Question.objects.filter(is_active=True).count()
        premium_questions = Question.objects.filter(is_active=True, is_premium=True).count()
        
        # Payment statistics
        pending_payments = PaymentProof.objects.filter(
            Q(status='pending') | Q(status='submitted')
        ).count()
        approved_payments = PaymentProof.objects.filter(status='approved').count()
        
        # Revenue statistics (mock data for now)
        total_revenue = approved_payments * 2000  # Assuming average 2000 PKR per payment
        monthly_revenue = PaymentProof.objects.filter(
            status='approved',
            submitted_at__date__gte=month_ago
        ).count() * 2000
        
        # Quiz statistics
        total_quiz_attempts = QuizSession.objects.count()
        quiz_attempts_today = QuizSession.objects.filter(started_at__date=today).count()
        
        # Recent activity
        recent_users = User.objects.order_by('-date_joined')[:5]
        recent_payments = PaymentProof.objects.order_by('-submitted_at')[:5]
        recent_quizzes = QuizSession.objects.order_by('-started_at')[:5]
        
        context.update({
            'total_users': total_users,
            'new_users_today': new_users_today,
            'new_users_week': new_users_week,
            'premium_users': premium_users,
            'premium_percentage': premium_percentage,
            'total_questions': total_questions,
            'premium_questions': premium_questions,
            'total_revenue': total_revenue,
            'monthly_revenue': monthly_revenue,
            'pending_payments': pending_payments,
            'approved_payments': approved_payments,
            'total_quiz_attempts': total_quiz_attempts,
            'quiz_attempts_today': quiz_attempts_today,
            'recent_users': recent_users,
            'recent_payments': recent_payments,
            'recent_quizzes': recent_quizzes,
        })
        
        return context
