from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test_list_create, name='test-list-create'),
    path('test/<uuid:pk>/', views.test_detail_update_delete, name='test-detail-update-delete'),
    path('notes/', views.note_list_create, name='note-list-create'),
    path('notes/<uuid:pk>/', views.note_detail_update_delete, name='note-detail-update-delete'),
    path('notes/all/', views.all_notes_index)
]
