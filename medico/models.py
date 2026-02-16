from django.db import models
from pacientes.models import Paciente
from usuarios.models import Usuario
from triagem.models import Triagem

class Atendimento(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    triagem = models.OneToOneField(Triagem, on_delete=models.CASCADE)

    diagnostico = models.TextField(blank=True, null=True)
    prescricao = models.TextField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)

    DECISAO_CHOICES = [
        ("dispensar", "Dispensar"),
        ("medicacao", "Medicação"),
        ("internacao", "Internação"),
    ]
    decisao = models.CharField(
        max_length=20,
        choices=DECISAO_CHOICES,
        blank=True,
        null=True
    )

    data_atendimento = models.DateTimeField(auto_now_add=True)
    finalizado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.paciente.nome} - {self.data_atendimento}"

