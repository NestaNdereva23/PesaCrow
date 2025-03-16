# contracts/forms.py
from django import forms
from .models import ContractSection

class ContractSectionForm(forms.ModelForm):
    class Meta:
        model = ContractSection
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'})
        }