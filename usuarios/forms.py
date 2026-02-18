from django import forms
from .models import Usuario

from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'perfil',
            'cpf',
            'data_nascimento',
            'telefone',
            'endereco',
            'cidade',
            'estado',
            'cep',
            'crm',
            'coren',
            'password',  # caso queira permitir definir senha aqui
        ]
        widgets = {
            'password': forms.PasswordInput(render_value=True),
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        perfil = cleaned_data.get('perfil')
        crm = cleaned_data.get('crm')
        coren = cleaned_data.get('coren')

        if perfil == 'medico' and not crm:
            self.add_error('crm', 'CRM é obrigatório para usuários com perfil Médico.')
        if perfil == 'enfermeiro' and not coren:
            self.add_error('coren', 'COREN é obrigatório para usuários com perfil Enfermeiro.')

        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    token = forms.CharField(max_length=6, required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Código 2FA'}))
