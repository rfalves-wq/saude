from django.urls import path
from . import views

urlpatterns = [
    path('', views.paciente_list, name='paciente_list'),
    path('novo/', views.paciente_create, name='paciente_create'),
    path('<int:pk>/editar/', views.paciente_update, name='paciente_update'),
    path('<int:pk>/deletar/', views.paciente_delete, name='paciente_delete'),
]
