from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect
from .models import Formateur
from .forms import FormateurForm
from django.db import models

class FormateurListView(LoginRequiredMixin, ListView):
    model = Formateur
    template_name = 'formateurs/formateur_list.html'
    context_object_name = 'formateur_list'
    paginate_by = 10
    ordering = ['nom', 'prenom']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        type_filter = self.request.GET.get('type', '')
        statut_filter = self.request.GET.get('statut', '')
        niveau_filter = self.request.GET.get('niveau', '')

        if search:
            queryset = queryset.filter(
                models.Q(nom__icontains=search) |
                models.Q(prenom__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(specialites__icontains=search)
            )

        if type_filter:
            queryset = queryset.filter(type_formateur=type_filter)
        
        if statut_filter:
            queryset = queryset.filter(statut=statut_filter)

        if niveau_filter:
            queryset = queryset.filter(niveau_expertise=niveau_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'search_query': self.request.GET.get('search', ''),
            'type_filter': self.request.GET.get('type', ''),
            'statut_filter': self.request.GET.get('statut', ''),
            'niveau_filter': self.request.GET.get('niveau', ''),
            'show_create_button': True,
            'create_url': reverse_lazy('formateur-create'),
            'create_button_text': 'Ajouter un formateur'
        })
        return context

class FormateurCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Formateur
    form_class = FormateurForm
    template_name = 'formateurs/formateur_form.html'
    success_url = reverse_lazy('formateur-list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        try:
            formateur = form.save()
            messages.success(self.request, f'Le formateur {formateur.get_full_name()} a été créé avec succès!')
            return redirect('formateur-detail', pk=formateur.formateurid)
        except Exception as e:
            messages.error(self.request, f'Erreur lors de la création du formateur: {str(e)}')
            return self.form_invalid(form)

class FormateurUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Formateur
    form_class = FormateurForm
    template_name = 'formateurs/formateur_form.html'
    pk_url_kwarg = 'pk'

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        try:
            formateur = form.save()
            messages.success(self.request, f'Le formateur {formateur.get_full_name()} a été mis à jour avec succès!')
            return redirect('formateur-detail', pk=formateur.formateurid)
        except Exception as e:
            messages.error(self.request, f'Erreur lors de la mise à jour du formateur: {str(e)}')
            return self.form_invalid(form)

class FormateurDetailView(LoginRequiredMixin, DetailView):
    model = Formateur
    template_name = 'formateurs/formateur_detail.html'
    context_object_name = 'formateur'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formateur = self.get_object()
        context['cours_actifs'] = formateur.get_cours_actifs()
        return context

class FormateurDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Formateur
    template_name = 'formateurs/formateur_confirm_delete.html'
    success_url = reverse_lazy('formateur-list')
    pk_url_kwarg = 'pk'

    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        formateur = self.get_object()
        messages.success(request, f'Le formateur {formateur.get_full_name()} a été supprimé avec succès!')
        return super().delete(request, *args, **kwargs) 