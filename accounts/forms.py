import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile

USERNAME_RE   = re.compile(r'^[A-Za-z0-9._@+\-]{3,30}$')
NAME_RE       = re.compile(r'^[A-Za-zÀ-ÿ\s\'\-]{1,50}$')
PHONE_RE      = re.compile(r'^[\d\+\-\s\(\)]{7,20}$')
NATIONALITY_RE = re.compile(r'^[A-Za-zÀ-ÿ\s\-]{2,60}$')


class GuestRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        min_length=10,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text='At least 10 characters. Cannot be entirely numeric or a common password.',
    )
    password2   = forms.CharField(label='Confirm Password', widget=forms.PasswordInput())
    first_name  = forms.CharField(max_length=50)
    last_name   = forms.CharField(max_length=50)
    phone       = forms.CharField(max_length=20, required=False)
    nationality = forms.CharField(max_length=60, required=False)

    class Meta:
        model  = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_username(self):
        u = self.cleaned_data['username'].strip()
        if not USERNAME_RE.match(u):
            raise forms.ValidationError(
                'Username may only contain letters, digits, and @/./+/-/_. (3–30 characters)'
            )
        if User.objects.filter(username__iexact=u).exists():
            raise forms.ValidationError('Username already taken.')
        return u

    def clean_email(self):
        e = self.cleaned_data['email'].strip().lower()
        if not e:
            raise forms.ValidationError('Email address is required.')
        if User.objects.filter(email__iexact=e).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return e

    def clean_first_name(self):
        n = self.cleaned_data['first_name'].strip()
        if not NAME_RE.match(n):
            raise forms.ValidationError('First name contains invalid characters.')
        return n

    def clean_last_name(self):
        n = self.cleaned_data['last_name'].strip()
        if not NAME_RE.match(n):
            raise forms.ValidationError('Last name contains invalid characters.')
        return n

    def clean_phone(self):
        p = self.cleaned_data.get('phone', '').strip()
        if p and not PHONE_RE.match(p):
            raise forms.ValidationError('Enter a valid phone number.')
        return p

    def clean_nationality(self):
        nat = self.cleaned_data.get('nationality', '').strip()
        if nat and not NATIONALITY_RE.match(nat):
            raise forms.ValidationError('Nationality contains invalid characters.')
        return nat

    def clean_password1(self):
        pw = self.cleaned_data.get('password1', '')
        # Use Django's built-in password validators (configured in settings.py)
        validate_password(pw)
        return pw

    def clean(self):
        cd = super().clean()
        if cd.get('password1') != cd.get('password2'):
            raise forms.ValidationError('Passwords do not match.')
        return cd

    def save(self, commit=True):
        user = super().save(commit=False)
        # set_password uses bcrypt (configured in PASSWORD_HASHERS)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role        = 'guest'
            profile.phone       = self.cleaned_data.get('phone', '')
            profile.nationality = self.cleaned_data.get('nationality', '')
            profile.save()
        return user


class SecureLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'autocomplete': 'username'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    def clean_username(self):
        u = self.cleaned_data['username'].strip()
        if not USERNAME_RE.match(u):
            raise forms.ValidationError('Invalid username format.')
        return u


class ProfileUpdateForm(forms.ModelForm):
    first_name  = forms.CharField(max_length=50)
    last_name   = forms.CharField(max_length=50)
    email       = forms.EmailField()
    phone       = forms.CharField(max_length=20, required=False)
    nationality = forms.CharField(max_length=60, required=False)

    class Meta:
        model  = UserProfile
        fields = ['phone', 'nationality']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial  = self.user.last_name
            self.fields['email'].initial      = self.user.email

    def clean_first_name(self):
        n = self.cleaned_data['first_name'].strip()
        if not NAME_RE.match(n):
            raise forms.ValidationError('First name contains invalid characters.')
        return n

    def clean_last_name(self):
        n = self.cleaned_data['last_name'].strip()
        if not NAME_RE.match(n):
            raise forms.ValidationError('Last name contains invalid characters.')
        return n

    def clean_phone(self):
        p = self.cleaned_data.get('phone', '').strip()
        if p and not PHONE_RE.match(p):
            raise forms.ValidationError('Enter a valid phone number.')
        return p

    def clean_nationality(self):
        nat = self.cleaned_data.get('nationality', '').strip()
        if nat and not NATIONALITY_RE.match(nat):
            raise forms.ValidationError('Nationality contains invalid characters.')
        return nat

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name  = self.cleaned_data['last_name']
            self.user.email      = self.cleaned_data['email']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile
