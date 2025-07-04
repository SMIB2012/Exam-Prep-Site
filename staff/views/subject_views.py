from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from core.models import Subject, Topic
from .user_views import StaffRequiredMixin


class SubjectListView(StaffRequiredMixin, ListView):
    """List all subjects"""
    model = Subject
    template_name = 'staff/subjects/subject_list.html'
    context_object_name = 'subjects'
    
    def get_context_data(self, **kwargs):
        """Add additional context for the template"""
        context = super().get_context_data(**kwargs)
        
        # Calculate statistics
        all_subjects = Subject.objects.all()
        context['active_subjects'] = all_subjects.filter(is_active=True).count()
        
        # Get total topics and questions count
        try:
            from core.models import Question
            context['total_topics'] = Topic.objects.count()
            context['total_questions'] = Question.objects.count()
        except ImportError:
            context['total_topics'] = 0
            context['total_questions'] = 0
        
        return context


class SubjectCreateView(StaffRequiredMixin, CreateView):
    """Create new subject"""
    model = Subject
    template_name = 'staff/subjects/subject_form.html'
    fields = ['name', 'code', 'description', 'year_applicable', 'is_active']
    success_url = reverse_lazy('staff:subject_list')


class SubjectEditView(StaffRequiredMixin, UpdateView):
    """Edit existing subject"""
    model = Subject
    template_name = 'staff/subjects/subject_form.html'
    fields = ['name', 'code', 'description', 'year_applicable', 'is_active']
    success_url = reverse_lazy('staff:subject_list')


class TopicListView(StaffRequiredMixin, ListView):
    """List all topics"""
    model = Topic
    template_name = 'staff/topics/topic_list.html'
    context_object_name = 'topics'


class TopicCreateView(StaffRequiredMixin, CreateView):
    """Create new topic"""
    model = Topic
    template_name = 'staff/topics/topic_form.html'
    fields = ['subject', 'name', 'description', 'order', 'is_active']
    success_url = reverse_lazy('staff:topic_list')


class TopicEditView(StaffRequiredMixin, UpdateView):
    """Edit existing topic"""
    model = Topic
    template_name = 'staff/topics/topic_form.html'
    fields = ['subject', 'name', 'description', 'order', 'is_active']
    success_url = reverse_lazy('staff:topic_list')
