"""
Payment verification utilities for subscription management
"""
import os
from datetime import datetime, timedelta
from django.core.files.storage import default_storage
from django.conf import settings
from core.models import PaymentProof, UserProfile


def verify_payment_proof(payment_proof):
    """
    Verify payment proof submission (basic validation)
    """
    if not payment_proof.proof_image:
        return False, "No payment proof image provided"
    
    # Check file size (max 5MB)
    if payment_proof.proof_image.size > 5 * 1024 * 1024:
        return False, "File size too large (max 5MB)"
    
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    file_ext = os.path.splitext(payment_proof.proof_image.name)[1].lower()
    if file_ext not in allowed_extensions:
        return False, "Invalid file format. Only JPG, PNG, and PDF files are allowed"
    
    return True, "Payment proof submitted successfully"


def process_payment_verification(payment_proof, admin_user):
    """
    Process payment verification by admin
    """
    if payment_proof.status == 'APPROVED':
        # Activate premium subscription
        user_profile = payment_proof.user.userprofile
        subscription_plan = payment_proof.subscription_plan
        
        # Calculate expiry date based on plan duration
        if subscription_plan.duration_months:
            expiry_date = datetime.now() + timedelta(days=subscription_plan.duration_months * 30)
            user_profile.premium_expires_at = expiry_date
            user_profile.subscription_plan = subscription_plan
            user_profile.save()
            
            return True, f"Premium subscription activated until {expiry_date.strftime('%Y-%m-%d')}"
    
    elif payment_proof.status == 'REJECTED':
        return False, "Payment proof rejected. Please contact support or resubmit with correct information."
    
    return None, "Payment verification pending"


def check_subscription_status(user):
    """
    Check if user's subscription is active
    """
    try:
        profile = user.userprofile
        if profile.is_premium_active():
            days_remaining = (profile.premium_expires_at - datetime.now()).days
            return {
                'is_active': True,
                'expires_at': profile.premium_expires_at,
                'days_remaining': max(0, days_remaining),
                'plan': profile.subscription_plan
            }
        else:
            return {
                'is_active': False,
                'expires_at': None,
                'days_remaining': 0,
                'plan': None
            }
    except UserProfile.DoesNotExist:
        return {
            'is_active': False,
            'expires_at': None,
            'days_remaining': 0,
            'plan': None
        }


def get_pending_payments():
    """
    Get all pending payment proofs for admin review
    """
    return PaymentProof.objects.filter(
        status='PENDING'
    ).order_by('-created_at')


def auto_expire_subscriptions():
    """
    Utility function to automatically expire subscriptions
    Can be run as a cron job or management command
    """
    from datetime import datetime
    
    expired_profiles = UserProfile.objects.filter(
        premium_expires_at__lt=datetime.now(),
        subscription_plan__isnull=False
    )
    
    count = 0
    for profile in expired_profiles:
        profile.subscription_plan = None
        profile.premium_expires_at = None
        profile.save()
        count += 1
    
    return count  # Number of subscriptions expired
