from django.db import models
from seances.models import Seance
from apprenants.models import Apprenant

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