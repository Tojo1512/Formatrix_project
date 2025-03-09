from django import forms
from .models import Lieu

class LieuForm(forms.ModelForm):
    lieu = forms.CharField(
        label='Location name',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    adresse = forms.CharField(
        label='Address',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    personne_contact = forms.CharField(
        label='Contact person',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telephone = forms.CharField(
        label='Phone',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mobile = forms.CharField(
        label='Mobile',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Lieu
        fields = ['lieu', 'adresse', 'personne_contact', 'telephone', 'mobile'] 