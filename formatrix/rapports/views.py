from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, F, Q, Case, When, Value, IntegerField, DecimalField
from django.db.models.functions import TruncYear, TruncMonth
from django.utils import timezone
from datetime import datetime, timedelta

from apprenants.models import Apprenant
from inscriptions.models import Inscription
from cours.models import Cours
from seances.models import Seance
from formateurs.models import Formateur
from lieux.models import Lieu
from paiements.models import Facture, Paiement

@login_required
def dashboard(request):
    """Vue principale du tableau de bord des rapports"""
    
    # Statistiques générales
    total_apprenants = Apprenant.objects.count()
    total_cours = Cours.objects.count()
    total_inscriptions = Inscription.objects.count()
    total_seances = Seance.objects.count()
    
    # Inscriptions récentes (30 derniers jours)
    date_limite = timezone.now() - timedelta(days=30)
    inscriptions_recentes = Inscription.objects.filter(date_inscription__gte=date_limite).count()
    
    # Répartition par genre
    repartition_genre = Apprenant.objects.values('sexe').annotate(
        total=Count('apprenant_id')
    ).order_by('sexe')
    
    # Répartition par âge
    repartition_age = Apprenant.objects.values('categorie_age').annotate(
        total=Count('apprenant_id')
    ).order_by('categorie_age')
    
    # Cours les plus populaires
    cours_populaires = Cours.objects.annotate(
        total_inscriptions=Count('seances__inscriptions')
    ).order_by('-total_inscriptions')[:5]
    
    context = {
        'total_apprenants': total_apprenants,
        'total_cours': total_cours,
        'total_inscriptions': total_inscriptions,
        'total_seances': total_seances,
        'inscriptions_recentes': inscriptions_recentes,
        'repartition_genre': repartition_genre,
        'repartition_age': repartition_age,
        'cours_populaires': cours_populaires,
    }
    
    return render(request, 'rapports/dashboard.html', context)

@login_required
def rapport_demographique(request):
    """Rapport démographique des apprenants par genre, âge et niveau académique"""
    
    # Répartition par genre et âge
    genre_age = Apprenant.objects.values('sexe', 'categorie_age').annotate(
        total=Count('apprenant_id')
    ).order_by('sexe', 'categorie_age')
    
    # Répartition par genre et niveau académique
    genre_niveau = Apprenant.objects.values('sexe', 'niveau_academique').annotate(
        total=Count('apprenant_id')
    ).order_by('sexe', 'niveau_academique')
    
    # Données pour les graphiques - utiliser des clés sans tirets
    hommes_par_age = {
        'tranche1': Apprenant.objects.filter(sexe='M', categorie_age='16-30').count(),
        'tranche2': Apprenant.objects.filter(sexe='M', categorie_age='31-60').count(),
        'tranche3': Apprenant.objects.filter(sexe='M', categorie_age='60+').count(),
    }
    
    femmes_par_age = {
        'tranche1': Apprenant.objects.filter(sexe='F', categorie_age='16-30').count(),
        'tranche2': Apprenant.objects.filter(sexe='F', categorie_age='31-60').count(),
        'tranche3': Apprenant.objects.filter(sexe='F', categorie_age='60+').count(),
    }
    
    hommes_par_niveau = {
        'below_certificate': Apprenant.objects.filter(sexe='M', niveau_academique='below_certificate').count(),
        'high_school': Apprenant.objects.filter(sexe='M', niveau_academique='high_school').count(),
        'higher_education': Apprenant.objects.filter(sexe='M', niveau_academique='higher_education').count(),
    }
    
    femmes_par_niveau = {
        'below_certificate': Apprenant.objects.filter(sexe='F', niveau_academique='below_certificate').count(),
        'high_school': Apprenant.objects.filter(sexe='F', niveau_academique='high_school').count(),
        'higher_education': Apprenant.objects.filter(sexe='F', niveau_academique='higher_education').count(),
    }
    
    context = {
        'genre_age': genre_age,
        'genre_niveau': genre_niveau,
        'hommes_par_age': hommes_par_age,
        'femmes_par_age': femmes_par_age,
        'hommes_par_niveau': hommes_par_niveau,
        'femmes_par_niveau': femmes_par_niveau,
    }
    
    return render(request, 'rapports/rapport_demographique.html', context)

@login_required
def rapport_ressources(request):
    """Rapport sur l'utilisation des ressources (formateurs, lieux, horaires)"""
    
    # Année en cours
    annee_courante = timezone.now().year
    
    # Nombre de cours par formateur pour l'année en cours
    cours_par_formateur = Formateur.objects.annotate(
        total_cours=Count('seances_assignees', 
                         filter=Q(seances_assignees__date__year=annee_courante))
    ).order_by('-total_cours')
    
    # Taux d'utilisation des lieux
    total_seances = Seance.objects.count()
    lieux_utilisation = Lieu.objects.annotate(
        total_seances=Count('seance'),
        pourcentage=Case(
            When(total_seances=0, then=Value(0)),
            default=Count('seance') * 100 / Value(total_seances),
            output_field=DecimalField()
        )
    ).order_by('-total_seances')
    
    # Répartition des cours selon les horaires
    repartition_horaires = Cours.objects.values('horaire').annotate(
        total=Count('cours_id')
    ).order_by('horaire')
    
    context = {
        'cours_par_formateur': cours_par_formateur,
        'lieux_utilisation': lieux_utilisation,
        'repartition_horaires': repartition_horaires,
        'annee_courante': annee_courante,
    }
    
    return render(request, 'rapports/rapport_ressources.html', context)

@login_required
def rapport_clients(request):
    """Rapport sur les clients (chiffre d'affaires, nombre de cours)"""
    
    # Chiffre d'affaires par client
    chiffre_affaires = Facture.objects.values(
        'destinataire_nom'
    ).annotate(
        total=Sum('montant_ttc')
    ).order_by('-total')
    
    # Nombre de cours par client
    cours_par_client = Inscription.objects.values(
        'client__nom_entite'
    ).annotate(
        total_cours=Count('seance', distinct=True)
    ).order_by('-total_cours')
    
    # Nombre de cours par apprenant
    cours_par_apprenant = Inscription.objects.values(
        'apprenant__nom_apprenant'
    ).annotate(
        total_cours=Count('seance', distinct=True)
    ).order_by('-total_cours')
    
    context = {
        'chiffre_affaires': chiffre_affaires,
        'cours_par_client': cours_par_client,
        'cours_par_apprenant': cours_par_apprenant,
    }
    
    return render(request, 'rapports/rapport_clients.html', context)

@login_required
def export_rapport(request, rapport_type):
    """Vue pour exporter les rapports au format CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{rapport_type}_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    if rapport_type == 'demographique':
        # En-tête du CSV
        writer.writerow(['Genre', 'Catégorie d\'âge', 'Nombre d\'apprenants'])
        
        # Données
        genre_age = Apprenant.objects.values('sexe', 'categorie_age').annotate(
            total=Count('apprenant_id')
        ).order_by('sexe', 'categorie_age')
        
        for item in genre_age:
            genre = 'Homme' if item['sexe'] == 'M' else 'Femme' if item['sexe'] == 'F' else 'Autre'
            writer.writerow([genre, item['categorie_age'], item['total']])
            
        writer.writerow([])  # Ligne vide
        writer.writerow(['Genre', 'Niveau académique', 'Nombre d\'apprenants'])
        
        genre_niveau = Apprenant.objects.values('sexe', 'niveau_academique').annotate(
            total=Count('apprenant_id')
        ).order_by('sexe', 'niveau_academique')
        
        for item in genre_niveau:
            genre = 'Homme' if item['sexe'] == 'M' else 'Femme' if item['sexe'] == 'F' else 'Autre'
            niveau = item['niveau_academique']
            if niveau == 'below_certificate':
                niveau = 'En dessous du certificat scolaire'
            elif niveau == 'high_school':
                niveau = 'Certificat scolaire'
            elif niveau == 'higher_education':
                niveau = 'Études supérieures'
            writer.writerow([genre, niveau, item['total']])
    
    elif rapport_type == 'ressources':
        # En-tête du CSV
        writer.writerow(['Formateur', 'Nombre de cours'])
        
        # Données
        annee_courante = timezone.now().year
        cours_par_formateur = Formateur.objects.annotate(
            total_cours=Count('seances_assignees', 
                             filter=Q(seances_assignees__date__year=annee_courante))
        ).order_by('-total_cours')
        
        for formateur in cours_par_formateur:
            writer.writerow([formateur.nom_formateur, formateur.total_cours])
            
        writer.writerow([])  # Ligne vide
        writer.writerow(['Lieu', 'Nombre de séances', 'Pourcentage d\'utilisation'])
        
        total_seances = Seance.objects.count()
        lieux_utilisation = Lieu.objects.annotate(
            total_seances=Count('seance'),
            pourcentage=Case(
                When(total_seances=0, then=Value(0)),
                default=Count('seance') * 100 / Value(total_seances),
                output_field=DecimalField()
            )
        ).order_by('-total_seances')
        
        for lieu in lieux_utilisation:
            writer.writerow([lieu.lieu, lieu.total_seances, f"{lieu.pourcentage:.2f}%"])
    
    elif rapport_type == 'clients':
        # En-tête du CSV
        writer.writerow(['Client', 'Chiffre d\'affaires'])
        
        # Données
        chiffre_affaires = Facture.objects.values(
            'destinataire_nom'
        ).annotate(
            total=Sum('montant_ttc')
        ).order_by('-total')
        
        for client in chiffre_affaires:
            writer.writerow([client['destinataire_nom'], f"{client['total']} Rs"])
            
        writer.writerow([])  # Ligne vide
        writer.writerow(['Client', 'Nombre de cours'])
        
        cours_par_client = Inscription.objects.values(
            'client__nom_entite'
        ).annotate(
            total_cours=Count('seance', distinct=True)
        ).order_by('-total_cours')
        
        for client in cours_par_client:
            writer.writerow([client['client__nom_entite'], client['total_cours']])
    
    return response
