from django.urls import path
from payment import views

app_name = 'payment'

urlpatterns = [
    path('milestone/<int:milestone_id>/pay/', views.pay_milestone, name='pay_milestone'),

    path('milestone-payment/', views.milestone_payment, name='milestone_payment'),
    path('check-transaction-status/', views.check_transaction_status, name='check_transaction_status'),

    path('mpesa/callback', views.mpesa_callback, name='mpesa_callback'),

    
    path('milestone/<int:milestone_id>/payment-success/', views.payment_success, name='payment_success'),
    # path('milestone/<int:milestone_id>/payment-cancel/', views.payment_cancel, name='payment_cancel'),

    ]