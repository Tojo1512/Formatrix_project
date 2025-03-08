from django.contrib import admin
from .models import TypeClient, Client

@admin.register(TypeClient)
class TypeClientAdmin(admin.ModelAdmin):
    list_display = ('typeclient', 'categorie', 'description')
    list_filter = ('categorie',)
    search_fields = ('typeclient', 'description')
    ordering = ('typeclient',)
    fieldsets = (
        ('Informations principales', {
            'fields': ('typeclient', 'categorie')
        }),
        ('Informations supplémentaires', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom_entite', 'sigle', 'typeclientid', 'secteur_activite', 'personne_contact', 'telephone', 'actif')
    list_filter = ('typeclientid__categorie', 'typeclientid', 'secteur_activite', 'ville', 'actif')
    search_fields = ('nom_entite', 'sigle', 'personne_contact', 'email', 'telephone', 'numero_immatriculation')
    ordering = ('nom_entite',)
    date_hierarchy = 'date_creation'
    list_editable = ('actif',)
    
    fieldsets = (
        ('Informations de l\'entité', {
            'fields': ('nom_entite', 'sigle', 'typeclientid', 'secteur_activite', 'actif')
        }),
        ('Coordonnées', {
            'fields': ('email', 'telephone', 'site_web')
        }),
        ('Adresse', {
            'fields': ('adresse_siege', 'ville', 'localite')
        }),
        ('Personne de contact', {
            'fields': ('personne_contact', 'fonction_contact', 'email_contact', 'telephone_contact'),
            'classes': ('collapse',)
        }),
        ('Informations légales', {
            'fields': ('numero_immatriculation',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('typeclientid')
