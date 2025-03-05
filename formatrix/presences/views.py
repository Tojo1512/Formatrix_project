from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, Avg
from .models import Presence
from .serializers import PresenceSerializer

class PresenceViewSet(viewsets.ModelViewSet):
    queryset = Presence.objects.all()
    serializer_class = PresenceSerializer

    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Retourne des statistiques sur les présences"""
        stats = {
            'total': Presence.objects.count(),
            'presents': Presence.objects.filter(present=True).count(),
            'absents': Presence.objects.filter(present=False).count(),
            'retards_moyens': Presence.objects.filter(retard__gt=0).aggregate(Avg('retard'))
        }
        return Response(stats)

    @action(detail=False, methods=['get'])
    def par_seance(self, request):
        """Retourne les présences groupées par séance"""
        seance_id = request.query_params.get('seance_id')
        if seance_id:
            presences = Presence.objects.filter(seance_id=seance_id)
            serializer = self.get_serializer(presences, many=True)
            return Response(serializer.data)
        return Response({'error': 'seance_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

