from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from .models import Cours
from .forms import CoursForm

class CoursListView(LoginRequiredMixin, ListView):
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
        return super().form_invalid(form)
