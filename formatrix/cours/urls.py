from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CoursViewSet, ModuleViewSet, DocumentViewSet, RenouvellementViewSet, SeanceViewSet
from .template_views import CoursListView, CoursCreateView, CoursDetailView, CoursUpdateView

router = DefaultRouter()
router.register(r'cours', CoursViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'renouvellements', RenouvellementViewSet)
router.register(r'seances', SeanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # URLs pour les vues basées sur des templates
    path('liste/', CoursListView.as_view(), name='cours-list'),
    path('creer/', CoursCreateView.as_view(), name='cours-create'),
    path('<int:pk>/', CoursDetailView.as_view(), name='cours-detail'),
    path('<int:pk>/modifier/', CoursUpdateView.as_view(), name='cours-update'),
]
