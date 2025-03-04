from django.shortcuts import render
from rest_framework import viewsets
from .models import Cours
from modules.models import Module
from documents.models import Document
from renouvellements.models import Renouvellement
from seances.models import Seance
from .serializers import (
    CoursSerializer, ModuleSerializer, DocumentSerializer,
    RenouvellementSerializer, SeanceSerializer
)

# Create your views here.

class CoursViewSet(viewsets.ModelViewSet):
    queryset = Cours.objects.all()
    serializer_class = CoursSerializer

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class RenouvellementViewSet(viewsets.ModelViewSet):
    queryset = Renouvellement.objects.all()
    serializer_class = RenouvellementSerializer

class SeanceViewSet(viewsets.ModelViewSet):
    queryset = Seance.objects.all()
    serializer_class = SeanceSerializer
