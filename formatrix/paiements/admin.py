from django.contrib import admin
from .models import Paiement, PlanPaiement, PaiementFormateur

# Register your models here.

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('paiement_id', 'inscription', 'montant', 'date_paiement', 'date_echeance', 'statut', 'mode_paiement')
    list_filter = ('statut', 'mode_paiement', 'date_paiement')
    search_fields = ('inscription__apprenant__nom_apprenant', 'inscription__apprenant__cin', 'reference')
    readonly_fields = ('paiement_id', 'date_creation', 'date_modification')
    fieldsets = (
        ('Informations principales', {
            'fields': ('paiement_id', 'inscription', 'montant', 'statut')
        }),
        ('Dates', {
            'fields': ('date_paiement', 'date_echeance')
        }),
        ('Détails du paiement', {
            'fields': ('mode_paiement', 'reference', 'commentaires')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PlanPaiement)
class PlanPaiementAdmin(admin.ModelAdmin):
    list_display = ('plan_id', 'inscription', 'montant_total', 'nombre_versements', 'date_debut', 'statut')
    list_filter = ('statut', 'date_debut')
    search_fields = ('inscription__apprenant__nom_apprenant', 'inscription__apprenant__cin')
    readonly_fields = ('plan_id', 'date_creation', 'date_modification')
    fieldsets = (
        ('Informations principales', {
            'fields': ('plan_id', 'inscription', 'montant_total', 'statut')
        }),
        ('Configuration du plan', {
            'fields': ('nombre_versements', 'date_debut', 'intervalle_jours')
        }),
        ('Détails', {
            'fields': ('commentaires',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaiementFormateur)
class PaiementFormateurAdmin(admin.ModelAdmin):
    list_display = ('paiement_formateur_id', 'formateur', 'montant', 'date_paiement', 'statut', 'mode_paiement')
    list_filter = ('statut', 'mode_paiement', 'date_paiement')
    search_fields = ('formateur__nom_apprenant', 'formateur__prenom', 'reference')
    readonly_fields = ('paiement_formateur_id', 'date_creation', 'date_modification')
    fieldsets = (
        ('Informations principales', {
            'fields': ('paiement_formateur_id', 'formateur', 'montant', 'statut')
        }),
        ('Période et calcul', {
            'fields': ('periode_debut', 'periode_fin', 'heures_travaillees', 'taux_horaire')
        }),
        ('Détails du paiement', {
            'fields': ('date_paiement', 'mode_paiement', 'reference', 'commentaires')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
