from django.urls import path
from . import views

urlpatterns = [
    path('medicacao/', views.lista_medicacao, name='lista_medicacao'),
    path('administrar/<int:atendimento_id>/', views.administrar_medicacao, name='administrar_medicacao'),
]
