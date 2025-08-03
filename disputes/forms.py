from django import forms
from .models import Dispute, DisputeMessage


class DisputeForm(forms.ModelForm):
    class Meta:
        model = Dispute
        fields = ['issue_summary', 'detailed_reason']


class DisputeMessageForm(forms.ModelForm):
    class Meta:
        model = DisputeMessage
        fields = ['message']
