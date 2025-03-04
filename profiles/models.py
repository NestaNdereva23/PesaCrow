from django.db import models

from django.contrib.auth.models import User

ROLE_TYPES = [
    ("CLIENT", "Client"),
    ("DEVELOPER", "Developer"),
]

class UserRole(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    role_type = models.CharField(max_length=255, choices=ROLE_TYPES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserProfile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=11, unique=True)
    mpesa_number = models.CharField(max_length=11, unique=True)
    payment_details = models.JSONField()
    portfolio_url = models.URLField()
    rating_as_client = models.DecimalField(decimal_places=2, max_digits=10)
    rating_as_developer = models.DecimalField(decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
