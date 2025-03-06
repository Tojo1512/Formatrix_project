from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views import View
from django.db.models import Q
from .models import Apprenant
from .forms import ApprenantForm

class ApprenantListView(LoginRequiredMixin, ListView):
    model = Apprenant
    template_name = 'apprenants/apprenant_list.html'
    context_object_name = 'apprenants_list'
    login_url = '/login/'
    ordering = ['-created_at']  # Tri par défaut
    paginate_by = 10  # Nombre d'éléments par page

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Récupération des paramètres de filtrage
        search = self.request.GET.get('search', '')
        sexe = self.request.GET.get('sexe', '')
        niveau_academique = self.request.GET.get('niveau_academique', '')
        categorie_age = self.request.GET.get('categorie_age', '')
        ville = self.request.GET.get('ville', '')
        ordering = self.request.GET.get('ordering', '-created_at')
        
        # Application des filtres
        if search:
            queryset = queryset.filter(
                Q(nom_apprenant__icontains=search) | 
                Q(cin__icontains=search) |
                Q(ville__icontains=search)
            )
            
        if sexe:
            queryset = queryset.filter(sexe=sexe)
            
        if niveau_academique:
            queryset = queryset.filter(niveau_academique=niveau_academique)
            
        if categorie_age:
            queryset = queryset.filter(categorie_age=categorie_age)
            
        if ville:
            queryset = queryset.filter(ville__icontains=ville)
            
        # Application du tri
        queryset = queryset.order_by(ordering)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Paramètres pour le template
        context.update({
            'search_query': self.request.GET.get('search', ''),
            'sexe_filter': self.request.GET.get('sexe', ''),
            'niveau_filter': self.request.GET.get('niveau_academique', ''),
            'age_filter': self.request.GET.get('categorie_age', ''),
            'ville_filter': self.request.GET.get('ville', ''),
            'ordering': self.request.GET.get('ordering', '-created_at'),
            'show_create_button': True,
            'create_url': reverse_lazy('apprenant-create'),
            'create_button_text': 'Ajouter un apprenant',
            'form_action': self.request.path,
            'reset_url': self.request.path,
            'has_active_filters': bool(
                self.request.GET.get('search', '') or 
                self.request.GET.get('sexe', '') or 
                self.request.GET.get('niveau_academique', '') or
                self.request.GET.get('categorie_age', '') or
                self.request.GET.get('ville', '')
            ),
            'sexe_choices': Apprenant.GENRE_CHOICES,
            'niveau_choices': Apprenant.NIVEAU_ACADEMIQUE_CHOICES,
            'age_choices': Apprenant.CATEGORIE_AGE_CHOICES
        })
        return context

class ApprenantCreateView(LoginRequiredMixin, CreateView):
    model = Apprenant
    template_name = 'apprenants/apprenant_form.html'
    form_class = ApprenantForm
    success_url = reverse_lazy('apprenant-list')
    login_url = '/login/'

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "L'apprenant a été créé avec succès!")
            return response
        except Exception as e:
            messages.error(self.request, f"Erreur lors de la création de l'apprenant: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field in form:
            for error in field.errors:
                messages.error(self.request, f'{field.label}: {error}')
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, error)
        return super().form_invalid(form)

class ApprenantDetailView(LoginRequiredMixin, DetailView):
    model = Apprenant
    template_name = 'apprenants/apprenant_detail.html'
    context_object_name = 'apprenant'
    login_url = '/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajout des choix pour l'affichage des libellés
        context.update({
            'sexe_choices': Apprenant.GENRE_CHOICES,
            'niveau_choices': Apprenant.NIVEAU_ACADEMIQUE_CHOICES,
            'age_choices': Apprenant.CATEGORIE_AGE_CHOICES
        })
        return context

class ApprenantUpdateView(LoginRequiredMixin, UpdateView):
    model = Apprenant
    template_name = 'apprenants/apprenant_form.html'
    form_class = ApprenantForm
    success_url = reverse_lazy('apprenant-list')
    login_url = '/login/'

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "L'apprenant a été mis à jour avec succès!")
            return response
        except Exception as e:
            messages.error(self.request, f"Erreur lors de la mise à jour de l'apprenant: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field in form:
            for error in field.errors:
                messages.error(self.request, f'{field.label}: {error}')
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, error)
        return super().form_invalid(form)

class ApprenantDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Apprenant
    template_name = 'apprenants/apprenant_confirm_delete.html'
    success_url = reverse_lazy('apprenant-list')
    login_url = '/login/'
    
    def test_func(self):
        # Seuls les administrateurs peuvent supprimer un apprenant
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        apprenant = self.get_object()
        messages.success(request, f"L'apprenant \"{apprenant.nom_apprenant}\" a été supprimé avec succès!")
        return super().delete(request, *args, **kwargs)
