from django import forms
from .models import Formateur

class FormateurForm(forms.ModelForm):
    class Meta:
        model = Formateur
        fields = [
            'nom', 'prenom', 'email', 'telephone', 'date_naissance',
            'adresse', 'ville', 'specialites', 'niveau_expertise',
            'type_formateur', 'cv', 'photo', 'date_embauche',
            'statut', 'disponibilite', 'notes'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'specialites': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'niveau_expertise': forms.Select(attrs={'class': 'form-control'}),
            'type_formateur': forms.Select(attrs={'class': 'form-control'}),
            'cv': forms.FileInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'disponibilite': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if Formateur.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("Un formateur avec cet email existe déjà.")
        return email

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            # Supprimer tous les caractères non numériques
            telephone = ''.join(filter(str.isdigit, telephone))
            # Vérifier la longueur
            if len(telephone) < 8 or len(telephone) > 15:
                raise forms.ValidationError("Le numéro de téléphone doit contenir entre 8 et 15 chiffres.")
        return telephone

    def clean_date_naissance(self):
        date_naissance = self.cleaned_data.get('date_naissance')
        if date_naissance:
            from datetime import date
            age = (date.today() - date_naissance).days / 365.25
            if age < 18:
                raise forms.ValidationError("Le formateur doit avoir au moins 18 ans.")
            if age > 70:
                raise forms.ValidationError("L'âge semble incorrect. Veuillez vérifier la date de naissance.")
        return date_naissance

    def clean_date_embauche(self):
        date_embauche = self.cleaned_data.get('date_embauche')
        date_naissance = self.cleaned_data.get('date_naissance')
        if date_embauche and date_naissance:
            if date_embauche < date_naissance:
                raise forms.ValidationError("La date d'embauche ne peut pas être antérieure à la date de naissance.")
        return date_embauche 