from django.urls import path
from .template_views import (
    ApprenantListView, ApprenantCreateView, ApprenantDetailView,
    ApprenantUpdateView, ApprenantDeleteView
)

urlpatterns = [
    path('liste/', ApprenantListView.as_view(), name='apprenant-list'),
    path('ajouter/', ApprenantCreateView.as_view(), name='apprenant-create'),
    path('<int:pk>/', ApprenantDetailView.as_view(), name='apprenant-detail'),
    path('<int:pk>/modifier/', ApprenantUpdateView.as_view(), name='apprenant-update'),
    path('<int:pk>/supprimer/', ApprenantDeleteView.as_view(), name='apprenant-delete'),
]
