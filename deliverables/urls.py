from django.urls import path
from . import views

app_name = 'deliverables'

urlpatterns = [
    # Developer views (require login)
    path('milestone/<int:milestone_id>/', views.submit_deliverable, name='milestone_detail'),
    path('deliverables_list/', views.deliverables_list, name='deliverable_list'),

    path('review/<int:deliverable_id>/', views.review_deliverables, name='review_deliverables')
]