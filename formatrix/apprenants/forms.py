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
            'nom_apprenant': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'apprenant'}),
            'autres_nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Autres noms'}),
            'cin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro CIN'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'adresse_rue': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse'}),
            'localite': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Localité'}),
            'ville': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville'}),
            'type_apprenant': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type d\'apprenant'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'niveau_academique': forms.Select(attrs={'class': 'form-control'}),
            'categorie_age': forms.Select(attrs={'class': 'form-control'}),
            'besoins_speciaux': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Besoins spéciaux (si applicable)'}),
            'contact_urgence': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Personne à contacter en cas d\'urgence'}),
            'telephone_urgence': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone d\'urgence'})
        }
