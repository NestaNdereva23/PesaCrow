from django.db import models
import uuid
from projects.models import Milestone


# Create your models here.

class MilestonePayment(models.Model):
    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Complete', 'Complete'),
    ]
    milestone = models.OneToOneField(Milestone, on_delete=models.CASCADE, related_name='payment')
    transaction_no = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    mpesa_number = models.CharField(max_length=15)
    checkout_request_id = models.CharField(max_length=200)
    reference = models.CharField(max_length=40, blank=True)
    description = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='Pending')
    receipt_no = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.transaction_no} - {self.checkout_request_id}'
