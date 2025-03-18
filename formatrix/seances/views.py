from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse

from .models import Seance, Absence
from .forms import SeanceForm, AbsenceForm

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
        
        # Filtre pour les absences
        absences_filter = self.request.GET.get('filtre', '')
        if absences_filter == 'absences':
            # Au lieu de filtrer uniquement les séances avec absences,
            # nous les affichons toutes mais nous pourrions les ordonner
            # pour mettre en avant celles avec des absences
            queryset = queryset.annotate(
                has_absences=Count('absences')
            ).order_by('-has_absences', '-date')
        
        # Tri
        ordering = self.request.GET.get('ordering', '-date')
        if absences_filter != 'absences':  # Ne réappliquons pas l'ordre si nous sommes en mode absences
            queryset = queryset.order_by(ordering)
        
        return queryset.prefetch_related('cours').select_related('lieu')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['statut_filter'] = self.request.GET.get('statut', '')
        context['horaire_filter'] = self.request.GET.get('horaire', '')
        context['ordering'] = self.request.GET.get('ordering', '-date')
        context['show_create_button'] = True
        context['create_url'] = reverse_lazy('seances:seance-create')
        context['create_button_text'] = 'Créer une séance'
        context['reset_url'] = reverse_lazy('seances:seance-list')
        context['has_active_filters'] = bool(context['search_query'] or context['statut_filter'] or context['horaire_filter'])
        context['STATUS_CHOICES'] = Seance.STATUS_CHOICES
        
        # Passer l'information si nous sommes en mode filtrage des absences
        context['filtre_absences'] = self.request.GET.get('filtre', '') == 'absences'
        if context['filtre_absences']:
            context['page_title'] = 'Séances avec absences à gérer'
        else:
            context['page_title'] = 'Liste des séances'
            
        return context

class SeanceDetailView(LoginRequiredMixin, DetailView):
    model = Seance
    template_name = 'seances/seance_detail.html'
    context_object_name = 'seance'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Seance.STATUS_CHOICES
        
        # Récupérer les absences associées à cette séance
        context['absences'] = Absence.objects.filter(seance=self.object).order_by('-date_absence')
        
        return context

class SeanceCreateView(LoginRequiredMixin, CreateView):
    model = Seance
    form_class = SeanceForm
    template_name = 'seances/seance_form.html'
    
    def get_success_url(self):
        return reverse_lazy('seances:seance-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        try:
            # Vérification du nombre de formateurs
            formateurs = form.cleaned_data.get('formateurs', [])
            if len(formateurs) < 2:
                form.add_error('formateurs', "Vous devez sélectionner au moins deux formateurs pour cette séance.")
                return self.form_invalid(form)
            
            # Enregistrement de la séance
            response = super().form_valid(form)
            messages.success(self.request, 'Séance créée avec succès avec {} formateurs assignés!'.format(len(formateurs)))
            return response
            
        except Exception as e:
            messages.error(self.request, f"Erreur lors de la création de la séance: {str(e)}")
            return self.form_invalid(form)

class SeanceUpdateView(LoginRequiredMixin, UpdateView):
    model = Seance
    form_class = SeanceForm
    template_name = 'seances/seance_form.html'
    
    def get_success_url(self):
        return reverse_lazy('seances:seance-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        try:
            # Vérification du nombre de formateurs
            formateurs = form.cleaned_data.get('formateurs', [])
            if len(formateurs) < 2:
                form.add_error('formateurs', "Vous devez sélectionner au moins deux formateurs pour cette séance.")
                return self.form_invalid(form)
            
            # Enregistrement de la séance mise à jour
            response = super().form_valid(form)
            messages.success(self.request, 'Séance mise à jour avec succès avec {} formateurs assignés!'.format(len(formateurs)))
            return response
            
        except Exception as e:
            messages.error(self.request, f"Erreur lors de la mise à jour de la séance: {str(e)}")
            return self.form_invalid(form)

class SeanceDeleteView(LoginRequiredMixin, DeleteView):
    model = Seance
    template_name = 'seances/seance_confirm_delete.html'
    success_url = reverse_lazy('seances:seance-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Séance supprimée avec succès!')
        return super().delete(request, *args, **kwargs)

def annuler_seance(request, pk):
    seance = get_object_or_404(Seance, pk=pk)
    if request.method == 'POST':
        seance.statut = 'annule_sans_paiement'
        seance.save()
        messages.success(request, 'La séance a été annulée avec succès.')
        return redirect('seances:seance-detail', pk=seance.pk)
    return redirect('seances:seance-detail', pk=seance.pk)

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

# Vues pour la gestion des absences
@login_required
def absence_list(request, seance_id):
    seance = get_object_or_404(Seance, pk=seance_id)
    absences = Absence.objects.filter(seance=seance).order_by('-date_absence')
    
    context = {
        'seance': seance,
        'absences': absences,
    }
    
    return render(request, 'seances/absence_list.html', context)

@login_required
def absence_create(request, seance_id):
    seance = get_object_or_404(Seance, pk=seance_id)
    
    if request.method == 'POST':
        form = AbsenceForm(request.POST, seance=seance)
        if form.is_valid():
            absence = form.save(commit=False)
            absence.seance = seance
            absence.save()
            
            # Message de succès différent selon qu'un remplaçant a été désigné ou non
            if absence.formateur_remplacant:
                messages.success(request, f"L'absence de {absence.formateur_absent.get_full_name()} a été enregistrée avec {absence.formateur_remplacant.get_full_name()} comme remplaçant.")
            else:
                messages.success(request, f"L'absence de {absence.formateur_absent.get_full_name()} a été enregistrée. Veuillez désigner un remplaçant dès que possible.")
            
            return redirect('seances:absence_list', seance_id=seance.seance_id)
    else:
        form = AbsenceForm(seance=seance)
    
    context = {
        'form': form,
        'seance': seance,
    }
    
    return render(request, 'seances/absence_form.html', context)

@login_required
def absence_update(request, absence_id):
    absence = get_object_or_404(Absence, pk=absence_id)
    seance = absence.seance
    
    if request.method == 'POST':
        form = AbsenceForm(request.POST, instance=absence, seance=seance)
        if form.is_valid():
            form.save()
            
            if absence.formateur_remplacant:
                messages.success(request, f"L'absence a été mise à jour avec {absence.formateur_remplacant.get_full_name()} comme remplaçant.")
            else:
                messages.success(request, "L'absence a été mise à jour.")
            
            return redirect('seances:absence_list', seance_id=seance.seance_id)
    else:
        form = AbsenceForm(instance=absence, seance=seance)
    
    context = {
        'form': form,
        'seance': seance,
        'absence': absence,
    }
    
    return render(request, 'seances/absence_form.html', context)

@login_required
def absence_delete(request, absence_id):
    absence = get_object_or_404(Absence, pk=absence_id)
    seance = absence.seance
    
    if request.method == 'POST':
        formateur_name = absence.formateur_absent.get_full_name()
        absence.delete()
        messages.success(request, f"L'absence de {formateur_name} a été supprimée.")
        return redirect('seances:absence_list', seance_id=seance.seance_id)
    
    context = {
        'absence': absence,
        'seance': seance,
    }
    
    return render(request, 'seances/absence_confirm_delete.html', context)
