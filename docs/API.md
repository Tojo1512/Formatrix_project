# API Documentation

## Table des matières
- [Base URL](#base-url)
- [Cours](#cours)
- [Modules](#modules)
- [Documents](#documents)
- [Renouvellements](#renouvellements)
- [Séances](#seances)
- [Clients](#clients)
- [Lieux](#lieux)
- [Apprenants](#apprenants)
- [Inscriptions](#inscriptions)
- [Evaluations](#evaluations)
- [Présences](#presences)

## Base URL
```
http://localhost:8000/api/
```

## Cours

### Liste des cours
```http
GET /cours/
```
[Tester dans le navigateur](http://localhost:8000/api/cours/)

### Détails d'un cours
```http
GET /cours/{cours_id}/
```
[Exemple](http://localhost:8000/api/cours/1/)

### Créer un cours
```http
POST /cours/
```

Exemple de requête :
```json
{
    "nom_cours": "Python pour débutants",
    "description": "Formation complète pour débutants en Python",
    "niveau": "Débutant",
    "frais_par_participant": 50000,
    "duree_heures": 20,
    "periode_mois": 1,
    "type_cours": "court",
    "objectifs": "Apprendre les bases de Python",
    "prerequis": "Aucun",
    "materiel_requis": "Ordinateur portable",
    "horaire": "pendant_bureau",
    "statut_approbation": "en_attente"
}
```

### Mettre à jour un cours
```http
PUT /cours/{cours_id}/
```

### Supprimer un cours
```http
DELETE /cours/{cours_id}/
```

## Modules

### Liste des modules
```http
GET /modules/
```
[Tester dans le navigateur](http://localhost:8000/api/modules/)

### Détails d'un module
```http
GET /modules/{module_id}/
```
[Exemple](http://localhost:8000/api/modules/1/)

### Créer un module
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

### Mettre à jour un module
```http
PUT /modules/{module_id}/
```

### Supprimer un module
```http
DELETE /modules/{module_id}/
```

## Documents

### Liste des documents
```http
GET /documents/
```
[Tester dans le navigateur](http://localhost:8000/api/documents/)

### Détails d'un document
```http
GET /documents/{document_id}/
```
[Exemple](http://localhost:8000/api/documents/1/)

### Créer un document
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
    "statut": "en_attente",
    "commentaires": "Version initiale"
}
```

### Mettre à jour un document
```http
PUT /documents/{document_id}/
```

### Supprimer un document
```http
DELETE /documents/{document_id}/
```

## Renouvellements

### Liste des renouvellements
```http
GET /renouvellements/
```
[Tester dans le navigateur](http://localhost:8000/api/renouvellements/)

### Détails d'un renouvellement
```http
GET /renouvellements/{renouvellement_id}/
```
[Exemple](http://localhost:8000/api/renouvellements/1/)

### Créer un renouvellement
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

### Mettre à jour un renouvellement
```http
PUT /renouvellements/{renouvellement_id}/
```

### Supprimer un renouvellement
```http
DELETE /renouvellements/{renouvellement_id}/
```

## Séances

### Liste des séances
```http
GET /seances/
```
[Tester dans le navigateur](http://localhost:8000/api/seances/)

### Détails d'une séance
```http
GET /seances/{seance_id}/
```
[Exemple](http://localhost:8000/api/seances/1/)

### Créer une séance
```http
POST /seances/
```

Exemple de requête :
```json
{
    "cours": 1,
    "lieu": 1,
    "horaires": "pendant_bureau",
    "date_debut": "2025-04-01",
    "date_fin": "2025-04-15",
    "statut": "en_cours",
    "nombre_places_total": 20,
    "nombre_places_restantes": 20
}
```

### Mettre à jour une séance
```http
PUT /seances/{seance_id}/
```

### Supprimer une séance
```http
DELETE /seances/{seance_id}/
```

## Clients

### Liste des clients
```http
GET /clients/
```
[Tester dans le navigateur](http://localhost:8000/api/clients/)

### Détails d'un client
```http
GET /clients/{client_id}/
```
[Exemple](http://localhost:8000/api/clients/1/)

### Créer un client
```http
POST /clients/
```

### Mettre à jour un client
```http
PUT /clients/{client_id}/
```

### Supprimer un client
```http
DELETE /clients/{client_id}/
```

## Lieux

### Liste des lieux
```http
GET /lieux/
```
[Tester dans le navigateur](http://localhost:8000/api/lieux/)

### Détails d'un lieu
```http
GET /lieux/{lieu_id}/
```
[Exemple](http://localhost:8000/api/lieux/1/)

### Créer un lieu
```http
POST /lieux/
```

### Mettre à jour un lieu
```http
PUT /lieux/{lieu_id}/
```

### Supprimer un lieu
```http
DELETE /lieux/{lieu_id}/
```

## Apprenants

### Liste des apprenants
```http
GET /api/apprenants/apprenants/
```
[Tester dans le navigateur](http://localhost:8000/api/apprenants/apprenants/)

### Détails d'un apprenant
```http
GET /api/apprenants/apprenants/{apprenant_id}/
```
[Exemple](http://localhost:8000/api/apprenants/apprenants/1/)

### Créer un apprenant
```http
POST /api/apprenants/apprenants/
```

Exemple de requête :
```json
{
    "nom_apprenant": "John Doe",
    "cin": "101234567890",
    "date_naissance": "1990-01-01",
    "adresse_rue": "123 Rue Exemple",
    "localite": "Quartier",
    "ville": "Ville",
    "type_apprenant": "individuel",
    "sexe": "M",
    "categorie_age": "31-60",
    "niveau_academique": "certificat",
    "contact_urgence": "Jane Doe",
    "telephone_urgence": "0341234567"
}
```

### Statistiques des apprenants
```http
GET /api/apprenants/apprenants/statistiques/
GET /api/apprenants/apprenants/par_ville/
```

Les statistiques incluent :
- Nombre total d'apprenants
- Répartition par genre
- Répartition par catégorie d'âge
- Répartition par niveau académique
- Répartition par type d'apprenant
- Répartition par ville

## Inscriptions

### Liste des inscriptions
```http
GET /api/inscriptions/inscriptions/
```
[Tester dans le navigateur](http://localhost:8000/api/inscriptions/inscriptions/)

### Créer une inscription
```http
POST /api/inscriptions/inscriptions/
```

Exemple de requête :
```json
{
    "apprenant_id": 1,
    "seance_id": 1,
    "client_id": 1,
    "type_inscription": "individuelle",
    "statut_inscription": "en_cours"
}
```

### Statistiques des inscriptions
```http
GET /api/inscriptions/inscriptions/par_type/
GET /api/inscriptions/inscriptions/par_statut/
GET /api/inscriptions/inscriptions/par_seance/
```

## Evaluations

### Liste des évaluations
```http
GET /api/apprenants/evaluations/
```
[Tester dans le navigateur](http://localhost:8000/api/apprenants/evaluations/)

### Créer une évaluation
```http
POST /api/apprenants/evaluations/
```

Exemple de requête :
```json
{
    "inscription_id": 1,
    "assiduite": 95.5,
    "evaluation_continue": {
        "module1": 85,
        "module2": 90
    },
    "portfolio_url": "https://exemple.com/portfolio",
    "statut_final": "reussite",
    "commentaires": "Excellent travail"
}
```

### Statistiques des évaluations
```http
GET /api/apprenants/evaluations/statistiques/
```

## Présences

### Liste des présences
```http
GET /api/presences/
```
[Tester dans le navigateur](http://localhost:8000/api/presences/)

### Détails d'une présence
```http
GET /api/presences/{presence_id}/
```

### Créer une présence
```http
POST /api/presences/
```

Exemple de requête :
```json
{
    "date_presence": "2025-03-05",
    "seance_id": 1,
    "apprenant_id": 1,
    "present": true,
    "retard": 0,
    "commentaires": "RAS"
}
```

### Statistiques des présences
```http
GET /api/presences/statistiques/
```

Retourne :
- Nombre total de présences
- Nombre de présents
- Nombre d'absents
- Retard moyen

### Présences par séance
```http
GET /api/presences/par_seance/?seance_id=1
```

### Résultats

#### Liste des résultats
```http
GET /api/evaluations/resultats/
```

#### Détails d'un résultat
```http
GET /api/evaluations/resultats/{resultat_id}/
```

#### Créer un résultat
```http
POST /api/evaluations/resultats/
```

Exemple de requête :
```json
{
    "seance_id": 1,
    "apprenant_id": 1,
    "resultat": "reussite",
    "evaluation_continue": 85.5,
    "portfolio_complete": true,
    "commentaires": "Excellent travail",
    "date_evaluation": "2025-03-05"
}
```

#### Statistiques des résultats
```http
GET /api/evaluations/resultats/statistiques/
```

Retourne :
- Nombre total de résultats
- Répartition par statut (réussite/échec/abandon)
- Moyenne des évaluations continues
- Nombre de portfolios complétés

#### Résultats par séance
```http
GET /api/evaluations/resultats/par_seance/?seance_id=1
```

## Notes sur l'API

### Authentification
- L'API utilise l'authentification par token JWT
- Incluez le token dans le header de chaque requête : `Authorization: Bearer <token>`

### Codes de réponse
- 200 : Succès
- 201 : Création réussie
- 400 : Erreur de validation
- 401 : Non authentifié
- 403 : Non autorisé
- 404 : Ressource non trouvée
- 500 : Erreur serveur

### Pagination
- Les listes sont paginées par défaut (20 éléments par page)
- Utilisez `?page=<numero>` pour naviguer entre les pages
- Utilisez `?limit=<nombre>` pour modifier le nombre d'éléments par page

### Filtres
- Utilisez `?search=<terme>` pour rechercher dans les champs texte
- Utilisez `?ordering=<champ>` pour trier les résultats
- Préfixez le champ avec `-` pour un tri descendant (ex: `?ordering=-date_creation`)
