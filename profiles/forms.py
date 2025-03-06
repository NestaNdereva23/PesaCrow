from django.contrib.auth.models import User
from profiles.models import  UserProfile
from django import forms

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']



class ContactUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role_type','phone_number', 'mpesa_number']