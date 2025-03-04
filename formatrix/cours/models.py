from django.db import models
from django.utils import timezone
from datetime import timedelta

class Cours(models.Model):
    TYPE_CHOICES = [
        ('formateur', 'Formation pour Formateur'),
        ('apprenant', 'Formation pour Apprenant'),
        ('court', 'Cours Court'),
        ('long', 'Cours Long')
    ]

    STATUT_APPROBATION_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('refuse', 'Refusé'),
        ('expire', 'Expiré')
    ]

    HORAIRE_CHOICES = [
        ('pendant_bureau', 'Pendant les heures de bureau'),
        ('apres_bureau', 'Après les heures de bureau'),
        ('weekend', 'Weekend')
    ]

    cours_id = models.AutoField(primary_key=True)
    nom_cours = models.CharField(max_length=200)
    description = models.TextField()
    niveau = models.CharField(max_length=50, null=True)
    frais_par_participant = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    duree_heures = models.IntegerField()
    periode_mois = models.IntegerField(null=True)  # Durée en mois pour les cours longs
    type_cours = models.CharField(max_length=50, choices=TYPE_CHOICES)
    objectifs = models.TextField()
    prerequis = models.TextField(null=True)
    materiel_requis = models.TextField(null=True)
    horaire = models.CharField(max_length=50, choices=HORAIRE_CHOICES)
    statut_approbation = models.CharField(max_length=50, choices=STATUT_APPROBATION_CHOICES)
    date_approbation = models.DateField(null=True)
    date_expiration_validite = models.DateField(null=True)
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cours'

    def __str__(self):
        return self.nom_cours

    def save(self, *args, **kwargs):
        if self.date_approbation and not self.date_expiration_validite:
            # Définir la date d'expiration à 3 ans après l'approbation
            self.date_expiration_validite = self.date_approbation + timedelta(days=3*365)
        super().save(*args, **kwargs)

    @property
    def alerte_expiration(self):
        """Retourne True si la date d'expiration est dans moins de 3 mois"""
        if self.date_expiration_validite:
            aujourd_hui = timezone.now().date()
            jours_restants = (self.date_expiration_validite - aujourd_hui).days
            return jours_restants <= 90
        return False

    @property
    def est_expire(self):
        """Retourne True si le cours est expiré"""
        if self.date_expiration_validite:
            return timezone.now().date() > self.date_expiration_validite
        return False
