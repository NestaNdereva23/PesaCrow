from django.urls import path
from projects import views

app_name = "projects"

urlpatterns = [
    path('', views.projectrequest, name="projectrequest"),
    path('developer/projects/', views.developers_projects, name="developers_projects"),  # Developers see project requests
    path('developer/projects/accept/<int:project_id>/', views.accept_project, name="accept_project"),  # Accept project request

]