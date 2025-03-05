from django.db import models
from clients.models import Client
from seances.models import Seance

class Apprenant(models.Model):
    GENRE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('A', 'Autre')
    ]

    CATEGORIE_AGE_CHOICES = [
        ('16-30', '16-30 ans'),
        ('31-60', '31-60 ans'),
        ('60+', 'Plus de 60 ans')
    ]

    NIVEAU_ACADEMIQUE_CHOICES = [
        ('sous_certificat', 'En dessous du certificat scolaire'),
        ('certificat', 'Certificat scolaire'),
        ('superieur', 'Au-dessus du certificat')
    ]

    apprenant_id = models.AutoField(primary_key=True)
    nom_apprenant = models.CharField(max_length=100)
    autres_nom = models.CharField(max_length=100, null=True, blank=True)
    cin = models.CharField(max_length=20, unique=True)
    date_naissance = models.DateField()
    adresse_rue = models.TextField()
    localite = models.CharField(max_length=100)
    ville = models.CharField(max_length=100)
    type_apprenant = models.CharField(max_length=50, null=True, blank=True)
    sexe = models.CharField(max_length=1, choices=GENRE_CHOICES)
    niveau_academique = models.CharField(max_length=50, choices=NIVEAU_ACADEMIQUE_CHOICES)
    categorie_age = models.CharField(max_length=20, choices=CATEGORIE_AGE_CHOICES)
    besoins_speciaux = models.TextField(null=True, blank=True)
    contact_urgence = models.CharField(max_length=100)
    telephone_urgence = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'apprenant'

    def __str__(self):
        return f"{self.nom_apprenant} ({self.cin})"
