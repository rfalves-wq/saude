from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('pacientes/', include('pacientes.urls')),
    path('recepcao/', include('recepcao.urls')),
path('triagem/', include('triagem.urls')),
path('medico/', include('medico.urls')),
path('tecnico/', include('tecnico.urls')),

    
]
