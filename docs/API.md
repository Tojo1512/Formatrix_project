# API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Endpoints

### Cours

#### Liste des cours
```http
GET /cours/
```

#### Détails d'un cours
```http
GET /cours/{cours_id}/
```

#### Créer un cours
```http
POST /cours/
```

Exemple de requête :
```json
{
    "nom_cours": "Python pour débutants",
    "niveau": "Débutant",
    "frais_par_participant": 50000,
    "duree_heures": 20,
    "type_cours": "court",
    "objectifs": "Apprendre les bases de Python",
    "prerequis": "Aucun",
    "materiel_requis": "Ordinateur portable",
    "statut_approbation": "en_attente"
}
```

#### Mettre à jour un cours
```http
PUT /cours/{cours_id}/
```

#### Supprimer un cours
```http
DELETE /cours/{cours_id}/
```

### Modules

#### Liste des modules
```http
GET /modules/
```

#### Détails d'un module
```http
GET /modules/{module_id}/
```

#### Créer un module
```http
POST /modules/
```

Exemple de requête :
```json
{
    "cours": 1,
    "nom_module": "Introduction à Python",
    "description": "Les bases du langage Python",
    "duree_heures": 4,
    "ordre": 1,
    "objectifs_module": "Comprendre la syntaxe de base"
}
```

#### Mettre à jour un module
```http
PUT /modules/{module_id}/
```

#### Supprimer un module
```http
DELETE /modules/{module_id}/
```

### Documents

#### Liste des documents
```http
GET /documents/
```

#### Détails d'un document
```http
GET /documents/{document_id}/
```

#### Créer un document
```http
POST /documents/
```

Exemple de requête :
```json
{
    "cours": 1,
    "type_document": "Support de cours",
    "nom_fichier": "python_basics.pdf",
    "chemin_fichier": "/uploads/python_basics.pdf",
    "date_soumission": "2025-03-04",
    "statut": "en_attente"
}
```

#### Mettre à jour un document
```http
PUT /documents/{document_id}/
```

#### Supprimer un document
```http
DELETE /documents/{document_id}/
```

### Renouvellements

#### Liste des renouvellements
```http
GET /renouvellements/
```

#### Détails d'un renouvellement
```http
GET /renouvellements/{renouvellement_id}/
```

#### Créer un renouvellement
```http
POST /renouvellements/
```

Exemple de requête :
```json
{
    "cours": 1,
    "date_demande": "2025-03-04",
    "statut": "en_cours",
    "commentaires": "Mise à jour du contenu",
    "documents_soumis": ["doc1.pdf", "doc2.pdf"]
}
```

#### Mettre à jour un renouvellement
```http
PUT /renouvellements/{renouvellement_id}/
```

#### Supprimer un renouvellement
```http
DELETE /renouvellements/{renouvellement_id}/
```

### Sessions

#### Liste des sessions
```http
GET /sessions/
```

#### Détails d'une session
```http
GET /sessions/{session_id}/
```

#### Créer une session
```http
POST /sessions/
```

Exemple de requête :
```json
{
    "cours": 1,
    "lieu": 1,
    "horaires": "Lundi-Vendredi, 9h-12h",
    "date_debut": "2025-04-01",
    "date_fin": "2025-04-15",
    "statut": "en_cours",
    "nombre_places_total": 20,
    "nombre_places_restantes": 20
}
```

#### Mettre à jour une session
```http
PUT /sessions/{session_id}/
```

#### Supprimer une session
```http
DELETE /sessions/{session_id}/
```

### Clients

#### Liste des clients
```http
GET /clients/
```

#### Détails d'un client
```http
GET /clients/{client_id}/
```

#### Créer un client
```http
POST /clients/
```

#### Mettre à jour un client
```http
PUT /clients/{client_id}/
```

#### Supprimer un client
```http
DELETE /clients/{client_id}/
```

### Lieux

#### Liste des lieux
```http
GET /lieux/
```

#### Détails d'un lieu
```http
GET /lieux/{lieu_id}/
```

#### Créer un lieu
```http
POST /lieux/
```

#### Mettre à jour un lieu
```http
PUT /lieux/{lieu_id}/
```

#### Supprimer un lieu
```http
DELETE /lieux/{lieu_id}/
```

## Codes de réponse

- `200 OK` : Requête réussie
- `201 Created` : Ressource créée avec succès
- `400 Bad Request` : Requête invalide
- `404 Not Found` : Ressource non trouvée
- `500 Internal Server Error` : Erreur serveur

## Authentification

Toutes les requêtes doivent inclure un token d'authentification dans l'en-tête :

```http
Authorization: Token votre_token_ici
```

## Pagination

Les listes sont paginées par défaut avec 10 éléments par page. Utilisez les paramètres `page` et `page_size` pour naviguer :

```http
GET /cours/?page=2&page_size=20
