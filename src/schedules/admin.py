from django.contrib import admin
from .models import Schedule, ScheduleRow, ScheduleAssignment


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['monthKey', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'monthKey']
    search_fields = ['monthKey']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ScheduleRow)
class ScheduleRowAdmin(admin.ModelAdmin):
    list_display = ['schedule', 'dateLabel', 'created_at']
    list_filter = ['schedule__monthKey']
    search_fields = ['dateLabel']
    readonly_fields = ['id']


@admin.register(ScheduleAssignment)
class ScheduleAssignmentAdmin(admin.ModelAdmin):
    list_display = ['row', 'teacher', 'seance_type', 'created_at']
    list_filter = ['seance_type', 'row__schedule__monthKey']
    search_fields = ['teacher__email']
    readonly_fields = ['id']
