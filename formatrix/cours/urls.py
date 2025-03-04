from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CoursViewSet, ModuleViewSet, DocumentViewSet, RenouvellementViewSet, SeanceViewSet

router = DefaultRouter()
router.register(r'cours', CoursViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'renouvellements', RenouvellementViewSet)
router.register(r'seances', SeanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
