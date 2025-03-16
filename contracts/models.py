from django.db import models
from projects.models import ProjectRequest

"""Store predefined contract clauses"""
class ContractTemplate(models.Model):
    name = models.CharField(max_length=255)
    section_key = models.CharField(max_length=50, unique=True)
    content = models.TextField()

    def __str__(self):
        return self.name

class Contract(models.Model):
    project = models.OneToOneField(ProjectRequest, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    signed_by_client = models.BooleanField(default=False)
    signed_by_developer = models.BooleanField(default=False)
    client_signature_date = models.DateTimeField(null=True, blank=True)
    developer_signature_date = models.DateTimeField(null=True, blank=True)

class ContractSection(models.Model):
    """individual sections/clauses of a specific contract """
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="sections")
    template = models.ForeignKey(ContractTemplate, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    editable = models.BooleanField(default=True)
    order = models.IntegerField()

