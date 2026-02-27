from django.contrib import admin
from .models import Triagem

@admin.register(Triagem)
class TriagemAdmin(admin.ModelAdmin):
    list_display = (
        'paciente',
        'classificacao_risco',
        'atendido',
        'data_triagem'
    )
    list_filter = (
        'classificacao_risco',
        'atendido'
    )
    search_fields = ('paciente__nome',)
    ordering = ('-data_triagem',)