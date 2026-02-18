from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.medico_dashboard, name='medico_dashboard'),
    path('iniciar/<int:triagem_id>/', views.iniciar_atendimento, name='iniciar_atendimento'),
    path('editar/<int:atendimento_id>/', views.editar_atendimento, name='editar_atendimento'),
     path('decidir/<int:atendimento_id>/', views.decidir_atendimento, name='decidir_atendimento'),
]
