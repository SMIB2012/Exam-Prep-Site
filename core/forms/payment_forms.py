"""
Payment-related forms for MedPrep application
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML

from ..models import PaymentProof, SubscriptionPlan


class PaymentProofForm(forms.ModelForm):
    """Form for uploading payment proof"""
    
    class Meta:
        model = PaymentProof
        fields = [
            'subscription_plan', 'payment_method', 'transaction_id', 
            'amount_paid', 'payment_screenshot'
        ]
        widgets = {
            'subscription_plan': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_screenshot': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Only show active subscription plans (excluding free)
        self.fields['subscription_plan'].queryset = SubscriptionPlan.objects.filter(
            is_active=True,
            plan_type__in=['monthly', 'quarterly', 'yearly']
        )
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            HTML("""
            <div class="alert alert-info">
                <h6><i class="fas fa-info-circle"></i> Payment Instructions</h6>
                <p class="mb-1"><strong>JazzCash:</strong> Send to 03XX-XXXXXXX</p>
                <p class="mb-1"><strong>EasyPaisa:</strong> Send to 03XX-XXXXXXX</p>
                <p class="mb-0"><strong>Bank Transfer:</strong> Account Details in About page</p>
            </div>
            """),
            Field('subscription_plan', css_class='form-group mb-3'),
            Row(
                Column('payment_method', css_class='form-group col-md-6 mb-3'),
                Column('amount_paid', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Field('transaction_id', css_class='form-group mb-3'),
            Field('payment_screenshot', css_class='form-group mb-3'),
            HTML("""
            <div class="alert alert-warning">
                <small>
                    <i class="fas fa-exclamation-triangle"></i>
                    Please upload a clear screenshot of your payment confirmation.
                    Your subscription will be activated after manual verification (usually within 24 hours).
                </small>
            </div>
            """),
            Submit('submit', 'Submit Payment Proof', css_class='btn btn-success btn-lg')
        )
    
    def clean_payment_screenshot(self):
        image = self.cleaned_data.get('payment_screenshot')
        
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large. Please upload an image smaller than 5MB.")
            
            # Check file format
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if not any(image.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError("Please upload a valid image file (JPG, PNG, or GIF).")
        
        return image
    
    def clean(self):
        cleaned_data = super().clean()
        subscription_plan = cleaned_data.get('subscription_plan')
        amount_paid = cleaned_data.get('amount_paid')
        
        if subscription_plan and amount_paid:
            # Check if amount matches the plan price
            if abs(float(amount_paid) - float(subscription_plan.price)) > 0.01:
                raise forms.ValidationError(
                    f"Amount paid (PKR {amount_paid}) does not match the plan price (PKR {subscription_plan.price}). "
                    f"Please enter the correct amount or select the appropriate plan."
                )
        
        return cleaned_data


class ContactForm(forms.Form):
    """Contact form for user inquiries"""
    
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('technical', 'Technical Support'),
        ('payment', 'Payment Issue'),
        ('content', 'Content Related'),
        ('other', 'Other'),
    ]
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    subject = forms.ChoiceField(
        choices=SUBJECT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Field('subject', css_class='form-group mb-3'),
            Field('message', css_class='form-group mb-3'),
            Submit('submit', 'Send Message', css_class='btn btn-primary')
        )
