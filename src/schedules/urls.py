from django.urls import path, re_path
from . import views

urlpatterns = [
    # Path format: /api/schedules/{monthKey} where monthKey is YYYY-MM
    re_path(r'^(?P<monthKey>\d{4}-\d{2})/$', views.schedule_detail, name='schedule-detail'),
]
