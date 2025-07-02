from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models  # Added import for models to support tags relationship


class UserProfile(models.Model):
    """Extended user profile for MBBS students"""
    
    YEAR_CHOICES = [
        ('1st_year', '1st Year MBBS'),
        ('2nd_year', '2nd Year MBBS'),
        ('3rd_year', '3rd Year MBBS'),
        ('4th_year', '4th Year MBBS'),
        ('final_year', '5th Year MBBS (Final)'),
        ('graduate', 'Graduate'),
    ]
    
    PROVINCE_CHOICES = [
        ('Punjab', 'Punjab'),
        ('Sindh', 'Sindh'),
        ('Khyber Pakhtunkhwa', 'Khyber Pakhtunkhwa'),
        ('Balochistan', 'Balochistan'),
        ('Azad Jammu & Kashmir', 'Azad Jammu & Kashmir'),
    ]
    
    COLLEGE_TYPE_CHOICES = [
        ('Public', 'Public'),
        ('Private', 'Private'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    year_of_study = models.CharField(max_length=20, choices=YEAR_CHOICES, blank=True)
    province = models.CharField(max_length=100, choices=PROVINCE_CHOICES, blank=True)
    college_type = models.CharField(max_length=20, choices=COLLEGE_TYPE_CHOICES, blank=True)
    college_name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='uploads/profiles/', blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    premium_expires_at = models.DateTimeField(null=True, blank=True)
    total_quiz_score = models.IntegerField(default=0)
    total_quizzes_taken = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Tags/Groups relationship
    tags = models.ManyToManyField('Tag', blank=True, help_text="Tags/groups assigned to this user")
    
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
