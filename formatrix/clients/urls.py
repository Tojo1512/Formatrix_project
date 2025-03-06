from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import TypeClientViewSet, ClientViewSet
from .template_views import (
    ClientListView, 
    ClientCreateView, 
    ClientDetailView, 
    ClientUpdateView, 
    ClientDeleteView
)

router = DefaultRouter()
router.register(r'type-clients', TypeClientViewSet)
router.register(r'clients', ClientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # URLs pour les templates
    path('liste/', ClientListView.as_view(), name='client-list'),
    path('creer/', ClientCreateView.as_view(), name='client-create'),
    path('<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('<int:pk>/modifier/', ClientUpdateView.as_view(), name='client-update'),
    path('<int:pk>/supprimer/', ClientDeleteView.as_view(), name='client-delete'),
]
