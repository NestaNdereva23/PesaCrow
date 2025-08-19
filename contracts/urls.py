from django.urls import path
from . import views

app_name = "contracts"

urlpatterns = [
    path('', views.contract, name='contract'),
    path('edit_contract/<int:contract_id>/', views.edit_contract, name='edit_contract'),
    path('review_contract/<int:contract_id>/', views.review_contract, name='review_contract'),
    path('view_contract/<int:contract_id>/', views.view_contract, name='view_contract'),
    path('download_contract_pdf/<int:contract_id>/', views.download_contract_pdf, name='download_contract_pdf'),
]