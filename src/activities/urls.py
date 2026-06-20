from django.urls import path
from . import views

urlpatterns = [
    # Routes Activity
    path('activities/', views.activity_list_create, name='activity-list-create'),
    path('activities/<uuid:pk>/', views.activity_detail_update_delete, name='activity-detail-update-delete'),
    
    # Routes Events (EventActivity - Liaisons Activités-Événements)
    path('events/', views.event_activity_list_create, name='event-list-create'),
    path('events/<uuid:pk>/', views.event_activity_detail_update_delete, name='event-detail-update-delete'),
]