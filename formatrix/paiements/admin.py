from django.contrib import admin
from .models import Paiement, PaiementFormateur, PlanPaiement, Facture, LigneFacture

class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 1
    fields = ('description', 'quantite', 'prix_unitaire_ht', 'taux_tva', 'montant_ht', 'montant_tva', 'montant_ttc')
    readonly_fields = ('montant_ht', 'montant_tva', 'montant_ttc')

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('paiement_id', 'inscription', 'montant', 'date_paiement', 'statut', 'mode_paiement')
    list_filter = ('statut', 'mode_paiement', 'date_paiement')
    search_fields = ('reference', 'commentaires', 'inscription__apprenant__nom_apprenant')
    date_hierarchy = 'date_paiement'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('inscription', 'montant', 'date_paiement')
        }),
        ('Payment Details', {
            'fields': ('statut', 'mode_paiement', 'reference', 'date_echeance')
        }),
        ('Comments', {
            'fields': ('commentaires',),
            'classes': ('collapse',)
        }),
    )
    
    raw_id_fields = ('inscription',)

@admin.register(PaiementFormateur)
class PaiementFormateurAdmin(admin.ModelAdmin):
    list_display = ('paiement_formateur_id', 'formateur', 'montant', 'date_paiement', 'periode_debut', 'periode_fin', 'statut')
    list_filter = ('statut', 'mode_paiement', 'date_paiement')
    search_fields = ('formateur__nom', 'formateur__prenom', 'reference', 'commentaires')
    date_hierarchy = 'date_paiement'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('formateur', 'montant', 'date_paiement')
        }),
        ('Period Covered', {
            'fields': ('periode_debut', 'periode_fin', 'heures_travaillees', 'taux_horaire')
        }),
        ('Payment Details', {
            'fields': ('statut', 'mode_paiement', 'reference')
        }),
        ('Comments', {
            'fields': ('commentaires',),
            'classes': ('collapse',)
        }),
    )
    
    raw_id_fields = ('formateur',)

@admin.register(PlanPaiement)
class PlanPaiementAdmin(admin.ModelAdmin):
    list_display = ('plan_id', 'inscription', 'montant_total', 'nombre_versements', 'date_debut', 'statut', 'progress')
    list_filter = ('statut', 'date_debut')
    search_fields = ('inscription__apprenant__nom_apprenant', 'commentaires')
    date_hierarchy = 'date_debut'
    
    readonly_fields = ('amount_paid', 'remaining_amount', 'progress')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('inscription', 'montant_total', 'nombre_versements')
        }),
        ('Plan Details', {
            'fields': ('date_debut', 'intervalle_jours', 'statut')
        }),
        ('Tracking', {
            'fields': ('amount_paid', 'remaining_amount', 'progress')
        }),
        ('Comments', {
            'fields': ('commentaires',),
            'classes': ('collapse',)
        }),
    )
    
    raw_id_fields = ('inscription',)

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('numero_facture', 'destinataire_nom', 'montant_ttc', 'date_emission', 'statut', 'type_facture')
    list_filter = ('statut', 'type_facture', 'date_emission')
    search_fields = ('numero_facture', 'destinataire_nom', 'destinataire_email', 'notes')
    date_hierarchy = 'date_emission'
    inlines = [LigneFactureInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('numero_facture', 'inscription', 'paiement', 'type_facture')
        }),
        ('Dates', {
            'fields': ('date_emission', 'date_echeance')
        }),
        ('Amounts', {
            'fields': ('montant_ht', 'taux_tva', 'montant_tva', 'montant_ttc')
        }),
        ('Recipient', {
            'fields': ('destinataire_nom', 'destinataire_adresse', 'destinataire_email', 'destinataire_telephone', 'destinataire_siret')
        }),
        ('Additional Information', {
            'fields': ('conditions_paiement', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    raw_id_fields = ('inscription', 'paiement')
    
    readonly_fields = ('montant_ht', 'montant_tva', 'montant_ttc')
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Recalculate invoice totals after saving related items
        form.instance.recalculate_amounts()
        form.instance.save()
