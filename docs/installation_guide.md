# Guide d'Installation et de Configuration - Formatrix

Ce document explique comment installer et configurer le projet Formatrix sur un nouveau PC.

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les éléments suivants sur votre système :

1. **Python 3.10+** - [Télécharger Python](https://www.python.org/downloads/)
2. **PostgreSQL 14+** - [Télécharger PostgreSQL](https://www.postgresql.org/download/)
3. **Git** (optionnel, pour cloner le dépôt) - [Télécharger Git](https://git-scm.com/downloads)

## Étape 1 : Obtenir le code source

### Option 1 : Cloner depuis Git (si disponible)

```bash
git clone https://github.com/Tojo1512/Formatrix_project.git
cd Formatrix_project
```

### Option 2 : Copier les fichiers manuellement

1. Copiez tous les fichiers du projet sur votre nouveau PC
2. Naviguez jusqu'au dossier du projet

## Étape 2 : Configurer l'environnement virtuel Python

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows
venv\Scripts\activate
# Sur macOS/Linux
source venv/bin/activate
```

## Étape 3 : Installer les dépendances

```bash
pip install -r requirements.txt
```

## Étape 4 : Configurer la base de données PostgreSQL

1. Ouvrez pgAdmin ou un autre outil PostgreSQL
2. Créez une nouvelle base de données nommée `formatrix`
3. Assurez-vous que l'utilisateur PostgreSQL a les droits nécessaires

Par défaut, le projet est configuré pour utiliser les paramètres suivants :
- **Nom de la base de données** : formatrix
- **Utilisateur** : postgres
- **Mot de passe** : root
- **Hôte** : localhost
- **Port** : 5432

Si vous souhaitez utiliser des paramètres différents, vous pouvez les modifier dans le fichier `formatrix/formatrix/settings.py` ou créer un fichier `.env` dans le dossier `formatrix/formatrix/` avec les variables suivantes :

```
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=votre_nom_de_base_de_donnees
DATABASE_USER=votre_utilisateur
DATABASE_PASSWORD=votre_mot_de_passe
DATABASE_HOST=votre_hote
DATABASE_PORT=votre_port
```

## Étape 5 : Appliquer les migrations

```bash
# Assurez-vous d'être dans le dossier du projet où se trouve manage.py
cd formatrix

# Appliquer les migrations
python manage.py migrate
```

## Étape 6 : Créer un superutilisateur (administrateur)

```bash
python manage.py createsuperuser
```

Suivez les instructions pour créer un compte administrateur.

## Étape 7 : Collecter les fichiers statiques

```bash
python manage.py collectstatic
```

## Étape 8 : Lancer le serveur de développement

```bash
python manage.py runserver
```

Le site sera accessible à l'adresse [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

L'interface d'administration sera accessible à [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Clés d'inscription

Le système utilise des clés d'inscription pour les formateurs et les administrateurs :

- **Clé d'inscription formateur** : `formateur_secret_key_2024`
- **Clé d'inscription administrateur** : `admin_secret_code_2024`

Ces clés sont définies dans le fichier `settings.py` et peuvent être modifiées si nécessaire.

## Structure du projet

Le projet Formatrix est organisé en plusieurs applications Django :

- **cours** : Gestion des cours et des programmes de formation
- **modules** : Gestion des modules de cours
- **documents** : Gestion des documents associés aux cours
- **renouvellements** : Gestion des renouvellements de certification
- **seances** : Gestion des séances de formation
- **clients** : Gestion des clients (entreprises, ONG)
- **lieux** : Gestion des lieux de formation
- **apprenants** : Gestion des apprenants
- **inscriptions** : Gestion des inscriptions aux formations
- **evaluations** : Gestion des évaluations des apprenants
- **presences** : Suivi des présences
- **formateurs** : Gestion des formateurs

## Dépannage

### Problèmes de base de données

Si vous rencontrez des erreurs liées à la base de données :

1. Vérifiez que PostgreSQL est en cours d'exécution
2. Vérifiez que les informations de connexion sont correctes
3. Assurez-vous que l'utilisateur a les droits nécessaires sur la base de données

### Problèmes de dépendances

Si vous rencontrez des erreurs liées aux dépendances :

```bash
pip install --upgrade -r requirements.txt
```

### Problèmes de fichiers statiques

Si les fichiers CSS/JS ne s'affichent pas correctement :

```bash
python manage.py collectstatic --clear
python manage.py collectstatic
```

## Mise en production

Pour un déploiement en production, des étapes supplémentaires sont nécessaires :

1. Désactivez le mode DEBUG dans settings.py ou via la variable d'environnement
2. Configurez un serveur web comme Nginx ou Apache
3. Utilisez Gunicorn ou uWSGI comme serveur d'application
4. Configurez HTTPS avec Let's Encrypt ou un autre fournisseur de certificats
5. Mettez en place des sauvegardes régulières de la base de données

## Ressources supplémentaires

- [Documentation Django](https://docs.djangoproject.com/)
- [Documentation PostgreSQL](https://www.postgresql.org/docs/)
