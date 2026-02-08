from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario

class UsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'perfil', 'password1', 'password2']

class UsuarioUpdateForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'perfil']
