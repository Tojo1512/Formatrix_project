from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PresenceViewSet

router = DefaultRouter()
router.register(r'presences', PresenceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
