from rest_framework import serializers
from .models import Inscription
from apprenants.models import Apprenant
from seances.models import Seance
from clients.models import Client
from apprenants.serializers import ApprenantSerializer
from seances.serializers import SeanceSerializer
from clients.serializers import ClientSerializer

class InscriptionSerializer(serializers.ModelSerializer):
    apprenant = ApprenantSerializer(read_only=True)
    seance = SeanceSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    sponsor = ClientSerializer(read_only=True)
    
    apprenant_id = serializers.PrimaryKeyRelatedField(
        source='apprenant',
        write_only=True,
        queryset=Apprenant.objects.all()
    )
    seance_id = serializers.PrimaryKeyRelatedField(
        source='seance',
        write_only=True,
        queryset=Seance.objects.all()
    )
    client_id = serializers.PrimaryKeyRelatedField(
        source='client',
        write_only=True,
        queryset=Client.objects.all()
    )
    sponsor_id = serializers.PrimaryKeyRelatedField(
        source='sponsor',
        write_only=True,
        queryset=Client.objects.all(),
        required=False
    )

    class Meta:
        model = Inscription
        fields = '__all__'
