from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class SubscriptionPlan(models.Model):
    """Available subscription plans"""
    
    PLAN_TYPES = [
        ('free', 'Free'),
        ('monthly', 'Monthly Premium'),
        ('quarterly', 'Quarterly Premium'),
        ('yearly', 'Yearly Premium'),
    ]
    
    name = models.CharField(max_length=50)
    plan_type = models.CharField(max_length=15, choices=PLAN_TYPES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()  # Duration in days
    features = models.TextField()  # JSON or text description of features
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - PKR {self.price}"
    
    def get_absolute_url(self):
        return reverse('core:subscription_detail', kwargs={'pk': self.pk})


class PaymentProof(models.Model):
    """Payment proof uploaded by users for manual verification"""
    
    PAYMENT_METHODS = [
        ('jazzcash', 'JazzCash'),
        ('easypaisa', 'EasyPaisa'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_proofs')
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_screenshot = models.ImageField(upload_to='uploads/payment_proofs/')
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_payments'
    )
    
    class Meta:
        verbose_name = 'Payment Proof'
        verbose_name_plural = 'Payment Proofs'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.subscription_plan.name} - {self.status}"
    
    def get_absolute_url(self):
        return reverse('core:payment_proof_detail', kwargs={'pk': self.pk})
    
    def approve_payment(self, admin_user):
        """Approve payment and activate subscription"""
        from django.utils import timezone
        from datetime import timedelta
        
        self.status = 'approved'
        self.reviewed_at = timezone.now()
        self.reviewed_by = admin_user
        self.save()
        
        # Activate user's premium subscription
        profile = self.user.userprofile
        profile.is_premium = True
        
        # Calculate expiry date
        if profile.premium_expires_at and profile.premium_expires_at > timezone.now():
            # Extend existing subscription
            profile.premium_expires_at += timedelta(days=self.subscription_plan.duration_days)
        else:
            # New subscription
            profile.premium_expires_at = timezone.now() + timedelta(days=self.subscription_plan.duration_days)
        
        profile.save()
    
    def reject_payment(self, admin_user, reason=""):
        """Reject payment with reason"""
        from django.utils import timezone
        
        self.status = 'rejected'
        self.reviewed_at = timezone.now()
        self.reviewed_by = admin_user
        self.admin_notes = reason
        self.save()
