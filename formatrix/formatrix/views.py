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

try:
    from cours.models import Cours
    from seances.models import Seance
    from apprenants.models import Apprenant
    from clients.models import Client
    from formateurs.models import Formateur
    from inscriptions.models import Inscription
except ImportError:
    # Pour gérer le cas où les modèles ne sont pas encore créés
    pass

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
    context = {}
    
    try:
        # Compter les entités principales
        context['apprenants_count'] = Apprenant.objects.count()
        context['seances_count'] = Seance.objects.count()
        context['cours_count'] = Cours.objects.count()
        context['clients_count'] = Client.objects.count()
        context['formateurs_count'] = Formateur.objects.count()
        
        # Calculer le pourcentage de formations terminées
        today = timezone.now().date()
        total_seances = Seance.objects.count()
        completed_seances = Seance.objects.filter(date_fin__lt=today).count()
        context['percentage_completed'] = int(completed_seances / total_seances * 100) if total_seances > 0 else 0
        
        # Séances à venir dans les 7 prochains jours
        next_week = today + timedelta(days=7)
        upcoming_seances = Seance.objects.filter(date_debut__gte=today, date_debut__lte=next_week)
        context['upcoming_seances_count'] = upcoming_seances.count()
        
        # Données pour le graphique des séances à venir
        days = [(today + timedelta(days=i)).strftime('%d/%m') for i in range(7)]
        counts = []
        for i in range(7):
            day = today + timedelta(days=i)
            count = upcoming_seances.filter(date_debut=day).count()
            counts.append(count)
        
        context['upcoming_days'] = json.dumps(days)
        context['upcoming_counts'] = json.dumps(counts)
        
        # Données pour le graphique principal
        months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
        cours_mensuel = [0] * 12
        seances_mensuel = [0] * 12
        inscriptions_mensuel = [0] * 12
        
        # Agrégation par mois pour chaque entité
        for cours in Cours.objects.all():
            creation_month = cours.date_creation.month - 1 if hasattr(cours, 'date_creation') else 0
            if 0 <= creation_month < 12:
                cours_mensuel[creation_month] += 1
        
        for seance in Seance.objects.all():
            debut_month = seance.date_debut.month - 1
            if 0 <= debut_month < 12:
                seances_mensuel[debut_month] += 1
        
        for inscription in Inscription.objects.all():
            inscription_month = inscription.date_inscription.month - 1 if hasattr(inscription, 'date_inscription') else 0
            if 0 <= inscription_month < 12:
                inscriptions_mensuel[inscription_month] += 1
        
        context['cours_mensuel'] = json.dumps(cours_mensuel)
        context['seances_mensuel'] = json.dumps(seances_mensuel)
        context['inscriptions_mensuel'] = json.dumps(inscriptions_mensuel)
        
        # Dernières inscriptions
        context['latest_inscriptions'] = Inscription.objects.all().order_by('-date_inscription')[:5]
        
        # Données pour le sparkline des formateurs
        activities = [0] * 14
        for i in range(14):
            day = today - timedelta(days=13-i)
            activities[i] = Seance.objects.filter(formateur__isnull=False, date_debut=day).count()
        
        context['activite_formateurs'] = json.dumps(activities)
    
    except Exception as e:
        # En cas d'erreur ou si les modèles ne sont pas chargés
        context = {
            'apprenants_count': 0,
            'seances_count': 0,
            'cours_count': 0,
            'clients_count': 0,
            'formateurs_count': 0,
            'percentage_completed': 0,
            'upcoming_seances_count': 0,
            'upcoming_days': json.dumps([]),
            'upcoming_counts': json.dumps([]),
            'cours_mensuel': json.dumps([0] * 12),
            'seances_mensuel': json.dumps([0] * 12),
            'inscriptions_mensuel': json.dumps([0] * 12),
            'latest_inscriptions': [],
            'activite_formateurs': json.dumps([0] * 14)
        }
    
    return render(request, 'home.html', context)

def register_view(request):
    return redirect('formateurs:formateur-register', registration_key=settings.FORMATEUR_REGISTRATION_KEY)

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