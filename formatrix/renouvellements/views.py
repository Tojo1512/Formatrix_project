from django.shortcuts import render
from rest_framework import viewsets
from .models import Renouvellement
from .serializers import RenouvellementSerializer

# Create your views here.

class RenouvellementViewSet(viewsets.ModelViewSet):
    queryset = Renouvellement.objects.all()
    serializer_class = RenouvellementSerializer
