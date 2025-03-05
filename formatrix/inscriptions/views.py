from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count
from .models import Inscription
from .serializers import InscriptionSerializer

# Create your views here.

class InscriptionViewSet(viewsets.ModelViewSet):
    queryset = Inscription.objects.all()
    serializer_class = InscriptionSerializer

    @action(detail=False, methods=['get'])
    def par_type(self, request):
        """Retourne les inscriptions groupées par type"""
        stats = dict(Inscription.objects.values('type_inscription').annotate(total=Count('inscription_id')))
        return Response(stats)

    @action(detail=False, methods=['get'])
    def par_statut(self, request):
        """Retourne les inscriptions groupées par statut"""
        stats = dict(Inscription.objects.values('statut_inscription').annotate(total=Count('inscription_id')))
        return Response(stats)

    @action(detail=False, methods=['get'])
    def par_seance(self, request):
        """Retourne les inscriptions groupées par séance"""
        stats = dict(Inscription.objects.values('seance__cours__nom_cours').annotate(total=Count('inscription_id')))
        return Response(stats)
