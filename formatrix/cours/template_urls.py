from django.urls import path
from .template_views import (
    CoursListView, CoursCreateView, CoursDetailView,
    CoursUpdateView, CoursDeleteView, CoursApprouverView, CoursRefuserView
)

urlpatterns = [
    path('liste/', CoursListView.as_view(), name='cours-list'),
    path('ajouter/', CoursCreateView.as_view(), name='cours-create'),
    path('<int:pk>/', CoursDetailView.as_view(), name='cours-detail'),
    path('<int:pk>/modifier/', CoursUpdateView.as_view(), name='cours-update'),
    path('<int:pk>/supprimer/', CoursDeleteView.as_view(), name='cours-delete'),
    path('<int:pk>/approuver/', CoursApprouverView.as_view(), name='cours-approuver'),
    path('<int:pk>/refuser/', CoursRefuserView.as_view(), name='cours-refuser'),
]
