from django.db import models
from cours.models import Cours
from lieux.models import Lieu

# Create your models here.

class Seance(models.Model):
    STATUT_CHOICES = [
        ('en_cours', 'En cours (live)'),
        ('termine', 'Terminé (completed)'),
        ('annule_avec_paiement', 'Annulé avec paiement'),
        ('annule_sans_paiement', 'Annulé sans paiement')
    ]

    HORAIRE_CHOICES = [
        ('pendant_bureau', 'Pendant les heures de bureau'),
        ('apres_bureau', 'Après les heures de bureau'),
        ('weekend', 'Weekend')
    ]

    seance_id = models.AutoField(primary_key=True)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE)
    horaires = models.CharField(max_length=100, choices=HORAIRE_CHOICES)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES)
    nombre_places_total = models.IntegerField()
    nombre_places_restantes = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'session'  # Utilise le même nom de table que dans SQL

    def __str__(self):
        return f"{self.cours.nom_cours} - {self.date_debut}"

    def save(self, *args, **kwargs):
        # Si c'est une nouvelle séance, initialiser les places restantes
        if not self.pk:
            self.nombre_places_restantes = self.nombre_places_total
        super().save(*args, **kwargs)

    @property
    def est_complet(self):
        """Retourne True si toutes les places sont prises"""
        return self.nombre_places_restantes == 0

    @property
    def duree_totale(self):
        """Retourne la durée totale en jours"""
        if self.date_fin:
            return (self.date_fin - self.date_debut).days + 1
        return None
