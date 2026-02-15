from django import forms
from .models import Triagem

class TriagemForm(forms.ModelForm):
    class Meta:
        model = Triagem
        fields = [
            'pressao_arterial',
            'temperatura',
            'frequencia_cardiaca',
            'saturacao',
            'observacoes'
        ]
