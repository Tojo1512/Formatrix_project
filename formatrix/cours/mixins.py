"""
Mixins pour les vues de l'application Cours
"""
from django.urls import reverse_lazy
from django.db.models import Q
from utils.filter_utils import FilterBuilder
from .models import Cours

class CoursFilterMixin:
    """
    Mixin pour ajouter des fonctionnalités de filtrage aux vues de cours
    """
    
    def get_queryset(self):
        """
        Applique les filtres au queryset
        """
        queryset = super().get_queryset()
        
        # Récupération des paramètres de filtrage
        search_query = self.request.GET.get('search', '').strip()
        statut = self.request.GET.get('statut_approbation', '').strip()
        type_cours = self.request.GET.get('type_cours', '').strip()
        
        # Application des filtres
        if search_query:
            queryset = queryset.filter(
                Q(nom_cours__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        if statut:
            queryset = queryset.filter(statut_approbation=statut)
            
        if type_cours:
            queryset = queryset.filter(type_cours=type_cours)
        
        return queryset
    
    def get_filter_context(self):
        """
        Retourne le contexte pour les filtres
        """
        # Création du FilterBuilder
        filter_builder = FilterBuilder(self.request)
        
        # Ajout des filtres
        filter_builder.add_filter(
            'statut_approbation', 
            'Statut', 
            Cours.STATUT_APPROBATION_CHOICES,
            all_option_text='Tous les statuts'
        )
        
        filter_builder.add_filter(
            'type_cours', 
            'Type de cours', 
            Cours.TYPE_CHOICES,
            all_option_text='Tous les types'
        )
        
        # Récupération du contexte des filtres
        filter_context = filter_builder.get_filter_context(
            search_placeholder='Rechercher un cours...',
            show_create_button=True,
            create_url=reverse_lazy('cours-create'),
            create_button_text='Créer un cours',
            form_action=self.request.path,
            reset_url=self.request.path
        )
        
        return filter_context
    
    def get_context_data(self, **kwargs):
        """
        Ajoute le contexte des filtres au contexte de la vue
        """
        context = super().get_context_data(**kwargs)
        context.update(self.get_filter_context())
        return context
