from django.shortcuts import render
from rest_framework import viewsets
from .models import Module
from .serializers import ModuleSerializer

# Create your views here.

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
