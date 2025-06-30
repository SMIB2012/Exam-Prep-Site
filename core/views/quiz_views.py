"""
Quiz-related views for MedPrep application
"""
import json
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q

from ..models import (
    Topic, Question, Option, QuizSession, UserAnswer
)
from ..forms import QuizSettingsForm


class QuizListView(LoginRequiredMixin, TemplateView):
    """List available quizzes by topic"""
    template_name = 'core/quiz/quiz_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's recent quiz sessions
        recent_quizzes = QuizSession.objects.filter(
            user=self.request.user
        ).order_by('-started_at')[:10]
        
        # Get available topics
        topics = Topic.objects.filter(is_active=True).select_related('subject')
        
        # Filter premium content for non-premium users
        if not (hasattr(self.request.user, 'userprofile') and 
                self.request.user.userprofile.is_premium_active):
            topics = topics.filter(questions__is_premium=False).distinct()
        
        context.update({
            'recent_quizzes': recent_quizzes,
            'topics': topics,
            'form': QuizSettingsForm(user=self.request.user),
        })
        return context


class StartQuizView(LoginRequiredMixin, TemplateView):
    """Start a new quiz session"""
    template_name = 'core/quiz/start_quiz.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_id = kwargs.get('topic_id')
        topic = get_object_or_404(Topic, pk=topic_id, is_active=True)
        
        context.update({
            'topic': topic,
            'form': QuizSettingsForm(user=self.request.user, initial={'topic': topic}),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        form = QuizSettingsForm(request.POST, user=request.user)
        
        if form.is_valid():
            topic = form.cleaned_data['topic']
            difficulty = form.cleaned_data['difficulty']
            number_of_questions = form.cleaned_data['number_of_questions']
            time_limit = form.cleaned_data['time_limit']
            
            # Build question queryset
            questions_query = topic.questions.filter(is_active=True)
            
            # Filter by difficulty if specified
            if difficulty and difficulty != 'all':
                questions_query = questions_query.filter(difficulty=difficulty)
            
            # Filter premium content for non-premium users
            if not (hasattr(request.user, 'userprofile') and 
                    request.user.userprofile.is_premium_active):
                questions_query = questions_query.filter(is_premium=False)
            
            # Get random questions
            questions = list(questions_query)
            if len(questions) < number_of_questions:
                messages.error(request, f"Not enough questions available. Only {len(questions)} questions found.")
                return self.get(request, *args, **kwargs)
            
            selected_questions = random.sample(questions, number_of_questions)
            
            # Create quiz session
            quiz_session = QuizSession.objects.create(
                user=request.user,
                topic=topic,
                total_questions=number_of_questions,
                time_limit_minutes=time_limit,
                status='in_progress'
            )
            
            # Add questions to session
            quiz_session.questions.set(selected_questions)
            
            messages.success(request, f"Quiz started! You have {time_limit} minutes to complete {number_of_questions} questions.")
            return redirect('core:quiz_session', pk=quiz_session.pk)
        
        # Form invalid
        topic_id = kwargs.get('topic_id')
        topic = get_object_or_404(Topic, pk=topic_id, is_active=True)
        
        return render(request, self.template_name, {
            'topic': topic,
            'form': form,
        })


class QuizSessionView(LoginRequiredMixin, DetailView):
    """Main quiz interface"""
    model = QuizSession
    template_name = 'core/quiz/quiz_session.html'
    context_object_name = 'quiz_session'
    
    def get_queryset(self):
        return QuizSession.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_session = self.get_object()
        
        # Check if quiz is expired
        if quiz_session.is_expired and quiz_session.status == 'in_progress':
            quiz_session.status = 'abandoned'
            quiz_session.save()
            messages.warning(self.request, "Quiz time has expired!")
        
        # Get questions with user answers
        questions = quiz_session.questions.all().prefetch_related('options')
        user_answers = {
            answer.question_id: answer 
            for answer in quiz_session.user_answers.all()
        }
        
        # Prepare questions data
        questions_data = []
        for i, question in enumerate(questions, 1):
            user_answer = user_answers.get(question.id)
            questions_data.append({
                'number': i,
                'question': question,
                'options': question.options.all(),
                'user_answer': user_answer,
                'is_answered': user_answer is not None,
            })
        
        # Calculate progress
        answered_count = len(user_answers)
        progress_percentage = (answered_count / quiz_session.total_questions) * 100 if quiz_session.total_questions > 0 else 0
        
        context.update({
            'questions_data': questions_data,
            'answered_count': answered_count,
            'progress_percentage': progress_percentage,
            'time_remaining_seconds': self._calculate_time_remaining(quiz_session),
        })
        return context
    
    def _calculate_time_remaining(self, quiz_session):
        """Calculate remaining time in seconds"""
        if quiz_session.status != 'in_progress':
            return 0
        
        elapsed = timezone.now() - quiz_session.started_at
        total_allowed = timezone.timedelta(minutes=quiz_session.time_limit_minutes)
        remaining = total_allowed - elapsed
        
        return max(0, int(remaining.total_seconds()))


class QuizQuestionView(LoginRequiredMixin, DetailView):
    """Handle individual question answering"""
    model = QuizSession
    
    def get_queryset(self):
        return QuizSession.objects.filter(user=self.request.user)
    
    def post(self, request, *args, **kwargs):
        quiz_session = self.get_object()
        question_id = kwargs.get('question_id')
        
        # Check if quiz is still in progress
        if quiz_session.status != 'in_progress' or quiz_session.is_expired:
            return JsonResponse({'error': 'Quiz is no longer active'}, status=400)
        
        question = get_object_or_404(
            Question, 
            pk=question_id, 
            quizsession=quiz_session
        )
        
        # Get selected option
        selected_option_id = request.POST.get('selected_option')
        if not selected_option_id:
            return JsonResponse({'error': 'No option selected'}, status=400)
        
        selected_option = get_object_or_404(Option, pk=selected_option_id, question=question)
        
        # Save or update user answer
        user_answer, created = UserAnswer.objects.update_or_create(
            quiz_session=quiz_session,
            question=question,
            defaults={
                'selected_option': selected_option,
                'time_taken_seconds': int(request.POST.get('time_taken', 0)),
            }
        )
        
        return JsonResponse({
            'success': True,
            'is_correct': user_answer.is_correct,
            'correct_option_id': question.correct_option.id if question.correct_option else None,
        })


class SubmitQuizView(LoginRequiredMixin, DetailView):
    """Submit and complete quiz"""
    model = QuizSession
    
    def get_queryset(self):
        return QuizSession.objects.filter(user=self.request.user)
    
    def post(self, request, *args, **kwargs):
        quiz_session = self.get_object()
        
        if quiz_session.status != 'in_progress':
            messages.warning(request, "Quiz is already completed.")
            return redirect('core:quiz_result', pk=quiz_session.pk)
        
        # Complete the quiz
        quiz_session.complete_quiz()
        
        messages.success(request, f"Quiz completed! Your score: {quiz_session.score}/{quiz_session.total_questions}")
        return redirect('core:quiz_result', pk=quiz_session.pk)


class QuizResultView(LoginRequiredMixin, DetailView):
    """Display quiz results and analysis"""
    model = QuizSession
    template_name = 'core/quiz/quiz_result.html'
    context_object_name = 'quiz_session'
    
    def get_queryset(self):
        return QuizSession.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_session = self.get_object()
        
        # Get detailed results
        questions = quiz_session.questions.all().prefetch_related('options')
        user_answers = {
            answer.question_id: answer 
            for answer in quiz_session.user_answers.select_related('selected_option').all()
        }
        
        # Prepare detailed results
        results_data = []
        correct_count = 0
        incorrect_count = 0
        unanswered_count = 0
        
        for i, question in enumerate(questions, 1):
            user_answer = user_answers.get(question.id)
            correct_option = question.correct_option
            
            if user_answer:
                is_correct = user_answer.is_correct
                if is_correct:
                    correct_count += 1
                else:
                    incorrect_count += 1
            else:
                is_correct = False
                unanswered_count += 1
            
            results_data.append({
                'number': i,
                'question': question,
                'options': question.options.all(),
                'user_answer': user_answer,
                'correct_option': correct_option,
                'is_correct': is_correct,
                'is_answered': user_answer is not None,
            })
        
        # Calculate topic-wise performance
        topic_performance = {
            'correct': correct_count,
            'incorrect': incorrect_count,
            'unanswered': unanswered_count,
            'percentage': quiz_session.percentage_score,
        }
        
        context.update({
            'results_data': results_data,
            'topic_performance': topic_performance,
            'can_retake': True,  # Allow retaking quizzes
        })
        return context
