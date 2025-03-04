from django.shortcuts import render
from rest_framework import viewsets
from .models import Seance
from .serializers import SeanceSerializer

# Create your views here.

class SeanceViewSet(viewsets.ModelViewSet):
    queryset = Seance.objects.all()
    serializer_class = SeanceSerializer
