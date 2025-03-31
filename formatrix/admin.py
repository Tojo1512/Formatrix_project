from django.contrib import admin

# Les imports des modèles restent nécessaires pour le fonctionnement de l'administration
from clients.models import Client, TypeClient
from cours.models import Cours
from apprenants.models import Apprenant
from formateurs.models import Formateur
from inscriptions.models import Inscription
from paiements.models import Paiement, PaiementFormateur, PlanPaiement, Facture
from lieux.models import Lieu
from presences.models import Presence
from seances.models import Seance, Absence

# Aucune personnalisation pour conserver le design par défaut de Django admin 