from django import forms
from .models import Triagem
class TriagemForm(forms.ModelForm):
    class Meta:
        model = Triagem
        fields = ['pressao_arterial', 'temperatura', 'frequencia_cardiaca',
                  'saturacao', 'classificacao_risco', 'observacoes']
        widgets = {
            'pressao_arterial': forms.TextInput(attrs={'class': 'form-control'}),
            'temperatura': forms.NumberInput(attrs={'class': 'form-control'}),
            'frequencia_cardiaca': forms.NumberInput(attrs={'class': 'form-control'}),
            'saturacao': forms.NumberInput(attrs={'class': 'form-control'}),
            'classificacao_risco': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
