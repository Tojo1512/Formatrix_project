from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import LieuViewSet

router = DefaultRouter()
router.register(r'lieux', LieuViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
