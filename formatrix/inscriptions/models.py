from django.db import models
from apprenants.models import Apprenant
from clients.models import Client
from seances.models import Seance

class Inscription(models.Model):
    TYPE_INSCRIPTION_CHOICES = [
        ('individuelle', 'Inscription individuelle'),
        ('groupe', 'Inscription par groupe'),
        ('entreprise', 'Inscription par entreprise'),
        ('rse', 'Inscription via RSE'),
        ('ong', 'Inscription via ONG')
    ]

    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('validee', 'Validée'),
        ('annulee', 'Annulée')
    ]

    inscription_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    seance = models.ForeignKey(Seance, on_delete=models.CASCADE)
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)
    type_inscription = models.CharField(max_length=50, choices=TYPE_INSCRIPTION_CHOICES)
    date_inscription = models.DateField(auto_now_add=True)
    statut_inscription = models.CharField(max_length=50, choices=STATUT_CHOICES, default='en_cours')
    sponsor = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='sponsorships')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inscription'
        unique_together = ['client', 'seance', 'apprenant']

    def __str__(self):
        return f"{self.apprenant.nom_apprenant} - {self.seance.cours.nom_cours}"
