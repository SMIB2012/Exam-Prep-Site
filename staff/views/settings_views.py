from django.views.generic import TemplateView
from .user_views import StaffRequiredMixin


class SettingsView(StaffRequiredMixin, TemplateView):
    """Site settings"""
    template_name = 'staff/settings/settings.html'


class ActivityLogsView(StaffRequiredMixin, TemplateView):
    """View activity logs"""
    template_name = 'staff/settings/logs.html'
