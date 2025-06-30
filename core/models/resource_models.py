from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from .academic_models import Subject, Topic


class Note(models.Model):
    """Study notes for different topics"""
    
    title = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()  # Rich text content
    pdf_file = models.FileField(upload_to='uploads/resources/notes/', blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.topic.name} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('core:note_detail', kwargs={'pk': self.pk})


class Flashcard(models.Model):
    """Flashcards for quick revision"""
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='flashcards')
    front_text = models.CharField(max_length=500)  # Question/Term
    back_text = models.TextField()  # Answer/Definition
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_flashcards')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Flashcard'
        verbose_name_plural = 'Flashcards'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.topic.name} - {self.front_text[:50]}..."
    
    def get_absolute_url(self):
        return reverse('core:flashcard_detail', kwargs={'pk': self.pk})


class VideoResource(models.Model):
    """Video tutorials and lectures"""
    
    title = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='videos')
    description = models.TextField(blank=True)
    video_url = models.URLField()  # YouTube, Vimeo, or other video platform URL
    duration_minutes = models.PositiveIntegerField(default=0)
    thumbnail = models.ImageField(upload_to='uploads/resources/thumbnails/', blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_videos')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Video Resource'
        verbose_name_plural = 'Video Resources'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.topic.name} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('core:video_detail', kwargs={'pk': self.pk})
    
    @property
    def duration_formatted(self):
        """Format duration as HH:MM"""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}"
        return f"{minutes} min"


class UserProgress(models.Model):
    """Track user progress through different topics and resources"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='user_progress')
    
    # Progress tracking
    notes_read = models.ManyToManyField(Note, blank=True)
    flashcards_reviewed = models.ManyToManyField(Flashcard, blank=True)
    videos_watched = models.ManyToManyField(VideoResource, blank=True)
    
    # Statistics
    total_quiz_attempts = models.IntegerField(default=0)
    best_quiz_score = models.IntegerField(default=0)
    total_time_spent_minutes = models.IntegerField(default=0)
    
    last_accessed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress'
        unique_together = ['user', 'topic']
        ordering = ['-last_accessed']
    
    def __str__(self):
        return f"{self.user.username} - {self.topic.name}"
    
    @property
    def completion_percentage(self):
        """Calculate completion percentage for this topic"""
        total_resources = (
            self.topic.notes.filter(is_active=True).count() +
            self.topic.flashcards.filter(is_active=True).count() +
            self.topic.videos.filter(is_active=True).count()
        )
        
        if total_resources == 0:
            return 0
        
        completed_resources = (
            self.notes_read.count() +
            self.flashcards_reviewed.count() +
            self.videos_watched.count()
        )
        
        return round((completed_resources / total_resources) * 100, 2)
