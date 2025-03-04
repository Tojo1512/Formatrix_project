from django.db import models

# Create your models here.

class TypeClient(models.Model):
    typeclientid = models.AutoField(primary_key=True)
    typeclient = models.CharField(max_length=100)
    reseau = models.CharField(max_length=50, choices=[('interne', 'Interne'), ('externe', 'Externe')])

    class Meta:
        db_table = 'typeclient'

    def __str__(self):
        return self.typeclient

class Client(models.Model):
    clientid = models.AutoField(primary_key=True)
    nomclient = models.CharField(max_length=100)
    autresnom = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)
    localite = models.CharField(max_length=100, null=True)
    ville = models.CharField(max_length=100, null=True)
    numero_immatriculation = models.CharField(max_length=50, null=True)
    adresse_rue = models.TextField(null=True)
    telephone = models.CharField(max_length=20, null=True)
    typeclientid = models.ForeignKey(TypeClient, on_delete=models.CASCADE, db_column='typeclientid')

    class Meta:
        db_table = 'client'

    def __str__(self):
        return self.nomclient
