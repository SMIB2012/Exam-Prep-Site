# MedPrep - MBBS Exam Preparation Platform

## 📋 Project Overview

**MedPrep** is a comprehensive web-based platform designed specifically for MBBS students to prepare for their medical examinations. The platform provides practice questions, performance tracking, study resources, and a competitive environment to enhance learning.

## 🏗️ Project Architecture

### **Technology Stack**
- **Backend**: Django 4.2+ (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Authentication**: Django's built-in authentication system
- **Payment**: Manual verification system (JazzCash/EasyPaisa screenshots)

### **Project Structure**
```
medprep/
├── core/                               # Main application
│   ├── migrations/                     # Database migrations
│   ├── fixtures/                       # Sample data (subjects, questions)
│   │   └── sample_subjects.json
│   ├── management/                     # Custom management commands
│   │   └── commands/
│   │       ├── import_questions.py    # Import questions from JSON/CSV
│   │       └── expire_subscriptions.py # Auto-expire old subscriptions
│   ├── models/                         # Organized model files
│   │   ├── __init__.py                # Model imports
│   │   ├── user_models.py             # User profiles and preferences
│   │   ├── academic_models.py         # Subjects, topics, questions
│   │   ├── quiz_models.py             # Quiz sessions and answers
│   │   ├── resource_models.py         # Study materials (notes, videos)
│   │   └── subscription_models.py     # Payment plans and subscriptions
│   ├── views/                          # Organized view files
│   │   ├── __init__.py                # View imports
│   │   ├── auth_views.py              # Authentication (login, register)
│   │   ├── main_views.py              # Home, dashboard
│   │   ├── quiz_views.py              # Quiz functionality
│   │   ├── payment_views.py           # Subscription and payments
│   │   ├── resource_views.py          # Study resources
│   │   └── static_views.py            # Static pages (about, contact, etc.)
│   ├── forms/                          # Django forms
│   │   ├── __init__.py
│   │   ├── user_forms.py              # User registration, profile forms
│   │   ├── quiz_forms.py              # Quiz-related forms
│   │   ├── payment_forms.py           # Payment proof upload forms
│   │   └── quiz_forms.py              # Contact and feedback forms
│   ├── utils/                          # Utility functions
│   │   ├── __init__.py
│   │   ├── scoring.py                 # Quiz scoring and analytics
│   │   ├── ranking.py                 # Leaderboard calculations
│   │   └── payment_check.py           # Payment verification logic
│   ├── templates/                      # HTML templates
│   │   └── core/
│   │       ├── base.html              # Base template
│   │       ├── home.html              # Landing page
│   │       ├── dashboard.html         # User dashboard
│   │       ├── auth/                  # Authentication templates
│   │       │   ├── login.html
│   │       │   ├── register.html
│   │       │   └── profile.html
│   │       ├── quiz/                  # Quiz templates
│   │       │   ├── quiz_list.html
│   │       │   ├── quiz_session.html
│   │       │   └── quiz_result.html
│   │       ├── resources/             # Study resource templates
│   │       │   └── resources.html
│   │       ├── subscription/          # Payment templates
│   │       │   ├── plans.html
│   │       │   └── subscription.html
│   │       └── static/                # Static page templates
│   │           ├── about.html
│   │           ├── contact.html
│   │           ├── faq.html
│   │           ├── privacy.html
│   │           └── terms.html
│   ├── static/                         # CSS, JS, Images
│   │   └── core/
│   │       ├── css/                   # Stylesheets
│   │       │   ├── main.css           # Global styles and color scheme
│   │       │   ├── home.css           # Homepage styles
│   │       │   ├── auth.css           # Authentication pages
│   │       │   ├── dashboard.css      # Dashboard styles
│   │       │   ├── quiz.css           # Quiz interface styles
│   │       │   ├── leaderboard.css    # Leaderboard styles
│   │       │   ├── resources.css      # Study resources styles
│   │       │   ├── profile.css        # Profile page styles
│   │       │   ├── subscription.css   # Subscription page styles
│   │       │   ├── subject-detail.css # Subject detail styles
│   │       │   └── static-pages.css   # Static pages styles
│   │       ├── js/                    # JavaScript files
│   │       │   ├── main.js           # Global JavaScript
│   │       │   └── home.js           # Homepage interactions
│   │       └── images/               # Static images
│   │           └── favicon.ico
│   ├── admin.py                       # Django admin configuration
│   ├── apps.py                        # App configuration
│   ├── signals.py                     # Django signals for auto-events
│   ├── urls.py                        # URL routing
│   └── tests.py                       # Test cases
├── medprep/                           # Django project settings
│   ├── __init__.py
│   ├── settings.py                    # Project settings
│   ├── urls.py                        # Main URL configuration
│   ├── wsgi.py                        # WSGI application
│   └── asgi.py                        # ASGI application
├── media/                             # User uploads
│   └── uploads/
│       ├── payment_proofs/            # Payment screenshot uploads
│       └── resources/                 # Uploaded study materials
├── static/                            # Collected static files (production)
├── templates/                         # Project-wide templates
│   └── base.html                      # Global base template
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
└── run_server.bat                     # Development server script
```

## 🎯 Core Features

### **1. User Management**
- User registration and authentication
- Profile management with year of study, preferences
- Premium subscription system with manual payment verification

### **2. Question Bank & Quizzes**
- Organized by subjects and topics
- Multiple difficulty levels (Easy, Medium, Hard)
- Timed quizzes with progress tracking
- Detailed explanations for each question
- Save and resume quiz functionality

### **3. Performance Analytics**
- Individual performance tracking
- Subject-wise performance breakdown
- Difficulty-level analysis
- Progress over time charts
- Detailed quiz result analysis

### **4. Study Resources**
- Notes and study materials
- Flashcards for quick review
- Video lectures (for premium users)
- Resource categorization by subject/topic

### **5. Competitive Features**
- Global leaderboard
- Weekly rankings
- Subject-specific leaderboards
- Achievement badges and progress milestones

### **6. Subscription System**
- Free tier with limited access
- Premium plans with full features
- Manual payment verification via screenshot upload
- Automatic subscription expiry handling

## 🎨 Design System

### **Color Palette**
- **Primary Colors**: Blue (#1e40af), Green (#059669), White (#ffffff)
- **Accent Colors**: Orange (#f97316), Gray (#6b7280), Navy (#1e3a8a)
- **Semantic Colors**: Success (#10b981), Warning (#f59e0b), Error (#ef4444)

### **Navigation Flow**
- **Landing Page**: Sign Up, Login, Explore Features
- **Dashboard**: Central hub with quick actions
- **Question Bank**: Subject/topic selection → Quiz
- **Quiz Session**: Question navigation with save/exit option
- **Results**: Performance analysis with next steps
- **All pages**: Clear back navigation to dashboard/home

## 🔧 Technical Features

### **Backend Organization**
- **Modular Models**: Separated by domain (user, academic, quiz, etc.)
- **Organized Views**: Feature-based view organization
- **Utility Functions**: Reusable logic for scoring, ranking, payments
- **Management Commands**: Data import and maintenance tasks
- **Django Signals**: Automated emails and statistics updates

### **Frontend Architecture**
- **Responsive Design**: Mobile-first approach with Bootstrap 5
- **Progressive Enhancement**: Works without JavaScript
- **Modern CSS**: CSS Grid, Flexbox, Custom Properties
- **Interactive Elements**: Smooth animations and transitions
- **Accessibility**: WCAG 2.1 AA compliance

### **Database Design**
- **Normalized Structure**: Efficient data relationships
- **Indexed Fields**: Optimized for common queries
- **Audit Fields**: Created/updated timestamps
- **Soft Deletes**: Data preservation with is_active flags

## 🚀 Development Setup

### **Requirements**
- Python 3.9+
- Django 4.2+
- SQLite (development) / PostgreSQL (production)

### **Installation**
1. Clone the repository
2. Create virtual environment: `python -m venv .venv`
3. Activate virtual environment: `.venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Load sample data: `python manage.py loaddata core/fixtures/sample_subjects.json`
7. Create superuser: `python manage.py createsuperuser`
8. Run server: `python manage.py runserver`

### **Management Commands**
- **Import Questions**: `python manage.py import_questions --file questions.json --format json --subject ANAT`
- **Expire Subscriptions**: `python manage.py expire_subscriptions`
- **Create Sample Data**: `python manage.py create_sample_data`

## 📊 Current Status

### **Completed Features** ✅
- Complete user authentication system
- Organized backend architecture with modular design
- Comprehensive quiz system with session management
- Performance analytics and scoring system
- Leaderboard functionality with rankings
- Study resources management
- Subscription system with payment verification
- Modern, responsive UI with proper color scheme
- Navigation flow matching user experience requirements
- Django admin interface for content management
- Email notifications system via Django signals
- Management commands for data import and maintenance

### **Architecture Improvements** ✅
- **Models**: Organized into domain-specific files
- **Views**: Separated by functionality for better maintainability
- **Utils**: Reusable business logic functions
- **Signals**: Automated email notifications and statistics
- **Management Commands**: Data import and maintenance tools
- **Fixtures**: Sample data for development and testing

### **In Progress** 🔄
- Advanced analytics dashboard
- Mobile app API endpoints
- Advanced search and filtering
- Bulk question import interface

### **Future Enhancements** 📋
- AI-powered question recommendations
- Study schedule optimization
- Social features (study groups, discussions)
- Advanced reporting for educators
- Integration with medical curriculum standards

## 📝 Notes

- **Payment System**: Currently uses manual verification via screenshot upload
- **Email System**: Configured for notifications (welcome, quiz completion, payment status)
- **Scalability**: Architecture supports horizontal scaling for increased user load
- **Security**: Implements Django's built-in security features
- **Testing**: Comprehensive test suite for all major functionality

---

**Last Updated**: June 30, 2025  
**Version**: 2.0.0 (Organized Architecture)  
**Status**: Production Ready
