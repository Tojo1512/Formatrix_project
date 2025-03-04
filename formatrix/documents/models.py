from django.db import models
from cours.models import Cours

# Create your models here.

class Document(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('refuse', 'Refusé'),
        ('expire', 'Expiré')
    ]

    document_id = models.AutoField(primary_key=True)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    type_document = models.CharField(max_length=100)
    nom_fichier = models.CharField(max_length=255)
    chemin_fichier = models.TextField()
    date_soumission = models.DateField()
    date_validation = models.DateField(null=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES)
    commentaires = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document'

    def __str__(self):
        return f"{self.cours.nom_cours} - {self.type_document}"
