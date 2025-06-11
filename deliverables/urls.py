from django.urls import path
from . import views

app_name = 'deliverables'

urlpatterns = [
    # Developer views (require login)
    path('milestone/<int:milestone_id>/', views.submit_deliverable, name='milestone_detail'),
    path('deliverables_list/', views.deliverables_list, name='deliverable_list')

]