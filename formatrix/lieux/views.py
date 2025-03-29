from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Lieu
from .serializers import LieuSerializer
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

# Create your views here.

class LieuViewSet(viewsets.ModelViewSet):
    queryset = Lieu.objects.all()
    serializer_class = LieuSerializer

@api_view(['POST'])
def create_lieu(request):
    """
    Vue API dédiée pour créer un lieu depuis le formulaire de séance.
    """
    serializer = LieuSerializer(data=request.data)
    if serializer.is_valid():
        lieu = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
@require_POST
def lieu_create_ajax(request):
    """
    Vue pour créer un lieu via AJAX depuis le formulaire de séance.
    """
    try:
        # Récupérer les données du formulaire
        nom = request.POST.get('lieu')
        adresse = request.POST.get('adresse')
        code_postal = request.POST.get('code_postal')
        ville = request.POST.get('ville')
        pays = request.POST.get('pays', 'France')
        capacite = request.POST.get('capacite')
        description = request.POST.get('description')
        
        # Vérifier les champs obligatoires
        if not all([nom, adresse, code_postal, ville]):
            return JsonResponse({
                'success': False,
                'errors': 'Veuillez remplir tous les champs obligatoires'
            })
        
        # Créer le lieu
        lieu = Lieu.objects.create(
            lieu=nom,
            adresse=adresse,
            code_postal=code_postal,
            ville=ville,
            pays=pays,
            capacite=int(capacite) if capacite else None,
            description=description
        )
        
        # Retourner la réponse JSON
        return JsonResponse({
            'success': True,
            'lieu': {
                'id': lieu.id,
                'nom': lieu.lieu
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': str(e)
        })
