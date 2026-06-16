import uuid
from django.db import models

class Child(models.Model):
    class ClasseType(models.TextChoices):
        PETIT = 'Petit', 'Petit'
        DEBUTANT = 'Débutant', 'Débutant'
        MOYEN = 'Moyen', 'Moyen'
        JUNIOR_A = 'JuniorA', 'JuniorA'
        JUNIOR_B = 'JuniorB', 'JuniorB'

    class Sexe(models.TextChoices):
        MASCULIN = 'Masculin', 'Masculin'  # 🎯 Matches 'Masculin' literal
        FEMININ = 'Feminin', 'Feminin'      # 🎯 Matches 'Feminin' literal

    # 🎯 Switched to UUID for the primary key id
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=255)
    classe = models.CharField(max_length=20, choices=ClasseType.choices)
    nivScolaire = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    tel = models.CharField(max_length=20, blank=True, null=True)
    telParent = models.CharField(max_length=20, blank=True, null=True)
    sexe = models.CharField(max_length=15, choices=Sexe.choices)
    sexeParent = models.CharField(max_length=15, choices=Sexe.choices)
    adresse = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name