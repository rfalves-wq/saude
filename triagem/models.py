from django.db import models
from pacientes.models import Paciente
from recepcao.models import Agendamento

class Triagem(models.Model):
    agendamento = models.OneToOneField(Agendamento, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)

    pressao_arterial = models.CharField(max_length=20)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1)
    frequencia_cardiaca = models.IntegerField()
    saturacao = models.IntegerField()

    observacoes = models.TextField(blank=True, null=True)

    data_triagem = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Triagem - {self.paciente.nome}"
