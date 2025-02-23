from . import views
from django.urls import path

urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('login/', views.login, name='login'),

    path('register/', views.registration, name='register'),
]