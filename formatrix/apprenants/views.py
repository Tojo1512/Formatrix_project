from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count
from .models import Apprenant
from .serializers import ApprenantSerializer

class ApprenantViewSet(viewsets.ModelViewSet):
    queryset = Apprenant.objects.all()
    serializer_class = ApprenantSerializer

    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Retourne des statistiques sur les apprenants"""
        stats = {
            'total': Apprenant.objects.count(),
            'par_genre': dict(Apprenant.objects.values('sexe').annotate(total=Count('apprenant_id'))),
            'par_age': dict(Apprenant.objects.values('categorie_age').annotate(total=Count('apprenant_id'))),
            'par_niveau': dict(Apprenant.objects.values('niveau_academique').annotate(total=Count('apprenant_id'))),
            'par_type': dict(Apprenant.objects.values('type_apprenant').annotate(total=Count('apprenant_id')))
        }
        return Response(stats)

    @action(detail=False, methods=['get'])
    def par_ville(self, request):
        """Retourne les apprenants groupés par ville"""
        stats = dict(Apprenant.objects.values('ville').annotate(total=Count('apprenant_id')))
        return Response(stats)

    @action(detail=False, methods=['get'])
    def count(self, request):
        """Retourne le nombre total d'apprenants"""
        count = Apprenant.objects.count()
        return Response({'count': count})
