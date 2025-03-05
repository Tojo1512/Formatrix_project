# Utilitaires Formatrix

Ce dossier contient des utilitaires réutilisables pour le projet Formatrix.

## FilterBuilder

Le `FilterBuilder` est une classe utilitaire pour construire et appliquer des filtres dans les vues Django.

### Utilisation

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
        search_placeholder='Rechercher...'
    )
    
    # Ajout du contexte des filtres au contexte de la vue
    context.update(filter_context)
    
    return context
```

Pour plus d'informations, consultez la documentation complète dans le dossier `docs/filters.md`.
