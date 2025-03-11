from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import SeanceViewSet

router = DefaultRouter()
router.register(r'', SeanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 