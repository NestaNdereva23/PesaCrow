from django.urls import path
from . import views

app_name = 'disputes'

urlpatterns = [

    path('disputes_list/', views.disputes_list, name="disputes_list"),
    path('dispute/<int:dispute_id>/', views.raise_dispute, name="dispute"),
    path('disputes/resolve_dispute/<int:dispute_id>/', views.resolve_dispute, name="resolve_dispute"),
    path('<int:dispute_id>/escalate/manual/', views.escalate_dispute_manually, name='escalate_dispute_manually'),


]