from django.db import models
from pacientes.models import Paciente
from django.contrib.auth import get_user_model

User = get_user_model()

class Agendamento(models.Model):
    STATUS_CHOICES = [
        ('AGENDADO', 'Agendado'),
        ('TRIAGEM', 'Em Triagem'),
        ('FINALIZADO', 'Finalizado'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    data = models.DateField()
    hora = models.TimeField()
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGENDADO')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.paciente.nome} - {self.data}"
