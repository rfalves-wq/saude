from django.db import models
from pacientes.models import Paciente
from recepcao.models import Agendamento
from usuarios.models import Usuario

class Triagem(models.Model):

    RISCO_CHOICES = [
        ('Vermelho', 'Vermelho'),
        ('Laranja', 'Laranja'),
        ('Amarelo', 'Amarelo'),
        ('Verde', 'Verde'),
        ('Azul', 'Azul'),
    ]

    agendamento = models.OneToOneField(Agendamento, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)

    enfermeiro = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triagens_realizadas"
    )

    pressao_arterial = models.CharField(max_length=20)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1)
    frequencia_cardiaca = models.IntegerField()
    saturacao = models.IntegerField()

    classificacao_risco = models.CharField(
        max_length=10,
        choices=RISCO_CHOICES,
        blank=True,
        null=True
    )

    observacoes = models.TextField(blank=True, null=True)

    atendido = models.BooleanField(default=False)
    data_triagem = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Triagem - {self.paciente.nome}"



from django.http import JsonResponse
from recepcao.models import Agendamento

def fila_triagem_json(request):
    fila = Agendamento.objects.filter(status="Em Triagem")

    dados = []

    for ag in fila:
        dados.append({
            'id': ag.id,
            'paciente': ag.paciente.nome,
            'data': ag.data.strftime("%d/%m/%Y"),
            'hora': ag.hora.strftime("%H:%M")
        })

    return JsonResponse({'fila': dados})
