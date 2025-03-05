from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InscriptionViewSet

router = DefaultRouter()
router.register(r'inscriptions', InscriptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
