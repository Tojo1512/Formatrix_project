from django.contrib import admin
from .models import Cours

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ('nom_cours', 'type_cours', 'niveau', 'duree_heures', 'status', 'statut_approbation')
    list_filter = ('type_cours', 'status', 'statut_approbation', 'horaire')
    search_fields = ('nom_cours', 'description', 'objectifs')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations essentielles', {
            'fields': ('nom_cours', 'description', 'type_cours', 'niveau')
        }),
        ('Détails du cours', {
            'fields': ('objectifs', 'prerequis', 'materiel_requis')
        }),
        ('Durée et coûts', {
            'fields': ('duree_heures', 'periode_mois', 'frais_par_participant')
        }),
        ('Planification', {
            'fields': ('horaire', 'start_time', 'status')
        }),
        ('Formateurs', {
            'fields': ('formateurs',)
        }),
        ('Approbation', {
            'fields': ('statut_approbation', 'date_approbation', 'date_expiration_validite', 'version')
        })
    )
    
    filter_horizontal = ('formateurs',)
    
    readonly_fields = ('created_at', 'updated_at')
