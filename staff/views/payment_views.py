from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy
from core.models import PaymentProof
from ..forms import PaymentReviewForm
from .user_views import StaffRequiredMixin


class PaymentListView(StaffRequiredMixin, ListView):
    """List pending payments"""
    model = PaymentProof
    template_name = 'staff/payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 25


class PaymentReviewView(StaffRequiredMixin, UpdateView):
    """Review payment proof"""
    model = PaymentProof
    form_class = PaymentReviewForm
    template_name = 'staff/payments/payment_review.html'
    success_url = reverse_lazy('staff:payment_list')


class PaymentHistoryView(StaffRequiredMixin, ListView):
    """View payment history"""
    model = PaymentProof
    template_name = 'staff/payments/payment_history.html'
    context_object_name = 'payments'
    paginate_by = 50
