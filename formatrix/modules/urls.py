from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModuleViewSet

router = DefaultRouter()
router.register(r'', ModuleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
