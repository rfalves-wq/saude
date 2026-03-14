from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.medico_dashboard, name='medico_dashboard'),
    path('iniciar/<int:triagem_id>/', views.iniciar_atendimento, name='iniciar_atendimento'),
    path('editar/<int:atendimento_id>/', views.editar_atendimento, name='editar_atendimento'),
     path('decidir/<int:atendimento_id>/', views.decidir_atendimento, name='decidir_atendimento'),
     path("laboratorio/", views.laboratorio_lista, name="laboratorio_lista"),
path("laboratorio/<int:pk>/resultado/", views.inserir_resultado, name="inserir_resultado"),
 path('dashboard/', views.medico_dashboard, name='medico_dashboard'),

    path('exame/<int:exame_id>/visualizar/', views.visualizar_exame, name='visualizar_exame'),
    path('exame/<int:exame_id>/pdf/', views.gerar_pdf_exame, name='gerar_pdf_exame'),

     path(
    "radiologia/",
    views.radiologia_lista,
    name="radiologia_lista"
),

path(
    "radiologia/resultado/<int:pk>/",
    views.inserir_resultado_radiologia,
    name="inserir_resultado_radiologia"
),
]
