"""
Scoring utilities for quiz results and performance analysis
"""
from django.db.models import Avg, Count, Q, Max, Min
from core.models import QuizSession, UserAnswer


def calculate_quiz_score(quiz_session):
    """
    Calculate the score for a quiz session
    """
    total_questions = quiz_session.user_answers.count()
    correct_answers = quiz_session.user_answers.filter(
        selected_option__is_correct=True
    ).count()
    
    if total_questions == 0:
        return 0
    
    percentage = (correct_answers / total_questions) * 100
    return round(percentage, 2)


def get_performance_analytics(user):
    """
    Get detailed performance analytics for a user
    """
    quiz_sessions = QuizSession.objects.filter(
        user=user, 
        completed_at__isnull=False
    )
    
    if not quiz_sessions.exists():
        return {
            'total_quizzes': 0,
            'average_score': 0,
            'best_score': 0,
            'worst_score': 0,
            'total_questions_attempted': 0,
            'correct_answers': 0,
            'accuracy_rate': 0
        }
    
    # Calculate aggregated statistics
    total_quizzes = quiz_sessions.count()
    average_score = quiz_sessions.aggregate(Avg('score'))['score__avg'] or 0
    best_score = quiz_sessions.aggregate(Max('score'))['score__max'] or 0
    worst_score = quiz_sessions.aggregate(Min('score'))['score__min'] or 0
    
    # Calculate question-level statistics
    user_answers = UserAnswer.objects.filter(quiz_session__in=quiz_sessions)
    total_questions = user_answers.count()
    correct_answers = user_answers.filter(selected_option__is_correct=True).count()
    accuracy_rate = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    return {
        'total_quizzes': total_quizzes,
        'average_score': round(average_score, 2),
        'best_score': best_score,
        'worst_score': worst_score,
        'total_questions_attempted': total_questions,
        'correct_answers': correct_answers,
        'accuracy_rate': round(accuracy_rate, 2)
    }


def get_difficulty_breakdown(user):
    """
    Get performance breakdown by difficulty level
    """
    user_answers = UserAnswer.objects.filter(
        quiz_session__user=user,
        quiz_session__completed_at__isnull=False
    )
    
    breakdown = {}
    for difficulty in ['EASY', 'MEDIUM', 'HARD']:
        answers = user_answers.filter(question__difficulty=difficulty)
        total = answers.count()
        correct = answers.filter(selected_option__is_correct=True).count()
        
        breakdown[difficulty] = {
            'total': total,
            'correct': correct,
            'accuracy': round((correct / total * 100) if total > 0 else 0, 2)
        }
    
    return breakdown


def get_subject_performance(user):
    """
    Get performance breakdown by subject
    """
    user_answers = UserAnswer.objects.filter(
        quiz_session__user=user,
        quiz_session__completed_at__isnull=False
    )
    
    subjects = {}
    for answer in user_answers:
        subject_name = answer.question.topic.subject.name
        if subject_name not in subjects:
            subjects[subject_name] = {'total': 0, 'correct': 0}
        
        subjects[subject_name]['total'] += 1
        if answer.selected_option and answer.selected_option.is_correct:
            subjects[subject_name]['correct'] += 1
    
    # Calculate accuracy for each subject
    for subject in subjects:
        total = subjects[subject]['total']
        correct = subjects[subject]['correct']
        subjects[subject]['accuracy'] = round((correct / total * 100) if total > 0 else 0, 2)
    
    return subjects
