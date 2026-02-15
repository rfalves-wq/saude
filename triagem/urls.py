from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.triagem_dashboard, name='triagem_dashboard'),
    path('realizar/<int:id>/', views.realizar_triagem, name='realizar_triagem'),
    path('historico/', views.historico_triagens, name='historico_triagens'),

]
