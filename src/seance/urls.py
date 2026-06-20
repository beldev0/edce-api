from django.urls import path
from . import views

urlpatterns = [
    path('', views.seance_list_create, name='seance-list-create'),
    path('<uuid:pk>/', views.seance_detail_update_delete, name='seance-detail-update-delete'),
]