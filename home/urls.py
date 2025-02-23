from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('login/', views.login, name='login'),

    path('register/', views.registration, name='register'),

    path('login/password_reset/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"), name="password_reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name="password_reset_done"),

]