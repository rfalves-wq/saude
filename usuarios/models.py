from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    PERFIL_CHOICES = [
        ('administrador', 'Administrador'),
        ('tecnico', 'Técnico'),
        ('medico', 'Médico'),
        ('enfermeiro', 'Enfermeiro'),
        ('recepcao', 'Recepção'),
    ]
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.perfil})"
