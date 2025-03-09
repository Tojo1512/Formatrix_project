from django.db import models
from cours.models import Cours
from lieux.models import Lieu
from django.utils import timezone
from decimal import Decimal

# Create your models here.

class Seance(models.Model):
    STATUS_CHOICES = [
        ('pas_commence', 'Pas encore commencé'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé')
    ]

    seance_id = models.AutoField(primary_key=True)
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE)
    date = models.DateField()
    cours = models.ForeignKey(
        Cours, 
        on_delete=models.CASCADE, 
        related_name='seances',
        null=True,  # Permettre temporairement null
        default=None  # Valeur par défaut None
    )
    nombre_places = models.IntegerField(default=10)
    places_reservees = models.IntegerField(default=0)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    statut = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pas_commence')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'session'

    def __str__(self):
        return f"Session de {self.cours.nom_cours if self.cours else 'Cours non défini'} à {self.lieu.lieu} le {self.date}"

    def start_session(self):
        """Start the session"""
        if self.statut == 'pas_commence':
            self.statut = 'en_cours'
            self.started_at = timezone.now()
            self.save()
            return True
        return False

    def complete_session(self):
        """Complete the session"""
        if self.statut == 'en_cours':
            self.statut = 'termine'
            self.completed_at = timezone.now()
            self.save()
            return True
        return False

    def cancel_session(self):
        """Cancel the session"""
        if self.statut in ['pas_commence', 'en_cours']:
            self.statut = 'annule'
            self.save()
            return True
        return False

    @property
    def can_start(self):
        """Check if the session can be started"""
        return self.statut == 'pas_commence'

    @property
    def can_complete(self):
        """Check if the session can be completed"""
        return self.statut == 'en_cours'

    @property
    def can_cancel(self):
        """Check if the session can be cancelled"""
        return self.statut in ['pas_commence', 'en_cours']

    @property
    def est_complet(self):
        """Returns True if all seats are taken"""
        return self.places_reservees >= self.nombre_places

    @property
    def places_disponibles(self):
        """Returns the number of available seats"""
        return max(0, self.nombre_places - self.places_reservees)

    @property
    def duree_totale(self):
        """Retourne la durée totale en jours"""
        if self.date_fin:
            return (self.date_fin - self.date_debut).days + 1
        return None
