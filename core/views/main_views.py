"""
Main views for MedPrep application
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg, Q
from django.contrib.auth.models import User

from ..models import (
    Subject, Topic, Question, UserProfile, 
    QuizSession, UserAnswer
)


class HomeView(TemplateView):
    """Landing page"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_subjects': Subject.objects.filter(is_active=True).count(),
            'total_questions': Question.objects.filter(is_active=True).count(),
            'total_users': UserProfile.objects.count(),
            'featured_subjects': Subject.objects.filter(is_active=True)[:6],
        })
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """User dashboard"""
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's quiz statistics
        quiz_sessions = QuizSession.objects.filter(user=user, status='completed')
        recent_quizzes = quiz_sessions.order_by('-completed_at')[:5]
        
        # Calculate statistics
        total_quizzes = quiz_sessions.count()
        avg_score = quiz_sessions.aggregate(Avg('score'))['score__avg'] or 0
        
        # Get subjects progress
        subjects_progress = []
        for subject in Subject.objects.filter(is_active=True):
            subject_quizzes = quiz_sessions.filter(topic__subject=subject)
            if subject_quizzes.exists():
                avg_subject_score = subject_quizzes.aggregate(Avg('score'))['score__avg']
                subjects_progress.append({
                    'subject': subject,
                    'avg_score': avg_subject_score,
                    'quiz_count': subject_quizzes.count()
                })
        
        context.update({
            'recent_quizzes': recent_quizzes,
            'total_quizzes': total_quizzes,
            'avg_score': round(avg_score, 2),
            'subjects_progress': subjects_progress,
            'available_subjects': Subject.objects.filter(is_active=True),
        })
        return context


class LeaderboardView(TemplateView):
    """Global leaderboard"""
    template_name = 'core/leaderboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get top users by total quiz score
        top_users = UserProfile.objects.filter(
            total_quizzes_taken__gt=0
        ).order_by('-total_quiz_score')[:50]
        
        # Weekly leaderboard (last 7 days)
        from django.utils import timezone
        from datetime import timedelta
        
        week_ago = timezone.now() - timedelta(days=7)
        weekly_stats = []
        
        for profile in UserProfile.objects.filter(total_quizzes_taken__gt=0):
            recent_quizzes = QuizSession.objects.filter(
                user=profile.user,
                status='completed',
                completed_at__gte=week_ago
            )
            if recent_quizzes.exists():
                weekly_score = sum(quiz.score for quiz in recent_quizzes)
                weekly_stats.append({
                    'user': profile,
                    'weekly_score': weekly_score,
                    'weekly_quizzes': recent_quizzes.count()
                })
        
        weekly_leaders = sorted(weekly_stats, key=lambda x: x['weekly_score'], reverse=True)[:20]
        
        context.update({
            'top_users': top_users,
            'weekly_leaders': weekly_leaders,
        })
        return context


class QuestionBankView(TemplateView):
    """Question bank with filters"""
    template_name = 'core/question_bank.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        subject_id = self.request.GET.get('subject')
        topic_id = self.request.GET.get('topic')
        difficulty = self.request.GET.get('difficulty')
        year = self.request.GET.get('year')
        
        # Build queryset
        subjects = Subject.objects.filter(is_active=True).annotate(
            topic_count=Count('topics', filter=Q(topics__is_active=True)),
            question_count=Count('topics__questions', filter=Q(topics__questions__is_active=True))
        )
        
        # Filter subjects if needed
        if year and year != 'all':
            subjects = subjects.filter(Q(year_applicable=year) | Q(year_applicable='all'))
        
        # Get topics for selected subject
        topics = []
        if subject_id:
            selected_subject = get_object_or_404(Subject, pk=subject_id, is_active=True)
            topics = selected_subject.topics.filter(is_active=True).annotate(
                question_count=Count('questions', filter=Q(questions__is_active=True))
            )
        
        context.update({
            'subjects': subjects,
            'topics': topics,
            'selected_subject_id': int(subject_id) if subject_id else None,
            'selected_topic_id': int(topic_id) if topic_id else None,
            'selected_difficulty': difficulty,
            'selected_year': year,
            'year_choices': Subject._meta.get_field('year_applicable').choices,
            'difficulty_choices': Question._meta.get_field('difficulty').choices,
        })
        return context


class SubjectDetailView(DetailView):
    """Subject detail page"""
    model = Subject
    template_name = 'core/subject_detail.html'
    context_object_name = 'subject'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject = self.get_object()
        
        topics = subject.topics.filter(is_active=True).annotate(
            question_count=Count('questions', filter=Q(questions__is_active=True)),
            note_count=Count('notes', filter=Q(notes__is_active=True)),
            video_count=Count('videos', filter=Q(videos__is_active=True)),
            flashcard_count=Count('flashcards', filter=Q(flashcards__is_active=True))
        )
        
        context.update({
            'topics': topics,
            'total_questions': sum(topic.question_count for topic in topics),
        })
        return context


class TopicDetailView(DetailView):
    """Topic detail page"""
    model = Topic
    template_name = 'core/topic_detail.html'
    context_object_name = 'topic'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.get_object()
        
        # Get user's progress for this topic if logged in
        user_progress = None
        if self.request.user.is_authenticated:
            from ..models import UserProgress
            user_progress, _ = UserProgress.objects.get_or_create(
                user=self.request.user,
                topic=topic
            )
        
        # Get resources
        questions = topic.questions.filter(is_active=True)
        notes = topic.notes.filter(is_active=True)
        videos = topic.videos.filter(is_active=True)
        flashcards = topic.flashcards.filter(is_active=True)
        
        # Filter premium content for non-premium users
        if not (self.request.user.is_authenticated and 
                hasattr(self.request.user, 'userprofile') and 
                self.request.user.userprofile.is_premium_active):
            questions = questions.filter(is_premium=False)
            notes = notes.filter(is_premium=False)
            videos = videos.filter(is_premium=False)
            flashcards = flashcards.filter(is_premium=False)
        
        context.update({
            'questions': questions,
            'notes': notes,
            'videos': videos,
            'flashcards': flashcards,
            'user_progress': user_progress,
        })
        return context
