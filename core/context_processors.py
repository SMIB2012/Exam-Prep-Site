"""
Context processors for MedPrep application
"""
from django.conf import settings


def site_context(request):
    """
    Add site-wide context variables
    """
    context = {
        'site_name': 'MedPrep',
        'site_description': 'MBBS Exam Preparation Platform',
        'current_year': 2025,
    }
    
    # Add user profile if authenticated
    if request.user.is_authenticated:
        try:
            context['user_profile'] = request.user.userprofile
        except:
            context['user_profile'] = None
    
    return context
