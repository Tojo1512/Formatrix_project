from django.contrib import admin
from .models import Apprenant

@admin.register(Apprenant)
class ApprenantAdmin(admin.ModelAdmin):
    list_display = ('nom_apprenant', 'autres_nom', 'cin', 'sexe', 'niveau_academique', 'categorie_age', 'ville')
    list_filter = ('sexe', 'niveau_academique', 'categorie_age', 'ville')
    search_fields = ('nom_apprenant', 'autres_nom', 'cin', 'adresse_rue', 'localite', 'ville')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('nom_apprenant', 'autres_nom', 'cin', 'date_naissance', 'sexe')
        }),
        ('Address', {
            'fields': ('adresse_rue', 'localite', 'ville')
        }),
        ('Learning Profile', {
            'fields': ('type_apprenant', 'niveau_academique', 'categorie_age', 'besoins_speciaux')
        }),
        ('Emergency Contact', {
            'fields': ('contact_urgence', 'telephone_urgence')
        }),
    )
