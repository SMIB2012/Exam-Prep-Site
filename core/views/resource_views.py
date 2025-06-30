"""
Resource-related views for MedPrep application
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse

from ..models import (
    Subject, Topic, Note, Flashcard, VideoResource, UserProgress
)


class ResourcesView(TemplateView):
    """Main resources page"""
    template_name = 'core/resources/resources.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get resource counts by type
        notes_count = Note.objects.filter(is_active=True).count()
        flashcards_count = Flashcard.objects.filter(is_active=True).count()
        videos_count = VideoResource.objects.filter(is_active=True).count()
        
        # Get featured resources
        featured_notes = Note.objects.filter(is_active=True)[:6]
        featured_videos = VideoResource.objects.filter(is_active=True)[:6]
        
        # Get subjects for filtering
        subjects = Subject.objects.filter(is_active=True)
        
        context.update({
            'notes_count': notes_count,
            'flashcards_count': flashcards_count,
            'videos_count': videos_count,
            'featured_notes': featured_notes,
            'featured_videos': featured_videos,
            'subjects': subjects,
        })
        return context


class NotesListView(ListView):
    """List all study notes"""
    model = Note
    template_name = 'core/resources/notes_list.html'
    context_object_name = 'notes'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Note.objects.filter(is_active=True).select_related('topic__subject')
        
        # Filter by subject
        subject_id = self.request.GET.get('subject')
        if subject_id:
            queryset = queryset.filter(topic__subject_id=subject_id)
        
        # Filter by topic
        topic_id = self.request.GET.get('topic')
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(topic__name__icontains=search)
            )
        
        # Filter premium content for non-premium users
        if not (self.request.user.is_authenticated and 
                hasattr(self.request.user, 'userprofile') and 
                self.request.user.userprofile.is_premium_active):
            queryset = queryset.filter(is_premium=False)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        context.update({
            'subjects': Subject.objects.filter(is_active=True),
            'selected_subject_id': int(self.request.GET.get('subject', 0)) or None,
            'selected_topic_id': int(self.request.GET.get('topic', 0)) or None,
            'search_query': self.request.GET.get('search', ''),
        })
        
        # Get topics for selected subject
        if context['selected_subject_id']:
            context['topics'] = Topic.objects.filter(
                subject_id=context['selected_subject_id'],
                is_active=True
            )
        
        return context


class NoteDetailView(DetailView):
    """Study note detail view"""
    model = Note
    template_name = 'core/resources/note_detail.html'
    context_object_name = 'note'
    
    def get_queryset(self):
        queryset = Note.objects.filter(is_active=True).select_related('topic__subject', 'created_by')
        
        # Filter premium content for non-premium users
        if not (self.request.user.is_authenticated and 
                hasattr(self.request.user, 'userprofile') and 
                self.request.user.userprofile.is_premium_active):
            queryset = queryset.filter(is_premium=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = self.get_object()
        
        # Track user progress if authenticated
        if self.request.user.is_authenticated:
            progress, created = UserProgress.objects.get_or_create(
                user=self.request.user,
                topic=note.topic
            )
            progress.notes_read.add(note)
            progress.save()
        
        # Get related notes
        related_notes = Note.objects.filter(
            topic=note.topic,
            is_active=True
        ).exclude(pk=note.pk)[:5]
        
        context.update({
            'related_notes': related_notes,
        })
        return context


class FlashcardsListView(ListView):
    """List flashcards by topic"""
    model = Flashcard
    template_name = 'core/resources/flashcards_list.html'
    context_object_name = 'flashcards'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Flashcard.objects.filter(is_active=True).select_related('topic__subject')
        
        # Filter by subject
        subject_id = self.request.GET.get('subject')
        if subject_id:
            queryset = queryset.filter(topic__subject_id=subject_id)
        
        # Filter by topic
        topic_id = self.request.GET.get('topic')
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
        
        # Filter premium content for non-premium users
        if not (self.request.user.is_authenticated and 
                hasattr(self.request.user, 'userprofile') and 
                self.request.user.userprofile.is_premium_active):
            queryset = queryset.filter(is_premium=False)
        
        return queryset.order_by('topic', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Group flashcards by topic
        topics_with_flashcards = {}
        for flashcard in context['flashcards']:
            topic = flashcard.topic
            if topic not in topics_with_flashcards:
                topics_with_flashcards[topic] = []
            topics_with_flashcards[topic].append(flashcard)
        
        context.update({
            'subjects': Subject.objects.filter(is_active=True),
            'topics_with_flashcards': topics_with_flashcards,
            'selected_subject_id': int(self.request.GET.get('subject', 0)) or None,
            'selected_topic_id': int(self.request.GET.get('topic', 0)) or None,
        })
        
        return context


class FlashcardStudyView(TemplateView):
    """Interactive flashcard study interface"""
    template_name = 'core/resources/flashcard_study.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_id = kwargs.get('topic_id')
        topic = get_object_or_404(Topic, pk=topic_id, is_active=True)
        
        # Get flashcards for this topic
        flashcards = Flashcard.objects.filter(
            topic=topic,
            is_active=True
        )
        
        # Filter premium content for non-premium users
        if not (self.request.user.is_authenticated and 
                hasattr(self.request.user, 'userprofile') and 
                self.request.user.userprofile.is_premium_active):
            flashcards = flashcards.filter(is_premium=False)
        
        # Track user progress if authenticated
        if self.request.user.is_authenticated:
            progress, created = UserProgress.objects.get_or_create(
                user=self.request.user,
                topic=topic
            )
            progress.flashcards_reviewed.add(*flashcards)
            progress.save()
        
        context.update({
            'topic': topic,
            'flashcards': flashcards,
            'flashcards_json': [
                {
                    'id': fc.id,
                    'front': fc.front_text,
                    'back': fc.back_text,
                }
                for fc in flashcards
            ],
        })
        return context


class VideosListView(ListView):
    """List video resources"""
    model = VideoResource
    template_name = 'core/resources/videos_list.html'
    context_object_name = 'videos'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = VideoResource.objects.filter(is_active=True).select_related('topic__subject')
        
        # Filter by subject
        subject_id = self.request.GET.get('subject')
        if subject_id:
            queryset = queryset.filter(topic__subject_id=subject_id)
        
        # Filter by topic
        topic_id = self.request.GET.get('topic')
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(topic__name__icontains=search)
            )
        
        # Filter premium content for non-premium users
        if not (self.request.user.is_authenticated and 
                hasattr(self.request.user, 'userprofile') and 
                self.request.user.userprofile.is_premium_active):
            queryset = queryset.filter(is_premium=False)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'subjects': Subject.objects.filter(is_active=True),
            'selected_subject_id': int(self.request.GET.get('subject', 0)) or None,
            'selected_topic_id': int(self.request.GET.get('topic', 0)) or None,
            'search_query': self.request.GET.get('search', ''),
        })
        
        # Get topics for selected subject
        if context['selected_subject_id']:
            context['topics'] = Topic.objects.filter(
                subject_id=context['selected_subject_id'],
                is_active=True
            )
        
        return context


class VideoDetailView(DetailView):
    """Video resource detail view"""
    model = VideoResource
    template_name = 'core/resources/video_detail.html'
    context_object_name = 'video'
    
    def get_queryset(self):
        queryset = VideoResource.objects.filter(is_active=True).select_related('topic__subject', 'created_by')
        
        # Filter premium content for non-premium users
        if not (self.request.user.is_authenticated and 
                hasattr(self.request.user, 'userprofile') and 
                self.request.user.userprofile.is_premium_active):
            queryset = queryset.filter(is_premium=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.get_object()
        
        # Track user progress if authenticated
        if self.request.user.is_authenticated:
            progress, created = UserProgress.objects.get_or_create(
                user=self.request.user,
                topic=video.topic
            )
            progress.videos_watched.add(video)
            progress.save()
        
        # Get related videos
        related_videos = VideoResource.objects.filter(
            topic=video.topic,
            is_active=True
        ).exclude(pk=video.pk)[:5]
        
        # Extract video embed URL (for YouTube)
        embed_url = self._get_embed_url(video.video_url)
        
        context.update({
            'related_videos': related_videos,
            'embed_url': embed_url,
        })
        return context
    
    def _get_embed_url(self, video_url):
        """Convert video URL to embeddable format"""
        if 'youtube.com/watch?v=' in video_url:
            video_id = video_url.split('v=')[1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        elif 'youtu.be/' in video_url:
            video_id = video_url.split('youtu.be/')[1].split('?')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        elif 'vimeo.com/' in video_url:
            video_id = video_url.split('vimeo.com/')[1]
            return f"https://player.vimeo.com/video/{video_id}"
        
        return video_url  # Return original if not recognized
