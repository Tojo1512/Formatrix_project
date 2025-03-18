from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Formateur
from .forms import FormateurForm
from django.db import models
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

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

class FormateurCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Formateur
    form_class = FormateurForm
    template_name = 'formateurs/formateur_form.html'
    success_url = reverse_lazy('formateurs:formateur-list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        try:
            formateur = form.save()
            messages.success(self.request, f'Le formateur {formateur.get_full_name()} a été créé avec succès!')
            return redirect('formateurs:formateur-detail', pk=formateur.formateurid)
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
            return redirect('formateurs:formateur-detail', pk=formateur.formateurid)
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

class FormateurRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nom = forms.CharField(max_length=100, required=True, label="Nom")
    prenom = forms.CharField(max_length=100, required=True, label="Prénom")
    telephone = forms.CharField(max_length=20, required=False, label="Téléphone")
    date_naissance = forms.DateField(required=False, label="Date de naissance", widget=forms.DateInput(attrs={'type': 'date'}))
    adresse = forms.CharField(max_length=200, required=False, label="Adresse")
    ville = forms.CharField(max_length=100, required=False, label="Ville")
    type_formateur = forms.ChoiceField(choices=Formateur.TYPE_CHOICES, required=True, label="Type de formateur")
    niveau_expertise = forms.ChoiceField(choices=Formateur.NIVEAU_CHOICES, required=True, label="Niveau d'expertise")
    specialites = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True, label="Spécialités")
    disponibilite = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True, label="Disponibilité")
    cv = forms.FileField(required=False, label="CV")
    photo = forms.ImageField(required=False, label="Photo")
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Notes")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "nom", "prenom", "telephone", "date_naissance", 
                 "adresse", "ville", "type_formateur", "niveau_expertise", "specialites", 
                 "disponibilite", "cv", "photo", "notes")
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

def formateur_register(request, registration_key):
    if registration_key != settings.FORMATEUR_REGISTRATION_KEY:
        messages.error(request, "Clé d'inscription invalide")
        return redirect('home')
        
    if request.method == 'POST':
        form = FormateurRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Créer l'utilisateur
                user = form.save()
                print(f"Utilisateur créé : ID={user.id}, Username={user.username}, Email={user.email}")
                
                # Créer un formateur associé à cet utilisateur
                formateur = Formateur(
                    user=user,  # Associer explicitement l'utilisateur
                    nom=form.cleaned_data.get('nom', ''),
                    prenom=form.cleaned_data.get('prenom', ''),
                    email=user.email,
                    telephone=form.cleaned_data.get('telephone', ''),
                    date_naissance=form.cleaned_data.get('date_naissance', timezone.now().date()),
                    adresse=form.cleaned_data.get('adresse', ''),
                    ville=form.cleaned_data.get('ville', ''),
                    type_formateur=form.cleaned_data.get('type_formateur', ''),
                    niveau_expertise=form.cleaned_data.get('niveau_expertise', ''),
                    specialites=form.cleaned_data.get('specialites', ''),
                    disponibilite=form.cleaned_data.get('disponibilite', ''),
                    cv=form.cleaned_data.get('cv'),
                    photo=form.cleaned_data.get('photo'),
                    notes=form.cleaned_data.get('notes', ''),
                    statut='actif',
                    date_embauche=timezone.now().date()
                )
                
                # Vérifier que l'utilisateur est bien associé avant de sauvegarder
                if formateur.user is None:
                    print("ERREUR : L'utilisateur n'est pas associé au formateur avant la sauvegarde")
                    formateur.user = user
                
                formateur.save()
                print(f"Formateur créé : ID={formateur.formateurid}, Nom={formateur.nom}, Prénom={formateur.prenom}, User ID={formateur.user_id}")
                
                # Double vérification après la sauvegarde
                formateur.refresh_from_db()
                if formateur.user_id != user.id:
                    print(f"ERREUR : L'association n'a pas été sauvegardée correctement. Tentative de correction...")
                    formateur.user = user
                    formateur.save(update_fields=['user'])
                    print(f"Correction effectuée : User ID maintenant = {formateur.user_id}")
                
                # Connecter l'utilisateur
                login(request, user)
                messages.success(request, "Inscription réussie ! Bienvenue sur Formatrix.")
                return redirect('formateurs:formateur-detail', pk=formateur.formateurid)
            except Exception as e:
                print(f"ERREUR lors de l'inscription : {str(e)}")
                messages.error(request, f"Une erreur est survenue lors de l'inscription : {str(e)}")
                return render(request, 'formateurs/formateur_register.html', {'form': form})
        else:
            print(f"Erreurs de formulaire : {form.errors}")
    else:
        form = FormateurRegistrationForm()
    
    return render(request, 'formateurs/formateur_register.html', {'form': form}) 