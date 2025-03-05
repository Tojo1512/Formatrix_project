from rest_framework import serializers
from .models import Apprenant

class ApprenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apprenant
        fields = '__all__'
