from django import forms
from .models import Seance, Absence
from formateurs.models import Formateur
from django.core.exceptions import ValidationError

class SeanceForm(forms.ModelForm):
    formateurs = forms.ModelMultipleChoiceField(
        queryset=Formateur.objects.filter(statut='actif'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
        required=True,
        help_text="Sélectionnez au moins deux formateurs pour cette séance."
    )
    
    class Meta:
        model = Seance
        fields = [
            'lieu',
            'date',
            'cours',
            'formateurs',
            'nombre_places',
            'prix',
            'statut'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'lieu': forms.Select(attrs={'class': 'form-control'}),
            'cours': forms.Select(attrs={
                'class': 'form-control'
            }),
            'nombre_places': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'prix': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'statut': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'lieu': 'Lieu',
            'date': 'Date',
            'cours': 'Cours',
            'formateurs': 'Formateurs assignés',
            'nombre_places': 'Nombre de places',
            'prix': 'Prix',
            'statut': 'Statut'
        }
        help_texts = {
            'nombre_places': 'Nombre total de places disponibles',
            'prix': 'Prix par personne'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        
        if date_debut and date_fin and date_fin < date_debut:
            raise forms.ValidationError("La date de fin ne peut pas être antérieure à la date de début.")
        
        return cleaned_data

    def clean_formateurs(self):
        formateurs = self.cleaned_data.get('formateurs')
        if formateurs and len(formateurs) < 2:
            raise ValidationError("Vous devez sélectionner au moins deux formateurs pour chaque séance.")
        return formateurs 

class AbsenceForm(forms.ModelForm):
    class Meta:
        model = Absence
        fields = [
            'formateur_absent',
            'date_absence',
            'raison',
            'details',
            'formateur_remplacant'
        ]
        widgets = {
            'formateur_absent': forms.Select(attrs={'class': 'form-control'}),
            'date_absence': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'raison': forms.Select(attrs={'class': 'form-control'}),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Détails complémentaires sur l\'absence'
            }),
            'formateur_remplacant': forms.Select(attrs={'class': 'form-control'})
        }
        
    def __init__(self, *args, seance=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if seance:
            # Filtrer les formateurs absents possibles par ceux assignés à la séance
            self.fields['formateur_absent'].queryset = seance.formateurs.all()
            
            # Initialiser le champ seance qui n'est pas dans le formulaire
            self.instance.seance = seance
            
            # Filtrer les remplaçants possibles
            assigned_formateurs_ids = list(seance.formateurs.values_list('formateurid', flat=True))
            self.fields['formateur_remplacant'].queryset = Formateur.objects.filter(
                statut='actif'
            ).exclude(
                formateurid__in=assigned_formateurs_ids
            )
    
    def clean(self):
        cleaned_data = super().clean()
        formateur_absent = cleaned_data.get('formateur_absent')
        formateur_remplacant = cleaned_data.get('formateur_remplacant')
        
        # Vérifications de cohérence
        if formateur_absent and formateur_remplacant:
            if formateur_absent.formateurid == formateur_remplacant.formateurid:
                self.add_error('formateur_remplacant', "Le formateur remplaçant ne peut pas être le même que le formateur absent.")
        
        return cleaned_data 