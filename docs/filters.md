# Système de Filtres Réutilisable

Ce document explique comment utiliser le système de filtres réutilisable dans le projet Formatrix.

## Vue d'ensemble

Le système de filtres réutilisable se compose de trois parties principales :

1. **FilterBuilder** : Une classe utilitaire pour construire et appliquer des filtres
2. **Composant de template** : Un template réutilisable pour afficher les filtres
3. **Mixins** : Des mixins pour intégrer facilement les filtres dans les vues

## Utilisation du FilterBuilder

Le `FilterBuilder` est une classe utilitaire qui facilite la construction et l'application des filtres.

```python
from formatrix.utils.filter_utils import FilterBuilder

# Dans une vue
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # Création du FilterBuilder avec la requête
    filter_builder = FilterBuilder(self.request)
    
    # Ajout des filtres
    filter_builder.add_filter(
        'status',                          # ID et nom du champ
        'Statut',                          # Libellé à afficher
        MyModel.STATUS_CHOICES,            # Choix (tuples value, label)
        all_option_text='Tous les statuts' # Texte pour l'option "Tous"
    )
    
    # Récupération du contexte des filtres
    filter_context = filter_builder.get_filter_context(
        search_placeholder='Rechercher...',
        show_create_button=True,
        create_url=reverse_lazy('create-view'),
        create_button_text='Créer'
    )
    
    # Ajout du contexte des filtres au contexte de la vue
    context.update(filter_context)
    
    return context

# Application des filtres au queryset
def get_queryset(self):
    queryset = super().get_queryset()
    
    filter_builder = FilterBuilder(self.request)
    
    # Définition des mappings entre les noms de filtres et les champs du modèle
    filter_mappings = {
        'status': 'status_field',
        'type': 'type_field',
    }
    
    # Application des filtres au queryset
    queryset = filter_builder.apply_filters_to_queryset(
        queryset,
        search_fields=['name', 'description'],  # Champs à utiliser pour la recherche
        filter_mappings=filter_mappings
    )
    
    return queryset
```

## Utilisation du Composant de Template

Le composant de template `filter_search_bar.html` peut être inclus dans n'importe quel template pour afficher les filtres.

```html
{% include "components/filter_search_bar.html" %}
```

Le composant s'attend à trouver certaines variables dans le contexte, qui sont fournies par le `FilterBuilder`.

## Utilisation des Mixins

Pour simplifier l'intégration des filtres dans les vues, vous pouvez créer des mixins spécifiques à vos modèles.

```python
# Dans un fichier mixins.py
from formatrix.utils.filter_utils import FilterBuilder

class MyModelFilterMixin:
    """
    Mixin pour ajouter des fonctionnalités de filtrage aux vues de MyModel
    """
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        filter_builder = FilterBuilder(self.request)
        
        filter_mappings = {
            'status': 'status_field',
            'type': 'type_field',
        }
        
        queryset = filter_builder.apply_filters_to_queryset(
            queryset,
            search_fields=['name'],
            filter_mappings=filter_mappings
        )
        
        return queryset
    
    def get_filter_context(self):
        filter_builder = FilterBuilder(self.request)
        
        filter_builder.add_filter(
            'status', 
            'Statut', 
            MyModel.STATUS_CHOICES
        )
        
        filter_context = filter_builder.get_filter_context(
            search_placeholder='Rechercher...',
            show_create_button=True,
            create_url=reverse_lazy('create-view')
        )
        
        return filter_context
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_filter_context())
        return context

# Dans vos vues
class MyModelListView(LoginRequiredMixin, MyModelFilterMixin, ListView):
    model = MyModel
    template_name = 'mymodel/list.html'
```

## Personnalisation

Le système de filtres est hautement personnalisable :

1. **Apparence** : Le composant de template utilise les variables CSS définies dans le projet
2. **Comportement** : Le JavaScript inclus gère le comportement des filtres
3. **Filtres** : Vous pouvez ajouter autant de filtres que nécessaire

## Options du FilterBuilder

### Méthode add_filter

```python
add_filter(id_name, label, choices, all_option_text=None)
```

- `id_name` : ID et nom du champ de filtre
- `label` : Libellé à afficher
- `choices` : Liste de tuples (value, label) pour les options
- `all_option_text` : Texte pour l'option "Tous" (optionnel)

### Méthode get_filter_context

```python
get_filter_context(form_action=None, reset_url=None, 
                  search_placeholder=None, show_reset=True,
                  show_create_button=False, create_url=None, 
                  create_button_text=None)
```

- `form_action` : URL de l'action du formulaire (optionnel)
- `reset_url` : URL pour le bouton de réinitialisation (optionnel)
- `search_placeholder` : Placeholder pour le champ de recherche (optionnel)
- `show_reset` : Booléen pour afficher ou non le bouton de réinitialisation (optionnel)
- `show_create_button` : Booléen pour afficher ou non le bouton de création (optionnel)
- `create_url` : URL pour le bouton de création (optionnel)
- `create_button_text` : Texte pour le bouton de création (optionnel)

### Méthode apply_filters_to_queryset

```python
apply_filters_to_queryset(queryset, search_fields=None, filter_mappings=None)
```

- `queryset` : Le queryset à filtrer
- `search_fields` : Liste des champs à utiliser pour la recherche
- `filter_mappings` : Dictionnaire de mapping entre les noms de filtres et les champs du modèle
