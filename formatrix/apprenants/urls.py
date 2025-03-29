from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApprenantViewSet
from .reports import RapportsDemographiquesView

router = DefaultRouter()
router.register(r'apprenants', ApprenantViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('rapports/demographiques/', RapportsDemographiquesView.as_view(), name='rapports-demographiques'),
]

# Template-based views are now in template_urls.py
