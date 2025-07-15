from django import forms
from .models import Dispute

class DisputeForm(forms.ModelForm):
    class Meta:
        model = Dispute
        fields = ['issue_summary', 'detailed_reason']
        widgets = {
            'issue_summary': forms.TextInput(attrs={'placeholder': 'Short description of the dispute'}),
            'detailed_reason': forms.Textarea(attrs={'placeholder': "Explain why you're initiating this dispute..."}),
        }

# , 'desired_resolution'