from rest_framework import serializers
from .models import Seance
from cours.models import Cours
from lieux.models import Lieu
from cours.serializers import CoursSerializer
from lieux.serializers import LieuSerializer

class SeanceSerializer(serializers.ModelSerializer):
    cours = CoursSerializer(read_only=True)
    lieu = LieuSerializer(read_only=True)
    cours_id = serializers.PrimaryKeyRelatedField(
        queryset=Cours.objects.all(),
        source='cours',
        write_only=True
    )
    lieu_id = serializers.PrimaryKeyRelatedField(
        queryset=Lieu.objects.all(),
        source='lieu',
        write_only=True
    )

    class Meta:
        model = Seance
        fields = '__all__'
