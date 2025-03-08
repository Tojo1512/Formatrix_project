from django.db import models
from django.utils import timezone
from datetime import timedelta

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

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
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
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='not_started')
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
        return self.nom_cours

    def save(self, *args, **kwargs):
        if self.date_approbation and not self.date_expiration_validite:
            # Set expiration date to 3 years after approval
            self.date_expiration_validite = self.date_approbation + timedelta(days=3*365)
        super().save(*args, **kwargs)

    @property
    def alerte_expiration(self):
        """Returns True if the expiration date is less than 3 months away"""
        if self.date_expiration_validite:
            aujourd_hui = timezone.now().date()
            jours_restants = (self.date_expiration_validite - aujourd_hui).days
            return jours_restants <= 90
        return False

    @property
    def est_expire(self):
        """Returns True if the course has expired"""
        if self.date_expiration_validite:
            return timezone.now().date() > self.date_expiration_validite
        return False

    def update_status(self):
        """Automatically updates course status based on start time and duration"""
        if not self.start_time:
            return

        now = timezone.now()
        end_time = self.start_time + timedelta(hours=self.duree_heures)

        if self.status == 'cancelled':
            return
        elif now < self.start_time:
            self.status = 'not_started'
        elif self.start_time <= now <= end_time:
            self.status = 'in_progress'
        elif now > end_time:
            self.status = 'completed'

        self.save()
