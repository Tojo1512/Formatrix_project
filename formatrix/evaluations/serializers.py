from rest_framework import serializers
from .models import Resultat
from apprenants.models import Apprenant
from seances.models import Seance
from apprenants.serializers import ApprenantSerializer
from seances.serializers import SeanceSerializer

class ResultatSerializer(serializers.ModelSerializer):
    apprenant = ApprenantSerializer(read_only=True)
    seance = SeanceSerializer(read_only=True)
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

    class Meta:
        model = Resultat
        fields = '__all__'
