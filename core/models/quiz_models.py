from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .academic_models import Question, Topic


class QuizSession(models.Model):
    """A quiz session/attempt by a user"""
    
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_sessions')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='quiz_sessions')
    questions = models.ManyToManyField(Question, related_name='quiz_sessions')
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_progress')
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    time_limit_minutes = models.IntegerField(default=30)  # Quiz time limit
    time_taken_seconds = models.IntegerField(default=0)  # Actual time taken
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Quiz Session'
        verbose_name_plural = 'Quiz Sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.topic.name} ({self.status})"
    
    def get_absolute_url(self):
        return reverse('core:quiz_result', kwargs={'pk': self.pk})
    
    @property
    def percentage_score(self):
        """Calculate percentage score"""
        if self.total_questions > 0:
            return round((self.score / self.total_questions) * 100, 2)
        return 0
    
    @property
    def time_taken_formatted(self):
        """Format time taken in MM:SS"""
        minutes = self.time_taken_seconds // 60
        seconds = self.time_taken_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def is_expired(self):
        """Check if quiz session has expired"""
        if self.status != 'in_progress':
            return False
        
        time_limit = timezone.timedelta(minutes=self.time_limit_minutes)
        return timezone.now() > (self.started_at + time_limit)
    
    def complete_quiz(self):
        """Mark quiz as completed and calculate final score"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.time_taken_seconds = (self.completed_at - self.started_at).total_seconds()
        
        # Calculate score
        correct_answers = self.user_answers.filter(is_correct=True).count()
        self.score = correct_answers
        self.total_questions = self.questions.count()
        
        self.save()
        
        # Update user profile stats
        profile = self.user.userprofile
        profile.total_quiz_score += self.score
        profile.total_quizzes_taken += 1
        profile.save()


class UserAnswer(models.Model):
    """User's answer to a specific question in a quiz session"""
    
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')
    selected_option = models.ForeignKey(
        'Option', 
        on_delete=models.CASCADE, 
        related_name='user_selections',
        null=True, 
        blank=True
    )
    is_correct = models.BooleanField(default=False)
    time_taken_seconds = models.IntegerField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Answer'
        verbose_name_plural = 'User Answers'
        unique_together = ['quiz_session', 'question']
        ordering = ['answered_at']
    
    def __str__(self):
        return f"{self.quiz_session.user.username} - Q{self.question.id} - {'✓' if self.is_correct else '✗'}"
    
    def save(self, *args, **kwargs):
        """Auto-determine if answer is correct"""
        if self.selected_option:
            from ..models.academic_models import Option
            self.is_correct = self.selected_option.is_correct
        super().save(*args, **kwargs)
