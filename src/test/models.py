import uuid
from django.db import models
from django.contrib.auth import get_user_model
from children.models import Child

User = get_user_model()

class Test(models.Model):
    class TypeTest(models.TextChoices):
        EVALUATION = 'EVALUATION', 'EVALUATION'
        SUNDAY_SCHOOL = 'SUNDAY_SCHOOL', 'SUNDAY_SCHOOL'
        CONCOURS = 'CONCOURS', 'CONCOURS'

    class ClasseType(models.TextChoices):
        PETIT = 'Petit', 'Petit'
        DEBUTANT = 'Débutant', 'Débutant'
        MOYEN = 'Moyen', 'Moyen'
        JUNIOR_A = 'JuniorA', 'JuniorA'
        JUNIOR_B = 'JuniorB', 'JuniorB'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titleTest = models.CharField(max_length=255)
    classe = models.CharField(max_length=20, choices=ClasseType.choices)
    typeTest = models.CharField(max_length=50, choices=TypeTest.choices)
    
    # Optional Google Drive URL paths
    sujetTest = models.URLField(max_length=500, blank=True, null=True)
    correctionTest = models.URLField(max_length=500, blank=True, null=True)
    
    # System metadata relations
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_tests")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titleTest} ({self.typeTest})"
    

class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="notes")
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="notes")
    
    note = models.DecimalField(max_digits=5, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents a child from having two different scores for the exact same test
        unique_together = ('child', 'test')

    def __str__(self):
        return f"{self.child.name} - {self.test.titleTest}: {self.note}"