# tecnico/forms.py
from django import forms
from .models import Medicacao

class MedicacaoForm(forms.ModelForm):
    class Meta:
        model = Medicacao
        fields = ['paciente', 'nome_medicamento', 'dosagem', 'frequencia', 'data_inicio', 'data_fim', 'observacoes']
