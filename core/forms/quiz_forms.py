"""
Quiz-related forms for MedPrep application
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

from ..models import Topic, Question


class QuizSettingsForm(forms.Form):
    """Form to configure quiz settings"""
    
    DIFFICULTY_CHOICES = [
        ('all', 'All Difficulties'),
    ] + Question.DIFFICULTY_CHOICES
    
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    difficulty = forms.ChoiceField(
        choices=DIFFICULTY_CHOICES,
        required=False,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    number_of_questions = forms.IntegerField(
        min_value=5,
        max_value=100,
        initial=20,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    time_limit = forms.IntegerField(
        min_value=5,
        max_value=180,
        initial=30,
        help_text="Time limit in minutes",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('topic', css_class='form-group mb-3'),
            Row(
                Column('difficulty', css_class='form-group col-md-6 mb-3'),
                Column('number_of_questions', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Field('time_limit', css_class='form-group mb-3'),
            Submit('submit', 'Start Quiz', css_class='btn btn-primary btn-lg')
        )
        
        # Filter topics based on user's premium status
        if user and hasattr(user, 'userprofile'):
            if not user.userprofile.is_premium_active:
                # Show only free topics
                self.fields['topic'].queryset = Topic.objects.filter(
                    is_active=True,
                    questions__is_premium=False
                ).distinct()
    
    def clean(self):
        cleaned_data = super().clean()
        topic = cleaned_data.get('topic')
        difficulty = cleaned_data.get('difficulty')
        number_of_questions = cleaned_data.get('number_of_questions')
        
        if topic:
            # Check if topic has enough questions
            questions_query = topic.questions.filter(is_active=True)
            
            if difficulty and difficulty != 'all':
                questions_query = questions_query.filter(difficulty=difficulty)
            
            available_questions = questions_query.count()
            
            if available_questions < number_of_questions:
                raise forms.ValidationError(
                    f"This topic only has {available_questions} questions "
                    f"available for the selected difficulty. "
                    f"Please reduce the number of questions or select a different difficulty."
                )
        
        return cleaned_data
