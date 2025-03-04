from rest_framework import serializers
from .models import TypeClient, Client

class TypeClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeClient
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
