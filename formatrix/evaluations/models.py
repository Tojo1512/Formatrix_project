from django.db import models
from seances.models import Seance
from apprenants.models import Apprenant
from inscriptions.models import Inscription

# Create your models here.

class Presence(models.Model):
    presence_id = models.AutoField(primary_key=True)
    date_presence = models.DateField()
    seance = models.ForeignKey(Seance, on_delete=models.CASCADE)
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)
    present = models.BooleanField(default=False)
    retard = models.IntegerField(default=0)
    commentaires = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'presence'

    def __str__(self):
        return f"{self.apprenant.nom_apprenant} - {self.date_presence}"

class Resultat(models.Model):
    STATUT_FINAL_CHOICES = [
        ('reussite', 'Réussite'),
        ('echec', 'Échec'),
        ('abandon', 'Abandon')
    ]

    resultat_id = models.AutoField(primary_key=True)
    inscription = models.OneToOneField(Inscription, on_delete=models.CASCADE)
    assiduite = models.DecimalField(max_digits=5, decimal_places=2, help_text="Pourcentage de présence")
    evaluation_continue = models.JSONField(help_text="Résultats des évaluations continues")
    portfolio_url = models.URLField(null=True, blank=True)
    statut_final = models.CharField(max_length=20, choices=STATUT_FINAL_CHOICES)
    commentaires = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'resultat'

    def __str__(self):
        return f"Résultat de {self.inscription.apprenant.nom_apprenant}"
