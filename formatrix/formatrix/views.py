from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.conf import settings
from django.contrib import messages
from django.db.models import Count, F
from django.utils import timezone
from datetime import timedelta
import json

# Import direct des modèles sans bloc try/except
from cours.models import Cours
from seances.models import Seance
from apprenants.models import Apprenant
from clients.models import Client
from formateurs.models import Formateur
from inscriptions.models import Inscription

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[('trainer', 'Trainer'), ('admin', 'Administrator')],
        required=True
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "role")

class AdminRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    admin_code = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter des placeholders et des classes
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Prénom'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})
        self.fields['admin_code'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Code administrateur'})

    def clean_admin_code(self):
        admin_code = self.cleaned_data.get('admin_code')
        if admin_code != settings.ADMIN_REGISTRATION_KEY:
            raise forms.ValidationError("Le code administrateur est incorrect.")
        return admin_code

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un utilisateur avec cet email existe déjà.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.is_staff = True
        user.is_superuser = True
        
        if commit:
            user.save()
        return user

def home_view(request):
    # Si l'utilisateur n'est pas connecté, afficher la page d'accueil avec les deux options
    if not request.user.is_authenticated:
        return render(request, 'welcome.html')
    
    # Si l'utilisateur est connecté, afficher le tableau de bord
    context = {}
    
    # Compter les entités principales
    context['apprenants_count'] = Apprenant.objects.count()
    context['seances_count'] = Seance.objects.count()
    context['cours_count'] = Cours.objects.count()
    context['clients_count'] = Client.objects.count()
    context['formateurs_count'] = Formateur.objects.count()
    
    # Calculer le pourcentage de formations terminées
    today = timezone.now().date()
    total_seances = Seance.objects.count()
    completed_seances = Seance.objects.filter(statut='termine').count()
    
    # Éviter la division par zéro
    context['percentage_completed'] = int(completed_seances / total_seances * 100) if total_seances > 0 else 0
    
    # Séances à venir dans les 7 prochains jours
    next_week = today + timedelta(days=7)
    upcoming_seances = Seance.objects.filter(date__gte=today, date__lte=next_week)
    context['upcoming_seances_count'] = upcoming_seances.count()
    
    # AMÉLIORATION 1: Données pour le donut chart des statuts de sessions
    # Définir l'ordre et les traductions françaises des statuts
    status_translations = {
        'Not started': 'Non commencé',
        'In progress': 'En cours',
        'Completed': 'Terminé',
        'Cancelled': 'Annulé'
    }
    
    # Obtenir tous les statuts possibles et leurs nombres
    statut_counts_dict = {}
    for status_choice in Seance.STATUS_CHOICES:
        status_key, status_label = status_choice
        translated_label = status_translations.get(status_label, status_label)
        count = Seance.objects.filter(statut=status_key).count()
        statut_counts_dict[translated_label] = count
    
    # Créer les listes dans un ordre spécifique
    ordered_status = ['Non commencé', 'En cours', 'Terminé', 'Annulé']
    session_status_labels = []
    session_status_counts = []
    
    for status in ordered_status:
        if status in statut_counts_dict:
            session_status_labels.append(status)
            session_status_counts.append(statut_counts_dict[status])
    
    context['session_status_labels'] = json.dumps(session_status_labels)
    context['session_status_counts'] = json.dumps(session_status_counts)
    
    # AMÉLIORATION 2: Données pour le bar chart des heures de formation par formateur
    # Get top 10 formateurs by total training hours
    formateurs_with_hours = Formateur.objects.annotate(
        total_seances=Count('seances_assignees', distinct=True)
    ).order_by('-total_seances')[:10]
    
    formateur_names = []
    formateur_heures = []
    
    for formateur in formateurs_with_hours:
        formateur_names.append(formateur.get_full_name())
        # Calculate total duration in months (as defined in the model)
        total_duree = 0
        for seance in formateur.seances_assignees.all():
            if hasattr(seance, 'duree') and seance.duree:
                # La durée est en mois, on la convertit en heures (approx 160h/mois)
                total_duree += seance.duree * 160
        formateur_heures.append(round(total_duree, 1))
    
    context['formateur_names'] = json.dumps(formateur_names)
    context['formateur_heures'] = json.dumps(formateur_heures)
    
    # Dernières inscriptions
    latest_inscriptions = Inscription.objects.all().order_by('-date_inscription')[:5]
    context['latest_inscriptions'] = latest_inscriptions
    
    # Données pour le sparkline des formateurs (keeping this for compatibility)
    activities = [0] * 14
    for i in range(14):
        day = today - timedelta(days=13-i)
        activities[i] = Seance.objects.filter(formateurs__isnull=False, date=day).count()
    
    context['activite_formateurs'] = json.dumps(activities)
    
    return render(request, 'home.html', context)

def register_view(request):
    """Redirige vers la page d'inscription formateur"""
    return redirect('formateurs:formateur-register')

def admin_register_view(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, "Inscription administrateur réussie ! Bienvenue sur Formatrix.")
                return redirect('home')
            except Exception as e:
                messages.error(request, f"Une erreur est survenue lors de l'inscription : {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'auth/admin_register.html', {'form': form})