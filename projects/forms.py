from django.forms import ModelForm, forms
from projects.models import ProjectRequest, Milestone
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

class MilestonesForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'deliverables', 'payment_amount', 'estimated_completion',
                  ]
        widgets = {
            'estimated_completion': forms.DateInput(attrs={'type': 'date'}),
        }

    #ensure each milestone maps to current project request
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            self.project = project

            if 'project' in self.fields:
                self.fields['project'].widget = forms.HiddenInput()
                self.fields['project'].initial = project.id

    def save(self, commit=True):
        instance = super().save(commit=False)
        if hasattr(self, 'project'):
            instance.project = self.project
        if commit:
            instance.save()
        return instance
    
class EditMilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'deliverables', 'payment_amount', 'estimated_completion',
                  ]
        widgets = {
            'estimated_completion': forms.DateInput(attrs={'type': 'date'}),
        }
