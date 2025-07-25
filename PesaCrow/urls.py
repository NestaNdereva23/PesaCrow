
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('home/', include('home.urls')),
    path('profile/', include('profiles.urls')),
    path('projects/', include('projects.urls')),
    path('contracts/', include('contracts.urls')),
    path('payment/', include('payment.urls')),
    path('deliverables/', include('deliverables.urls')),
    path('disputes/', include('disputes.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    path('admin/', admin.site.urls),    
]
