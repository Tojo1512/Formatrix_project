from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import LieuViewSet, create_lieu
from .template_views import LieuCreateView, LieuUpdateView

router = DefaultRouter()
router.register(r'lieux', LieuViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create/', create_lieu, name='create-lieu'),
    
    # URLs pour les templates
    path('creer/', LieuCreateView.as_view(), name='lieu-create'),
    path('<int:pk>/modifier/', LieuUpdateView.as_view(), name='lieu-update'),
]
