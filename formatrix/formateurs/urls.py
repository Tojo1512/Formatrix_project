from django.urls import path
from . import views

app_name = 'formateurs'

urlpatterns = [
    path('', views.FormateurListView.as_view(), name='formateur-list'),
    path('create/', views.FormateurCreateView.as_view(), name='formateur-create'),
    path('<int:pk>/', views.FormateurDetailView.as_view(), name='formateur-detail'),
    path('<int:pk>/update/', views.FormateurUpdateView.as_view(), name='formateur-update'),
    path('<int:pk>/delete/', views.FormateurDeleteView.as_view(), name='formateur-delete'),
    path('register/', views.formateur_register, name='formateur-register'),
] 