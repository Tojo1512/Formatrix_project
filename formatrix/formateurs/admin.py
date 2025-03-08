from django.contrib import admin
from .models import Formateur

@admin.register(Formateur)
class FormateurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'telephone', 'type_formateur', 'niveau_expertise', 'statut')
    list_filter = ('type_formateur', 'niveau_expertise', 'statut', 'ville')
    search_fields = ('nom', 'prenom', 'email', 'specialites')
    ordering = ('nom', 'prenom')
    date_hierarchy = 'date_creation'
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'email', 'telephone', 'date_naissance', 'photo')
        }),
        ('Informations professionnelles', {
            'fields': ('type_formateur', 'niveau_expertise', 'specialites', 'cv', 'date_embauche')
        }),
        ('Localisation', {
            'fields': ('adresse', 'ville')
        }),
        ('Statut et disponibilité', {
            'fields': ('statut', 'disponibilite')
        }),
        # La section Cours a été supprimée
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )

    # filter_horizontal = ('cours',)  # Supprimé

    def get_readonly_fields(self, request, obj=None):
        if obj:  # En mode édition
            return ('date_creation', 'date_modification')
        return () 