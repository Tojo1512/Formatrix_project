from django.contrib import admin
from .models import Inscription

@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('inscription_id', 'client', 'apprenant', 'seance', 'date_inscription', 'type_inscription', 'statut_inscription')
    list_filter = ('type_inscription', 'statut_inscription', 'date_inscription')
    search_fields = ('client__nom_entite', 'apprenant__nom_apprenant', 'seance__cours__nom_cours')
    date_hierarchy = 'date_inscription'
    
    fieldsets = (
        ('Main Information', {
            'fields': ('client', 'apprenant', 'seance')
        }),
        ('Registration Details', {
            'fields': ('date_inscription', 'type_inscription', 'statut_inscription')
        }),
        ('Sponsor', {
            'fields': ('sponsor',),
            'classes': ('collapse',)
        }),
    )
    
    raw_id_fields = ('client', 'apprenant', 'seance', 'sponsor')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('client', 'apprenant', 'seance', 'sponsor')
