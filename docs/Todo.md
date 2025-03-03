# Todo List Formatrix - Implémentation Django & PostgreSQL

## 1. Configuration de l'environnement

- [ ] Installer Python et créer un environnement virtuel
  ```bash
  python -m venv formatrix_env
  source formatrix_env/bin/activate  # Sur Windows: formatrix_env\Scripts\activate
  ```

- [ ] Installer Django et dépendances
  ```bash
  pip install django psycopg2-binary django-crispy-forms django-tables2 django-filter
  ```

- [ ] Configurer PostgreSQL
  - [ ] Vérifier que le script PostgreSQL existant est prêt à être utilisé
  - [ ] Créer une base de données pour Formatrix
  - [ ] Créer un utilisateur avec les droits appropriés

## 2. Initialisation du projet Django

- [ ] Créer le projet Django
  ```bash
  django-admin startproject formatrix
  cd formatrix
  ```

- [ ] Configurer la connexion à PostgreSQL dans settings.py
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'NAME': 'formatrix_db',
          'USER': 'formatrix_user',
          'PASSWORD': 'votre_mot_de_passe',
          'HOST': 'localhost',
          'PORT': '5432',
      }
  }
  ```

- [ ] Configurer les paramètres internationaux pour le français
  ```python
  LANGUAGE_CODE = 'fr-fr'
  TIME_ZONE = 'Indian/Mauritius'
  USE_I18N = True
  USE_L10N = True
  USE_TZ = True
  ```

## 3. Création des applications Django

- [ ] Créer les applications principales
  ```bash
  python manage.py startapp courses  # Gestion des cours
  python manage.py startapp students  # Gestion des étudiants
  python manage.py startapp trainers  # Gestion des formateurs
  python manage.py startapp billing  # Facturation et paiements
  python manage.py startapp reports  # Rapports et analyses
  python manage.py startapp dashboard  # Tableau de bord principal
  ```

- [ ] Enregistrer les applications dans settings.py
  ```python
  INSTALLED_APPS = [
      # ...
      'courses',
      'students',
      'trainers',
      'billing',
      'reports',
      'dashboard',
      'crispy_forms',
      'django_tables2',
      'django_filters',
  ]
  ```

## 4. Définition des modèles

### Application Courses

- [ ] Modèle Course
  - [ ] Titre, description, objectifs
  - [ ] Durée, date début/fin
  - [ ] Type (formation de formateurs, apprentissage)
  - [ ] État (en cours, terminé, annulé)
  - [ ] Informations d'approbation (date, validité)

- [ ] Modèle CourseSession
  - [ ] Lieu, horaire, dates
  - [ ] Association aux formateurs

- [ ] Créer les signaux pour les alertes de fin de validité

### Application Students

- [ ] Modèle Student
  - [ ] Informations personnelles
  - [ ] Âge, genre, niveau académique

- [ ] Modèle Enrollment
  - [ ] Type d'inscription (individuelle, entreprise, ONG)
  - [ ] Lien vers le sponsor (si applicable)
  - [ ] Statut de paiement

- [ ] Modèle Result
  - [ ] Assiduité, évaluations, portfolio
  - [ ] Statut final (réussite, échec, abandon)

### Application Trainers

- [ ] Modèle Trainer
  - [ ] Informations personnelles, qualifications
  - [ ] Spécialités, disponibilités

- [ ] Modèle TrainerAttendance
  - [ ] Heures de présence
  - [ ] Remplacements

### Application Billing

- [ ] Modèle Client
  - [ ] Type (individu, entreprise, ONG)
  - [ ] Informations de contact

- [ ] Modèle Invoice
  - [ ] Type de facturation
  - [ ] Montants, dates
  - [ ] Statut de paiement

- [ ] Modèle TrainerPayment
  - [ ] Calcul automatique (300 Rs/heure)
  - [ ] Suivi des paiements

## 5. Migrations et création de la base de données

- [ ] Générer les migrations
  ```bash
  python manage.py makemigrations
  ```

- [ ] Appliquer les migrations
  ```bash
  python manage.py migrate
  ```

- [ ] Créer un superutilisateur
  ```bash
  python manage.py createsuperuser
  ```

## 6. Développement des vues et formulaires

### Application Dashboard

- [ ] Créer la vue du tableau de bord principal
- [ ] Implémenter les widgets pour chaque section

### Application Courses

- [ ] Formulaires de création/édition de cours
- [ ] Vue de liste des cours
- [ ] Gestion des sessions de cours
- [ ] Système d'alertes pour les cours expirant bientôt

### Application Students

- [ ] Formulaires d'inscription (individuelle et par lot)
- [ ] Vues de gestion des étudiants par cours
- [ ] Système de suivi des résultats

### Application Trainers

- [ ] Gestion des formateurs et de leurs compétences
- [ ] Système d'affectation aux cours
- [ ] Suivi des présences et calcul des heures

### Application Billing

- [ ] Génération automatique des factures
- [ ] Suivi des paiements clients
- [ ] Calcul et suivi des paiements formateurs

### Application Reports

- [ ] Rapports démographiques
- [ ] Rapports de performance
- [ ] Rapports d'utilisation des ressources
- [ ] Rapports financiers

## 7. Intégration des exportations CSV

- [ ] Développer une fonction d'exportation CSV pour chaque type de rapport
- [ ] Intégrer les boutons d'exportation dans l'interface

## 8. Interface utilisateur

- [ ] Configurer les templates de base (héritage)
- [ ] Intégrer un framework CSS (Bootstrap)
- [ ] Créer la barre de navigation principale
- [ ] Implémenter des formulaires réactifs et conviviaux
- [ ] Développer les tableaux de données avec filtrage et tri

## 9. Système d'authentification et sécurité

- [ ] Configurer les groupes d'utilisateurs (manager, admin)
- [ ] Définir les permissions pour chaque groupe
- [ ] Mettre en place le middleware d'authentification
- [ ] Sécuriser les vues et URLs

## 10. Notifications et alertes

- [ ] Développer le système d'alertes pour les cours expirant bientôt
- [ ] Implémenter les notifications pour les utilisateurs

## 11. Tests

- [ ] Écrire des tests unitaires pour les modèles
- [ ] Écrire des tests d'intégration pour les vues
- [ ] Effectuer des tests fonctionnels pour les processus clés

## 12. Déploiement

- [ ] Configurer les paramètres de production
- [ ] Mettre en place la sauvegarde automatique de la base de données
- [ ] Déployer l'application sur un serveur
- [ ] Configurer le serveur web (Nginx/Apache)

## 13. Documentation et formation

- [ ] Préparer la documentation technique
- [ ] Rédiger le manuel d'utilisation
- [ ] Préparer les supports de formation pour les utilisateurs