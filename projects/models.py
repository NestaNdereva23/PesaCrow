from django.db import models
from django.contrib.auth.models import User

PROJECT_STATUS = [
    ("Active", "Active"),
    ("Pending", "Pending"),
    ("Completed", "Completed"),
]

class ProjectRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    sender_email = models.EmailField(max_length=255)
    receiver_email = models.EmailField(max_length=255)
    title = models.CharField(max_length=255)
    project_description = models.TextField(max_length=1000)
    status = models.CharField(max_length=255, choices=PROJECT_STATUS, default="Pending")
    budget = models.DecimalField(decimal_places=2, max_digits=12, null=True)
    verified = models.BooleanField(default=False)
    requirements = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Milestone(models.Model):
    project = models.ForeignKey(ProjectRequest, on_delete=models.CASCADE, related_name="project_milestones")
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)
    deliverables = models.CharField(max_length=255)
    payment_amount = models.DecimalField(decimal_places=2, max_digits=12, null=True)
    estimated_completion = models.DateField()
    status = models.CharField(max_length=255, choices=PROJECT_STATUS, default="Pending")
    order_number = models.IntegerField()

    def __str__(self):
        return f'{self.project} + {self.title}'






