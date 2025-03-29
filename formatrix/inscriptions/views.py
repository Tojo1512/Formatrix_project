from django.shortcuts import get_object_or_404, render, redirect
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, F, Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Inscription
from .serializers import InscriptionSerializer, InscriptionMultipleSerializer
from apprenants.models import Apprenant
from seances.models import Seance
from clients.models import Client
from django.contrib.auth.decorators import login_required

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
        
    @action(detail=False, methods=['post'])
    def inscrire_multiple(self, request):
        """Inscrit plusieurs apprenants à une séance"""
        serializer = InscriptionMultipleSerializer(data=request.data)
        if serializer.is_valid():
            try:
                inscriptions = serializer.save()
                return Response(
                    {
                        'message': f"{len(inscriptions)} apprenants inscrits avec succès",
                        'created': len(inscriptions),
                        'failed': 0,
                        'details': [f"{inscription.apprenant.nom_apprenant} {inscription.apprenant.autres_nom}" for inscription in inscriptions]
                    }, 
                    status=status.HTTP_201_CREATED
                )
            except ValueError as e:
                return Response({'error': str(e), 'created': 0, 'failed': 1}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['get'])
    def par_seance_id(self, request):
        """Retourne les inscriptions pour une séance spécifique"""
        seance_id = request.query_params.get('seance_id')
        if not seance_id:
            return Response({'error': 'Le paramètre seance_id est requis'}, status=status.HTTP_400_BAD_REQUEST)
            
        inscriptions = Inscription.objects.filter(seance_id=seance_id)
        serializer = InscriptionSerializer(inscriptions, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'], url_path='formulaire-multiple')
    def formulaire_multiple(self, request):
        """Affiche le formulaire pour inscrire plusieurs apprenants"""
        # Récupérer tous les clients et les trier par nom
        clients = Client.objects.all().order_by('nom_entite')
        
        # Filtrer les séances où le nombre de places réservées est inférieur au nombre de places total
        seances = Seance.objects.filter(places_reservees__lt=F('nombre_places')).order_by('date', 'cours__nom_cours')
        
        # Récupérer tous les apprenants et les trier par nom et prénom
        apprenants = Apprenant.objects.all().order_by('nom_apprenant', 'autres_nom')
        
        context = {
            'clients': clients,
            'seances': seances,
            'apprenants': apprenants
        }
        
        return render(request, 'inscriptions/inscription_multiple.html', context)


class InscriptionListView(ListView):
    model = Inscription
    template_name = 'inscriptions/inscription_list.html'
    context_object_name = 'inscriptions'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Inscription.objects.all().order_by('-date_inscription')
        
        # Filtres
        seance_id = self.request.GET.get('seance')
        client_id = self.request.GET.get('client')
        statut = self.request.GET.get('statut')
        type_inscription = self.request.GET.get('type')
        search_query = self.request.GET.get('search')
        ordering = self.request.GET.get('ordering', '-date_inscription')
        
        if seance_id:
            queryset = queryset.filter(seance_id=seance_id)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        if statut:
            queryset = queryset.filter(statut_inscription=statut)
        if type_inscription:
            queryset = queryset.filter(type_inscription=type_inscription)
        if search_query:
            queryset = queryset.filter(
                Q(apprenant__nom_apprenant__icontains=search_query) |
                Q(client__nom_entite__icontains=search_query) |
                Q(seance__cours__nom_cours__icontains=search_query)
            )
        
        # Appliquer le tri
        if ordering:
            queryset = queryset.order_by(ordering)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seances'] = Seance.objects.all()
        context['clients'] = Client.objects.all().order_by('nom_entite')
        context['status_choices'] = Inscription.STATUT_CHOICES
        context['type_choices'] = Inscription.TYPE_INSCRIPTION_CHOICES
        
        # Récupération des filtres actifs pour la navigation
        context['seance_filter'] = self.request.GET.get('seance', '')
        context['client_filter'] = self.request.GET.get('client', '')
        context['statut_filter'] = self.request.GET.get('statut', '')
        context['search_query'] = self.request.GET.get('search', '')
        context['ordering'] = self.request.GET.get('ordering', '-date_inscription')
        
        # Déterminer si des filtres sont actifs
        context['has_active_filters'] = any([
            context['seance_filter'], 
            context['client_filter'], 
            context['statut_filter'], 
            context['search_query']
        ])
        
        # URL pour réinitialiser les filtres
        context['reset_url'] = reverse_lazy('inscriptions:inscription-list')
        
        return context


class InscriptionDetailView(DetailView):
    model = Inscription
    template_name = 'inscriptions/inscription_detail.html'
    context_object_name = 'inscription'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Inscription.STATUT_CHOICES
        context['type_choices'] = Inscription.TYPE_INSCRIPTION_CHOICES
        return context
        
    def post(self, request, *args, **kwargs):
        """Gère la mise à jour du statut d'une inscription"""
        inscription = self.get_object()
        status_param = request.POST.get('status')
        
        if status_param and status_param in dict(Inscription.STATUT_CHOICES):
            # Mettre à jour le statut
            old_status = inscription.statut_inscription
            inscription.statut_inscription = status_param
            inscription.save()
            
            # Mettre à jour les places disponibles si nécessaire
            if status_param == 'annulee' and old_status != 'annulee':
                # Libérer une place si l'inscription est annulée
                seance = inscription.seance
                seance.places_disponibles += 1
                seance.save()
                messages.success(request, f"L'inscription a été annulée et une place a été libérée pour la séance.")
            elif status_param != 'annulee' and old_status == 'annulee':
                # Réserver une place si l'inscription n'est plus annulée
                seance = inscription.seance
                if seance.places_disponibles <= 0:
                    messages.error(request, "Impossible de réactiver l'inscription : aucune place disponible.")
                    return redirect('inscription-detail', pk=inscription.pk)
                
                seance.places_disponibles -= 1
                seance.save()
                messages.success(request, "L'inscription a été réactivée et une place a été réservée.")
            else:
                messages.success(request, f"Le statut de l'inscription a été mis à jour avec succès.")
                
            return redirect('inscription-detail', pk=inscription.pk)
        
        messages.error(request, "Statut d'inscription invalide.")
        return redirect('inscription-detail', pk=inscription.pk)


class InscriptionCreateView(CreateView):
    model = Inscription
    template_name = 'inscriptions/inscription_form.html'
    fields = ['client', 'seance', 'apprenant', 'type_inscription', 'statut_inscription', 'sponsor']
    success_url = reverse_lazy('inscriptions:inscription-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nouvelle Inscription'
        context['status_choices'] = Inscription.STATUT_CHOICES
        context['type_choices'] = Inscription.TYPE_INSCRIPTION_CHOICES
        return context
        
    def form_valid(self, form):
        """Vérifie si des places sont disponibles avant de créer l'inscription"""
        seance = form.cleaned_data['seance']
        
        if seance.places_disponibles <= 0:
            messages.error(self.request, "Impossible de créer l'inscription : aucune place disponible pour cette séance.")
            return self.form_invalid(form)
            
        # Incrémenter le nombre de places réservées au lieu de modifier places_disponibles
        seance.places_reservees += 1
        seance.save()
        
        messages.success(self.request, "L'inscription a été créée avec succès.")
        return super().form_valid(form)


class InscriptionUpdateView(UpdateView):
    model = Inscription
    template_name = 'inscriptions/inscription_form.html'
    fields = ['client', 'seance', 'apprenant', 'type_inscription', 'statut_inscription', 'sponsor']
    success_url = reverse_lazy('inscriptions:inscription-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier Inscription'
        context['status_choices'] = Inscription.STATUT_CHOICES
        context['type_choices'] = Inscription.TYPE_INSCRIPTION_CHOICES
        return context
        
    def form_valid(self, form):
        """Vérifie si la modification de séance est possible"""
        old_inscription = self.get_object()
        new_seance = form.cleaned_data['seance']
        
        # Si la séance a changé
        if old_inscription.seance != new_seance:
            # Vérifier si la nouvelle séance a des places disponibles
            if new_seance.places_disponibles <= 0:
                messages.error(self.request, "Impossible de modifier l'inscription : aucune place disponible pour la nouvelle séance.")
                return self.form_invalid(form)
                
            # Libérer une place dans l'ancienne séance
            old_seance = old_inscription.seance
            old_seance.places_reservees -= 1
            old_seance.save()
            
            # Réserver une place dans la nouvelle séance
            new_seance.places_reservees += 1
            new_seance.save()
            
            messages.success(self.request, "L'inscription a été modifiée avec succès. Les places ont été mises à jour.")
        else:
            messages.success(self.request, "L'inscription a été modifiée avec succès.")
            
        return super().form_valid(form)


class InscriptionDeleteView(DeleteView):
    model = Inscription
    template_name = 'inscriptions/inscription_confirm_delete.html'
    success_url = reverse_lazy('inscriptions:inscription-list')
    
    def delete(self, request, *args, **kwargs):
        """Libère une place lorsqu'une inscription est supprimée"""
        inscription = self.get_object()
        seance = inscription.seance
        
        # Libérer une place dans la séance
        seance.places_reservees -= 1
        seance.save()
        
        messages.success(request, "L'inscription a été supprimée avec succès. Une place a été libérée.")
        return super().delete(request, *args, **kwargs)


@login_required
def valider_inscription(request, pk):
    """Valide une inscription en changeant son statut"""
    inscription = get_object_or_404(Inscription, pk=pk)
    
    if inscription.statut_inscription == 'en_cours':
        inscription.statut_inscription = 'validee'
        inscription.save()
        messages.success(request, "L'inscription a été validée avec succès.")
    else:
        messages.warning(request, "Cette inscription ne peut pas être validée car elle n'est pas en cours.")
    
    return redirect('inscriptions:inscription-list')
