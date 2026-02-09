from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('pacientes/', include('pacientes.urls')),
    
]
