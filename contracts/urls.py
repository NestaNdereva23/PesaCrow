from django.urls import path
from . import views

app_name = "contracts"

urlpatterns = [
    path('', views.contract, name='contract'),
    path('edit_contract/<int:contract_id>/', views.edit_contract, name='edit_contract'),
    path('review_contract/<int:contract_id>/', views.review_contract, name='review_contract'),
]