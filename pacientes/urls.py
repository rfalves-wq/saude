from django.urls import path
from . import views

urlpatterns = [
    path('', views.paciente_list, name='paciente_list'),
    path('novo/', views.paciente_create, name='paciente_create'),
    path('<int:pk>/editar/', views.paciente_update, name='paciente_update'),
    path('<int:pk>/deletar/', views.paciente_delete, name='paciente_delete'),
    
    # Histórico do paciente (tela)
    path('paciente/<int:paciente_id>/historico/', views.historico_paciente, name='historico_paciente'),

    # Histórico pronto para imprimir
    path('<int:paciente_id>/historico/', views.imprimir_historico, name='imprimir_historico'),  # atenção: mesma URL que acima
    path('<int:paciente_id>/historico/dia/', views.imprimir_historico_do_dia, name='imprimir_historico_dia'),
    path('paciente/<int:paciente_id>/historico/pdf/', views.imprimir_historico_pdf, name='imprimir_historico_pdf'),
    # PDF Histórico Completo
path('paciente/<int:paciente_id>/historico/pdf/', views.imprimir_historico_pdf, name='imprimir_historico_pdf'),

# PDF Histórico do Dia
path('paciente/<int:paciente_id>/historico/pdf/dia/', views.imprimir_historico_dia_pdf, name='imprimir_historico_dia_pdf'),
path('paciente/<int:paciente_id>/historico/pdf/dia/', views.imprimir_historico_dia_pdf, name='imprimir_historico_dia_pdf'),


]
