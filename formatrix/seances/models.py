from django.db import models
from cours.models import Cours
from lieux.models import Lieu
from django.utils import timezone
from decimal import Decimal
from formateurs.models import Formateur
from django.core.exceptions import ValidationError

# Create your models here.

class Seance(models.Model):
    STATUS_CHOICES = [
        ('pas_commence', 'Not started'),
        ('en_cours', 'In progress'),
        ('termine', 'Completed'),
        ('annule', 'Cancelled')
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
    duree = models.IntegerField(default=1, verbose_name="Duration (months)", help_text="Duration of the session in months")
    formateurs = models.ManyToManyField(
        Formateur,
        related_name='seances_assignees',
        verbose_name="Assigned trainers"
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

    def clean(self):
        super().clean()
        # Cette validation sera appliquée lors de l'enregistrement via un formulaire
        # Nous vérifierons le nombre de formateurs dans la vue
    
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
        """Returns the total duration in days"""
        if self.date_fin:
            return (self.date_fin - self.date_debut).days + 1
        return None

class Absence(models.Model):
    RAISON_CHOICES = [
        ('maladie', 'Illness'),
        ('conge', 'Leave'),
        ('formation', 'Training'),
        ('autre', 'Other reason')
    ]
    
    absence_id = models.AutoField(primary_key=True)
    seance = models.ForeignKey(Seance, on_delete=models.CASCADE, related_name='absences')
    formateur_absent = models.ForeignKey(
        Formateur, 
        on_delete=models.CASCADE, 
        related_name='absences',
        verbose_name="Absent trainer"
    )
    formateur_remplacant = models.ForeignKey(
        Formateur, 
        on_delete=models.CASCADE, 
        related_name='remplacements',
        verbose_name="Replacement trainer",
        null=True,
        blank=True
    )
    date_absence = models.DateField(verbose_name="Absence date")
    raison = models.CharField(max_length=50, choices=RAISON_CHOICES, default='autre')
    details = models.TextField(verbose_name="Absence details", blank=True, null=True)
    est_remplace = models.BooleanField(default=False, verbose_name="Is replaced")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Absence"
        verbose_name_plural = "Absences"
        ordering = ['-date_absence']
        unique_together = ['seance', 'formateur_absent', 'date_absence']
    
    def __str__(self):
        return f"Absence de {self.formateur_absent} le {self.date_absence} pour la séance {self.seance}"
    
    def clean(self):
        # Vérifier que le formateur absent est bien assigné à la séance
        if not self.seance.formateurs.filter(formateurid=self.formateur_absent.formateurid).exists():
            raise ValidationError("The trainer is not assigned to this session.")
            
        # Vérifier que le remplaçant n'est pas le formateur absent
        if self.formateur_remplacant and self.formateur_remplacant.formateurid == self.formateur_absent.formateurid:
            raise ValidationError("The replacement trainer cannot be the same as the absent trainer.")
            
        # Vérifier que le remplaçant n'est pas déjà assigné à la séance
        if self.formateur_remplacant and self.seance.formateurs.filter(formateurid=self.formateur_remplacant.formateurid).exists():
            raise ValidationError("The replacement trainer is already assigned to this session.")
    
    def save(self, *args, **kwargs):
        # Mettre à jour l'état du remplacement
        if self.formateur_remplacant:
            self.est_remplace = True
        else:
            self.est_remplace = False
        
        super().save(*args, **kwargs)
