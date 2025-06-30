"""
Ranking utilities for leaderboard functionality
"""
from django.db.models import Avg, Count, Q
from django.contrib.auth.models import User
from core.models import QuizSession, UserProfile


def get_global_leaderboard(limit=50):
    """
    Get global leaderboard rankings based on average scores
    """
    users_with_scores = User.objects.filter(
        quiz_sessions__completed_at__isnull=False
    ).annotate(
        total_quizzes=Count('quiz_sessions'),
        average_score=Avg('quiz_sessions__score')
    ).filter(
        total_quizzes__gte=3  # Only include users with at least 3 completed quizzes
    ).order_by(
        '-average_score', '-total_quizzes'
    )[:limit]
    
    leaderboard = []
    for rank, user in enumerate(users_with_scores, 1):
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = None
            
        leaderboard.append({
            'rank': rank,
            'user': user,
            'profile': profile,
            'average_score': round(user.average_score, 2),
            'total_quizzes': user.total_quizzes
        })
    
    return leaderboard


def get_weekly_leaderboard(limit=50):
    """
    Get weekly leaderboard rankings
    """
    from datetime import datetime, timedelta
    
    week_ago = datetime.now() - timedelta(days=7)
    
    users_with_scores = User.objects.filter(
        quiz_sessions__completed_at__gte=week_ago,
        quiz_sessions__completed_at__isnull=False
    ).annotate(
        weekly_quizzes=Count('quiz_sessions'),
        weekly_average=Avg('quiz_sessions__score')
    ).filter(
        weekly_quizzes__gte=1
    ).order_by(
        '-weekly_average', '-weekly_quizzes'
    )[:limit]
    
    leaderboard = []
    for rank, user in enumerate(users_with_scores, 1):
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = None
            
        leaderboard.append({
            'rank': rank,
            'user': user,
            'profile': profile,
            'weekly_average': round(user.weekly_average, 2),
            'weekly_quizzes': user.weekly_quizzes
        })
    
    return leaderboard


def get_user_rank(user):
    """
    Get a specific user's rank in the global leaderboard
    """
    # Get all users with their average scores
    users_with_scores = User.objects.filter(
        quiz_sessions__completed_at__isnull=False
    ).annotate(
        total_quizzes=Count('quiz_sessions'),
        average_score=Avg('quiz_sessions__score')
    ).filter(
        total_quizzes__gte=3
    ).order_by(
        '-average_score', '-total_quizzes'
    )
    
    # Find the user's position
    for rank, ranked_user in enumerate(users_with_scores, 1):
        if ranked_user.id == user.id:
            return rank
    
    return None  # User not ranked (less than 3 quizzes)


def get_subject_leaderboard(subject, limit=20):
    """
    Get leaderboard for a specific subject
    """
    users_with_scores = User.objects.filter(
        quiz_sessions__topic__subject=subject,
        quiz_sessions__completed_at__isnull=False
    ).annotate(
        subject_quizzes=Count('quiz_sessions'),
        subject_average=Avg('quiz_sessions__score')
    ).filter(
        subject_quizzes__gte=2
    ).order_by(
        '-subject_average', '-subject_quizzes'
    )[:limit]
    
    leaderboard = []
    for rank, user in enumerate(users_with_scores, 1):
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = None
            
        leaderboard.append({
            'rank': rank,
            'user': user,
            'profile': profile,
            'subject_average': round(user.subject_average, 2),
            'subject_quizzes': user.subject_quizzes
        })
    
    return leaderboard
