
from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

from .views import dashboard_view

# from .views import DashboardView

app_name = "home"
urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('', views.homepage, name='home'),
    path('login/', views.login_page, name="login"),
    path("logout/", views.logoutPage, name="logout"),

    path('register/', views.RegistrationView.as_view(), name='register'),

    path('login/password_reset/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"), name="password_reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name="password_reset_done"),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-disputes/', views.admin_disputes, name='admin_disputes'),

    # path('dashboard/project_detail<int:id>' views.d)


]