from django import forms
from django.core.validators import MinValueValidator
from .models import Cours

class CoursForm(forms.ModelForm):
    type_cours = forms.ChoiceField(
        choices=Cours.TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    horaire = forms.ChoiceField(
        choices=Cours.HORAIRE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    statut_approbation = forms.ChoiceField(
        choices=Cours.STATUT_APPROBATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    class Meta:
        model = Cours
        fields = [
            'nom_cours',
            'description',
            'niveau',
            'frais_par_participant',
            'duree_heures',
            'periode_mois',
            'type_cours',
            'objectifs',
            'prerequis',
            'materiel_requis',
            'horaire',
            'statut_approbation'
        ]
        widgets = {
            'nom_cours': forms.TextInput(attrs={
                'placeholder': 'Nom du cours',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Description détaillée du cours',
                'class': 'form-control'
            }),
            'niveau': forms.TextInput(attrs={
                'placeholder': 'Niveau requis',
                'class': 'form-control'
            }),
            'frais_par_participant': forms.NumberInput(attrs={
                'placeholder': 'Frais en Ariary',
                'class': 'form-control',
                'min': '0'
            }),
            'duree_heures': forms.NumberInput(attrs={
                'placeholder': 'Durée en heures',
                'class': 'form-control',
                'min': '1'
            }),
            'periode_mois': forms.NumberInput(attrs={
                'placeholder': 'Durée en mois',
                'class': 'form-control',
                'min': '1'
            }),
            'objectifs': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Objectifs du cours',
                'class': 'form-control'
            }),
            'prerequis': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Prérequis nécessaires',
                'class': 'form-control'
            }),
            'materiel_requis': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Matériel nécessaire',
                'class': 'form-control'
            }),
        }
        error_messages = {
            'nom_cours': {
                'required': 'Le nom du cours est obligatoire.',
                'max_length': 'Le nom du cours ne doit pas dépasser 200 caractères.'
            },
            'description': {
                'required': 'La description du cours est obligatoire.'
            },
            'niveau': {
                'required': 'Le niveau du cours est obligatoire.'
            },
            'duree_heures': {
                'required': 'La durée en heures est obligatoire.',
                'invalid': 'Veuillez entrer un nombre valide d\'heures.'
            },
            'type_cours': {
                'required': 'Le type de cours est obligatoire.'
            },
            'objectifs': {
                'required': 'Les objectifs du cours sont obligatoires.'
            },
            'horaire': {
                'required': 'L\'horaire est obligatoire.'
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configuration des champs obligatoires/optionnels
        self.fields['prerequis'].required = False
        self.fields['materiel_requis'].required = False
        self.fields['periode_mois'].required = False

        # Ajout des validateurs
        self.fields['duree_heures'].validators.append(MinValueValidator(1))
        self.fields['frais_par_participant'].validators.append(MinValueValidator(0))
        
        # Gestion du statut d'approbation
        if not self.instance.pk:  # Si c'est une création
            self.fields['statut_approbation'].initial = 'en_attente'
            self.fields['statut_approbation'].required = False

    def clean(self):
        cleaned_data = super().clean()
        type_cours = cleaned_data.get('type_cours')
        periode_mois = cleaned_data.get('periode_mois')
        duree_heures = cleaned_data.get('duree_heures')
        frais = cleaned_data.get('frais_par_participant')

        if type_cours == 'long' and not periode_mois:
            self.add_error('periode_mois', 'La période en mois est requise pour les cours longs')

        if duree_heures is not None and duree_heures <= 0:
            self.add_error('duree_heures', 'La durée doit être supérieure à 0')

        if frais is not None and frais < 0:
            self.add_error('frais_par_participant', 'Les frais ne peuvent pas être négatifs')

        return cleaned_data
