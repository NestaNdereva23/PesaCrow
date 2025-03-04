
from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

app_name = "home"
urlpatterns = [
    path('', views.homepage, name='home'),
    path('login/', views.login_page, name='login'),

    path('register/', views.registration, name='register'),

    path('login/password_reset/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"), name="password_reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name="password_reset_done"),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

]