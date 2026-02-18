from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class Usuario(AbstractUser):
    PERFIL_CHOICES = [
        ('administrador', 'Administrador'),
        ('medico', 'Médico'),
        ('enfermeiro', 'Enfermeiro'),
        ('tecnico', 'Técnico'),
        ('recepcao', 'Recepção'),
    ]
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES, default='recepcao')

    # DADOS CADASTRAIS
    cpf = models.CharField("CPF", max_length=14, unique=True, blank=True, null=True)
    data_nascimento = models.DateField("Data de Nascimento", blank=True, null=True)
    telefone = models.CharField("Telefone", max_length=20, blank=True, null=True)
    endereco = models.CharField("Endereço", max_length=255, blank=True, null=True)
    cidade = models.CharField("Cidade", max_length=100, blank=True, null=True)
    estado = models.CharField("Estado", max_length=50, blank=True, null=True)
    cep = models.CharField("CEP", max_length=10, blank=True, null=True)

    # CAMPOS ESPECÍFICOS
    crm = models.CharField("CRM", max_length=20, blank=True, null=True)
    coren = models.CharField("COREN", max_length=20, blank=True, null=True)

    def __str__(self):
        return self.get_full_name() or self.username

    def clean(self):
        # Valida obrigatoriedade de CRM para médicos
        if self.perfil == 'medico' and not self.crm:
            raise ValidationError({'crm': 'CRM é obrigatório para usuários com perfil Médico.'})
        # Valida obrigatoriedade de COREN para enfermeiros
        if self.perfil == 'enfermeiro' and not self.coren:
            raise ValidationError({'coren': 'COREN é obrigatório para usuários com perfil Enfermeiro.'})
        super().clean()
