from django import forms
from .models import Dispute, DisputeMessage, Evidence, DECISION_CHOICES


class DisputeForm(forms.ModelForm):
    class Meta:
        model = Dispute
        fields = ['issue_summary', 'detailed_reason']


class DisputeMessageForm(forms.ModelForm):
    class Meta:
        model = DisputeMessage
        fields = ['message']


class EvidenceForm(forms.ModelForm):
    class Meta:
        model = Evidence
        fields = ['file', 'description']


class RulingForm(forms.Form):
    decision = forms.ChoiceField(choices=DECISION_CHOICES)
    justification = forms.CharField(widget=forms.Textarea)
