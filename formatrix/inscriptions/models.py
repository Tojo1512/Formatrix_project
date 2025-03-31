from django.db import models
from django.utils import timezone
from django.db.models import F
from clients.models import Client
from apprenants.models import Apprenant
from seances.models import Seance

# Create your models here.

class Inscription(models.Model):
    """Model for learner registrations to training sessions"""
    
    STATUS_CHOICES = [
        ('en_cours', 'In progress'),
        ('validee', 'Validated'),
        ('annulee', 'Cancelled'),
    ]
    
    REGISTRATION_TYPE_CHOICES = [
        ('individuelle', 'Individual'),
        ('groupe', 'Group'),
        ('entreprise', 'Company'),
        ('rse', 'CSR'),
        ('ong', 'NGO'),
    ]
    
    inscription_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='inscriptions')
    seance = models.ForeignKey(Seance, on_delete=models.CASCADE, related_name='inscriptions')
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE, related_name='inscriptions')
    date_inscription = models.DateTimeField(default=timezone.now)
    type_inscription = models.CharField(max_length=20, choices=REGISTRATION_TYPE_CHOICES, default='individuelle')
    statut_inscription = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_cours')
    sponsor = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='inscriptions_sponsorisees')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        db_table = 'inscription'
        
    def __str__(self):
        """Text representation of the registration"""
        # Access names through relations instead of using attributes directly
        apprenant_nom = f"{self.apprenant.nom_apprenant} {self.apprenant.autres_nom or ''}"
        cours_nom = self.seance.cours.nom_cours if hasattr(self.seance, 'cours') else "Unknown course"
        return f"Registration of {apprenant_nom} for {cours_nom}"
    
    @classmethod
    def register_learners(cls, client_id, seance_id, apprenants_ids, type_inscription='groupe', sponsor_id=None):
        """
        Register multiple learners to a session
        
        Args:
            client_id: ID of the client making the registration
            seance_id: ID of the session
            apprenants_ids: List of learner IDs to register
            type_inscription: Registration type (default: 'groupe')
            sponsor_id: Sponsor ID (optional)
            
        Returns:
            List of created registrations
            
        Raises:
            ValueError: If the number of learners exceeds available seats
        """
        # Get objects
        client = Client.objects.get(pk=client_id)
        seance = Seance.objects.get(pk=seance_id)
        
        # Check available seats
        places_disponibles = seance.nombre_places - seance.places_reservees
        if len(apprenants_ids) > places_disponibles:
            raise ValueError(f"Not enough available seats. Requested: {len(apprenants_ids)}, Available: {places_disponibles}")
        
        # Create registrations
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
        
        # Update number of reserved seats
        seance.places_reservees = F('places_reservees') + len(apprenants_ids)
        seance.save()
        
        return inscriptions
