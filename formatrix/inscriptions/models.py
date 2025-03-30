from django.db import models
from django.utils import timezone
from django.db.models import F
from clients.models import Client
from apprenants.models import Apprenant
from seances.models import Seance

# Create your models here.

class Inscription(models.Model):
    """Modèle pour les inscriptions des apprenants aux séances de formation"""
    
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('validee', 'Validée'),
        ('annulee', 'Annulée'),
    ]
    
    TYPE_INSCRIPTION_CHOICES = [
        ('individuelle', 'Individuelle'),
        ('groupe', 'Groupe'),
        ('entreprise', 'Entreprise'),
        ('rse', 'RSE'),
        ('ong', 'ONG'),
    ]
    
    inscription_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='inscriptions')
    seance = models.ForeignKey(Seance, on_delete=models.CASCADE, related_name='inscriptions')
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE, related_name='inscriptions')
    date_inscription = models.DateTimeField(default=timezone.now)
    type_inscription = models.CharField(max_length=20, choices=TYPE_INSCRIPTION_CHOICES, default='individuelle')
    statut_inscription = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    sponsor = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='inscriptions_sponsorisees')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        db_table = 'inscription'
        
    def __str__(self):
        """Représentation textuelle de l'inscription"""
        # Accéder aux noms via les relations au lieu d'utiliser directement les attributs
        apprenant_nom = f"{self.apprenant.nom_apprenant} {self.apprenant.autres_nom or ''}"
        cours_nom = self.seance.cours.nom_cours if hasattr(self.seance, 'cours') else "Cours inconnu"
        return f"Inscription de {apprenant_nom} pour {cours_nom}"
    
    @classmethod
    def inscrire_apprenants(cls, client_id, seance_id, apprenants_ids, type_inscription='groupe', sponsor_id=None):
        """
        Inscrit plusieurs apprenants à une séance
        
        Args:
            client_id: ID du client qui fait l'inscription
            seance_id: ID de la séance
            apprenants_ids: Liste des IDs des apprenants à inscrire
            type_inscription: Type d'inscription (par défaut: 'groupe')
            sponsor_id: ID du sponsor (optionnel)
            
        Returns:
            Liste des inscriptions créées
            
        Raises:
            ValueError: Si le nombre d'apprenants dépasse les places disponibles
        """
        # Récupérer les objets
        client = Client.objects.get(pk=client_id)
        seance = Seance.objects.get(pk=seance_id)
        
        # Vérifier les places disponibles
        places_disponibles = seance.nombre_places - seance.places_reservees
        if len(apprenants_ids) > places_disponibles:
            raise ValueError(f"Pas assez de places disponibles. Demandé: {len(apprenants_ids)}, Disponible: {places_disponibles}")
        
        # Créer les inscriptions
        inscriptions = []
        for apprenant_id in apprenants_ids:
            apprenant = Apprenant.objects.get(pk=apprenant_id)
            sponsor = Client.objects.get(pk=sponsor_id) if sponsor_id else None
            
            inscription = cls.objects.create(
                client=client,
                seance=seance,
                apprenant=apprenant,
                type_inscription=type_inscription,
                sponsor=sponsor
            )
            inscriptions.append(inscription)
        
        # Mettre à jour le nombre de places réservées
        seance.places_reservees = F('places_reservees') + len(apprenants_ids)
        seance.save()
        
        return inscriptions
