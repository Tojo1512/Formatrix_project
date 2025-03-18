from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InscriptionViewSet, 
    InscriptionListView, 
    InscriptionDetailView, 
    InscriptionCreateView, 
    InscriptionUpdateView, 
    InscriptionDeleteView
)

router = DefaultRouter()
router.register(r'inscriptions', InscriptionViewSet)

urlpatterns = [
    path('api/', include((router.urls, 'inscriptions-api'))),
    path('', InscriptionListView.as_view(), name='inscription-list'),
    path('<int:pk>/', InscriptionDetailView.as_view(), name='inscription-detail'),
    path('create/', InscriptionCreateView.as_view(), name='inscription-create'),
    path('<int:pk>/update/', InscriptionUpdateView.as_view(), name='inscription-update'),
    path('<int:pk>/delete/', InscriptionDeleteView.as_view(), name='inscription-delete'),
    path('<int:pk>/update-status/<str:status>/', InscriptionDetailView.as_view(), name='inscription-update-status'),
    path('multiple/', InscriptionViewSet.as_view({'get': 'formulaire_multiple'}), name='inscription-multiple'),
]
