from django import forms
from .models import ContractSection

class ContractSectionForm(forms.ModelForm):
    class Meta:
        model = ContractSection
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 10, 
                'class': 'w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500'
            })
        }