from django.urls import path
from . import views

urlpatterns = [
    path('agendar/', views.agendar_paciente, name='agendar_paciente'),
    path('lista/', views.lista_agendamentos, name='lista_agendamentos'),
    path('triagem/<int:id>/', views.enviar_para_triagem, name='enviar_para_triagem'),
    path('buscar-paciente/', views.buscar_paciente, name='buscar_paciente'),
]
