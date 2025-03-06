from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views import View
from .models import Client
from .forms import ClientForm

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'client_list'
    login_url = '/login/'
    ordering = ['-clientid']  # Tri par défaut
    paginate_by = 10  # Nombre d'éléments par page

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Récupération des paramètres de l'API
        search = self.request.GET.get('search', '')
        ordering = self.request.GET.get('ordering', '-clientid')
        type_client = self.request.GET.get('type', '')
        ville = self.request.GET.get('ville', '')
        
        # Application des filtres de l'API
        if search:
            queryset = queryset.filter(nomclient__icontains=search)
            
        if type_client:
            queryset = queryset.filter(typeclientid__typeclient=type_client)
            
        if ville:
            queryset = queryset.filter(ville=ville)
            
        # Application du tri
        queryset = queryset.order_by(ordering)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Paramètres de l'API pour le template
        context.update({
            'search_query': self.request.GET.get('search', ''),
            'ordering': self.request.GET.get('ordering', '-clientid'),
            'type_filter': self.request.GET.get('type', ''),
            'ville_filter': self.request.GET.get('ville', ''),
            'show_create_button': True,
            'create_url': reverse_lazy('client-create'),
            'create_button_text': 'Créer un client',
            'form_action': self.request.path,
            'reset_url': self.request.path,
            'has_active_filters': bool(
                self.request.GET.get('search', '') or 
                self.request.GET.get('type', '') or 
                self.request.GET.get('ville', '')
            )
        })
        return context

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    template_name = 'clients/client_form.html'
    form_class = ClientForm
    success_url = reverse_lazy('client-list')
    login_url = '/login/'

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Le client a été créé avec succès!')
            return response
        except Exception as e:
            messages.error(self.request, f'Erreur lors de la création du client: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field in form:
            for error in field.errors:
                messages.error(self.request, f'{field.label}: {error}')
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, error)
        return super().form_invalid(form)

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'
    login_url = '/login/'
    pk_url_kwarg = 'pk'  # Utilise 'pk' comme paramètre d'URL pour l'ID

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = 'clients/client_form.html'
    form_class = ClientForm
    success_url = reverse_lazy('client-list')
    login_url = '/login/'
    pk_url_kwarg = 'pk'  # Utilise 'pk' comme paramètre d'URL pour l'ID

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Le client a été mis à jour avec succès!')
            return response
        except Exception as e:
            messages.error(self.request, f'Erreur lors de la mise à jour du client: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field in form:
            for error in field.errors:
                messages.error(self.request, f'{field.label}: {error}')
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, error)
        return super().form_invalid(form)

class ClientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('client-list')
    login_url = '/login/'
    pk_url_kwarg = 'pk'  # Utilise 'pk' comme paramètre d'URL pour l'ID
    
    def test_func(self):
        # Seuls les administrateurs peuvent supprimer un client
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        client = self.get_object()
        messages.success(request, f'Le client "{client.nomclient}" a été supprimé avec succès!')
        return super().delete(request, *args, **kwargs)
