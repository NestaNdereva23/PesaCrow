from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid
import os
from projects.models import Milestone

DELIVERABLE_STATUS = [
    ("pending", "Pending Review"),
    ("approved", "Approved"),
    ("revision_requested", "Revision Requested"),
    ("rejected", "Rejected"),
]

SUBMISSION_TYPE = [
    ("file", "File Upload"),
    ("link", "External Link"),
]


class Deliverable(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name="milestone_deliverables")
    developer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submitted_deliverables")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    submission_type = models.CharField(max_length=10, choices=SUBMISSION_TYPE, default="link")
    submission_link = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=DELIVERABLE_STATUS, default="pending")
    review_token = models.UUIDField(default=uuid.uuid4, unique=True)  # For secure review links
    reviewer_comments = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.title} - {self.milestone.title}"
    
    def get_review_url(self):
        """Generate secure review URL for clients"""
        return reverse('deliverable_review', kwargs={'token': self.review_token})
    
    @property
    def client(self):
        """Get the client for this deliverable"""
        return User.objects.get(email=self.milestone.project.receiver_email)

def deliverable_file_path(instance, filename):
    """Generate file path for deliverable uploads"""
    # Create path: deliverables/project_id/milestone_id/filename
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('deliverables', str(instance.deliverable.milestone.project.id), 
                    str(instance.deliverable.milestone.id), filename)

# class DeliverableFile(models.Model):
#     deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE, related_name="files")
#     original_filename = models.CharField(max_length=255)
#     file = models.FileField(upload_to=deliverable_file_path)
#     file_size = models.BigIntegerField()  # in bytes
#     mime_type = models.CharField(max_length=100)
#     uploaded_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return self.original_filename
    
#     @property
#     def formatted_size(self):
#         """Return human-readable file size"""
#         size = self.file_size
#         for unit in ['B', 'KB', 'MB', 'GB']:
#             if size < 1024.0:
#                 return f"{size:.1f} {unit}"
#             size /= 1024.0
#         return f"{size:.1f} TB"

class DeliverableReview(models.Model):
    """Track review history and comments"""
    deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    decision = models.CharField(max_length=20, choices=DELIVERABLE_STATUS)
    comments = models.TextField()
    reviewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-reviewed_at']
 
    def __str__(self):
        return f"Review for {self.deliverable.title} - {self.decision}"


