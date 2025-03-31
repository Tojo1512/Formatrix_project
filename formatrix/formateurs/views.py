from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import Formateur
from .forms import FormateurForm
from django.db import models
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponseForbidden
from cours.models import Cours

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
            'create_url': reverse_lazy('formateurs:formateur-create'),
            'create_button_text': 'Ajouter un formateur'
        })
        return context

class FormateurCreateView(LoginRequiredMixin, CreateView):
    model = Formateur
    form_class = FormateurForm
    template_name = 'formateurs/formateur_form.html'
    success_url = reverse_lazy('formateurs:formateur-list')

    def form_valid(self, form):
        try:
            formateur = form.save()
            messages.success(self.request, f'Trainer {formateur.get_full_name()} has been created successfully!')
            return redirect('formateurs:formateur-detail', pk=formateur.formateurid)
        except Exception as e:
            messages.error(self.request, f'Error creating trainer: {str(e)}')
            return self.form_invalid(form)

class FormateurUpdateView(LoginRequiredMixin, UpdateView):
    model = Formateur
    form_class = FormateurForm
    template_name = 'formateurs/formateur_form.html'
    pk_url_kwarg = 'pk'
    
    def get_success_url(self):
        return reverse_lazy('formateurs:formateur-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        try:
            formateur = form.save()
            messages.success(self.request, f'Trainer {formateur.get_full_name()} has been updated successfully!')
            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(self.request, f'Error updating trainer: {str(e)}')
            return self.form_invalid(form)

class FormateurDetailView(LoginRequiredMixin, DetailView):
    model = Formateur
    template_name = 'formateurs/formateur_detail.html'
    context_object_name = 'formateur'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formateur = self.get_object()
        # Préparer la liste des spécialités
        if formateur.specialites:
            context['specialites_list'] = [spec.strip() for spec in formateur.specialites.split(',')]
        else:
            context['specialites_list'] = []
        # Ajouter les cours actifs
        context['cours_actifs'] = formateur.get_active_courses()
        return context

class FormateurDeleteView(LoginRequiredMixin, DeleteView):
    model = Formateur
    template_name = 'formateurs/formateur_confirm_delete.html'
    success_url = reverse_lazy('formateurs:formateur-list')
    pk_url_kwarg = 'pk'

    def delete(self, request, *args, **kwargs):
        formateur = self.get_object()
        messages.success(request, f'Trainer {formateur.get_full_name()} has been deleted successfully!')
        return super().delete(request, *args, **kwargs)

class FormateurRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nom = forms.CharField(max_length=100, required=True, label="Last Name")
    prenom = forms.CharField(max_length=100, required=True, label="First Name")
    telephone = forms.CharField(max_length=20, required=False, label="Phone")
    date_naissance = forms.DateField(required=False, label="Birth Date", widget=forms.DateInput(attrs={'type': 'date'}))
    adresse = forms.CharField(max_length=200, required=False, label="Address")
    ville = forms.CharField(max_length=100, required=False, label="City")
    code_postal = forms.CharField(max_length=10, required=False, label="Postal Code")
    type_formateur = forms.ChoiceField(choices=Formateur.TYPE_CHOICES, required=True, label="Trainer Type")
    niveau_expertise = forms.ChoiceField(choices=Formateur.LEVEL_CHOICES, required=True, label="Expertise Level")
    specialites = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True, label="Specialties")
    disponibilite = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True, label="Availability")
    cv = forms.FileField(required=False, label="Resume/CV")
    photo = forms.ImageField(required=False, label="Photo")
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Notes")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "nom", "prenom", "telephone", "date_naissance", 
                 "adresse", "ville", "code_postal", "type_formateur", "niveau_expertise", "specialites", 
                 "disponibilite", "cv", "photo", "notes")
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

def formateur_register(request):
    """
    Vue pour l'inscription des formateurs.
    Cette fonction gère à la fois la création d'un utilisateur dans auth.User
    et d'un profil dans le modèle Formateur.
    """
    if request.method == 'POST':
        form = FormateurRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Créer l'utilisateur auth.User
                user = form.save()
                
                # Créer un formateur associé à cet utilisateur
                formateur = Formateur(
                    # Ne pas utiliser user=user car la colonne user_id n'existe pas encore
                    nom=form.cleaned_data.get('nom', ''),
                    prenom=form.cleaned_data.get('prenom', ''),
                    email=user.email,
                    telephone=form.cleaned_data.get('telephone', ''),
                    date_naissance=form.cleaned_data.get('date_naissance'),
                    adresse=form.cleaned_data.get('adresse', ''),
                    ville=form.cleaned_data.get('ville', ''),
                    specialites=form.cleaned_data.get('specialites', ''),
                    niveau_expertise=form.cleaned_data.get('niveau_expertise', ''),
                    type_formateur=form.cleaned_data.get('type_formateur', ''),
                    disponibilite=form.cleaned_data.get('disponibilite', ''),
                    cv=form.cleaned_data.get('cv'),
                    photo=form.cleaned_data.get('photo'),
                    notes=form.cleaned_data.get('notes', ''),
                    statut='active',
                    date_embauche=timezone.now().date()
                )
                formateur.save()
                
                # Connecter l'utilisateur
                login(request, user)
                messages.success(request, "Registration successful! Welcome to Formatrix.")
                
                # Rediriger vers le dashboard formateur ou la page d'accueil
                return redirect('formateurs:formateur-detail', pk=formateur.formateurid)
            except Exception as e:
                messages.error(request, f"An error occurred during registration: {str(e)}")
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = FormateurRegistrationForm()
    
    return render(request, 'formateurs/formateur_register.html', {'form': form})

class FormateurCoursListView(LoginRequiredMixin, ListView):
    model = Cours
    template_name = 'formateurs/formateur_cours_list.html'
    context_object_name = 'cours_list'
    paginate_by = 10
    
    def get_queryset(self):
        # Vérifier si l'utilisateur est un formateur
        try:
            formateur = None
            if self.kwargs.get('pk'):
                # S'il y a un ID de formateur spécifié dans l'URL
                formateur = get_object_or_404(Formateur, formateurid=self.kwargs.get('pk'))
            elif hasattr(self.request.user, 'formateur_profile'):
                # Si l'utilisateur connecté est un formateur
                formateur = self.request.user.formateur_profile
            
            if formateur:
                # Récupérer tous les cours assignés à ce formateur
                return Cours.objects.filter(formateurs=formateur).order_by('-created_at')
            else:
                return Cours.objects.none()
        except Formateur.DoesNotExist:
            return Cours.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtenir le formateur pour le titre de la page
        try:
            formateur = None
            if self.kwargs.get('pk'):
                formateur = get_object_or_404(Formateur, formateurid=self.kwargs.get('pk'))
            elif hasattr(self.request.user, 'formateur_profile'):
                formateur = self.request.user.formateur_profile
            
            if formateur:
                context['formateur'] = formateur
                context['page_title'] = f"Courses assigned to {formateur.prenom} {formateur.nom}"
            else:
                context['page_title'] = "Your courses"
        except Formateur.DoesNotExist:
            context['page_title'] = "Your courses"
        
        return context 