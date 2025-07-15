from django import forms
from .models import Deliverable, DeliverableReview

class DeliverableSubmissionForm(forms.ModelForm):
    files = forms.FileField(
        # widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False,
        label="Upload Files"
    )
    submission_link = forms.URLField(
        required=False,
        label="External Link (Google Drive, GitHub, etc.)"
    )

    class Meta:
        model = Deliverable
        fields = ['title', 'description', 'submission_type', 'reviewer_comments']

    def clean(self):
        cleaned_data = super().clean()
        submission_type = cleaned_data.get("submission_type")
        submission_link = cleaned_data.get("submission_link")
        files = self.files.getlist("files")

        if submission_type == "file" and not files:
            raise forms.ValidationError("Please upload at least one file.")
        if submission_type == "link" and not submission_link:
            raise forms.ValidationError("Please provide a valid external link.")

        return cleaned_data

class DeliverableReviewForm(forms.ModelForm):
    class Meta:
        model = DeliverableReview
        fields = ['deliverable', 'reviewer', 'decision', 'comments']

    def clean_comments(self):
        comments = self.cleaned_data.get('comments')
        if not comments or len(comments.strip()) < 10:
            raise forms.ValidationError("Please provide detailed feedback (at least 10 characters).")
        return comments