from django.urls import path
from . import views

urlpatterns = [
    path('', views.SeanceListView.as_view(), name='seance-list'),
    path('<int:pk>/', views.SeanceDetailView.as_view(), name='seance-detail'),
    path('create/', views.SeanceCreateView.as_view(), name='seance-create'),
    path('<int:pk>/update/', views.SeanceUpdateView.as_view(), name='seance-update'),
    path('<int:pk>/delete/', views.SeanceDeleteView.as_view(), name='seance-delete'),
    path('<int:pk>/start/', views.start_session, name='seance-start'),
    path('<int:pk>/complete/', views.complete_session, name='seance-complete'),
    path('<int:pk>/cancel/', views.cancel_session, name='seance-cancel'),
]
