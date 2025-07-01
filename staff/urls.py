from django.urls import path, include
from . import views

app_name = 'staff'

urlpatterns = [
    # Authentication
    path('login/', views.AdminLoginView.as_view(), name='login'),
    path('logout/', views.AdminLogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # User Management
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
    
    # Question Management
    path('questions/', views.QuestionListView.as_view(), name='question_list'),
    path('questions/add/', views.QuestionCreateView.as_view(), name='question_add'),
    path('questions/<int:pk>/edit/', views.QuestionEditView.as_view(), name='question_edit'),
    path('questions/<int:pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
    path('questions/bulk-upload/', views.BulkQuestionUploadView.as_view(), name='question_bulk_upload'),
    
    # Subject and Topic Management
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/add/', views.SubjectCreateView.as_view(), name='subject_add'),
    path('subjects/<int:pk>/edit/', views.SubjectEditView.as_view(), name='subject_edit'),
    path('topics/', views.TopicListView.as_view(), name='topic_list'),
    path('topics/add/', views.TopicCreateView.as_view(), name='topic_add'),
    path('topics/<int:pk>/edit/', views.TopicEditView.as_view(), name='topic_edit'),
    
    # Tag Management
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/add/', views.TagCreateView.as_view(), name='tag_add'),
    path('tags/<int:pk>/edit/', views.TagEditView.as_view(), name='tag_edit'),
    path('tags/<int:pk>/delete/', views.TagDeleteView.as_view(), name='tag_delete'),
    
    # Quiz Management
    path('quizzes/', views.QuizAttemptListView.as_view(), name='quiz_list'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    
    # Resource Management
    path('resources/', views.ResourceListView.as_view(), name='resource_list'),
    path('resources/notes/add/', views.NoteCreateView.as_view(), name='note_add'),
    path('resources/notes/<int:pk>/edit/', views.NoteEditView.as_view(), name='note_edit'),
    path('resources/videos/add/', views.VideoCreateView.as_view(), name='video_add'),
    path('resources/videos/<int:pk>/edit/', views.VideoEditView.as_view(), name='video_edit'),
    path('resources/flashcards/add/', views.FlashcardCreateView.as_view(), name='flashcard_add'),
    path('resources/flashcards/<int:pk>/edit/', views.FlashcardEditView.as_view(), name='flashcard_edit'),
    
    # Payment Management
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/review/', views.PaymentReviewView.as_view(), name='payment_review'),
    path('payments/history/', views.PaymentHistoryView.as_view(), name='payment_history'),
    
    # Support Management
    path('support/', views.SupportInboxView.as_view(), name='support_inbox'),
    path('support/<int:pk>/', views.SupportMessageView.as_view(), name='support_message'),
    
    # Settings and Logs
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('logs/', views.ActivityLogsView.as_view(), name='logs'),
]
