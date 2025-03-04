
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('home/', include('home.urls')),
    path('profile/', include('profiles.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    path('admin/', admin.site.urls),
    

    
]
