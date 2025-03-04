from rest_framework import serializers
from .models import Cours
from modules.models import Module
from documents.models import Document
from renouvellements.models import Renouvellement
from seances.models import Seance
from lieux.models import Lieu
from lieux.serializers import LieuSerializer

class CoursSerializer(serializers.ModelSerializer):
    alerte_expiration = serializers.BooleanField(read_only=True)
    jours_restants = serializers.SerializerMethodField()

    class Meta:
        model = Cours
        fields = '__all__'

    def get_jours_restants(self, obj):
        if obj.date_expiration_validite:
            from django.utils import timezone
            aujourd_hui = timezone.now().date()
            return (obj.date_expiration_validite - aujourd_hui).days
        return None

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class RenouvellementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Renouvellement
        fields = '__all__'

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
