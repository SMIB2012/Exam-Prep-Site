"""
URL configuration for core app
"""
from django.urls import path, include
from . import views

app_name = 'core'

# Authentication URLs
auth_patterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
]

# Quiz URLs
quiz_patterns = [
    path('quiz/', views.QuizListView.as_view(), name='quiz_list'),
    path('quiz/topic/<int:topic_id>/', views.StartQuizView.as_view(), name='start_quiz'),
    path('quiz/session/<int:pk>/', views.QuizSessionView.as_view(), name='quiz_session'),
    path('quiz/session/<int:pk>/question/<int:question_id>/', views.QuizQuestionView.as_view(), name='quiz_question'),
    path('quiz/session/<int:pk>/submit/', views.SubmitQuizView.as_view(), name='submit_quiz'),
    path('quiz/result/<int:pk>/', views.QuizResultView.as_view(), name='quiz_result'),
]

# Study Resources URLs
resource_patterns = [
    path('resources/', views.ResourcesView.as_view(), name='resources'),
    path('resources/notes/', views.NotesListView.as_view(), name='notes_list'),
    path('resources/notes/<int:pk>/', views.NoteDetailView.as_view(), name='note_detail'),
    path('resources/flashcards/', views.FlashcardsListView.as_view(), name='flashcards_list'),
    path('resources/flashcards/<int:topic_id>/', views.FlashcardStudyView.as_view(), name='flashcard_study'),
    path('resources/videos/', views.VideosListView.as_view(), name='videos_list'),
    path('resources/videos/<int:pk>/', views.VideoDetailView.as_view(), name='video_detail'),
]

# Subscription URLs
subscription_patterns = [
    path('subscription/', views.SubscriptionView.as_view(), name='subscription'),
    path('subscription/payment/<int:plan_id>/', views.PaymentView.as_view(), name='payment'),
    path('subscription/payment/proof/', views.PaymentProofUploadView.as_view(), name='payment_proof_upload'),
    path('subscription/payment/status/', views.PaymentStatusView.as_view(), name='payment_status'),
]

# Static page URLs
static_patterns = [
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
]

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('question-bank/', views.QuestionBankView.as_view(), name='question_bank'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject_detail'),
    path('topics/<int:pk>/', views.TopicDetailView.as_view(), name='topic_detail'),
    
    # Include pattern groups
    path('auth/', include(auth_patterns)),
    path('', include(quiz_patterns)),
    path('', include(resource_patterns)),
    path('', include(subscription_patterns)),
    path('', include(static_patterns)),
]
