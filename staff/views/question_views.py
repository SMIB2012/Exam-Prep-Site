from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from core.models import Question, Option
from ..forms import QuestionForm, OptionFormSet
from .user_views import StaffRequiredMixin


class QuestionListView(StaffRequiredMixin, ListView):
    """List all questions"""
    model = Question
    template_name = 'staff/questions/question_list.html'
    context_object_name = 'questions'
    paginate_by = 25


class QuestionCreateView(StaffRequiredMixin, CreateView):
    """Create new question"""
    model = Question
    form_class = QuestionForm
    template_name = 'staff/questions/question_form.html'
    success_url = reverse_lazy('staff:question_list')


class QuestionEditView(StaffRequiredMixin, UpdateView):
    """Edit existing question"""
    model = Question
    form_class = QuestionForm
    template_name = 'staff/questions/question_form.html'
    success_url = reverse_lazy('staff:question_list')


class QuestionDeleteView(StaffRequiredMixin, DeleteView):
    """Delete question"""
    model = Question
    template_name = 'staff/questions/question_confirm_delete.html'
    success_url = reverse_lazy('staff:question_list')


class BulkQuestionUploadView(StaffRequiredMixin, CreateView):
    """Bulk upload questions"""
    template_name = 'staff/questions/bulk_upload.html'
    success_url = reverse_lazy('staff:question_list')
