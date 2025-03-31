from django.db import models
from django.utils import timezone

# Create your models here.

class TypeClient(models.Model):
    TYPE_CHOICES = [
        ('ong', 'ONG'),
        ('sponsor', 'Sponsor'),
        ('entreprise', 'Entreprise'),
        ('autre', 'Autre')
    ]
    
    typeclientid = models.AutoField(primary_key=True)
    typeclient = models.CharField(max_length=100)
    categorie = models.CharField(max_length=50, choices=TYPE_CHOICES, default='autre', 
                               help_text="Main category of the client")
    description = models.TextField(blank=True, null=True, 
                                 help_text="Additional description of client type")

    class Meta:
        db_table = 'typeclient'
        verbose_name = "Client Type"
        verbose_name_plural = "Client Types"

    def __str__(self):
        return f"{self.typeclient} ({self.get_categorie_display()})"

class Client(models.Model):
    SECTEUR_CHOICES = [
        ('education', 'Education'),
        ('sante', 'Health'),
        ('agriculture', 'Agriculture'),
        ('technologie', 'Technology'),
        ('finance', 'Finance'),
        ('humanitaire', 'Humanitarian'),
        ('environnement', 'Environment'),
        ('autre', 'Other')
    ]
    
    clientid = models.AutoField(primary_key=True)
    nom_entite = models.CharField(max_length=100, verbose_name="Entity name")
    sigle = models.CharField(max_length=50, null=True, blank=True, verbose_name="Acronym")
    secteur_activite = models.CharField(max_length=50, choices=SECTEUR_CHOICES, default='autre', 
                                      verbose_name="Business sector")
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="Contact email")
    localite = models.CharField(max_length=100, null=True, blank=True)
    ville = models.CharField(max_length=100, null=True, blank=True)
    numero_immatriculation = models.CharField(max_length=50, null=True, blank=True, 
                                            verbose_name="Registration number")
    adresse_siege = models.TextField(null=True, blank=True, verbose_name="Headquarters address")
    telephone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Main phone")
    site_web = models.URLField(max_length=200, null=True, blank=True, verbose_name="Website")
    typeclientid = models.ForeignKey(TypeClient, on_delete=models.CASCADE, 
                                   db_column='typeclientid', verbose_name="Client type")
    personne_contact = models.CharField(max_length=100, null=True, blank=True, 
                                      verbose_name="Contact person")
    fonction_contact = models.CharField(max_length=100, null=True, blank=True, 
                                      verbose_name="Contact person role")
    email_contact = models.EmailField(max_length=100, null=True, blank=True, 
                                    verbose_name="Contact person email")
    telephone_contact = models.CharField(max_length=20, null=True, blank=True, 
                                       verbose_name="Contact person phone")
    date_creation = models.DateTimeField(default=timezone.now, verbose_name="Creation date")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Last update")
    actif = models.BooleanField(default=True, verbose_name="Active client")

    class Meta:
        db_table = 'client'
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['-date_creation']

    def __str__(self):
        return self.nom_entite
