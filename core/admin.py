"""
Admin configuration for MedPrep application
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    UserProfile, Subject, Topic, Question, Option,
    QuizSession, UserAnswer, SubscriptionPlan, PaymentProof,
    Note, Flashcard, VideoResource, UserProgress
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'year_of_study', 'college_name', 'is_premium', 'total_quiz_score', 'created_at']
    list_filter = ['year_of_study', 'is_premium', 'created_at']
    search_fields = ['user__username', 'user__email', 'college_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'year_of_study', 'college_name', 'phone_number', 'profile_picture')
        }),
        ('Subscription', {
            'fields': ('is_premium', 'premium_expires_at')
        }),
        ('Statistics', {
            'fields': ('total_quiz_score', 'total_quizzes_taken'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'year_applicable', 'topics_count', 'questions_count', 'is_active']
    list_filter = ['year_applicable', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at']
    
    def topics_count(self, obj):
        return obj.topics.count()
    topics_count.short_description = 'Topics'
    
    def questions_count(self, obj):
        return sum(topic.questions.count() for topic in obj.topics.all())
    questions_count.short_description = 'Questions'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'questions_count', 'order', 'is_active']
    list_filter = ['subject', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'subject__name']
    readonly_fields = ['created_at']
    ordering = ['subject', 'order', 'name']
    
    def questions_count(self, obj):
        return obj.questions.count()
    questions_count.short_description = 'Questions'


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4
    max_num = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'topic', 'difficulty', 'is_premium', 'is_active', 'created_at']
    list_filter = ['topic__subject', 'difficulty', 'is_premium', 'is_active', 'created_at']
    search_fields = ['question_text', 'explanation', 'topic__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OptionInline]
    
    fieldsets = (
        ('Question Details', {
            'fields': ('topic', 'question_text', 'explanation', 'difficulty')
        }),
        ('Settings', {
            'fields': ('is_premium', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def question_preview(self, obj):
        return obj.question_text[:100] + "..." if len(obj.question_text) > 100 else obj.question_text
    question_preview.short_description = 'Question'


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'status', 'score', 'total_questions', 'percentage', 'started_at']
    list_filter = ['status', 'topic__subject', 'started_at']
    search_fields = ['user__username', 'topic__name']
    readonly_fields = ['started_at', 'completed_at', 'percentage']
    
    def percentage(self, obj):
        return f"{obj.percentage_score}%"
    percentage.short_description = 'Score %'


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['quiz_session', 'question_preview', 'selected_option_preview', 'is_correct', 'answered_at']
    list_filter = ['is_correct', 'answered_at']
    search_fields = ['quiz_session__user__username', 'question__question_text']
    readonly_fields = ['answered_at']
    
    def question_preview(self, obj):
        return obj.question.question_text[:50] + "..."
    question_preview.short_description = 'Question'
    
    def selected_option_preview(self, obj):
        return obj.selected_option.option_text[:50] + "..." if obj.selected_option else "No answer"
    selected_option_preview.short_description = 'Selected Option'


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price', 'duration_days', 'is_active', 'created_at']
    list_filter = ['plan_type', 'is_active', 'created_at']
    search_fields = ['name', 'features']
    readonly_fields = ['created_at']


@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription_plan', 'payment_method', 'amount_paid', 'status', 'submitted_at']
    list_filter = ['status', 'payment_method', 'subscription_plan', 'submitted_at']
    search_fields = ['user__username', 'transaction_id']
    readonly_fields = ['submitted_at']
    actions = ['approve_payments', 'reject_payments']
    
    fieldsets = (
        ('Payment Details', {
            'fields': ('user', 'subscription_plan', 'payment_method', 'transaction_id', 'amount_paid')
        }),
        ('Proof', {
            'fields': ('payment_screenshot', 'screenshot_preview')
        }),
        ('Review', {
            'fields': ('status', 'admin_notes', 'reviewed_by', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['submitted_at', 'screenshot_preview']
    
    def screenshot_preview(self, obj):
        if obj.payment_screenshot:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px;" />',
                obj.payment_screenshot.url
            )
        return "No screenshot"
    screenshot_preview.short_description = 'Screenshot Preview'
    
    def approve_payments(self, request, queryset):
        for payment in queryset.filter(status='pending'):
            payment.approve_payment(request.user)
        self.message_user(request, f"Approved {queryset.count()} payment(s)")
    approve_payments.short_description = "Approve selected payments"
    
    def reject_payments(self, request, queryset):
        for payment in queryset.filter(status='pending'):
            payment.reject_payment(request.user, "Rejected by admin")
        self.message_user(request, f"Rejected {queryset.count()} payment(s)")
    reject_payments.short_description = "Reject selected payments"


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'is_premium', 'is_active', 'created_by', 'created_at']
    list_filter = ['topic__subject', 'is_premium', 'is_active', 'created_at']
    search_fields = ['title', 'content', 'topic__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ['front_preview', 'topic', 'is_premium', 'is_active', 'created_by', 'created_at']
    list_filter = ['topic__subject', 'is_premium', 'is_active', 'created_at']
    search_fields = ['front_text', 'back_text', 'topic__name']
    readonly_fields = ['created_at']
    
    def front_preview(self, obj):
        return obj.front_text[:50] + "..." if len(obj.front_text) > 50 else obj.front_text
    front_preview.short_description = 'Front Text'


@admin.register(VideoResource)
class VideoResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'duration_formatted', 'is_premium', 'is_active', 'created_by', 'created_at']
    list_filter = ['topic__subject', 'is_premium', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'topic__name']
    readonly_fields = ['created_at']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'completion_percentage', 'total_quiz_attempts', 'best_quiz_score', 'last_accessed']
    list_filter = ['topic__subject', 'last_accessed']
    search_fields = ['user__username', 'topic__name']
    readonly_fields = ['created_at', 'last_accessed', 'completion_percentage']
    
    def completion_percentage(self, obj):
        return f"{obj.completion_percentage}%"
    completion_percentage.short_description = 'Completion %'


# Customize admin site
admin.site.site_header = "MedPrep Administration"
admin.site.site_title = "MedPrep Admin"
admin.site.index_title = "Welcome to MedPrep Administration Panel"
