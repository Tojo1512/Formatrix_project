from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Seance
from .forms import SeanceForm

# Create your views here.

class SeanceListView(LoginRequiredMixin, ListView):
    model = Seance
    template_name = 'seances/seance_list.html'
    context_object_name = 'seance_list'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Seance.objects.all()
        
        # Recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(cours__nom_cours__icontains=search_query) |
                Q(lieu__lieu__icontains=search_query)
            )
        
        # Filtres
        statut_filter = self.request.GET.get('statut', '')
        if statut_filter:
            queryset = queryset.filter(statut=statut_filter)
            
        horaire_filter = self.request.GET.get('horaire', '')
        if horaire_filter:
            queryset = queryset.filter(horaires=horaire_filter)
        
        # Tri
        ordering = self.request.GET.get('ordering', '-date')
        queryset = queryset.order_by(ordering)
        
        return queryset.prefetch_related('cours').select_related('lieu')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['statut_filter'] = self.request.GET.get('statut', '')
        context['horaire_filter'] = self.request.GET.get('horaire', '')
        context['ordering'] = self.request.GET.get('ordering', '-date')
        context['show_create_button'] = True
        context['create_url'] = reverse_lazy('seance-create')
        context['create_button_text'] = 'Créer une séance'
        context['reset_url'] = reverse_lazy('seance-list')
        context['has_active_filters'] = bool(context['search_query'] or context['statut_filter'] or context['horaire_filter'])
        context['STATUS_CHOICES'] = Seance.STATUS_CHOICES
        return context

class SeanceDetailView(LoginRequiredMixin, DetailView):
    model = Seance
    template_name = 'seances/seance_detail.html'
    context_object_name = 'seance'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Seance.STATUS_CHOICES
        return context

class SeanceCreateView(LoginRequiredMixin, CreateView):
    model = Seance
    form_class = SeanceForm
    template_name = 'seances/seance_form.html'
    success_url = reverse_lazy('seance-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Séance créée avec succès!')
        return super().form_valid(form)

class SeanceUpdateView(LoginRequiredMixin, UpdateView):
    model = Seance
    form_class = SeanceForm
    template_name = 'seances/seance_form.html'
    
    def get_success_url(self):
        return reverse_lazy('seance-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Séance mise à jour avec succès!')
        return super().form_valid(form)

class SeanceDeleteView(LoginRequiredMixin, DeleteView):
    model = Seance
    template_name = 'seances/seance_confirm_delete.html'
    success_url = reverse_lazy('seance-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Séance supprimée avec succès!')
        return super().delete(request, *args, **kwargs)

def annuler_seance(request, pk):
    seance = get_object_or_404(Seance, pk=pk)
    if request.method == 'POST':
        seance.statut = 'annule_sans_paiement'
        seance.save()
        messages.success(request, 'La séance a été annulée avec succès.')
        return redirect('seance-detail', pk=seance.pk)
    return redirect('seance-detail', pk=seance.pk)

@login_required
@require_POST
def start_session(request, pk):
    seance = get_object_or_404(Seance, pk=pk)
    if seance.start_session():
        messages.success(request, 'La séance a été démarrée avec succès!')
        return JsonResponse({
            'status': 'success',
            'new_status': dict(Seance.STATUS_CHOICES)[seance.statut]
        }, json_dumps_params={'ensure_ascii': False})
    messages.error(request, 'Impossible de démarrer la séance. Vérifiez son statut.')
    return JsonResponse({'status': 'error'}, status=400)

@login_required
@require_POST
def complete_session(request, pk):
    seance = get_object_or_404(Seance, pk=pk)
    if seance.complete_session():
        messages.success(request, 'La séance a été terminée avec succès!')
        return JsonResponse({
            'status': 'success',
            'new_status': dict(Seance.STATUS_CHOICES)[seance.statut]
        }, json_dumps_params={'ensure_ascii': False})
    messages.error(request, 'Impossible de terminer la séance. Vérifiez si elle est en cours.')
    return JsonResponse({'status': 'error'}, status=400)

@login_required
@require_POST
def cancel_session(request, pk):
    seance = get_object_or_404(Seance, pk=pk)
    if seance.cancel_session():
        messages.success(request, 'La séance a été annulée avec succès!')
        return JsonResponse({
            'status': 'success',
            'new_status': dict(Seance.STATUS_CHOICES)[seance.statut]
        }, json_dumps_params={'ensure_ascii': False})
    messages.error(request, 'Impossible d\'annuler la séance. Vérifiez son statut.')
    return JsonResponse({'status': 'error'}, status=400)
