from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from core.models import UserProfile


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require staff permissions"""
    def test_func(self):
        return self.request.user.is_staff


class UserListView(StaffRequiredMixin, ListView):
    """List all users with search and filter capabilities"""
    model = User
    template_name = 'staff/users/user_list.html'
    context_object_name = 'users'
    paginate_by = 25


class UserDetailView(StaffRequiredMixin, DetailView):
    """View user details"""
    model = User
    template_name = 'staff/users/user_detail.html'
    context_object_name = 'user'


class UserEditView(StaffRequiredMixin, UpdateView):
    """Edit user details"""
    model = User
    template_name = 'staff/users/user_edit.html'
    fields = ['first_name', 'last_name', 'email', 'is_active']
