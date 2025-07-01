from django.db import models
from django.urls import reverse


class Subject(models.Model):
    """Medical subjects for MBBS curriculum"""
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    year_applicable = models.CharField(
        max_length=3, 
        choices=[
            ('1st', '1st Year'),
            ('2nd', '2nd Year'),
            ('3rd', '3rd Year'),
            ('4th', '4th Year'),
            ('5th', '5th Year (Final)'),
            ('all', 'All Years'),
        ],
        default='all'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        ordering = ['year_applicable', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_absolute_url(self):
        return reverse('core:subject_detail', kwargs={'pk': self.pk})


class Topic(models.Model):
    """Topics within each subject"""
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
        ordering = ['subject', 'order', 'name']
        unique_together = ['subject', 'name']
    
    def __str__(self):
        return f"{self.subject.name} - {self.name}"
    
    def get_absolute_url(self):
        return reverse('core:topic_detail', kwargs={'pk': self.pk})


class Question(models.Model):
    """MCQ Questions for practice"""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    explanation = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    is_premium = models.BooleanField(default=False)  # Premium questions for paid users
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Many-to-many relationship with tags
    tags = models.ManyToManyField('Tag', blank=True, related_name='questions')
    
    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.topic.name} - {self.question_text[:50]}..."
    
    def get_absolute_url(self):
        return reverse('core:question_detail', kwargs={'pk': self.pk})
    
    @property
    def correct_option(self):
        """Get the correct option for this question"""
        return self.options.filter(is_correct=True).first()


class Option(models.Model):
    """Multiple choice options for questions"""
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Option'
        verbose_name_plural = 'Options'
        ordering = ['question', 'order']
    
    def __str__(self):
        return f"{self.question.question_text[:30]}... - {self.option_text[:50]}..."
