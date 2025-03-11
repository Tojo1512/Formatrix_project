from rest_framework import viewsets
from .models import Seance
from .serializers import SeanceSerializer

class SeanceViewSet(viewsets.ModelViewSet):
    queryset = Seance.objects.all()
    serializer_class = SeanceSerializer 