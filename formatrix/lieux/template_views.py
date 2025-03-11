from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from .models import Lieu
from .forms import LieuForm

class LieuCreateView(LoginRequiredMixin, CreateView):
    model = Lieu
    form_class = LieuForm
    template_name = 'lieux/lieu_form.html'
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('seance-list')

class LieuUpdateView(LoginRequiredMixin, UpdateView):
    model = Lieu
    form_class = LieuForm
    template_name = 'lieux/lieu_form.html'
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('seance-list') 