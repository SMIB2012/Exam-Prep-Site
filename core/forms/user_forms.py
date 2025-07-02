"""
User-related forms for MedPrep application
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

from ..models import UserProfile


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form that accepts both username and email"""
    
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address or username',
            'autofocus': True
        }),
        label='Email or Username'
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username is not None and password:
            # Check if the input is an email
            if '@' in username:
                # Try to find user by email
                try:
                    user = User.objects.get(email=username)
                    username = user.username
                except User.DoesNotExist:
                    pass
            
            # Authenticate with username (either original or converted from email)
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data


class UserRegistrationForm(UserCreationForm):
    """Extended user registration form"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    year_of_study = forms.ChoiceField(
        choices=UserProfile.YEAR_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
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
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_province'})
    )
    college_type = forms.ChoiceField(
        choices=[
            ('', 'Select Type'),
            ('Public', 'Public'),
            ('Private', 'Private'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_college_type'})
    )
    college_name = forms.ChoiceField(
        choices=[('', 'Select province and type first')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_college_name', 'disabled': True})
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('username', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-3'),
                Column('password2', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('year_of_study', css_class='form-group col-md-6 mb-3'),
                Column('phone_number', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('province', css_class='form-group col-md-6 mb-3'),
                Column('college_type', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Field('college_name', css_class='form-group mb-3'),
            Submit('submit', 'Register', css_class='btn btn-primary btn-lg')
        )
        
        # Add custom styling to password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        # Add custom validation for college selection
        if 'province' in self.data and 'college_type' in self.data:
            self.update_college_choices()
    
    def update_college_choices(self):
        """Update college choices based on province and college type"""
        province = self.data.get('province')
        college_type = self.data.get('college_type')
        
        # Medical colleges data
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
            self.fields['college_name'].widget.attrs.pop('disabled', None)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Get or create user profile and update it with form data
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.year_of_study = self.cleaned_data['year_of_study']
            profile.province = self.cleaned_data['province']
            profile.college_type = self.cleaned_data['college_type']
            profile.college_name = self.cleaned_data['college_name']
            profile.phone_number = self.cleaned_data.get('phone_number', '')
            profile.save()
        return user


class UserProfileForm(forms.ModelForm):
    """User profile edit form"""
    
    class Meta:
        model = UserProfile
        fields = [
            'year_of_study', 'province', 'college_type', 'college_name', 'phone_number', 'profile_picture'
        ]
        widgets = {
            'year_of_study': forms.Select(attrs={'class': 'form-control'}),
            'province': forms.Select(attrs={'class': 'form-control'}),
            'college_type': forms.Select(attrs={'class': 'form-control'}),
            'college_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('year_of_study', css_class='form-group col-md-6 mb-3'),
                Column('phone_number', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Field('college_name', css_class='form-group mb-3'),
            Field('profile_picture', css_class='form-group mb-3'),
            Submit('submit', 'Update Profile', css_class='btn btn-primary')
        )
