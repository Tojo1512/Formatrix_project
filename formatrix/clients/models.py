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
                               help_text="Catégorie principale du client")
    description = models.TextField(blank=True, null=True, 
                                 help_text="Description supplémentaire du type de client")

    class Meta:
        db_table = 'typeclient'
        verbose_name = "Type de client"
        verbose_name_plural = "Types de clients"

    def __str__(self):
        return f"{self.typeclient} ({self.get_categorie_display()})"

class Client(models.Model):
    SECTEUR_CHOICES = [
        ('education', 'Éducation'),
        ('sante', 'Santé'),
        ('agriculture', 'Agriculture'),
        ('technologie', 'Technologie'),
        ('finance', 'Finance'),
        ('humanitaire', 'Humanitaire'),
        ('environnement', 'Environnement'),
        ('autre', 'Autre')
    ]
    
    clientid = models.AutoField(primary_key=True)
    nom_entite = models.CharField(max_length=100, verbose_name="Nom de l'entité")
    sigle = models.CharField(max_length=50, null=True, blank=True, verbose_name="Sigle/Acronyme")
    secteur_activite = models.CharField(max_length=50, choices=SECTEUR_CHOICES, default='autre', 
                                      verbose_name="Secteur d'activité")
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="Email de contact")
    localite = models.CharField(max_length=100, null=True, blank=True)
    ville = models.CharField(max_length=100, null=True, blank=True)
    numero_immatriculation = models.CharField(max_length=50, null=True, blank=True, 
                                            verbose_name="Numéro d'immatriculation/Enregistrement")
    adresse_siege = models.TextField(null=True, blank=True, verbose_name="Adresse du siège")
    telephone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Téléphone principal")
    site_web = models.URLField(max_length=200, null=True, blank=True, verbose_name="Site web")
    typeclientid = models.ForeignKey(TypeClient, on_delete=models.CASCADE, 
                                   db_column='typeclientid', verbose_name="Type de client")
    personne_contact = models.CharField(max_length=100, null=True, blank=True, 
                                      verbose_name="Personne de contact")
    fonction_contact = models.CharField(max_length=100, null=True, blank=True, 
                                      verbose_name="Fonction de la personne de contact")
    email_contact = models.EmailField(max_length=100, null=True, blank=True, 
                                    verbose_name="Email de la personne de contact")
    telephone_contact = models.CharField(max_length=20, null=True, blank=True, 
                                       verbose_name="Téléphone de la personne de contact")
    date_creation = models.DateTimeField(default=timezone.now, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    actif = models.BooleanField(default=True, verbose_name="Client actif")

    class Meta:
        db_table = 'client'
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['-date_creation']

    def __str__(self):
        return self.nom_entite
