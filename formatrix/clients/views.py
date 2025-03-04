from django.shortcuts import render
from rest_framework import viewsets
from .models import TypeClient, Client
from .serializers import TypeClientSerializer, ClientSerializer

# Create your views here.

class TypeClientViewSet(viewsets.ModelViewSet):
    queryset = TypeClient.objects.all()
    serializer_class = TypeClientSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
