from django.contrib import admin
from .models import Presence

@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ('apprenant', 'seance', 'date_presence', 'present', 'retard', 'created_at')
    list_filter = ('present', 'date_presence', 'seance__cours')
    search_fields = ('apprenant__nom_apprenant', 'apprenant__cin', 'seance__cours__nom_cours')
    date_hierarchy = 'date_presence'
    
    fieldsets = (
        ('Attendance Information', {
            'fields': ('apprenant', 'seance', 'date_presence')
        }),
        ('Status', {
            'fields': ('present', 'retard')
        }),
        ('Additional Information', {
            'fields': ('commentaires',),
            'classes': ('collapse',)
        }),
    )
    
    raw_id_fields = ('apprenant', 'seance')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('apprenant', 'seance', 'seance__cours')
