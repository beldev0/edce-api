import uuid
from django.db import models

class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title


class EventActivity(models.Model):
    class EventType(models.TextChoices):
        ARBRE_DE_NOEL = "Arbre de noël", "Arbre de noël"
        SOIREE_RECREATIVE = "Soirée récréative des enfants", "Soirée récréative des enfants"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="event_links")
    eventType = models.CharField(max_length=100, choices=EventType.choices)
    year = models.CharField(max_length=4)  # Stores years like "2026"

    def __str__(self):
        return f"{self.eventType} ({self.year}) - {self.activity.title}"