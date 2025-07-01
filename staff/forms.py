from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from core.models import Question, Option, Subject, Topic, Tag, Note, VideoResource, Flashcard, PaymentProof, UserProfile
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
        fields = ['topic', 'question_text', 'explanation', 'difficulty', 'is_premium', 'tags', 'is_active'
        ]
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
            ('', 'All Subscriptions'),
            ('premium', 'Premium Users'),
            ('free', 'Free Users'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    is_active = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Status'),
            ('true', 'Active'),
            ('false', 'Inactive'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    year_filter = forms.ChoiceField(
        required=False,
        choices=[('', 'All Years')] + [
            ('1st_year', '1st Year MBBS'),
            ('2nd_year', '2nd Year MBBS'),
            ('3rd_year', '3rd Year MBBS'),
            ('4th_year', '4th Year MBBS'),
            ('final_year', '5th Year MBBS (Final)'),
            ('graduate', 'Graduate'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class UserCreateForm(forms.ModelForm):
    """Form for creating new users by admin"""
    
    # User fields
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    # Profile fields
    year_of_study = forms.ChoiceField(
        choices=[('', 'Select Year of Study')] + UserProfile.YEAR_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    province = forms.ChoiceField(
        choices=[
            ('', 'Select Province'),
            ('Punjab', 'Punjab'),
            ('Sindh', 'Sindh'),
            ('Khyber Pakhtunkhwa', 'Khyber Pakhtunkhwa'),
            ('Balochistan', 'Balochistan'),
            ('Azad Jammu & Kashmir', 'Azad Jammu & Kashmir'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_province'
        })
    )
    college_type = forms.ChoiceField(
        choices=[
            ('', 'Select College Type'), 
            ('Public', 'Public'), 
            ('Private', 'Private')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_college_type'
        })
    )
    college_name = forms.ChoiceField(
        choices=[('', 'Select province and type first')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_college_name'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number'
        })
    )
    
    # Admin fields
    user_role = forms.ChoiceField(
        choices=[
            ('student', 'Student'),
            ('faculty', 'Faculty'),
            ('admin', 'Admin'),
        ],
        initial='student',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    is_premium = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    is_active = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    # Additional options
    send_welcome_email = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Send a welcome email with login credentials to the user"
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update college choices if province and college_type are provided
        if 'province' in self.data and 'college_type' in self.data:
            self.update_college_choices()
    
    def update_college_choices(self):
        """Update college choices based on province and college type"""
        province = self.data.get('province')
        college_type = self.data.get('college_type')
        
        # Medical colleges data (same as signup form)
        medical_colleges = {
            "Punjab": {
                "Public": [
                    "Allama Iqbal Medical College (Lahore)",
                    "Ameer-ud-Din (PGMI) Medical College (Lahore)",
                    "Army Medical College (Rawalpindi)",
                    "D.G. Khan Medical College (Dera Ghazi Khan)",
                    "Fatima Jinnah Medical College (Lahore)",
                    "Services Institute of Medical Sciences (Lahore)",
                    "Gujranwala Medical College",
                    "Khawaja Muhammad Safdar MC (Sialkot)",
                    "King Edward Medical University (Lahore)",
                    "Nawaz Sharif Medical College (Gujrat)",
                    "Nishtar Medical College (Multan)",
                    "Punjab Medical College (Faisalabad)",
                    "Quaid‑e‑Azam Medical College (Bahawalpur)",
                    "Rawalpindi Medical College (Rawalpindi)",
                    "Sahiwal Medical College",
                    "Sargodha Medical College",
                    "Shaikh Khalifa Bin Zayed MC (Lahore)",
                    "Sheikh Zayed Medical College (Rahim Yar Khan)",
                    "Narowal Medical College"
                ],
                "Private": [
                    "FMH College of Medicine & Dentistry (Lahore)",
                    "Lahore Medical & Dental College",
                    "University College of Medicine & Dentistry (Lahore)",
                    "Al Aleem Medical College",
                    "Rahbar Medical College",
                    "Rashid Latif Medical College",
                    "Azra Naheed Medical College",
                    "Pak Red Crescent Medical College",
                    "Sharif Medical & Dental College",
                    "Continental Medical College",
                    "Akhtar Saeed Medical College",
                    "CMH Lahore Medical & Dental College",
                    "Shalamar Medical & Dental College",
                    "Avicenna Medical College",
                    "Abwa Medical College",
                    "Independent Medical College",
                    "Aziz Fatima Medical College",
                    "Multan Medical & Dental College",
                    "Bakhtawar Amin Medical & Dental College",
                    "Central Park Medical College",
                    "CIMS Multan",
                    "HITEC Institute of Medical Sciences",
                    "Hashmat Medical & Dental College",
                    "Shahida Islam Medical College",
                    "Wah Medical College",
                    "Sahara Medical College",
                    "CMH Kharian Medical College",
                    "M. Islam Medical College",
                    "Islam Medical College",
                    "Fazaia Medical College",
                    "Rai Medical College",
                    "Margalla Institute of Health Sciences",
                    "Mohammad Dental College",
                    "Islamabad Medical & Dental College",
                    "Yusra Medical & Dental College"
                ]
            },
            "Sindh": {
                "Public": [
                    "Dow Medical College",
                    "Dow International Medical College",
                    "Karachi Medical & Dental College",
                    "Chandka Medical College (Larkana)",
                    "Ghulam Muhammad Mahar Medical College (Sukkur)",
                    "Liaquat University of Medical & Health Sciences (Jamshoro)",
                    "Peoples UMHS for Women (Nawabshah)",
                    "Shaheed Mohtarma Benazir Bhutto MC (Lyari, Karachi)",
                    "Jinnah Sindh Medical University",
                    "Khairpur Medical College",
                    "Bilawal Medical College (Hyderabad)"
                ],
                "Private": [
                    "Aga Khan University",
                    "Baqai Medical College",
                    "Hamdard College of Medicine & Dentistry",
                    "Jinnah Medical & Dental College",
                    "Sir Syed College of Medical Sciences",
                    "Ziauddin Medical College",
                    "Liaquat National Medical College",
                    "Bahria University Medical College",
                    "Karachi Institute of Medical Sciences",
                    "Al‑Tibri Medical College",
                    "United Medical & Dental College",
                    "Indus Medical College (Tando Muhammad Khan)",
                    "Isra University Hyderabad",
                    "Muhammad Medical College (Mirpurkhas)",
                    "Suleman Roshan Medical College (Tando Adam)",
                    "Fazaia Ruth Pfau Medical College (Karachi)"
                ]
            },
            "Khyber Pakhtunkhwa": {
                "Public": [
                    "Khyber Medical College (Peshawar)",
                    "Khyber Girls Medical College",
                    "Ayub Medical College (Abbottabad)",
                    "Saidu Medical College (Swat)",
                    "Gomal Medical College (D.I. Khan)",
                    "KMU Institute of Medical Sciences (Kohat)",
                    "Bannu Medical College",
                    "Bacha Khan Medical College (Mardan)",
                    "Gajju Khan Medical College (Swabi)",
                    "Nowshera Medical College"
                ],
                "Private": [
                    "Abbottabad International Medical College",
                    "Al‑Razi Medical College",
                    "Frontier Medical College (Abbottabad)",
                    "Kabir Medical College (Peshawar)",
                    "Northwest School of Medicine",
                    "Pak International Medical College",
                    "Peshawar Medical College",
                    "Rehman Medical College",
                    "Women Medical & Dental College (Abbottabad)",
                    "Swat Medical College",
                    "Jinnah Medical College (Peshawar)"
                ]
            },
            "Balochistan": {
                "Public": [
                    "Bolan Medical College (Quetta)",
                    "Loralai Medical College",
                    "Makran Medical College (Turbat)",
                    "Jhalawan Medical College (Khuzdar)"
                ],
                "Private": [
                    "Quetta Institute of Medical Sciences (Quetta)"
                ]
            },
            "Azad Jammu & Kashmir": {
                "Public": [
                    "Azad Jammu & Kashmir Medical College (Muzaffarabad)",
                    "Mohtarma Benazir Bhutto Shaheed Medical College (Mirpur)",
                    "Poonch Medical College (Rawalakot)"
                ],
                "Private": [
                    "Mohiuddin Islamic Medical College (Mirpur)"
                ]
            }
        }
        
        if province and college_type and province in medical_colleges and college_type in medical_colleges[province]:
            choices = [('', 'Select medical college')]
            for college in medical_colleges[province][college_type]:
                choices.append((college, college))
            self.fields['college_name'].choices = choices
        
    def clean_email(self):
        """Ensure email is unique"""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def clean_confirm_password(self):
        """Ensure passwords match"""
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return confirm_password
    
    def clean_password(self):
        """Validate password strength"""
        password = self.cleaned_data.get('password')
        if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password
    
    def clean(self):
        """Additional form validation"""
        cleaned_data = super().clean()
        user_role = cleaned_data.get('user_role', 'student')
        year_of_study = cleaned_data.get('year_of_study')
        
        # Validate year of study for students
        if user_role == 'student' and not year_of_study:
            self.add_error('year_of_study', 'Year of study is required for students.')
        
        # Clear year of study for non-students
        if user_role != 'student':
            cleaned_data['year_of_study'] = ''
        
        return cleaned_data
