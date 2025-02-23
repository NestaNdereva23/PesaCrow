from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, forms, PasswordInput
from home.models import *
from django.core.exceptions import ValidationError
from django.db.models import CharField

class RegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_confirm_password(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("password2")

        if password != confirm_password:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email already registered')
        return email