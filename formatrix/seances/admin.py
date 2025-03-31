from django.contrib import admin
from .models import Seance, Absence

class AbsenceInline(admin.TabularInline):
    model = Absence
    extra = 0
    fields = ('formateur_absent', 'date_absence', 'raison', 'formateur_remplacant', 'est_remplace')
    raw_id_fields = ('formateur_absent', 'formateur_remplacant')

@admin.register(Seance)
class SeanceAdmin(admin.ModelAdmin):
    list_display = ('seance_id', 'cours', 'lieu', 'date', 'nombre_places', 'places_reservees', 'places_disponibles', 'statut')
    list_filter = ('statut', 'lieu', 'date')
    search_fields = ('cours__nom_cours', 'lieu__lieu')
    date_hierarchy = 'date'
    inlines = [AbsenceInline]
    
    fieldsets = (
        ('Session Information', {
            'fields': ('cours', 'lieu', 'date', 'duree')
        }),
        ('Capacity and Pricing', {
            'fields': ('nombre_places', 'places_reservees', 'prix')
        }),
        ('Status', {
            'fields': ('statut', 'started_at', 'completed_at')
        }),
    )
    
    readonly_fields = ('places_reservees', 'started_at', 'completed_at')
    filter_horizontal = ('formateurs',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cours', 'lieu')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Additional logic if needed when saving a session

@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ('absence_id', 'seance', 'formateur_absent', 'date_absence', 'raison', 'est_remplace', 'formateur_remplacant')
    list_filter = ('est_remplace', 'raison', 'date_absence')
    search_fields = ('formateur_absent__nom', 'formateur_absent__prenom', 'seance__cours__nom_cours')
    date_hierarchy = 'date_absence'
    
    fieldsets = (
        ('Absence Information', {
            'fields': ('seance', 'formateur_absent', 'date_absence', 'raison')
        }),
        ('Replacement', {
            'fields': ('est_remplace', 'formateur_remplacant')
        }),
        ('Details', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
    )
    
    raw_id_fields = ('seance', 'formateur_absent', 'formateur_remplacant')
    readonly_fields = ('est_remplace',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('seance', 'formateur_absent', 'formateur_remplacant', 'seance__cours')
