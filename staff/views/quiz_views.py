from django.views.generic import ListView
from core.models import QuizSession
from .user_views import StaffRequiredMixin


class QuizAttemptListView(StaffRequiredMixin, ListView):
    """List all quiz attempts"""
    model = QuizSession
    template_name = 'staff/quizzes/quiz_list.html'
    context_object_name = 'quiz_attempts'
    paginate_by = 25


class LeaderboardView(StaffRequiredMixin, ListView):
    """View leaderboard"""
    model = QuizSession
    template_name = 'staff/quizzes/leaderboard.html'
    context_object_name = 'top_performers'
    
    def get_queryset(self):
        # This will be implemented with proper leaderboard logic
        return QuizSession.objects.filter(completed_at__isnull=False).order_by('-score')[:50]
