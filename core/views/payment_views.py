"""
Payment and subscription views for MedPrep application
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy

from ..models import SubscriptionPlan, PaymentProof
from ..forms import PaymentProofForm


class SubscriptionView(TemplateView):
    """Subscription plans and pricing"""
    template_name = 'core/subscription/subscription.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get active subscription plans
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
        
        # Get user's current subscription status
        user_subscription = None
        if self.request.user.is_authenticated:
            try:
                profile = self.request.user.userprofile
                user_subscription = {
                    'is_premium': profile.is_premium,
                    'is_active': profile.is_premium_active,
                    'expires_at': profile.premium_expires_at,
                }
            except:
                user_subscription = None
        
        context.update({
            'plans': plans,
            'user_subscription': user_subscription,
        })
        return context


class PaymentView(LoginRequiredMixin, TemplateView):
    """Payment instructions and form"""
    template_name = 'core/subscription/payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan_id = kwargs.get('plan_id')
        plan = get_object_or_404(SubscriptionPlan, pk=plan_id, is_active=True)
        
        # Check if user already has a pending payment for this plan
        pending_payment = PaymentProof.objects.filter(
            user=self.request.user,
            subscription_plan=plan,
            status='pending'
        ).first()
        
        context.update({
            'plan': plan,
            'pending_payment': pending_payment,
            'form': PaymentProofForm(initial={'subscription_plan': plan}),
        })
        return context


class PaymentProofUploadView(LoginRequiredMixin, CreateView):
    """Upload payment proof"""
    model = PaymentProof
    form_class = PaymentProofForm
    template_name = 'core/subscription/payment_proof_upload.html'
    success_url = reverse_lazy('core:payment_status')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Check if user already has pending payment for this plan
        existing_payment = PaymentProof.objects.filter(
            user=self.request.user,
            subscription_plan=form.instance.subscription_plan,
            status='pending'
        ).first()
        
        if existing_payment:
            messages.warning(
                self.request, 
                f"You already have a pending payment proof for {form.instance.subscription_plan.name}. "
                f"Please wait for verification or contact support."
            )
            return redirect('core:payment_status')
        
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            f"Payment proof uploaded successfully for {form.instance.subscription_plan.name}. "
            f"Your subscription will be activated after verification (usually within 24 hours)."
        )
        
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class PaymentStatusView(LoginRequiredMixin, ListView):
    """View payment status and history"""
    model = PaymentProof
    template_name = 'core/subscription/payment_status.html'
    context_object_name = 'payment_proofs'
    paginate_by = 10
    
    def get_queryset(self):
        return PaymentProof.objects.filter(
            user=self.request.user
        ).select_related('subscription_plan').order_by('-submitted_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current subscription status
        try:
            profile = self.request.user.userprofile
            subscription_status = {
                'is_premium': profile.is_premium,
                'is_active': profile.is_premium_active,
                'expires_at': profile.premium_expires_at,
                'total_score': profile.total_quiz_score,
                'total_quizzes': profile.total_quizzes_taken,
            }
        except:
            subscription_status = None
        
        # Get payment statistics
        payments = self.get_queryset()
        payment_stats = {
            'total_payments': payments.count(),
            'pending_payments': payments.filter(status='pending').count(),
            'approved_payments': payments.filter(status='approved').count(),
            'rejected_payments': payments.filter(status='rejected').count(),
        }
        
        context.update({
            'subscription_status': subscription_status,
            'payment_stats': payment_stats,
        })
        return context
