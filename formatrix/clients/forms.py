from django import forms
from .models import Client, TypeClient

class ClientForm(forms.ModelForm):
    # Remplacer le champ email du modèle par un champ CharField personnalisé
    email = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'exemple@email.com'})
    )
    
    class Meta:
        model = Client
        fields = ['nom_entite', 'sigle', 'secteur_activite', 'email', 'localite', 'ville', 
                 'numero_immatriculation', 'adresse_siege', 'telephone', 'site_web',
                 'typeclientid', 'personne_contact', 'fonction_contact', 'email_contact', 
                 'telephone_contact']
        labels = {
            'nom_entite': 'Nom de l\'entité',
            'sigle': 'Sigle/Acronyme',
            'secteur_activite': 'Secteur d\'activité',
            'email': 'Email',
            'localite': 'Localité',
            'ville': 'Ville',
            'numero_immatriculation': 'Numéro d\'immatriculation',
            'adresse_siege': 'Adresse du siège',
            'telephone': 'Téléphone',
            'site_web': 'Site web',
            'typeclientid': 'Type de client',
            'personne_contact': 'Personne de contact',
            'fonction_contact': 'Fonction',
            'email_contact': 'Email de contact',
            'telephone_contact': 'Téléphone de contact',
        }
        widgets = {
            'nom_entite': forms.TextInput(attrs={'class': 'form-control'}),
            'sigle': forms.TextInput(attrs={'class': 'form-control'}),
            'secteur_activite': forms.Select(attrs={'class': 'form-control'}),
            'localite': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_immatriculation': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse_siege': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'site_web': forms.URLInput(attrs={'class': 'form-control'}),
            'typeclientid': forms.Select(attrs={'class': 'form-control'}),
            'personne_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'fonction_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'email_contact': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone_contact': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def clean_email(self):
        """Valider que l'email est au bon format"""
        email = self.cleaned_data.get('email')
        if email:
            # Vérification simple du format email
            if '@' not in email or '.' not in email:
                raise forms.ValidationError("Veuillez entrer une adresse email valide.")
        return email
