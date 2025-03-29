from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Lieu
from .forms import LieuForm

class LieuCreateView(LoginRequiredMixin, CreateView):
    model = Lieu
    form_class = LieuForm
    template_name = 'lieux/lieu_form.html'
    
    def get_success_url(self):
        # Vérifier s'il y a un paramètre 'next' dans l'URL
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('lieux:lieu-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le lieu a été créé avec succès.')
        return super().form_valid(form)

class LieuUpdateView(LoginRequiredMixin, UpdateView):
    model = Lieu
    form_class = LieuForm
    template_name = 'lieux/lieu_form.html'
    
    def get_success_url(self):
        return reverse_lazy('lieux:lieu-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Le lieu a été mis à jour avec succès.')
        return super().form_valid(form)

class LieuDeleteView(LoginRequiredMixin, DeleteView):
    model = Lieu
    template_name = 'lieux/lieu_confirm_delete.html'
    success_url = reverse_lazy('lieux:lieu-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Le lieu a été supprimé avec succès.')
        return super().delete(request, *args, **kwargs)

class LieuDetailView(LoginRequiredMixin, DetailView):
    model = Lieu
    template_name = 'lieux/lieu_detail.html'

class LieuListView(LoginRequiredMixin, ListView):
    model = Lieu
    template_name = 'lieux/lieu_list.html'
    context_object_name = 'lieux'
    ordering = ['lieu']