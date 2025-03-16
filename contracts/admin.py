from django.contrib import admin
from .models import Contract, ContractSection, ContractTemplate
# Register your models here.

admin.site.register(Contract)
admin.site.register(ContractSection)
admin.site.register(ContractTemplate)
