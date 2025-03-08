from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.urls import path

from clients.models import Client
from cours.models import Cours
from apprenants.models import Apprenant

# Personnalisation de l'interface d'administration
admin.site.site_header = "Formatrix Administration"
admin.site.site_title = "Formatrix Admin"
admin.site.index_title = "Tableau de bord"

# Vue personnalisée pour le tableau de bord
@staff_member_required
def admin_dashboard(request):
    # Compter les éléments pour les statistiques
    client_count = Client.objects.count()
    cours_count = Cours.objects.count()
    apprenant_count = Apprenant.objects.count()
    
    # Contexte pour le template
    context = {
        'client_count': client_count,
        'cours_count': cours_count,
        'apprenant_count': apprenant_count,
        'title': 'Tableau de bord',
        **admin.site.each_context(request),
    }
    
    return TemplateResponse(request, "admin/index.html", context)

# Remplacer la vue d'index par défaut
admin.site.index = admin_dashboard 