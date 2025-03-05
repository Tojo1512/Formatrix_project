from rest_framework import serializers
from .models import Presence
from apprenants.models import Apprenant
from seances.models import Seance
from apprenants.serializers import ApprenantSerializer
from seances.serializers import SeanceSerializer

class PresenceSerializer(serializers.ModelSerializer):
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
        model = Presence
        fields = '__all__'
