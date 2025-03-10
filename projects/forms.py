from django.forms import ModelForm, forms
from projects.models import ProjectRequest
from django.core.exceptions import ValidationError
from django import forms


class ProjectRequestForm(forms.ModelForm):
    class Meta:
        model = ProjectRequest
        fields = ['title', 'project_description', 'budget', 'receiver_email']
        widgets = {
            'project_description': forms.Textarea(attrs={'rows': 4}),
        }
