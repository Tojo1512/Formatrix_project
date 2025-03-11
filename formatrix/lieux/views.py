from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Lieu
from .serializers import LieuSerializer

# Create your views here.

class LieuViewSet(viewsets.ModelViewSet):
    queryset = Lieu.objects.all()
    serializer_class = LieuSerializer

@api_view(['POST'])
def create_lieu(request):
    """
    Vue API dédiée pour créer un lieu depuis le formulaire de séance.
    """
    serializer = LieuSerializer(data=request.data)
    if serializer.is_valid():
        lieu = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
