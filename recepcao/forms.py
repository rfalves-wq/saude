from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Agendamento
from pacientes.models import Paciente

class AgendamentoForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.all(),
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Agendamento
        fields = ['paciente', 'data', 'hora']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        paciente = cleaned_data.get('paciente')
        data = cleaned_data.get('data')
        hora = cleaned_data.get('hora')

        if data and hora:
            # Combina data e hora em um datetime
            agendamento_datetime = datetime.combine(data, hora)
            agendamento_datetime = timezone.make_aware(
                agendamento_datetime,
                timezone.get_current_timezone()
            )
            now = timezone.localtime()
            # Permite agendar mesmo na hora atual (buffer 1 minuto)
            if agendamento_datetime < now - timedelta(minutes=1):
                raise forms.ValidationError(
                    "Não é possível agendar para uma data/hora passada."
                )

        # Verifica se já existe agendamento para mesmo paciente, data e hora
        if paciente and data and hora:
            if Agendamento.objects.filter(paciente=paciente, data=data, hora=hora).exists():
                raise forms.ValidationError(
                    "Este paciente já possui agendamento neste horário."
                )

        return cleaned_data
