from django.urls import path
from . import views

urlpatterns = [
    path('seances/', views.participant_seances, name='participant-seances'),
    path('events/', views.participant_events, name='participant-events'),
]
