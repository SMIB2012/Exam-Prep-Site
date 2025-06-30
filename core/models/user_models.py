from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class UserProfile(models.Model):
    """Extended user profile for MBBS students"""
    
    YEAR_CHOICES = [
        ('1st', '1st Year'),
        ('2nd', '2nd Year'),
        ('3rd', '3rd Year'),
        ('4th', '4th Year'),
        ('5th', '5th Year (Final)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    year_of_study = models.CharField(max_length=3, choices=YEAR_CHOICES)
    college_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='uploads/profiles/', blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    premium_expires_at = models.DateTimeField(null=True, blank=True)
    total_quiz_score = models.IntegerField(default=0)
    total_quizzes_taken = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.year_of_study})"
    
    def get_absolute_url(self):
        return reverse('core:profile', kwargs={'pk': self.pk})
    
    @property
    def average_score(self):
        """Calculate average quiz score"""
        if self.total_quizzes_taken > 0:
            return round(self.total_quiz_score / self.total_quizzes_taken, 2)
        return 0
    
    @property
    def is_premium_active(self):
        """Check if premium subscription is active"""
        if not self.is_premium or not self.premium_expires_at:
            return False
        from django.utils import timezone
        return timezone.now() < self.premium_expires_at
