from django.urls import path
from . import views

urlpatterns = [
    path('', views.child_list_create, name='child-list-create'),
    path('<uuid:pk>/', views.child_detail_update_delete, name='child-detail-update-delete'),
]