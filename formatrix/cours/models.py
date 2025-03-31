from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

class Cours(models.Model):
    TYPE_CHOICES = [
        ('formateur', 'Training for Trainer'),
        ('apprenant', 'Training for Learner'),
        ('court', 'Short Course'),
        ('long', 'Long Course')
    ]

    STATUT_APPROBATION_CHOICES = [
        ('en_attente', 'Pending'),
        ('approuve', 'Approved'),
        ('refuse', 'Rejected'),
        ('expire', 'Expired')
    ]

    HORAIRE_CHOICES = [
        ('pendant_bureau', 'During office hours'),
        ('apres_bureau', 'After office hours'),
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
    statut_approbation = models.CharField(
        max_length=50,
        choices=STATUT_APPROBATION_CHOICES,
        default='en_attente'
    )
    date_approbation = models.DateField(null=True)
    date_expiration_validite = models.DateField(null=True)
    version = models.IntegerField(default=1)
    start_time = models.DateTimeField(null=True)
    formateurs = models.ManyToManyField(
        'formateurs.Formateur',
        related_name='cours_assignes',
        blank=True,
        verbose_name="Formateurs assignés"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cours'

    def __str__(self):
        return str(self.nom_cours)

    def save(self, *args, **kwargs):
        if self.date_approbation and not self.date_expiration_validite:
            # Set expiration date to 3 years after approval
            self.date_expiration_validite = self.date_approbation + timedelta(days=3*365)
        super().save(*args, **kwargs)

    @property
    def alert_expiration(self):
        """Returns True if the expiration date is less than 3 months away"""
        if self.date_expiration_validite:
            aujourd_hui = timezone.now().date()
            jours_restants = (self.date_expiration_validite - aujourd_hui).days
            return jours_restants <= 90
        return False

    @property
    def is_expired(self):
        """Returns True if the course has expired"""
        if self.date_expiration_validite:
            return timezone.now().date() > self.date_expiration_validite
        return False

@receiver(post_save, sender=Cours)
def create_cours_notification(sender, instance, created, **kwargs):
    if created:
        # Importer ici pour éviter les importations circulaires
        from notifications.views import create_notification
        
        message = f"Nouveau cours créé : {instance.nom_cours}"
        create_notification(message, 'new_course', instance.cours_id)
