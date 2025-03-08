from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApprenantViewSet
from .template_views import (
    ApprenantListView, ApprenantCreateView, ApprenantUpdateView,
    ApprenantDetailView, ApprenantDeleteView
)
from .reports import RapportsDemographiquesView

router = DefaultRouter()
router.register(r'apprenants', ApprenantViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', ApprenantListView.as_view(), name='apprenant-list'),
    path('create/', ApprenantCreateView.as_view(), name='apprenant-create'),
    path('<int:pk>/', ApprenantDetailView.as_view(), name='apprenant-detail'),
    path('<int:pk>/update/', ApprenantUpdateView.as_view(), name='apprenant-update'),
    path('<int:pk>/delete/', ApprenantDeleteView.as_view(), name='apprenant-delete'),
    path('rapports/demographiques/', RapportsDemographiquesView.as_view(), name='rapports-demographiques'),
]

# Template-based views are now in template_urls.py
