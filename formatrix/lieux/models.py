from django.db import models

# Create your models here.

class Lieu(models.Model):
    lieuid = models.AutoField(primary_key=True)
    lieu = models.CharField(max_length=100)
    adresse = models.TextField(null=True)
    personne_contact = models.CharField(max_length=100, null=True)
    telephone = models.CharField(max_length=20, null=True)
    mobile = models.CharField(max_length=20, null=True)

    class Meta:
        db_table = 'lieu'

    def __str__(self):
        return self.lieu
