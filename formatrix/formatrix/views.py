from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[('formateur', 'Formateur'), ('admin', 'Administrateur')],
        required=True
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "role")

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            # Définir is_staff en fonction du rôle choisi
            if form.cleaned_data['role'] == 'admin':
                user.is_staff = True
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form}) 