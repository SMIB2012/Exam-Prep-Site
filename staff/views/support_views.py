from django.views.generic import ListView, DetailView
from django.contrib import messages
from .user_views import StaffRequiredMixin


class SupportInboxView(StaffRequiredMixin, ListView):
    """View support messages"""
    template_name = 'staff/support/inbox.html'
    context_object_name = 'messages'
    paginate_by = 25
    
    def get_queryset(self):
        # Will be implemented when contact model is available
        return []


class SupportMessageView(StaffRequiredMixin, DetailView):
    """View individual support message"""
    template_name = 'staff/support/message_detail.html'
    context_object_name = 'message'
