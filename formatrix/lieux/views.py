from django.shortcuts import render
from rest_framework import viewsets
from .models import Lieu
from .serializers import LieuSerializer

# Create your views here.

class LieuViewSet(viewsets.ModelViewSet):
    queryset = Lieu.objects.all()
    serializer_class = LieuSerializer
