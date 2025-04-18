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
            'duree_heures',
            'type_cours',
            'objectifs',
            'prerequis',
            'materiel_requis',
            'horaire',
            'statut_approbation'
        ]
        widgets = {
            'nom_cours': forms.TextInput(attrs={
                'placeholder': 'Course name',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Detailed course description',
                'class': 'form-control'
            }),
            'niveau': forms.TextInput(attrs={
                'placeholder': 'Required level',
                'class': 'form-control'
            }),
            'duree_heures': forms.NumberInput(attrs={
                'placeholder': 'Duration in hours',
                'class': 'form-control',
                'min': '1'
            }),
            'objectifs': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Course objectives',
                'class': 'form-control'
            }),
            'prerequis': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Necessary prerequisites',
                'class': 'form-control'
            }),
            'materiel_requis': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Required materials',
                'class': 'form-control'
            }),
            'formateurs': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'placeholder': 'Select trainers'
            }),
        }
        error_messages = {
            'nom_cours': {
                'required': 'Course name is required.',
                'max_length': 'Course name must not exceed 200 characters.'
            },
            'description': {
                'required': 'Course description is required.'
            },
            'niveau': {
                'required': 'Course level is required.'
            },
            'duree_heures': {
                'required': 'Duration in hours is required.',
                'invalid': 'Please enter a valid number of hours.'
            },
            'type_cours': {
                'required': 'Course type is required.'
            },
            'objectifs': {
                'required': 'Course objectives are required.'
            },
            'horaire': {
                'required': 'Schedule is required.'
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configuration of required/optional fields
        self.fields['prerequis'].required = False
        self.fields['materiel_requis'].required = False

        # Add validators
        self.fields['duree_heures'].validators.append(MinValueValidator(1))
        
        # Approval status management
        if not self.instance.pk:  # If it's a creation
            self.fields['statut_approbation'].initial = 'en_attente'
            self.fields['statut_approbation'].required = False

    def clean(self):
        cleaned_data = super().clean()
        duree_heures = cleaned_data.get('duree_heures')

        if duree_heures is not None and duree_heures <= 0:
            self.add_error('duree_heures', 'Duration must be greater than 0')

        return cleaned_data
