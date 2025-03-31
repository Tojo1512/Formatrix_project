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
        secteur = self.request.GET.get('secteur', '')
        ville = self.request.GET.get('ville', '')
        
        # Application des filtres de l'API
        if search:
            queryset = queryset.filter(nom_entite__icontains=search)
            
        if type_client and type_client != '':
            queryset = queryset.filter(typeclientid__categorie=type_client)
            
        if secteur and secteur != '':
            queryset = queryset.filter(secteur_activite=secteur)
            
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
            'secteur_filter': self.request.GET.get('secteur', ''),
            'ville_filter': self.request.GET.get('ville', ''),
            'show_create_button': True,
            'create_url': '/clients/creer/',
            'create_button_text': 'Create a client',
            'form_action': self.request.path,
            'reset_url': self.request.path,
            'has_active_filters': bool(
                self.request.GET.get('search', '') or 
                self.request.GET.get('type', '') or 
                self.request.GET.get('secteur', '') or
                self.request.GET.get('ville', '')
            )
        })
        return context

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    template_name = 'clients/client_form.html'
    form_class = ClientForm
    success_url = reverse_lazy('clients:client-list')  
    login_url = '/login/'

    def form_valid(self, form):
        try:
            client = form.save()
            messages.success(self.request, f'Client "{client.nom_entite}" has been created successfully!')
            return redirect(reverse_lazy('clients:client-detail', kwargs={'pk': client.clientid}))
        except Exception as e:
            messages.error(self.request, f'Error creating client: {str(e)}')
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
    pk_url_kwarg = 'pk'  

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = 'clients/client_form.html'
    form_class = ClientForm
    success_url = reverse_lazy('clients:client-list')  
    login_url = '/login/'
    pk_url_kwarg = 'pk'  

    def form_valid(self, form):
        try:
            client = form.save()
            messages.success(self.request, f'Client "{client.nom_entite}" has been updated successfully!')
            return redirect(reverse_lazy('clients:client-detail', kwargs={'pk': client.clientid}))
        except Exception as e:
            messages.error(self.request, f'Error updating client: {str(e)}')
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
    success_url = reverse_lazy('clients:client-list')  
    login_url = '/login/'
    pk_url_kwarg = 'pk'  
    
    def test_func(self):
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        client = self.get_object()
        messages.success(request, f'Client "{client.nom_entite}" has been deleted successfully!')
        return super().delete(request, *args, **kwargs)
