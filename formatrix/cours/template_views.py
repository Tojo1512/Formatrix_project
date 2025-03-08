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

class CoursListView(LoginRequiredMixin, ListView):
    model = Cours
    template_name = 'cours/cours_list.html'
    context_object_name = 'cours_list'
    login_url = '/login/'
    ordering = ['-created_at']  # Tri par défaut
    paginate_by = 10  # Nombre d'éléments par page

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Récupération des paramètres de l'API
        search = self.request.GET.get('search', '')
        ordering = self.request.GET.get('ordering', '-created_at')
        statut = self.request.GET.get('statut', '')
        type_cours = self.request.GET.get('type', '')
        
        # Application des filtres de l'API
        if search:
            queryset = queryset.filter(nom_cours__icontains=search)
            
        if statut:
            queryset = queryset.filter(statut_approbation=statut)
            
        if type_cours:
            queryset = queryset.filter(type_cours=type_cours)
            
        # Application du tri
        queryset = queryset.order_by(ordering)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Paramètres de l'API pour le template
        context.update({
            'search_query': self.request.GET.get('search', ''),
            'ordering': self.request.GET.get('ordering', '-created_at'),
            'statut_filter': self.request.GET.get('statut', ''),
            'type_filter': self.request.GET.get('type', ''),
            'show_create_button': True,
            'create_url': reverse_lazy('cours-create'),
            'create_button_text': 'Create a course',
            'form_action': self.request.path,
            'reset_url': self.request.path,
            'has_active_filters': bool(
                self.request.GET.get('search', '') or 
                self.request.GET.get('statut', '') or 
                self.request.GET.get('type', '')
            )
        })
        return context

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
            messages.success(self.request, 'Course has been created successfully!')
            return response
        except Exception as e:
            messages.error(self.request, f'Error creating course: {str(e)}')
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
            messages.success(self.request, 'Course has been updated successfully!')
            return response
        except Exception as e:
            messages.error(self.request, f'Error updating course: {str(e)}')
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
        messages.success(request, f'Course "{cours.nom_cours}" has been deleted successfully!')
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
        messages.success(request, f'Course "{cours.nom_cours}" has been approved successfully!')
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
        messages.success(request, f'Course "{cours.nom_cours}" has been rejected!')
        return HttpResponseRedirect(reverse_lazy('cours-list'))


class CoursCancelView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/login/'
    
    def test_func(self):
        # Only staff members can cancel a course
        return self.request.user.is_staff
    
    def post(self, request, pk):
        cours = get_object_or_404(Cours, pk=pk)
        cours.status = 'cancelled'
        cours.save()
        messages.success(request, f'Course "{cours.nom_cours}" has been cancelled!')
        return HttpResponseRedirect(reverse_lazy('cours-detail', kwargs={'pk': pk}))
