from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RenouvellementViewSet

router = DefaultRouter()
router.register(r'', RenouvellementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
