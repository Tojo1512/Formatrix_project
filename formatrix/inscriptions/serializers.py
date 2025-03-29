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


class InscriptionMultipleSerializer(serializers.Serializer):
    """
    Sérialiseur pour inscrire plusieurs apprenants à une séance
    """
    clientid = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source='client_id'
    )
    seance_id = serializers.PrimaryKeyRelatedField(
        queryset=Seance.objects.all()
    )
    apprenants_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Apprenant.objects.all())
    )
    type_inscription = serializers.ChoiceField(
        choices=Inscription.TYPE_INSCRIPTION_CHOICES,
        default='groupe'
    )
    sponsorid = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        required=False,
        allow_null=True,
        source='sponsor_id'
    )

    def create(self, validated_data):
        client_id = validated_data['client_id'].clientid
        seance_id = validated_data['seance_id'].seance_id
        apprenants_ids = [apprenant.apprenant_id for apprenant in validated_data['apprenants_ids']]
        type_inscription = validated_data.get('type_inscription', 'groupe')
        sponsor_id = validated_data.get('sponsor_id')
        sponsor_id = sponsor_id.clientid if sponsor_id else None
        
        # Utiliser la méthode de classe pour inscrire les apprenants
        return Inscription.inscrire_apprenants(
            client_id=client_id,
            seance_id=seance_id,
            apprenants_ids=apprenants_ids,
            type_inscription=type_inscription,
            sponsor_id=sponsor_id
        )
        
    def update(self, instance, validated_data):
        """
        Cette méthode n'est pas utilisée car nous ne mettons pas à jour des inscriptions multiples
        """
        raise NotImplementedError("La mise à jour d'inscriptions multiples n'est pas supportée")
