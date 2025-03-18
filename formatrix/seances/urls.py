from django.urls import path
from . import views

app_name = 'seances'

urlpatterns = [
    path('', views.SeanceListView.as_view(), name='seance-list'),
    path('<int:pk>/', views.SeanceDetailView.as_view(), name='seance-detail'),
    path('creer/', views.SeanceCreateView.as_view(), name='seance-create'),
    path('<int:pk>/modifier/', views.SeanceUpdateView.as_view(), name='seance-update'),
    path('<int:pk>/supprimer/', views.SeanceDeleteView.as_view(), name='seance-delete'),
    path('<int:pk>/annuler/', views.annuler_seance, name='annuler-seance'),
    
    # Routes pour les actions d'état de la séance
    path('<int:pk>/start/', views.start_session, name='start-session'),
    path('<int:pk>/complete/', views.complete_session, name='complete-session'),
    path('<int:pk>/cancel/', views.cancel_session, name='cancel-session'),
    
    # Routes pour la gestion des absences
    path('<int:seance_id>/absences/', views.absence_list, name='absence_list'),
    path('<int:seance_id>/absences/ajouter/', views.absence_create, name='absence_create'),
    path('absences/<int:absence_id>/modifier/', views.absence_update, name='absence_update'),
    path('absences/<int:absence_id>/supprimer/', views.absence_delete, name='absence_delete'),
]
