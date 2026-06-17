from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.conf import settings
from uuid import uuid4
from django.utils import timezone


# Create your models here.
class CustomManager(BaseUserManager) :
    def create_user(self, email, password=None, **extra_fields) :
        if not email :
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields) :
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('status', True)
        user = self.create_user(email,password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin) :
    id           = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    username     = None
    created_at   = models.DateTimeField(auto_now_add=True)
    status       = models.CharField(max_length=12, choices=[('teacher', 'teacher'), ('moderator', 'moderator'), ('admin', 'admin')], default='teacher')
    is_staff     = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=False)
    email        = models.EmailField(unique=True)
    
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []

    objects = CustomManager()

    def __str__(self):
        return self.email
    

class UserProfil(models.Model) :
    last_name  = models.CharField(max_length=30, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    quarter    = models.CharField(max_length=30, blank=True)
    sexe       = models.CharField(max_length=12, choices=[('Masculin', 'MASCULIN'), ('Feminin', 'FEMININ')], blank=True)
    tel        = models.CharField(max_length=15, blank=True)
    user       = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profil')


class AccountVerificationCode(models.Model) :
    created_at = models.DateTimeField(auto_now_add=True)
    code       = models.IntegerField()
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_used    = models.BooleanField(default=False)

    def is_valid(self) :
        return timezone.now().minute - self.created_at.minute < 30 and self.is_used != True