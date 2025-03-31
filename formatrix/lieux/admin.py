from django.contrib import admin
from .models import Lieu

@admin.register(Lieu)
class LieuAdmin(admin.ModelAdmin):
    list_display = ('lieu', 'adresse', 'personne_contact', 'telephone', 'mobile')
    search_fields = ('lieu', 'adresse', 'personne_contact')
    
    fieldsets = (
        ('Location Information', {
            'fields': ('lieu', 'adresse')
        }),
        ('Contact', {
            'fields': ('personne_contact', 'telephone', 'mobile')
        }),
    )
