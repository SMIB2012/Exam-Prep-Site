from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from core.models import Note, VideoResource, Flashcard
from ..forms import NoteForm, VideoResourceForm, FlashcardForm
from .user_views import StaffRequiredMixin


class ResourceListView(StaffRequiredMixin, ListView):
    """List all resources"""
    template_name = 'staff/resources/resource_list.html'
    
    def get_queryset(self):
        return None  # Will be implemented with combined resources


class NoteCreateView(StaffRequiredMixin, CreateView):
    """Create new note"""
    model = Note
    form_class = NoteForm
    template_name = 'staff/resources/note_form.html'
    success_url = reverse_lazy('staff:resource_list')


class NoteEditView(StaffRequiredMixin, UpdateView):
    """Edit existing note"""
    model = Note
    form_class = NoteForm
    template_name = 'staff/resources/note_form.html'
    success_url = reverse_lazy('staff:resource_list')


class VideoCreateView(StaffRequiredMixin, CreateView):
    """Create new video"""
    model = VideoResource
    form_class = VideoResourceForm
    template_name = 'staff/resources/video_form.html'
    success_url = reverse_lazy('staff:resource_list')


class VideoEditView(StaffRequiredMixin, UpdateView):
    """Edit existing video"""
    model = VideoResource
    form_class = VideoResourceForm
    template_name = 'staff/resources/video_form.html'
    success_url = reverse_lazy('staff:resource_list')


class FlashcardCreateView(StaffRequiredMixin, CreateView):
    """Create new flashcard"""
    model = Flashcard
    form_class = FlashcardForm
    template_name = 'staff/resources/flashcard_form.html'
    success_url = reverse_lazy('staff:resource_list')


class FlashcardEditView(StaffRequiredMixin, UpdateView):
    """Edit existing flashcard"""
    model = Flashcard
    form_class = FlashcardForm
    template_name = 'staff/resources/flashcard_form.html'
    success_url = reverse_lazy('staff:resource_list')
