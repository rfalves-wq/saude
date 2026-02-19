from django.db import models
from django.utils import timezone
from pacientes.models import Paciente
from usuarios.models import Usuario
from triagem.models import Triagem


class Atendimento(models.Model):

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE
    )

    medico = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,  # ⚠ Melhor que CASCADE
        null=True,
        related_name="atendimentos_realizados"
    )

    triagem = models.OneToOneField(
        Triagem,
        on_delete=models.CASCADE
    )

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

    # ==============================
    # CONTROLE DA MEDICAÇÃO
    # ==============================

    medicacao_aplicada = models.BooleanField(default=False)

    tecnico_aplicou = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicacoes_aplicadas"
    )

    horario_medicacao = models.DateTimeField(
        null=True,
        blank=True
    )

    # ==============================
    # CONTROLE DO ATENDIMENTO
    # ==============================

    data_atendimento = models.DateTimeField(auto_now_add=True)
    finalizado = models.BooleanField(default=False)

    # ==============================
    # MÉTODO PARA APLICAR MEDICAÇÃO
    # ==============================

    def aplicar_medicacao(self, tecnico):
        self.medicacao_aplicada = True
        self.tecnico_aplicou = tecnico
        self.horario_medicacao = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.paciente.nome} - {self.data_atendimento.strftime('%d/%m/%Y %H:%M')}"
