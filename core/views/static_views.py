"""
Static page views for MedPrep application
"""
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from ..forms import ContactForm


class AboutView(TemplateView):
    """About page"""
    template_name = 'core/static/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add some statistics
        from ..models import Subject, Question, UserProfile
        
        context.update({
            'total_subjects': Subject.objects.filter(is_active=True).count(),
            'total_questions': Question.objects.filter(is_active=True).count(),
            'total_students': UserProfile.objects.count(),
        })
        return context


class ContactView(TemplateView):
    """Contact page with form"""
    template_name = 'core/static/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        
        if form.is_valid():
            # Send email (you would implement actual email sending here)
            try:
                # In a real implementation, you would send this email
                # send_mail(
                #     subject=f"Contact Form: {form.cleaned_data['subject']}",
                #     message=f"From: {form.cleaned_data['name']} <{form.cleaned_data['email']}>\n\n{form.cleaned_data['message']}",
                #     from_email=settings.DEFAULT_FROM_EMAIL,
                #     recipient_list=['admin@medprep.com'],
                # )
                
                messages.success(request, "Thank you for your message! We'll get back to you soon.")
                return self.get(request, *args, **kwargs)
            except Exception as e:
                messages.error(request, "Sorry, there was an error sending your message. Please try again.")
        
        return render(request, self.template_name, {
            'form': form,
        })


class FAQView(TemplateView):
    """Frequently Asked Questions"""
    template_name = 'core/static/faq.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # FAQ data
        faqs = [
            {
                'category': 'General',
                'questions': [
                    {
                        'question': 'What is MedPrep?',
                        'answer': 'MedPrep is a comprehensive online platform designed to help MBBS students prepare for their exams through practice MCQs, study materials, and performance tracking.'
                    },
                    {
                        'question': 'How do I create an account?',
                        'answer': 'Click on the "Register" button, fill in your details including your year of study and college name, and verify your email address.'
                    },
                    {
                        'question': 'Is MedPrep free to use?',
                        'answer': 'MedPrep offers both free and premium plans. Free users have access to basic features, while premium users get access to advanced questions, detailed explanations, and additional study resources.'
                    },
                ]
            },
            {
                'category': 'Subscription & Payment',
                'questions': [
                    {
                        'question': 'How do I upgrade to premium?',
                        'answer': 'Go to the Subscription page, choose a plan, and follow the payment instructions. Upload your payment screenshot for verification.'
                    },
                    {
                        'question': 'What payment methods do you accept?',
                        'answer': 'We accept JazzCash, EasyPaisa, and bank transfers. All payments are manually verified by our team.'
                    },
                    {
                        'question': 'How long does payment verification take?',
                        'answer': 'Payment verification usually takes 24-48 hours. You will receive a notification once your subscription is activated.'
                    },
                ]
            },
            {
                'category': 'Quizzes & Study',
                'questions': [
                    {
                        'question': 'How many questions can I practice?',
                        'answer': 'Free users can access basic questions, while premium users have access to our complete question bank with detailed explanations.'
                    },
                    {
                        'question': 'Can I retake quizzes?',
                        'answer': 'Yes, you can retake quizzes as many times as you want to improve your understanding and scores.'
                    },
                    {
                        'question': 'How is my performance tracked?',
                        'answer': 'We track your quiz scores, time taken, subject-wise performance, and overall progress through your dashboard.'
                    },
                ]
            },
        ]
        
        context['faqs'] = faqs
        return context


class TermsView(TemplateView):
    """Terms of Service"""
    template_name = 'core/static/terms.html'


class PrivacyView(TemplateView):
    """Privacy Policy"""
    template_name = 'core/static/privacy.html'
