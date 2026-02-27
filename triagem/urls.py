from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.triagem_dashboard, name='triagem_dashboard'),
    path('realizar/<int:id>/', views.realizar_triagem, name='realizar_triagem'),
    path('historico/', views.historico_triagens, name='historico_triagens'),
        path('fila-json/', views.fila_triagem_json, name='fila_triagem_json'),
    path('triagens/por-dia/', views.triagens_por_dia, name='triagens_por_dia'),
    



]
