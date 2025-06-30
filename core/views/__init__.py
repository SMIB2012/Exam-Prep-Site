from .main_views import (
    HomeView, DashboardView, LeaderboardView, 
    QuestionBankView, SubjectDetailView, TopicDetailView
)
from .auth_views import (
    CustomLoginView, CustomLogoutView, RegisterView,
    ProfileView, ProfileEditView
)
from .quiz_views import (
    QuizListView, StartQuizView, QuizSessionView,
    QuizQuestionView, SubmitQuizView, QuizResultView
)
from .resource_views import (
    ResourcesView, NotesListView, NoteDetailView,
    FlashcardsListView, FlashcardStudyView,
    VideosListView, VideoDetailView
)
from .payment_views import (
    SubscriptionView, PaymentView, PaymentProofUploadView,
    PaymentStatusView
)
from .static_views import (
    AboutView, ContactView, FAQView, TermsView, PrivacyView
)

__all__ = [
    # Main views
    'HomeView', 'DashboardView', 'LeaderboardView',
    'QuestionBankView', 'SubjectDetailView', 'TopicDetailView',
    
    # Auth views
    'CustomLoginView', 'CustomLogoutView', 'RegisterView',
    'ProfileView', 'ProfileEditView',
    
    # Quiz views
    'QuizListView', 'StartQuizView', 'QuizSessionView',
    'QuizQuestionView', 'SubmitQuizView', 'QuizResultView',
    
    # Resource views
    'ResourcesView', 'NotesListView', 'NoteDetailView',
    'FlashcardsListView', 'FlashcardStudyView',
    'VideosListView', 'VideoDetailView',
    
    # Payment views
    'SubscriptionView', 'PaymentView', 'PaymentProofUploadView',
    'PaymentStatusView',
    
    # Static views
    'AboutView', 'ContactView', 'FAQView', 'TermsView', 'PrivacyView',
]
