from django.db import models
from django.contrib.auth.models import User

# Defines the possible statuses for a project
PROJECT_STATUS = [
    ("Pending", "Pending"),
    ("Active", "Active"), 
    ("Completed", "Completed"),
    ("Cancelled", "Cancelled"),
]
# Defines the possible statuses for a project
MILESTONE_STATUS = [
    ("Pending", "Pending"),      # Waiting to be worked on
    ("Active", "Active"),        # Currently being worked on
    ("Completed", "Completed"),  # Work finished
    ("Cancelled", "Cancelled"),  # Milestone cancelled
]

PAYMENT_STATUS = [
    ("Unpaid", "Unpaid"),        # Not yet paid
    ("Processing", "Processing"), # Payment initiated (STK push sent)
    ("Paid", "Paid"),           # Payment successful
    ("Failed", "Failed"),       # Payment failed
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
    status = models.CharField(max_length=255, choices=MILESTONE_STATUS, default="Pending")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="Unpaid")
    order_number = models.IntegerField()
    
    def __str__(self):
        return f'{self.project} + {self.title}'

    @property
    def latest_payment(self):
        """most recent payment attempt for this milestone"""
        return self.payment.order_by('-id').first()
    
    @property 
    def is_paid(self):
        """check if milestone has been successfully paid"""
        return self.payment_status == 'Paid'

    @property
    def pending_deliverables(self):
        """Get deliverables awaiting review"""
        return self.milestone_deliverables.filter(status='pending')

    @property
    def has_pending_deliverables(self):
        """Check if milestone has deliverables awaiting review"""
        return self.pending_deliverables.exists()











