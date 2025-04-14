from django.urls import path
from projects import views

app_name = "projects"

urlpatterns = [
    path('client/projects/', views.projectrequest, name="projectrequest"),

    path('developer/projects/', views.developers_projects, name="developers_projects"),  # Developers see project requests
    
    path('developer/projects/accept/<int:project_id>/', views.accept_project, name="accept_project"),# Accept project request

    path('developer/projects/milestones/<int:project_id>/', views.create_milestones, name="milestones"),

    path("developer/projects/milestones/<int:milestone_id>/edit/", views.edit_milestone, name="edit_milestone"),

    path("milestones/<int:id>/", views.client_milestone_verification, name="client_verify_milestone"),

]