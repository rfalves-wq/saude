from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),

    # dashboards
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/medico/', views.medico_dashboard, name='medico_dashboard'),
    path('dashboard/enfermeiro/', views.enfermeiro_dashboard, name='enfermeiro_dashboard'),
    path('dashboard/tecnico/', views.tecnico_dashboard, name='tecnico_dashboard'),
    path('dashboard/recepcao/', views.recepcao_dashboard, name='recepcao_dashboard'),

    # CRUD
    path('', views.usuario_list, name='usuario_list'),
    path('novo/', views.usuario_create, name='usuario_create'),
    path('<int:pk>/editar/', views.usuario_update, name='usuario_update'),
    path('<int:pk>/deletar/', views.usuario_delete, name='usuario_delete'),
]
