from rest_framework import serializers
from .models import Renouvellement

class RenouvellementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Renouvellement
        fields = '__all__'
