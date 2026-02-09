from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'perfil']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    token = forms.CharField(max_length=6, required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Código 2FA'}))
