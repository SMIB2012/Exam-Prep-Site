"""
Django signals for MedPrep application
Handles automatic events like sending emails, updating statistics, etc.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from core.models import UserProfile, QuizSession, PaymentProof


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create UserProfile when a new User is created
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save UserProfile when User is saved
    """
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=QuizSession)
def quiz_completed_notification(sender, instance, created, **kwargs):
    """
    Send notification when a quiz is completed
    """
    if not created and instance.completed_at and instance.score is not None:
        # Quiz was just completed
        user = instance.user
        
        # Send congratulatory email for high scores
        if instance.score >= 80:
            try:
                send_mail(
                    subject='Congratulations on Your Excellent Score!',
                    message=f'''
                    Dear {user.first_name or user.username},
                    
                    Congratulations! You scored {instance.score}% on the {instance.topic.name} quiz.
                    This is an excellent performance!
                    
                    Keep up the great work in your MBBS preparation.
                    
                    Best regards,
                    MedPrep Team
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass  # Don't fail if email sending fails
        
        # Update user statistics
        update_user_statistics(user)


@receiver(post_save, sender=PaymentProof)
def payment_proof_notification(sender, instance, created, **kwargs):
    """
    Send notifications when payment proof is uploaded or verified
    """
    if created:
        # Payment proof uploaded - notify admin
        try:
            send_mail(
                subject='New Payment Proof Uploaded',
                message=f'''
                A new payment proof has been uploaded by {instance.user.username}.
                
                Plan: {instance.subscription_plan.name}
                Amount: ${instance.subscription_plan.price}
                
                Please review in the admin panel.
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else [],
                fail_silently=True,
            )
        except Exception:
            pass
    
    elif instance.status == 'APPROVED':
        # Payment approved - notify user
        try:
            send_mail(
                subject='Payment Approved - Premium Activated!',
                message=f'''
                Dear {instance.user.first_name or instance.user.username},
                
                Great news! Your payment has been approved and your premium subscription is now active.
                
                Plan: {instance.subscription_plan.name}
                Duration: {instance.subscription_plan.duration_months} months
                
                You now have access to all premium features including:
                - Unlimited practice questions
                - Detailed performance analytics
                - Video lectures
                - Priority support
                
                Thank you for choosing MedPrep!
                
                Best regards,
                MedPrep Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.user.email],
                fail_silently=True,
            )
        except Exception:
            pass
    
    elif instance.status == 'REJECTED':
        # Payment rejected - notify user
        try:
            send_mail(
                subject='Payment Verification Issue',
                message=f'''
                Dear {instance.user.first_name or instance.user.username},
                
                We were unable to verify your payment proof for the {instance.subscription_plan.name} plan.
                
                Reason: {instance.admin_notes or 'Please contact support for details'}
                
                Please check your payment details and resubmit, or contact our support team for assistance.
                
                Best regards,
                MedPrep Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.user.email],
                fail_silently=True,
            )
        except Exception:
            pass


def update_user_statistics(user):
    """
    Update user's cached statistics
    """
    try:
        profile = user.userprofile
        completed_quizzes = QuizSession.objects.filter(
            user=user,
            completed_at__isnull=False
        )
        
        if completed_quizzes.exists():
            from django.db.models import Avg
            avg_score = completed_quizzes.aggregate(Avg('score'))['score__avg']
            profile.average_score = round(avg_score or 0, 2)
            profile.total_quizzes = completed_quizzes.count()
            profile.save()
    except Exception:
        pass  # Don't fail if statistics update fails


# Signal for welcoming new users
@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """
    Send welcome email to new users
    """
    if created and instance.email:
        try:
            send_mail(
                subject='Welcome to MedPrep!',
                message=f'''
                Dear {instance.first_name or instance.username},
                
                Welcome to MedPrep - your comprehensive MBBS exam preparation platform!
                
                You can now:
                ✓ Access thousands of practice questions
                ✓ Track your performance and progress
                ✓ Compete with fellow medical students
                ✓ Access study resources and materials
                
                Get started by taking your first quiz or exploring our study materials.
                
                If you have any questions, feel free to contact our support team.
                
                Best of luck with your studies!
                
                The MedPrep Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=True,
            )
        except Exception:
            pass  # Don't fail registration if email fails
