from django import forms
from .models import Paciente
from django.core.exceptions import ValidationError
import re

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        widgets = {
            # Campos já existentes
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXX.XXX.XXX-XX'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'rows': 2}),
            'cartao_sus': forms.TextInput(attrs={'class': 'form-control'}),

            # =========================
            # Novos campos solicitados
            # =========================
            'nome_social': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_mae': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_pai': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo_biologico': forms.Select(attrs={'class': 'form-select'}),
            'identidade_genero': forms.TextInput(attrs={'class': 'form-control'}),
            'orientacao_sexual': forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidade': forms.Select(attrs={'class': 'form-select'}),
            'naturalidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade/UF'}),
            'raca_cor': forms.Select(attrs={'class': 'form-select'}),
            'estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'escolaridade':forms.Select(attrs={'class': 'form-select'}),
            'profissao': forms.TextInput(attrs={'class': 'form-control'}),
            'rg': forms.TextInput(attrs={'class': 'form-control'}),
            'orgao_emissor': forms.TextInput(attrs={'class': 'form-control'}),
            'uf_rg': forms.Select(attrs={'class': 'form-select'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXXXX-XXX'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control'}),
            'uf': forms.Select(attrs={'class': 'form-select'}),
            'zona': forms.Select(attrs={'class': 'form-select'}),
            'telefone_fixo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXX-XXXX'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
            'whatsapp': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # =========================
    # Validações
    # =========================
    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
            raise ValidationError("CPF inválido! Use XXX.XXX.XXX-XX")
        return cpf

    def clean_telefone(self):
        telefone = self.cleaned_data['telefone']
        if not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', telefone):
            raise ValidationError("Telefone inválido! Use (XX) XXXXX-XXXX")
        return telefone

    def clean_telefone_fixo(self):
        telefone = self.cleaned_data.get('telefone_fixo')
        if telefone and not re.match(r'^\(\d{2}\)\s\d{4}-\d{4}$', telefone):
            raise ValidationError("Telefone inválido! Use (XX) XXXX-XXXX")
        return telefone

    def clean_celular(self):
        celular = self.cleaned_data['celular']
        if not re.match(r'^\(\d{2}\)\s\d{5}-\d{4}$', celular):
            raise ValidationError("Celular inválido! Use (XX) XXXXX-XXXX")
        return celular
