from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import LieuViewSet, create_lieu, lieu_create_ajax
from .template_views import LieuCreateView, LieuUpdateView, LieuDetailView, LieuListView, LieuDeleteView

router = DefaultRouter()
router.register(r'lieux', LieuViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create/', create_lieu, name='create-lieu'),
    
    # URLs pour les templates
    path('creer/', LieuCreateView.as_view(), name='lieu-create'),
    path('<int:pk>/modifier/', LieuUpdateView.as_view(), name='lieu-update'),
    path('<int:pk>/', LieuDetailView.as_view(), name='lieu-detail'),
    path('<int:pk>/supprimer/', LieuDeleteView.as_view(), name='lieu-delete'),
    path('liste/', LieuListView.as_view(), name='lieu-list'),
    
    # URL pour AJAX
    path('creer-ajax/', lieu_create_ajax, name='lieu-create-ajax'),
]
