from django import forms
from django.utils import timezone
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
            'data': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'hora': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
        }


    # ✅ Validação de data passada
    def clean_data(self):
        data = self.cleaned_data.get('data')

        if data and data < timezone.now().date():
            raise forms.ValidationError(
                "Não é possível agendar para uma data passada."
            )

        return data

    # ✅ Validação de horário duplicado
    def clean(self):
        cleaned_data = super().clean()
        paciente = cleaned_data.get('paciente')
        data = cleaned_data.get('data')
        hora = cleaned_data.get('hora')

        if paciente and data and hora:
            if Agendamento.objects.filter(
                paciente=paciente,
                data=data,
                hora=hora
            ).exists():
                raise forms.ValidationError(
                    "Este paciente já possui agendamento neste horário."
                )

        return cleaned_data
