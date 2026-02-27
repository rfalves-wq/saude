from django.contrib import admin
from .models import Atendimento

@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):

    list_display = (
        'paciente',
        'medico',
        'finalizado',
        'data_atendimento'
    )

    list_filter = (
        'finalizado',
        'medico'
    )

    search_fields = (
        'paciente__nome',
        'medico__username'
    )

    ordering = ('-data_atendimento',)

    readonly_fields = ('data_atendimento',)