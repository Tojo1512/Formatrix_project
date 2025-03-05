"""
Utilitaires pour la gestion des filtres et de la recherche dans les vues
"""

class FilterBuilder:
    """
    Classe utilitaire pour construire les filtres pour les templates
    """
    
    def __init__(self, request):
        """
        Initialise le FilterBuilder avec la requête
        
        Args:
            request: La requête HTTP
        """
        self.request = request
        self.filters = []
        self.search_query = request.GET.get('search', '')
        self.active_filters_count = 0
        
    def add_filter(self, id_name, label, choices, all_option_text=None):
        """
        Ajoute un filtre à la liste des filtres
        
        Args:
            id_name: ID et nom du champ de filtre
            label: Libellé à afficher
            choices: Liste de tuples (value, label) pour les options
            all_option_text: Texte pour l'option "Tous" (optionnel)
            
        Returns:
            self pour chaînage
        """
        selected = self.request.GET.get(id_name, '')
        
        if selected:
            self.active_filters_count += 1
            
        filter_data = {
            'id': id_name,
            'name': id_name,
            'label': label,
            'choices': choices,
            'selected': selected,
        }
        
        if all_option_text:
            filter_data['all_option_text'] = all_option_text
            
        self.filters.append(filter_data)
        return self
    
    def get_filter_context(self, form_action=None, reset_url=None, 
                          search_placeholder=None, show_reset=True,
                          show_create_button=False, create_url=None, 
                          create_button_text=None):
        """
        Retourne le contexte pour le template de filtres
        
        Args:
            form_action: URL de l'action du formulaire (optionnel)
            reset_url: URL pour le bouton de réinitialisation (optionnel)
            search_placeholder: Placeholder pour le champ de recherche (optionnel)
            show_reset: Booléen pour afficher ou non le bouton de réinitialisation (optionnel)
            show_create_button: Booléen pour afficher ou non le bouton de création (optionnel)
            create_url: URL pour le bouton de création (optionnel)
            create_button_text: Texte pour le bouton de création (optionnel)
            
        Returns:
            Dictionnaire de contexte pour le template
        """
        has_active_filters = self.search_query != '' or self.active_filters_count > 0
        
        context = {
            'form_action': form_action or self.request.path,
            'reset_url': reset_url or self.request.path,
            'search_query': self.search_query,
            'filters': self.filters,
            'has_active_filters': has_active_filters,
            'active_filters_count': self.active_filters_count + (1 if self.search_query else 0),
            'show_reset': show_reset,
        }
        
        if search_placeholder:
            context['search_placeholder'] = search_placeholder
            
        if show_create_button:
            context['show_create_button'] = True
            context['create_url'] = create_url
            
            if create_button_text:
                context['create_button_text'] = create_button_text
                
        return context
    
    def apply_filters_to_queryset(self, queryset, search_fields=None, filter_mappings=None):
        """
        Applique les filtres au queryset
        
        Args:
            queryset: Le queryset à filtrer
            search_fields: Liste des champs à utiliser pour la recherche
            filter_mappings: Dictionnaire de mapping entre les noms de filtres et les champs du modèle
            
        Returns:
            Le queryset filtré
        """
        # Appliquer la recherche
        if self.search_query and search_fields:
            from django.db.models import Q
            query = Q()
            for field in search_fields:
                query |= Q(**{f"{field}__icontains": self.search_query})
            queryset = queryset.filter(query)
        
        # Appliquer les filtres
        if filter_mappings:
            for filter_item in self.filters:
                filter_name = filter_item['name']
                filter_value = filter_item['selected']
                
                if filter_value and filter_name in filter_mappings:
                    field_name = filter_mappings[filter_name]
                    queryset = queryset.filter(**{field_name: filter_value})
        
        return queryset
