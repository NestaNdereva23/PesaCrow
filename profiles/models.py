from django.db import models

from django.contrib.auth.models import User

ROLE_TYPES = [
    ("Client", "Client"),
    ("Developer", "Developer"),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
    role_type = models.CharField(max_length=255, choices=ROLE_TYPES, default="CLIENT")
    phone_number = models.CharField(max_length=11, unique=True)
    mpesa_number = models.CharField(max_length=11, unique=True)
    payment_details = models.JSONField(null=True, blank=True)
    portfolio_url = models.URLField()
    rating_as_client = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    rating_as_developer = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
