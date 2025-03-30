from django.urls import path
from . import views

app_name = 'rapports'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('demographique/', views.rapport_demographique, name='demographique'),
    path('ressources/', views.rapport_ressources, name='ressources'),
    path('clients/', views.rapport_clients, name='clients'),
    path('export/<str:rapport_type>/', views.export_rapport, name='export'),
]
