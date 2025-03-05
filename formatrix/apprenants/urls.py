from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApprenantViewSet

router = DefaultRouter()
router.register(r'apprenants', ApprenantViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
