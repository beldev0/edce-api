import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Seance(models.Model):
    class SeanceType(models.TextChoices):
        NORMAL = "NORMAL", "NORMAL"
        DLT = "DLT", "DLT"
        SUNDAY_SCHOOL = "SUNDAY_SCHOOL", "SUNDAY_SCHOOL"

    class ClasseType(models.TextChoices):
        PETIT = 'Petit', 'Petit'
        DEBUTANT = 'Débutant', 'Débutant'
        MOYEN = 'Moyen', 'Moyen'
        JUNIOR_A = 'JuniorA', 'JuniorA'
        JUNIOR_B = 'JuniorB', 'JuniorB'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=SeanceType.choices)
    classe = models.CharField(max_length=20, choices=ClasseType.choices)
    
    # Foreign keys pointing to your User model
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_seances")
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="supervised_seances")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.type})"
    

class ParticipantSeance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    child = models.ForeignKey('children.Child', on_delete=models.CASCADE, related_name="seance_participations")
    seance = models.ForeignKey(Seance, on_delete=models.CASCADE, related_name="participants")

    class Meta:
        unique_together = ('child', 'seance')

    def __str__(self):
        return f"{self.child.name} -> {self.seance.title}"