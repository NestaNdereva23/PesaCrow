from django.db import models
from django.contrib.auth.models import User
from deliverables.models import Deliverable, Milestone

DISPUTE_STATUS = [
    ('open', 'Open'),
    ('resolved_by_parties', 'Resolved by Parties'),
    ('escalated', 'Escalated to Admin'),
    ('resolved_by_admin', 'Resolved by Admin'),
]

DECISION_CHOICES = [
    ('client_favored', 'Client Favored'),
    ('developer_favored', 'Developer Favored'),
    ('mutual_agreement', 'Mutual Agreement'),
    ('no_decision', 'No Decision Yet'),
]


class Dispute(models.Model):
    deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE, related_name='disputes')
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='disputes')

    raised_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='raised_disputes')
    raised_against = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disputes_against')

    issue_summary = models.CharField(max_length=255, help_text="Short description of the dispute")
    detailed_reason = models.TextField(help_text="Detailed explanation of the issue", blank=True, null=True)

    status = models.CharField(max_length=30, choices=DISPUTE_STATUS, default='open')
    decision = models.CharField(max_length=30, choices=DECISION_CHOICES, default='no_decision')

    is_escalated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    escalation_deadline = models.DateTimeField(help_text="Time by which the issue should be resolved before escalation")

    def __str__(self):
        """
        String representation of the Dispute object.
        """
        return f"Dispute: {self.issue_summary} (Status: {self.get_status_display()})"

    class Meta:
        """
        Meta options for the Dispute model.
        """
        verbose_name = "Dispute"
        verbose_name_plural = "Disputes"
        # Order disputes by creation date, newest first
        ordering = ['-created_at']


class DisputeMessage(models.Model):
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_dispute_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['created_at']