from django.views.generic import TemplateView
from django.db.models import Count
from django.db.models.functions import ExtractYear
from .models import Apprenant
import logging

logger = logging.getLogger(__name__)

class RapportsDemographiquesView(TemplateView):
    template_name = 'apprenants/rapports_demographiques.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all learners
        all_apprenants = Apprenant.objects.all()
        
        # Get men and women
        hommes = Apprenant.objects.filter(sexe='M')
        femmes = Apprenant.objects.filter(sexe='F')
        
        # Statistics by gender and age group
        stats_age_hommes = {}
        stats_age_femmes = {}
        
        # Statistics by gender and academic level
        stats_niveau_hommes = {}
        stats_niveau_femmes = {}
        
        # Initialize dictionaries with zeros
        categories_age = [x[0] for x in Apprenant.CATEGORIE_AGE_CHOICES]
        niveaux_academiques = [x[0] for x in Apprenant.NIVEAU_ACADEMIQUE_CHOICES]
        
        for categorie in categories_age:
            stats_age_hommes[categorie] = 0
            stats_age_femmes[categorie] = 0
            
        for niveau in niveaux_academiques:
            stats_niveau_hommes[niveau] = 0
            stats_niveau_femmes[niveau] = 0
        
        # Fill dictionaries manually
        for homme in hommes:
            stats_age_hommes[homme.categorie_age] = stats_age_hommes.get(homme.categorie_age, 0) + 1
            stats_niveau_hommes[homme.niveau_academique] = stats_niveau_hommes.get(homme.niveau_academique, 0) + 1
            
        for femme in femmes:
            stats_age_femmes[femme.categorie_age] = stats_age_femmes.get(femme.categorie_age, 0) + 1
            stats_niveau_femmes[femme.niveau_academique] = stats_niveau_femmes.get(femme.niveau_academique, 0) + 1
        
        # Calculate totals from sum of values
        total_hommes_age = sum(stats_age_hommes.values())
        total_hommes_niveau = sum(stats_niveau_hommes.values())
        total_femmes_age = sum(stats_age_femmes.values())
        total_femmes_niveau = sum(stats_niveau_femmes.values())
        
        # Use calculated totals
        total_hommes = total_hommes_age
        total_femmes = total_femmes_age
        total_apprenants = total_hommes + total_femmes
        
        # Check consistency
        if total_hommes_age != total_hommes_niveau:
            logger.warning(f"Inconsistency detected between age and level totals for men: {total_hommes_age} != {total_hommes_niveau}")
        
        if total_femmes_age != total_femmes_niveau:
            logger.warning(f"Inconsistency detected between age and level totals for women: {total_femmes_age} != {total_femmes_niveau}")
        
        context.update({
            'stats_age_hommes': stats_age_hommes,
            'stats_age_femmes': stats_age_femmes,
            'stats_niveau_hommes': stats_niveau_hommes,
            'stats_niveau_femmes': stats_niveau_femmes,
            'total_hommes': total_hommes,
            'total_femmes': total_femmes,
            'total_apprenants': total_apprenants,
            'categories_age': categories_age,
            'niveaux_academiques': niveaux_academiques
        })
        
        return context 