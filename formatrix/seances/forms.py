from django import forms
from .models import Seance

class SeanceForm(forms.ModelForm):
    class Meta:
        model = Seance
        fields = [
            'lieu',
            'date',
            'cours',
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