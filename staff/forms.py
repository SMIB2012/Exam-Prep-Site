from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from core.models import Question, Option, Subject, Topic, Tag, Note, VideoResource, Flashcard, PaymentProof
from django.forms import inlineformset_factory


class StaffLoginForm(AuthenticationForm):
    """Custom login form for staff/admin users"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'id': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username/Email'
        self.fields['password'].label = 'Password'


class TagForm(forms.ModelForm):
    """Form for creating and editing tags"""
    
    class Meta:
        model = Tag
        fields = ['name', 'parent', 'description', 'color', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tag name'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active tags as parent options
        self.fields['parent'].queryset = Tag.objects.filter(is_active=True)
        # Exclude current tag from parent options to prevent self-reference
        if self.instance.pk:
            self.fields['parent'].queryset = self.fields['parent'].queryset.exclude(pk=self.instance.pk)


class QuestionForm(forms.ModelForm):
    """Form for creating and editing questions"""
    
    class Meta:
        model = Question
        fields = ['topic', 'question_text', 'explanation', 'difficulty', 'is_premium', 'tags', 'is_active']
        widgets = {
            'topic': forms.Select(attrs={
                'class': 'form-control'
            }),
            'question_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter the question text'
            }),
            'explanation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Explain the correct answer'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_premium': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tags': forms.CheckboxSelectMultiple(),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.filter(is_active=True)


class OptionForm(forms.ModelForm):
    """Form for question options"""
    
    class Meta:
        model = Option
        fields = ['option_text', 'is_correct', 'order']
        widgets = {
            'option_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option text'
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            })
        }


# Create formset for options
OptionFormSet = inlineformset_factory(
    Question, 
    Option, 
    form=OptionForm,
    extra=4,  # Show 4 option forms by default
    can_delete=True,
    min_num=2,  # Minimum 2 options
    validate_min=True
)


class BulkQuestionUploadForm(forms.Form):
    """Form for bulk uploading questions via CSV/Excel"""
    
    csv_file = forms.FileField(
        label="CSV/Excel File",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'
        }),
        help_text="Upload a CSV or Excel file with questions"
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text="Default subject for questions (can be overridden in file)"
    )


class ResourceForm(forms.ModelForm):
    """Base form for resources (Notes, Videos, Flashcards)"""
    
    class Meta:
        fields = ['topic', 'is_premium', 'tags', 'is_active']
        widgets = {
            'topic': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_premium': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tags': forms.CheckboxSelectMultiple(),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.filter(is_active=True)


class NoteForm(ResourceForm):
    """Form for creating and editing notes"""
    
    class Meta(ResourceForm.Meta):
        model = Note
        fields = ['title', 'content', 'pdf_file'] + ResourceForm.Meta.fields
        widgets = {
            **ResourceForm.Meta.widgets,
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Note title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Note content'
            }),
            'pdf_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            })
        }


class VideoResourceForm(ResourceForm):
    """Form for creating and editing video resources"""
    
    class Meta(ResourceForm.Meta):
        model = VideoResource
        fields = ['title', 'description', 'video_url', 'duration_minutes', 'thumbnail'] + ResourceForm.Meta.fields
        widgets = {
            **ResourceForm.Meta.widgets,
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Video title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Video description'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'YouTube/Vimeo URL'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Duration in minutes'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }


class FlashcardForm(ResourceForm):
    """Form for creating and editing flashcards"""
    
    class Meta(ResourceForm.Meta):
        model = Flashcard
        fields = ['front_text', 'back_text'] + ResourceForm.Meta.fields
        widgets = {
            **ResourceForm.Meta.widgets,
            'front_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Question or term'
            }),
            'back_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Answer or definition'
            })
        }


class PaymentReviewForm(forms.ModelForm):
    """Form for reviewing payment proofs"""
    
    REVIEW_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending Review')
    ]
    
    review_status = forms.ChoiceField(
        choices=REVIEW_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    admin_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional notes about the review'
        })
    )
    
    class Meta:
        model = PaymentProof
        fields = ['review_status', 'admin_notes']


class UserSearchForm(forms.Form):
    """Form for searching and filtering users"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, email, or username'
        })
    )
    
    subscription_status = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Users'),
            ('premium', 'Premium'),
            ('free', 'Free'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    is_active = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All'),
            ('true', 'Active'),
            ('false', 'Inactive'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
