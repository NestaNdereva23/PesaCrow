
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('home/', include('home.urls')),
    path('profile/', include('profiles.urls')),
    path('projects/', include('projects.urls')),
    path('contracts/', include('contracts.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    path('admin/', admin.site.urls),    
]
