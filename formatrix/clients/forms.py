from django import forms
from .models import Client, TypeClient

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nomclient', 'autresnom', 'email', 'localite', 'ville', 
                 'numero_immatriculation', 'adresse_rue', 'telephone', 'typeclientid']
        labels = {
            'nomclient': 'Nom du client',
            'autresnom': 'Autres noms',
            'email': 'Email',
            'localite': 'Localité',
            'ville': 'Ville',
            'numero_immatriculation': 'Numéro d\'immatriculation',
            'adresse_rue': 'Adresse',
            'telephone': 'Téléphone',
            'typeclientid': 'Type de client',
        }
        widgets = {
            'nomclient': forms.TextInput(attrs={'class': 'form-control'}),
            'autresnom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'localite': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_immatriculation': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse_rue': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'typeclientid': forms.Select(attrs={'class': 'form-control'}),
        }
