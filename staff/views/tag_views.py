from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from core.models import Tag
from ..forms import TagForm
from .user_views import StaffRequiredMixin


class TagListView(StaffRequiredMixin, ListView):
    """List all tags"""
    model = Tag
    template_name = 'staff/tags/tag_list.html'
    context_object_name = 'tags'


class TagCreateView(StaffRequiredMixin, CreateView):
    """Create new tag"""
    model = Tag
    form_class = TagForm
    template_name = 'staff/tags/tag_form.html'
    success_url = reverse_lazy('staff:tag_list')


class TagEditView(StaffRequiredMixin, UpdateView):
    """Edit existing tag"""
    model = Tag
    form_class = TagForm
    template_name = 'staff/tags/tag_form.html'
    success_url = reverse_lazy('staff:tag_list')


class TagDeleteView(StaffRequiredMixin, DeleteView):
    """Delete tag"""
    model = Tag
    template_name = 'staff/tags/tag_confirm_delete.html'
    success_url = reverse_lazy('staff:tag_list')
