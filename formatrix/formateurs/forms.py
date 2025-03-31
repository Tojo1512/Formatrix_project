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
                raise forms.ValidationError("A trainer with this email already exists.")
        return email

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            # Supprimer tous les caractères non numériques
            telephone = ''.join(filter(str.isdigit, telephone))
            # Vérifier la longueur
            if len(telephone) < 8 or len(telephone) > 15:
                raise forms.ValidationError("The phone number must contain between 8 and 15 digits.")
        return telephone

    def clean_date_naissance(self):
        date_naissance = self.cleaned_data.get('date_naissance')
        if date_naissance:
            from datetime import date
            age = (date.today() - date_naissance).days / 365.25
            if age < 18:
                raise forms.ValidationError("The trainer must be at least 18 years old.")
            if age > 70:
                raise forms.ValidationError("The age seems incorrect. Please verify the birth date.")
        return date_naissance

    def clean_date_embauche(self):
        date_embauche = self.cleaned_data.get('date_embauche')
        date_naissance = self.cleaned_data.get('date_naissance')
        if date_embauche and date_naissance:
            if date_embauche < date_naissance:
                raise forms.ValidationError("The hire date cannot be earlier than the birth date.")
        return date_embauche 