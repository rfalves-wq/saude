from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    PERFIL_CHOICES = [
        ('administrador', 'Administrador'),
        ('medico', 'Médico'),
        ('enfermeiro', 'Enfermeiro'),
        ('tecnico', 'Técnico'),
        ('recepcao', 'Recepção'),
    ]
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES, default='recepcao')

    def __str__(self):
        return self.get_full_name() or self.username