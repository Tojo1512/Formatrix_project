from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views import View
from .models import Cours
from .forms import CoursForm
from .mixins import CoursFilterMixin

class CoursListView(LoginRequiredMixin, CoursFilterMixin, ListView):
    model = Cours
    template_name = 'cours/cours_list.html'
    context_object_name = 'cours_list'
    login_url = '/login/'

class CoursCreateView(LoginRequiredMixin, CreateView):
    model = Cours
    template_name = 'cours/cours_form.html'
    form_class = CoursForm
    success_url = reverse_lazy('cours-list')
    login_url = '/login/'

    def form_valid(self, form):
        try:
            # Si le statut est 'approuve', on définit la date d'approbation
            if form.cleaned_data['statut_approbation'] == 'approuve':
                form.instance.date_approbation = timezone.now().date()
            
            response = super().form_valid(form)
            messages.success(self.request, 'Le cours a été créé avec succès!')
            return response
        except Exception as e:
            messages.error(self.request, f'Erreur lors de la création du cours: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field in form:
            for error in field.errors:
                messages.error(self.request, f'{field.label}: {error}')
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, error)
        return super().form_invalid(form)

class CoursDetailView(LoginRequiredMixin, DetailView):
    model = Cours
    template_name = 'cours/cours_detail.html'
    context_object_name = 'cours'
    login_url = '/login/'

class CoursUpdateView(LoginRequiredMixin, UpdateView):
    model = Cours
    template_name = 'cours/cours_form.html'
    form_class = CoursForm
    success_url = reverse_lazy('cours-list')
    login_url = '/login/'

    def form_valid(self, form):
        try:
            # Si le statut change pour 'approuve', on définit la date d'approbation
            if form.cleaned_data['statut_approbation'] == 'approuve' and not form.instance.date_approbation:
                form.instance.date_approbation = timezone.now().date()
            # Si le statut n'est plus 'approuve', on réinitialise les dates
            elif form.cleaned_data['statut_approbation'] != 'approuve':
                form.instance.date_approbation = None
                form.instance.date_expiration_validite = None
                
            response = super().form_valid(form)
            messages.success(self.request, 'Le cours a été mis à jour avec succès!')
            return response
        except Exception as e:
            messages.error(self.request, f'Erreur lors de la mise à jour du cours: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field in form:
            for error in field.errors:
                messages.error(self.request, f'{field.label}: {error}')
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, error)
        return super().form_invalid(form)


class CoursDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Cours
    template_name = 'cours/cours_confirm_delete.html'
    success_url = reverse_lazy('cours-list')
    login_url = '/login/'
    
    def test_func(self):
        # Seuls les administrateurs peuvent supprimer un cours
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        cours = self.get_object()
        messages.success(request, f'Le cours "{cours.nom_cours}" a été supprimé avec succès!')
        return super().delete(request, *args, **kwargs)


class CoursApprouverView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/login/'
    
    def test_func(self):
        # Seuls les administrateurs peuvent approuver un cours
        return self.request.user.is_staff
    
    def get(self, request, pk):
        cours = get_object_or_404(Cours, pk=pk)
        cours.statut_approbation = 'approuve'
        cours.date_approbation = timezone.now().date()
        # La date d'expiration sera automatiquement calculée dans la méthode save() du modèle
        cours.save()
        messages.success(request, f'Le cours "{cours.nom_cours}" a été approuvé avec succès!')
        return HttpResponseRedirect(reverse_lazy('cours-list'))


class CoursRefuserView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/login/'
    
    def test_func(self):
        # Seuls les administrateurs peuvent refuser un cours
        return self.request.user.is_staff
    
    def get(self, request, pk):
        cours = get_object_or_404(Cours, pk=pk)
        cours.statut_approbation = 'refuse'
        cours.date_approbation = None
        cours.date_expiration_validite = None
        cours.save()
        messages.success(request, f'Le cours "{cours.nom_cours}" a été refusé!')
        return HttpResponseRedirect(reverse_lazy('cours-list'))
