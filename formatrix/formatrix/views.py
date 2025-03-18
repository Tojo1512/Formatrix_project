from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.conf import settings

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[('trainer', 'Trainer'), ('admin', 'Administrator')],
        required=True
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "role")

def home_view(request):
    return render(request, 'home.html')

def register_view(request):
    return redirect('formateurs:formateur-register', registration_key=settings.FORMATEUR_REGISTRATION_KEY)