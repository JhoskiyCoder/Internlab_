from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager


class CustomUser(AbstractUser):

    class Role(models.TextChoices):
        STUDENT = ("student", "Студент")
        EMPLOYER = ("employer", "Работодатель")
        ADMIN = ("admin", "Администратор")

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"
