from django.db import models
from django.contrib.auth import get_user_model
from uuid import uuid4

User = get_user_model()


class Schedule(models.Model):
    """
    Modèle pour la gestion des plannings mensuels.
    Stocke les affectations des enseignants par date et type de séance.
    """
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    monthKey = models.CharField(max_length=7, unique=True)  # Format: YYYY-MM
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'draft'), ('published', 'published')],
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-monthKey']
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'

    def __str__(self):
        return f"Schedule {self.monthKey} ({self.status})"


class ScheduleRow(models.Model):
    """
    Modèle pour stocker chaque ligne du planning (une date + ses assignements).
    """
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='rows')
    dateLabel = models.CharField(max_length=100)  # Format: "Dimanche 07 Juin"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Schedule Row'
        verbose_name_plural = 'Schedule Rows'

    def __str__(self):
        return f"{self.schedule.monthKey} - {self.dateLabel}"


class ScheduleAssignment(models.Model):
    """
    Modèle pour stocker chaque assignement d'un enseignant.
    """
    SEANCE_TYPES = [
        ('NORMAL', 'NORMAL'),
        ('SUNDAY_SCHOOL', 'SUNDAY_SCHOOL'),
        ('DLT', 'DLT')
    ]
    
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    row = models.ForeignKey(ScheduleRow, on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedule_assignments')
    seance_type = models.CharField(max_length=20, choices=SEANCE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['seance_type']
        unique_together = [['row', 'teacher', 'seance_type']]
        verbose_name = 'Schedule Assignment'
        verbose_name_plural = 'Schedule Assignments'

    def __str__(self):
        return f"{self.row.dateLabel} - {self.teacher.email} ({self.seance_type})"
