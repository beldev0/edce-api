from django.urls import path
from . import views

urlpatterns = [
    # Routes Activity
    path('activities/', views.activity_list_create, name='activity-list-create'),
    path('activities/<uuid:pk>/', views.activity_detail_update_delete, name='activity-detail-update-delete'),
    
    # Routes EventActivity (Liaisons)
    path('event-activities/', views.event_activity_list_create, name='event-activity-list-create'),
    path('event-activities/<uuid:pk>/', views.event_activity_detail_update_delete, name='event-activity-detail-update-delete'),

    path('participants/', views.participant_event_list_create, name='participant-event-list-create'),
    path('participants/<uuid:pk>/', views.participant_event_delete, name='participant-event-delete'),
]