from django.forms import ModelForm, forms
from projects.models import ProjectRequest
from django.core.exceptions import ValidationError
from django import forms


class ProjectRequestForm(forms.ModelForm):
    class Meta:
        model = ProjectRequest
        fields = ['title', 'project_description', 'budget', 'receiver_email', 'sender_email']
        widgets = {
            'project_description': forms.Textarea(attrs={'rows': 4}),
        }

    #initialize the sender email with the current users email
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['sender_email'].initial = user.email
            self.fields['sender_email'].widget_attrs['readonly'] = True

