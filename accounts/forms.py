# accounts/forms.py - VULNERABLE VERSION (BEFORE HARDENING)
import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile


class GuestRegistrationForm(forms.ModelForm):
    # VULNERABLE: No minimum length enforcement
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        # min_length=10  # DISABLED - no minimum length
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
        # VULNERABLE: No whitelist validation - accepts any characters
        # Attack: username = "<script>alert('XSS')</script>"
        u = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=u).exists():
            raise forms.ValidationError('Username already taken.')
        return u

    def clean_email(self):
        # VULNERABLE: No email format validation
        e = self.cleaned_data['email'].strip().lower()
        return e

    def clean_first_name(self):
        # VULNERABLE: No sanitization - accepts HTML/scripts
        return self.cleaned_data['first_name'].strip()

    def clean_last_name(self):
        # VULNERABLE: No sanitization
        return self.cleaned_data['last_name'].strip()

    def clean_phone(self):
        # VULNERABLE: No format validation
        return self.cleaned_data.get('phone', '').strip()

    def clean_password1(self):
        # VULNERABLE: No complexity requirements
        # Accepts "123", "aaa", "password"
        return self.cleaned_data.get('password1', '')

    def clean(self):
        cd = super().clean()
        if cd.get('password1') != cd.get('password2'):
            raise forms.ValidationError('Passwords do not match.')
        return cd

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = 'guest'
            profile.phone = self.cleaned_data.get('phone', '')
            profile.nationality = self.cleaned_data.get('nationality', '')
            profile.save()
        return user


class SecureLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,  # VULNERABLE: Too long, no format check
        widget=forms.TextInput(attrs={'autocomplete': 'username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )

    def clean_username(self):
        # VULNERABLE: No format validation - accepts any characters
        return self.cleaned_data['username'].strip()


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