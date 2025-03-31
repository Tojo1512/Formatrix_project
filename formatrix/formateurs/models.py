from django.db import models
from django.utils import timezone
from cours.models import Cours
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Formateur(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave')
    ]

    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert')
    ]

    TYPE_CHOICES = [
        ('internal', 'Internal'),
        ('external', 'External'),
        ('consultant', 'Consultant')
    ]

    formateurid = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='formateur_profile')
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    email = models.EmailField(unique=True, verbose_name="Email")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone", null=True, blank=True)
    date_naissance = models.DateField(verbose_name="Date de naissance", null=True, blank=True)
    adresse = models.TextField(verbose_name="Adresse", null=True, blank=True)
    ville = models.CharField(max_length=100, verbose_name="Ville", null=True, blank=True)
    specialites = models.TextField(verbose_name="Spécialités", null=True, blank=True)
    niveau_expertise = models.CharField(
        max_length=20, 
        choices=LEVEL_CHOICES,
        default='intermediate',
        verbose_name="Niveau d'expertise"
    )
    type_formateur = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='internal',
        verbose_name="Type de formateur"
    )
    cv = models.FileField(
        upload_to='formateurs/cv/',
        null=True,
        blank=True,
        verbose_name="CV"
    )
    photo = models.ImageField(
        upload_to='formateurs/photos/',
        null=True,
        blank=True,
        verbose_name="Photo"
    )
    date_embauche = models.DateField(verbose_name="Date d'embauche", null=True, blank=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="Statut"
    )
    disponibilite = models.TextField(
        verbose_name="Disponibilité",
        help_text="Précisez les horaires de disponibilité"
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notes"
    )
    date_creation = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date de création"
    )
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )

    class Meta:
        verbose_name = "Formateur"
        verbose_name_plural = "Formateurs"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def get_full_name(self):
        return f"{self.prenom} {self.nom}"

    def get_active_courses(self):
        from cours.models import Cours
        return Cours.objects.filter(formateurs=self, statut_approbation='approved')

    def is_available(self):
        return self.statut == 'active'

@receiver(post_save, sender=Formateur)
def create_formateur_notification(sender, instance, created, **kwargs):
    if created:
        # Importer ici pour éviter les importations circulaires
        from notifications.views import create_notification
        
        message = f"Nouveau formateur inscrit : {instance.get_full_name()}"
        create_notification(message, 'new_trainer', instance.formateurid)