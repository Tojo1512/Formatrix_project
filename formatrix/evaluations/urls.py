from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PresenceViewSet, ResultatViewSet

router = DefaultRouter()
router.register(r'presences', PresenceViewSet)
router.register(r'resultats', ResultatViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
