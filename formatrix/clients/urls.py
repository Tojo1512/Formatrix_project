from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import TypeClientViewSet, ClientViewSet

router = DefaultRouter()
router.register(r'type-clients', TypeClientViewSet)
router.register(r'clients', ClientViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
