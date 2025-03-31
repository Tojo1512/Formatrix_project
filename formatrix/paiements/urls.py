from django.urls import path
from . import views

app_name = 'paiements'

urlpatterns = [
    # Dashboard
    path('', views.tableau_bord_paiements, name='tableau-bord'),
    
    # Payments
    path('liste/', views.PaiementListView.as_view(), name='paiement-list'),
    path('detail/<uuid:paiement_id>/', views.PaiementDetailView.as_view(), name='paiement-detail'),
    path('creer/', views.PaiementCreateView.as_view(), name='paiement-create'),
    path('modifier/<uuid:paiement_id>/', views.PaiementUpdateView.as_view(), name='paiement-update'),
    
    # Payment Plans
    path('plans/', views.PlanPaiementListView.as_view(), name='plan-list'),
    path('plans/detail/<uuid:plan_id>/', views.PlanPaiementDetailView.as_view(), name='plan-detail'),
    path('plans/creer/', views.PlanPaiementCreateView.as_view(), name='plan-create'),
    path('plans/modifier/<uuid:plan_id>/', views.PlanPaiementUpdateView.as_view(), name='plan-update'),
    
    # Trainer Payments
    path('formateurs/', views.PaiementFormateurListView.as_view(), name='paiement-formateur-list'),
    path('formateurs/detail/<uuid:paiement_formateur_id>/', views.PaiementFormateurDetailView.as_view(), name='paiement-formateur-detail'),
    path('formateurs/creer/', views.PaiementFormateurCreateView.as_view(), name='paiement-formateur-create'),
    path('formateurs/modifier/<uuid:paiement_formateur_id>/', views.PaiementFormateurUpdateView.as_view(), name='paiement-formateur-update'),
    path('formateurs/calculer-heures/<uuid:formateur_id>/', views.calculer_heures_formateur, name='calculer-heures-formateur'),
    
    # Invoices
    path('factures/', views.FactureListView.as_view(), name='facture-list'),
    path('factures/nouvelle/', views.FactureCreateView.as_view(), name='facture-create'),
    path('factures/<uuid:facture_id>/', views.FactureDetailView.as_view(), name='facture-detail'),
    path('factures/<uuid:facture_id>/modifier/', views.recreer_facture, name='facture-edit'),
    path('factures/<uuid:facture_id>/recreer/', views.recreer_facture, name='facture-recreer'),
    path('factures/generer/', views.generer_facture, name='generer-facture'),
    path('factures/<uuid:facture_id>/telecharger/', views.telecharger_facture_pdf, name='facture-pdf'),
    # Désactivation des fonctionnalités d'email
    # path('factures/<uuid:facture_id>/envoyer/', views.envoyer_facture_email, name='envoyer-facture'),
    # path('factures/<uuid:facture_id>/rappel/', views.envoyer_rappel_facture, name='envoyer-rappel-facture'),
    path('factures/<uuid:facture_id>/statut/', views.changer_statut_facture, name='changer-statut-facture'),
    path('factures/<uuid:facture_id>/ligne/ajouter/', views.ajouter_ligne_facture, name='ajouter-ligne-facture'),
    path('factures/ligne/<uuid:ligne_id>/supprimer/', views.supprimer_ligne_facture, name='supprimer-ligne-facture'),
    
    # Gestion des statuts de facture
    path('factures/<uuid:facture_id>/emettre/', views.emettre_facture, name='emettre-facture'),
    path('factures/<uuid:facture_id>/payer/', views.marquer_facture_payee, name='marquer-facture-payee'),
    path('factures/<uuid:facture_id>/annuler/', views.annuler_facture, name='annuler-facture'),
    
    # API
    path('api/inscription/<int:inscription_id>/prix/', views.get_inscription_prix, name='api-inscription-prix'),
]
