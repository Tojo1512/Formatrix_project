from django import forms
from .models import Apprenant

class ApprenantForm(forms.ModelForm):
    class Meta:
        model = Apprenant
        fields = [
            'nom_apprenant', 'autres_nom', 'cin', 'date_naissance', 
            'adresse_rue', 'localite', 'ville', 'type_apprenant', 
            'sexe', 'niveau_academique', 'categorie_age', 
            'besoins_speciaux', 'contact_urgence', 'telephone_urgence'
        ]
        widgets = {
            'nom_apprenant': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Learner\'s name'}),
            'autres_nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Other names'}),
            'cin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID number'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'adresse_rue': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'localite': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'ville': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'type_apprenant': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Learner type'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'niveau_academique': forms.Select(attrs={'class': 'form-control'}),
            'categorie_age': forms.Select(attrs={'class': 'form-control'}),
            'besoins_speciaux': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Special needs (if applicable)'}),
            'contact_urgence': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency contact person'}),
            'telephone_urgence': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency phone number'})
        }
