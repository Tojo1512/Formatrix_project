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
            # Le widget email est défini directement dans le champ personnalisé ci-dessus
            'localite': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_immatriculation': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse_rue': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'typeclientid': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def clean_email(self):
        """Valider que l'email est au bon format"""
        email = self.cleaned_data.get('email')
        if email:
            # Vérification simple du format email
            if '@' not in email or '.' not in email:
                raise forms.ValidationError("Veuillez entrer une adresse email valide.")
        return email
