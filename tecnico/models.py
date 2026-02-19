from django.db import models

# Create your models here.
# tecnico/models.py
from django.db import models
from pacientes.models import Paciente
from usuarios.models import Usuario  # Técnico
from django.utils import timezone

class Medicacao(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    tecnico = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    nome_medicamento = models.CharField(max_length=200)
    dosagem = models.CharField(max_length=50)  # ex: 500mg
    frequencia = models.CharField(max_length=100)  # ex: 3x ao dia
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    administrado = models.BooleanField(default=False)
    horario_administracao = models.TimeField(null=True, blank=True)
    observacao = models.TextField(blank=True, null=True)
    coren = models.CharField(max_length=20, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome_medicamento} - {self.paciente.nome}"
