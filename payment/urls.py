from django.urls import include, path
from payment import views

app_name = 'payment'

urlpatterns = [
    path('milestone_payment/', views.milestone_payment, name='milestone_payment'),
    path('check-transaction-status/', views.check_transaction_status, name='check_transaction_status'),

    path('mpesa/callback', views.mpesa_callback, name='mpesa_callback'),
]