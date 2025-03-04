from django.db import models
from cours.models import Cours

# Create your models here.

class Module(models.Model):
    module_id = models.AutoField(primary_key=True)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    nom_module = models.CharField(max_length=200)
    description = models.TextField()
    duree_heures = models.IntegerField()
    ordre = models.IntegerField()
    objectifs_module = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'module'

    def __str__(self):
        return f"{self.cours.nom_cours} - {self.nom_module}"
