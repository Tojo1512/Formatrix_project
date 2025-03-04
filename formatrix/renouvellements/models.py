from django.db import models
from cours.models import Cours

# Create your models here.

class Renouvellement(models.Model):
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('approuve', 'Approuvé'),
        ('refuse', 'Refusé')
    ]

    renouvellement_id = models.AutoField(primary_key=True)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    date_demande = models.DateField()
    date_renouvellement = models.DateField(null=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES)
    commentaires = models.TextField(null=True)
    documents_soumis = models.JSONField(null=True)  # Pour stocker le tableau de documents
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'renouvellement'

    def __str__(self):
        return f"{self.cours.nom_cours} - {self.date_demande}"
