from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.db import transaction
from decimal import Decimal

from .models import Paiement, PaiementFormateur, PlanPaiement, Facture, LigneFacture
from .forms import PaiementForm, PaiementFormateurForm, CalculPaiementFormateurForm, PlanPaiementForm, FactureForm, LigneFactureForm, GenerationFactureForm
from inscriptions.models import Inscription
from formateurs.models import Formateur
from seances.models import Seance

import os
import csv
import json
import datetime
from io import BytesIO

# Import conditionnel de WeasyPrint
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False

# Import de ReportLab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

# Create your views here.

class PaiementListView(LoginRequiredMixin, ListView):
    model = Paiement
    template_name = 'paiements/paiement_list.html'
    context_object_name = 'paiements'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtres
        statut = self.request.GET.get('statut', '')
        if statut:
            queryset = queryset.filter(statut=statut)
            
        mode = self.request.GET.get('mode', '')
        if mode:
            queryset = queryset.filter(mode_paiement=mode)
            
        date_debut = self.request.GET.get('date_debut', '')
        if date_debut:
            queryset = queryset.filter(date_paiement__gte=date_debut)
            
        date_fin = self.request.GET.get('date_fin', '')
        if date_fin:
            queryset = queryset.filter(date_paiement__lte=date_fin)
            
        en_retard = self.request.GET.get('en_retard', '')
        if en_retard == 'oui':
            queryset = queryset.filter(
                statut='en_attente',
                date_echeance__lt=timezone.now().date()
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques
        context['total_recus'] = Paiement.objects.filter(statut='recu').aggregate(total=Sum('montant'))['total'] or 0
        context['total_en_attente'] = Paiement.objects.filter(statut='en_attente').aggregate(total=Sum('montant'))['total'] or 0
        context['total_en_retard'] = Paiement.objects.filter(
            statut='en_attente',
            date_echeance__lt=timezone.now().date()
        ).aggregate(total=Sum('montant'))['total'] or 0
        
        # Filtres actifs
        context['filtres'] = {
            'statut': self.request.GET.get('statut', ''),
            'mode': self.request.GET.get('mode', ''),
            'date_debut': self.request.GET.get('date_debut', ''),
            'date_fin': self.request.GET.get('date_fin', ''),
            'en_retard': self.request.GET.get('en_retard', ''),
        }
        
        return context


class PaiementDetailView(LoginRequiredMixin, DetailView):
    model = Paiement
    template_name = 'paiements/paiement_detail.html'
    context_object_name = 'paiement'
    pk_url_kwarg = 'paiement_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PaiementCreateView(LoginRequiredMixin, CreateView):
    model = Paiement
    template_name = 'paiements/paiement_form.html'
    form_class = PaiementForm
    
    def get_success_url(self):
        return reverse_lazy('paiements:paiement-detail', kwargs={'paiement_id': self.object.paiement_id})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pré-remplir l'inscription si fournie dans l'URL
        inscription_id = self.request.GET.get('inscription_id')
        if inscription_id:
            kwargs['inscription_id'] = inscription_id
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Vérifier s'il y a des inscriptions disponibles
        inscriptions_count = Inscription.objects.count()
        context['inscriptions_count'] = inscriptions_count
        return context
    
    def form_valid(self, form):
        try:
            # Afficher les données du formulaire pour le débogage
            messages.success(self.request, 'Paiement créé avec succès.')
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Erreur lors de la création du paiement: {e}")
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, f"Le formulaire contient des erreurs: {form.errors}")
        return super().form_invalid(form)


class PaiementUpdateView(LoginRequiredMixin, UpdateView):
    model = Paiement
    template_name = 'paiements/paiement_form.html'
    form_class = PaiementForm
    pk_url_kwarg = 'paiement_id'
    
    def get_success_url(self):
        return reverse_lazy('paiements:paiement-detail', kwargs={'paiement_id': self.object.paiement_id})
    
    def get(self, request, *args, **kwargs):
        # Vérifier si l'action est de marquer le paiement comme payé
        if request.GET.get('action') == 'payer':
            paiement = self.get_object()
            paiement.statut = 'recu'
            paiement.date_paiement = timezone.now().date()
            paiement.save()
            messages.success(request, 'Le paiement a été marqué comme reçu.')
            return redirect('paiements:paiement-detail', paiement_id=paiement.paiement_id)
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Paiement mis à jour avec succès.')
        return super().form_valid(form)


class PlanPaiementListView(LoginRequiredMixin, ListView):
    model = PlanPaiement
    template_name = 'paiements/plan_paiement_list.html'
    context_object_name = 'plans'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtres
        statut = self.request.GET.get('statut', '')
        if statut:
            queryset = queryset.filter(statut=statut)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques
        context['total_plans'] = PlanPaiement.objects.count()
        context['plans_actifs'] = PlanPaiement.objects.filter(statut='actif').count()
        context['plans_completes'] = PlanPaiement.objects.filter(statut='complete').count()
        
        return context


class PlanPaiementDetailView(LoginRequiredMixin, DetailView):
    model = PlanPaiement
    template_name = 'paiements/plan_paiement_detail.html'
    context_object_name = 'plan'
    pk_url_kwarg = 'plan_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['echeancier'] = self.object.generer_echeancier()
        context['paiements'] = self.object.inscription.paiements.all().order_by('-date_paiement')
        return context


class PlanPaiementCreateView(LoginRequiredMixin, CreateView):
    model = PlanPaiement
    template_name = 'paiements/plan_paiement_form.html'
    fields = ['inscription', 'montant_total', 'nombre_versements', 'date_debut', 'intervalle_jours', 'commentaires']
    
    def get_success_url(self):
        return reverse_lazy('paiements:plan-detail', kwargs={'plan_id': self.object.plan_id})
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Pré-remplir l'inscription si fournie dans l'URL
        inscription_id = self.request.GET.get('inscription_id')
        if inscription_id:
            try:
                form.fields['inscription'].initial = Inscription.objects.get(inscription_id=inscription_id)
                # Pré-remplir le montant total avec le coût de la séance
                if hasattr(inscription, 'seance') and hasattr(inscription.seance, 'cours'):
                    form.fields['montant_total'].initial = inscription.seance.cours.cout_formation
            except Inscription.DoesNotExist:
                pass
        return form
    
    def form_valid(self, form):
        messages.success(self.request, 'Plan de paiement créé avec succès.')
        return super().form_valid(form)


class PlanPaiementUpdateView(LoginRequiredMixin, UpdateView):
    model = PlanPaiement
    template_name = 'paiements/plan_paiement_form.html'
    fields = ['montant_total', 'nombre_versements', 'date_debut', 'intervalle_jours', 'statut', 'commentaires']
    pk_url_kwarg = 'plan_id'
    
    def get_success_url(self):
        return reverse_lazy('paiements:plan-detail', kwargs={'plan_id': self.object.plan_id})
    
    def form_valid(self, form):
        messages.success(self.request, 'Plan de paiement mis à jour avec succès.')
        return super().form_valid(form)


class PaiementFormateurListView(LoginRequiredMixin, ListView):
    model = PaiementFormateur
    template_name = 'paiements/paiement_formateur_list.html'
    context_object_name = 'paiements_formateurs'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtres
        statut = self.request.GET.get('statut', '')
        if statut:
            queryset = queryset.filter(statut=statut)
            
        formateur_id = self.request.GET.get('formateur_id', '')
        if formateur_id:
            queryset = queryset.filter(formateur__formateur_id=formateur_id)
            
        date_debut = self.request.GET.get('date_debut', '')
        if date_debut:
            queryset = queryset.filter(date_paiement__gte=date_debut)
            
        date_fin = self.request.GET.get('date_fin', '')
        if date_fin:
            queryset = queryset.filter(date_paiement__lte=date_fin)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques
        context['total_paiements'] = self.model.objects.count()
        context['montant_total'] = self.model.objects.aggregate(total=Sum('montant'))['total'] or 0
        context['paiements_en_attente'] = self.model.objects.filter(statut='en_attente').count()
        context['montant_en_attente'] = self.model.objects.filter(statut='en_attente').aggregate(total=Sum('montant'))['total'] or 0
        
        # Formateurs pour le filtre
        context['formateurs'] = Formateur.objects.all().order_by('nom', 'prenom')
        
        return context


class PaiementFormateurDetailView(LoginRequiredMixin, DetailView):
    model = PaiementFormateur
    template_name = 'paiements/paiement_formateur_detail.html'
    context_object_name = 'paiement'
    pk_url_kwarg = 'paiement_formateur_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter les séances associées à la période de paiement
        formateur = self.object.formateur
        context['seances'] = formateur.seances.filter(
            date_seance__gte=self.object.periode_debut,
            date_seance__lte=self.object.periode_fin
        ).order_by('date_seance')
        return context


class PaiementFormateurCreateView(LoginRequiredMixin, CreateView):
    model = PaiementFormateur
    template_name = 'paiements/paiement_formateur_form.html'
    form_class = PaiementFormateurForm
    
    def get_success_url(self):
        return reverse_lazy('paiements:paiement-formateur-detail', kwargs={'paiement_formateur_id': self.object.paiement_formateur_id})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        formateur_id = self.request.GET.get('formateur_id')
        if formateur_id:
            kwargs['formateur_id'] = formateur_id
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        # Définir la période par défaut (mois en cours)
        today = timezone.now().date()
        initial['periode_debut'] = today.replace(day=1)  # Premier jour du mois
        if today.month == 12:
            initial['periode_fin'] = today.replace(year=today.year + 1, month=1, day=1).replace(day=1) - timezone.timedelta(days=1)
        else:
            initial['periode_fin'] = today.replace(month=today.month + 1, day=1) - timezone.timedelta(days=1)
        return initial
    
    def form_valid(self, form):
        messages.success(self.request, "Le paiement au formateur a été créé avec succès.")
        return super().form_valid(form)


class PaiementFormateurUpdateView(LoginRequiredMixin, UpdateView):
    model = PaiementFormateur
    template_name = 'paiements/paiement_formateur_form.html'
    form_class = PaiementFormateurForm
    pk_url_kwarg = 'paiement_formateur_id'
    
    def get_success_url(self):
        return reverse_lazy('paiements:paiement-formateur-detail', kwargs={'paiement_formateur_id': self.object.paiement_formateur_id})
    
    def form_valid(self, form):
        messages.success(self.request, "Le paiement au formateur a été mis à jour avec succès.")
        return super().form_valid(form)


@login_required
def calculer_heures_formateur(request, formateur_id):
    """Vue pour calculer les heures travaillées par un formateur sur une période donnée."""
    formateur = get_object_or_404(Formateur, formateur_id=formateur_id)
    
    if request.method == 'POST':
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        
        if date_debut and date_fin:
            # Récupérer les séances du formateur dans la période
            seances = formateur.seances.filter(
                date_seance__gte=date_debut,
                date_seance__lte=date_fin
            ).order_by('date_seance')
            
            # Calculer le nombre total d'heures
            total_heures = sum(seance.duree.total_seconds() / 3600 for seance in seances)
            
            # Créer un nouveau paiement pré-rempli
            return redirect(
                f"{reverse_lazy('paiements:paiement-formateur-create')}?formateur_id={formateur_id}"
                f"&periode_debut={date_debut}&periode_fin={date_fin}&heures_travaillees={total_heures:.2f}"
            )
        else:
            messages.error(request, "Veuillez spécifier une période valide.")
    
    # Afficher le formulaire de calcul
    return render(request, 'paiements/calculer_heures_formateur.html', {
        'formateur': formateur
    })


@login_required
def tableau_bord_paiements(request):
    """Vue pour le tableau de bord des paiements."""
    
    # Statistiques générales
    total_recus = Paiement.objects.filter(statut='recu').aggregate(total=Sum('montant'))['total'] or 0
    total_en_attente = Paiement.objects.filter(statut='en_attente').aggregate(total=Sum('montant'))['total'] or 0
    total_en_retard = Paiement.objects.filter(
        statut='en_attente',
        date_echeance__lt=timezone.now().date()
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Paiements récents
    paiements_recents = Paiement.objects.all().order_by('-date_paiement')[:5]
    
    # Paiements en retard
    paiements_en_retard = Paiement.objects.filter(
        statut='en_attente',
        date_echeance__lt=timezone.now().date()
    ).order_by('date_echeance')[:10]
    
    # Paiements à venir
    paiements_a_venir = Paiement.objects.filter(
        statut='en_attente',
        date_echeance__gte=timezone.now().date()
    ).order_by('date_echeance')[:10]
    
    context = {
        'total_recus': total_recus,
        'total_en_attente': total_en_attente,
        'total_en_retard': total_en_retard,
        'paiements_recents': paiements_recents,
        'paiements_en_retard': paiements_en_retard,
        'paiements_a_venir': paiements_a_venir,
    }
    
    return render(request, 'paiements/tableau_bord.html', context)

# Vues pour la gestion des factures
class FactureListView(LoginRequiredMixin, ListView):
    """Vue pour afficher la liste des factures."""
    model = Facture
    template_name = 'paiements/facture_list.html'
    context_object_name = 'factures'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Facture.objects.all().order_by('-date_emission')
        
        # Filtrage par statut
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        # Filtrage par type de facture
        type_facture = self.request.GET.get('type_facture')
        if type_facture:
            queryset = queryset.filter(type_facture=type_facture)
        
        # Filtrage par date d'émission
        date_debut = self.request.GET.get('date_debut')
        if date_debut:
            queryset = queryset.filter(date_emission__gte=date_debut)
        
        date_fin = self.request.GET.get('date_fin')
        if date_fin:
            queryset = queryset.filter(date_emission__lte=date_fin)
        
        # Recherche par numéro de facture ou destinataire
        recherche = self.request.GET.get('recherche')
        if recherche:
            queryset = queryset.filter(
                Q(numero_facture__icontains=recherche) |
                Q(destinataire_nom__icontains=recherche) |
                Q(destinataire_email__icontains=recherche)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques
        context['total_factures'] = Facture.objects.count()
        context['total_montant'] = Facture.objects.aggregate(total=Sum('montant_ttc'))['total'] or 0
        
        # Ajouter les choices au contexte pour les templates
        context['statut_choices'] = Facture.STATUS_CHOICES
        context['type_facture_choices'] = Facture.INVOICE_TYPE_CHOICES
        
        # Factures par statut
        statuts = dict(Facture.STATUS_CHOICES)
        stats_statut = []
        for code, label in statuts.items():
            count = Facture.objects.filter(statut=code).count()
            montant = Facture.objects.filter(statut=code).aggregate(total=Sum('montant_ttc'))['total'] or 0
            stats_statut.append({
                'code': code,
                'label': label,
                'count': count,
                'montant': montant
            })
        context['stats_statut'] = stats_statut
        
        # Factures par type
        types = dict(Facture.INVOICE_TYPE_CHOICES)
        stats_type = []
        for code, label in types.items():
            count = Facture.objects.filter(type_facture=code).count()
            montant = Facture.objects.filter(type_facture=code).aggregate(total=Sum('montant_ttc'))['total'] or 0
            stats_type.append({
                'code': code,
                'label': label,
                'count': count,
                'montant': montant
            })
        context['stats_type'] = stats_type
        
        # Paramètres de filtrage
        context['filtres'] = {
            'statut': self.request.GET.get('statut', ''),
            'type_facture': self.request.GET.get('type_facture', ''),
            'date_debut': self.request.GET.get('date_debut', ''),
            'date_fin': self.request.GET.get('date_fin', ''),
            'recherche': self.request.GET.get('recherche', '')
        }
        
        return context


class FactureDetailView(LoginRequiredMixin, DetailView):
    """Vue pour afficher les détails d'une facture."""
    model = Facture
    template_name = 'paiements/facture_detail.html'
    context_object_name = 'facture'
    pk_url_kwarg = 'facture_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        facture = self.get_object()
        context['lignes'] = LigneFacture.objects.filter(facture=facture)
        
        # Récupérer l'inscription associée si elle existe
        if facture.inscription:
            context['inscription'] = facture.inscription
        
        return context


class FactureCreateView(LoginRequiredMixin, CreateView):
    """Vue pour créer une nouvelle facture."""
    model = Facture
    form_class = FactureForm
    template_name = 'paiements/facture_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = 'Nouvelle facture'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Facture créée avec succès.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('paiements:facture-detail', kwargs={'facture_id': self.object.facture_id})

class FactureUpdateView(LoginRequiredMixin, UpdateView):
    """Vue pour modifier une facture existante."""
    model = Facture
    form_class = FactureForm
    template_name = 'paiements/facture_form.html'
    pk_url_kwarg = 'facture_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = f'Modifier la facture {self.object.numero_facture}'
        return context
    
    def get_success_url(self):
        return reverse('paiements:facture-detail', kwargs={'facture_id': self.object.facture_id})

@login_required
def ajouter_ligne_facture(request, facture_id):
    facture = get_object_or_404(Facture, facture_id=facture_id)
    
    if request.method == 'POST':
        form = LigneFactureForm(request.POST)
        if form.is_valid():
            ligne = form.save(commit=False)
            ligne.facture = facture
            ligne.save()
            
            # Mettre à jour les montants de la facture
            facture.recalculer_montants()
            
            messages.success(request, 'Ligne ajoutée avec succès à la facture.')
            return redirect('paiements:facture-detail', facture_id=facture.facture_id)
    else:
        # Pré-remplir le taux de TVA avec celui de la facture
        form = LigneFactureForm(initial={'taux_tva': facture.taux_tva})
    
    return render(request, 'paiements/ligne_facture_form.html', {
        'form': form,
        'facture': facture
    })

@login_required
def supprimer_ligne_facture(request, ligne_id):
    ligne = get_object_or_404(LigneFacture, ligne_id=ligne_id)
    facture = ligne.facture
    
    if request.method == 'POST':
        ligne.delete()
        
        # Mettre à jour les montants de la facture
        facture.recalculer_montants()
        
        messages.success(request, 'Ligne supprimée avec succès.')
        return redirect('paiements:facture-detail', facture_id=facture.facture_id)
    
    return redirect('paiements:facture-detail', facture_id=facture.facture_id)

@login_required
def generer_facture(request):
    if request.method == 'POST':
        form = GenerationFactureForm(request.POST)
        if form.is_valid():
            inscription_id = form.cleaned_data['inscription'].inscription_id
            inscription = form.cleaned_data['inscription']
            type_facture = form.cleaned_data['type_facture']
            statut_initial = form.cleaned_data['statut_initial']
            montant_ht = form.cleaned_data['montant_ht']
            taux_tva = form.cleaned_data['taux_tva']
            generer_pdf = form.cleaned_data['generer_pdf']
            
            try:
                # Générer la facture
                facture = Facture.generer_facture_pour_inscription(
                    inscription_id=inscription_id,
                    statut=statut_initial
                )
                
                # Mettre à jour les montants et le taux de TVA
                facture.montant_ht = montant_ht
                facture.taux_tva = taux_tva
                facture.montant_tva = montant_ht * (taux_tva / Decimal('100.0')) if taux_tva > 0 else Decimal('0.0')
                facture.montant_ttc = facture.montant_ht + facture.montant_tva
                
                # Si le type de facture est spécifié et différent de celui déterminé automatiquement
                if type_facture and type_facture != facture.type_facture:
                    facture.type_facture = type_facture
                
                facture.save()
                
                # Mettre à jour la ligne de facture existante ou en créer une nouvelle
                lignes = LigneFacture.objects.filter(facture__facture_id=facture.facture_id)
                if lignes.exists():
                    ligne = lignes.first()
                    ligne.prix_unitaire_ht = montant_ht
                    ligne.taux_tva = taux_tva
                    ligne.montant_ht = montant_ht
                    ligne.montant_tva = montant_ht * (taux_tva / Decimal('100.0')) if taux_tva > 0 else Decimal('0.0')
                    ligne.montant_ttc = ligne.montant_ht + ligne.montant_tva
                    ligne.save()
                else:
                    # Créer une ligne de facture par défaut
                    LigneFacture.objects.create(
                        facture=facture,
                        description=f"Formation: {inscription.seance.cours.nom_cours}",
                        quantite=1,
                        prix_unitaire_ht=montant_ht,
                        taux_tva=taux_tva,
                        montant_ht=montant_ht,
                        montant_tva=montant_ht * (taux_tva / Decimal('100.0')) if taux_tva > 0 else Decimal('0.0'),
                        montant_ttc=montant_ht + (montant_ht * (taux_tva / Decimal('100.0')) if taux_tva > 0 else Decimal('0.0'))
                    )
                
                messages.success(request, f'Facture {facture.numero_facture} générée avec succès.')
                
                # Générer le PDF si demandé
                if generer_pdf:
                    # La génération du PDF est gérée par la vue telecharger_facture_pdf
                    # Nous redirigeons simplement vers cette vue
                    return redirect('paiements:facture-pdf', facture_id=facture.facture_id)
                
                return redirect('paiements:facture-detail', facture_id=facture.facture_id)
            
            except Exception as e:
                messages.error(request, f'Erreur lors de la génération de la facture: {str(e)}')
    else:
        form = GenerationFactureForm()
    
    return render(request, 'paiements/generer_facture.html', {
        'form': form,
        'titre': 'Generate Invoice'
    })

@login_required
def telecharger_facture_pdf(request, facture_id):
    """Vue pour télécharger une facture au format PDF en utilisant ReportLab."""
    try:
        # Récupérer la facture
        facture = None
        for f in Facture.objects.all():
            if str(f.facture_id) == str(facture_id):
                facture = f
                break
        
        if not facture:
            messages.error(request, "La facture n'existe pas.")
            return redirect('paiements:facture-list')
        
        # Récupérer les lignes de facture
        lignes = []
        for ligne in LigneFacture.objects.all():
            if hasattr(ligne, 'facture') and ligne.facture and str(ligne.facture.facture_id) == str(facture_id):
                lignes.append(ligne)
        
        # Créer un buffer pour le PDF
        buffer = BytesIO()
        
        # Créer le document PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Contenu du PDF
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        subtitle_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # En-tête
        elements.append(Paragraph(f"FACTURE #{facture.numero_facture}", title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Informations de la facture
        elements.append(Paragraph(f"Date d'émission: {facture.date_emission.strftime('%d/%m/%Y')}", normal_style))
        elements.append(Paragraph(f"Date d'échéance: {facture.date_echeance.strftime('%d/%m/%Y')}", normal_style))
        elements.append(Paragraph(f"Statut: {facture.get_statut_display()}", normal_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Informations du destinataire
        elements.append(Paragraph("Destinataire:", subtitle_style))
        elements.append(Paragraph(facture.destinataire_nom, normal_style))
        elements.append(Paragraph(facture.destinataire_adresse, normal_style))
        elements.append(Paragraph(f"Email: {facture.destinataire_email}", normal_style))
        elements.append(Paragraph(f"Téléphone: {facture.destinataire_telephone or 'Non spécifié'}", normal_style))
        if facture.destinataire_siret:
            elements.append(Paragraph(f"SIRET: {facture.destinataire_siret}", normal_style))
        elements.append(Spacer(1, 1*cm))
        
        # Tableau des lignes de facture
        data = [['Description', 'Quantité', 'Prix unitaire HT', 'TVA', 'Montant HT', 'Montant TTC']]
        
        for ligne in lignes:
            data.append([
                ligne.description,
                str(ligne.quantite),
                f"{ligne.prix_unitaire_ht} €",
                f"{ligne.taux_tva} %",
                f"{ligne.montant_ht} €",
                f"{ligne.montant_ttc} €"
            ])
        
        # Ajouter les totaux
        data.append(['', '', '', '', 'Total HT:', f"{facture.montant_ht} €"])
        data.append(['', '', '', '', 'TVA:', f"{facture.montant_tva} €"])
        data.append(['', '', '', '', 'Total TTC:', f"{facture.montant_ttc} €"])
        
        # Créer le tableau
        table = Table(data, colWidths=[6*cm, 2*cm, 2.5*cm, 2*cm, 2.5*cm, 2.5*cm])
        
        # Style du tableau
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -4), colors.white),
            ('BACKGROUND', (4, -3), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ])
        
        table.setStyle(table_style)
        elements.append(table)
        elements.append(Spacer(1, 1*cm))
        
        # Notes et conditions de paiement
        if facture.notes:
            elements.append(Paragraph("Notes:", subtitle_style))
            elements.append(Paragraph(facture.notes, normal_style))
            elements.append(Spacer(1, 0.5*cm))
        
        if facture.conditions_paiement:
            elements.append(Paragraph("Conditions de paiement:", subtitle_style))
            elements.append(Paragraph(facture.conditions_paiement, normal_style))
        
        # Générer le PDF
        doc.build(elements)
        
        # Récupérer le contenu du PDF
        pdf = buffer.getvalue()
        buffer.close()
        
        # Créer la réponse HTTP avec le PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{facture.numero_facture}.pdf"'
        response.write(pdf)
        
        # Retourner le PDF généré
        return response
    except Exception as e:
        messages.error(request, f"Erreur lors de la génération du PDF: {str(e)}")
        return redirect('paiements:facture-detail', facture_id=facture_id)

@login_required
def envoyer_facture_email(request, facture_id):
    facture = get_object_or_404(Facture, facture_id=facture_id)
    
    if not facture.destinataire_email:
        messages.error(request, "Impossible d'envoyer la facture : aucune adresse email n'est spécifiée pour le destinataire.")
        return redirect('paiements:facture-detail', facture_id=facture.facture_id)
    
    try:
        sujet = f'Facture {facture.numero_facture} - Formatrix'
        message = f"""
        Bonjour,
        
        Veuillez trouver ci-joint votre facture {facture.numero_facture}.
        
        Montant total : {facture.montant_ttc} €
        
        Pour toute question concernant cette facture, n'hésitez pas à nous contacter.
        
        Cordialement,
        L'équipe Formatrix
        """
        
        email = EmailMessage(
            subject=sujet,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[facture.destinataire_email]
        )
        
        # Générer le PDF en utilisant ReportLab
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        subtitle_style = styles['Heading2']
        normal_style = styles['Normal']
        
        elements.append(Paragraph(f"FACTURE #{facture.numero_facture}", title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        elements.append(Paragraph(f"Date d'émission: {facture.date_emission.strftime('%d/%m/%Y')}", normal_style))
        elements.append(Paragraph(f"Date d'échéance: {facture.date_echeance.strftime('%d/%m/%Y')}", normal_style))
        elements.append(Paragraph(f"Statut: {facture.get_statut_display()}", normal_style))
        elements.append(Spacer(1, 0.5*cm))
        
        elements.append(Paragraph("Destinataire:", subtitle_style))
        elements.append(Paragraph(facture.destinataire_nom, normal_style))
        elements.append(Paragraph(facture.destinataire_adresse, normal_style))
        elements.append(Paragraph(f"Email: {facture.destinataire_email}", normal_style))
        elements.append(Paragraph(f"Téléphone: {facture.destinataire_telephone or 'Non spécifié'}", normal_style))
        if facture.destinataire_siret:
            elements.append(Paragraph(f"SIRET: {facture.destinataire_siret}", normal_style))
        elements.append(Spacer(1, 1*cm))
        
        lignes = LigneFacture.objects.filter(facture=facture)
        data = [['Description', 'Quantité', 'Prix unitaire HT', 'TVA', 'Montant HT', 'Montant TTC']]
        
        for ligne in lignes:
            data.append([
                ligne.description,
                str(ligne.quantite),
                f"{ligne.prix_unitaire_ht} €",
                f"{ligne.taux_tva} %",
                f"{ligne.montant_ht} €",
                f"{ligne.montant_ttc} €"
            ])
        
        data.append(['', '', '', '', 'Total HT:', f"{facture.montant_ht} €"])
        data.append(['', '', '', '', 'TVA:', f"{facture.montant_tva} €"])
        data.append(['', '', '', '', 'Total TTC:', f"{facture.montant_ttc} €"])
        
        table = Table(data, colWidths=[6*cm, 2*cm, 2.5*cm, 2*cm, 2.5*cm, 2.5*cm])
        
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -4), colors.white),
            ('BACKGROUND', (4, -3), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ])
        
        table.setStyle(table_style)
        elements.append(table)
        elements.append(Spacer(1, 1*cm))
        
        if facture.notes:
            elements.append(Paragraph("Notes:", subtitle_style))
            elements.append(Paragraph(facture.notes, normal_style))
            elements.append(Spacer(1, 0.5*cm))
        
        if facture.conditions_paiement:
            elements.append(Paragraph("Conditions de paiement:", subtitle_style))
            elements.append(Paragraph(facture.conditions_paiement, normal_style))
        
        doc.build(elements)
        
        pdf = buffer.getvalue()
        buffer.close()
        
        email.attach(f'facture_{facture.numero_facture}.pdf', pdf, 'application/pdf')
        
        email.send()
        
        if facture.statut == 'brouillon':
            facture.statut = 'emise'
            facture.save()
        
        messages.success(request, f'Facture envoyée avec succès à {facture.destinataire_email}.')
    
    except Exception as e:
        messages.error(request, f"Erreur lors de l'envoi de la facture : {str(e)}")
    
    return redirect('paiements:facture-detail', facture_id=facture.facture_id)

@login_required
def envoyer_rappel_facture(request, facture_id):
    """Vue pour envoyer un rappel de paiement pour une facture."""
    facture = get_object_or_404(Facture, facture_id=facture_id)
    
    if facture.statut in ['payee', 'annulee']:
        messages.error(request, f"Impossible d'envoyer un rappel pour une facture {facture.get_statut_display().lower()}.")
        return redirect('paiements:facture-detail', facture_id=facture.facture_id)
    
    rappels = []
    
    if request.method == 'POST':
        email_destinataire = request.POST.get('email')
        objet = request.POST.get('objet')
        message = request.POST.get('message')
        joindre_facture = request.POST.get('joindre_facture') == 'on'
        
        if not email_destinataire or not message:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return render(request, 'paiements/facture_rappel.html', {
                'facture': facture,
                'rappels': rappels
            })
        
        try:
            email = EmailMessage(
                subject=objet,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email_destinataire]
            )
            
            if joindre_facture:
                # Générer le PDF en utilisant ReportLab
                buffer = BytesIO()
                doc = SimpleDocTemplate(
                    buffer,
                    pagesize=A4,
                    rightMargin=72,
                    leftMargin=72,
                    topMargin=72,
                    bottomMargin=72
                )
                
                elements = []
                
                styles = getSampleStyleSheet()
                title_style = styles['Heading1']
                subtitle_style = styles['Heading2']
                normal_style = styles['Normal']
                
                elements.append(Paragraph(f"FACTURE #{facture.numero_facture}", title_style))
                elements.append(Spacer(1, 0.5*cm))
                
                elements.append(Paragraph(f"Date d'émission: {facture.date_emission.strftime('%d/%m/%Y')}", normal_style))
                elements.append(Paragraph(f"Date d'échéance: {facture.date_echeance.strftime('%d/%m/%Y')}", normal_style))
                elements.append(Paragraph(f"Statut: {facture.get_statut_display()}", normal_style))
                elements.append(Spacer(1, 0.5*cm))
                
                elements.append(Paragraph("Destinataire:", subtitle_style))
                elements.append(Paragraph(facture.destinataire_nom, normal_style))
                elements.append(Paragraph(facture.destinataire_adresse, normal_style))
                elements.append(Paragraph(f"Email: {facture.destinataire_email}", normal_style))
                elements.append(Paragraph(f"Téléphone: {facture.destinataire_telephone or 'Non spécifié'}", normal_style))
                if facture.destinataire_siret:
                    elements.append(Paragraph(f"SIRET: {facture.destinataire_siret}", normal_style))
                elements.append(Spacer(1, 1*cm))
                
                lignes = LigneFacture.objects.filter(facture=facture)
                data = [['Description', 'Quantité', 'Prix unitaire HT', 'TVA', 'Montant HT', 'Montant TTC']]
                
                for ligne in lignes:
                    data.append([
                        ligne.description,
                        str(ligne.quantite),
                        f"{ligne.prix_unitaire_ht} €",
                        f"{ligne.taux_tva} %",
                        f"{ligne.montant_ht} €",
                        f"{ligne.montant_ttc} €"
                    ])
                
                data.append(['', '', '', '', 'Total HT:', f"{facture.montant_ht} €"])
                data.append(['', '', '', '', 'TVA:', f"{facture.montant_tva} €"])
                data.append(['', '', '', '', 'Total TTC:', f"{facture.montant_ttc} €"])
                
                table = Table(data, colWidths=[6*cm, 2*cm, 2.5*cm, 2*cm, 2.5*cm, 2.5*cm])
                
                table_style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -4), colors.white),
                    ('BACKGROUND', (4, -3), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
                ])
                
                table.setStyle(table_style)
                elements.append(table)
                elements.append(Spacer(1, 1*cm))
                
                if facture.notes:
                    elements.append(Paragraph("Notes:", subtitle_style))
                    elements.append(Paragraph(facture.notes, normal_style))
                    elements.append(Spacer(1, 0.5*cm))
                
                if facture.conditions_paiement:
                    elements.append(Paragraph("Conditions de paiement:", subtitle_style))
                    elements.append(Paragraph(facture.conditions_paiement, normal_style))
                
                doc.build(elements)
                
                pdf = buffer.getvalue()
                buffer.close()
                
                email.attach(f'facture_{facture.numero_facture}.pdf', pdf, 'application/pdf')
            
            email.send()
            
            messages.success(request, f'Rappel envoyé avec succès à {email_destinataire}.')
            return redirect('paiements:facture-detail', facture_id=facture.facture_id)
            
        except Exception as e:
            messages.error(request, f"Erreur lors de l'envoi du rappel : {str(e)}")
    
    if facture.date_echeance and facture.date_echeance < timezone.now().date():
        jours_retard = (timezone.now().date() - facture.date_echeance).days
        facture.est_en_retard = True
        facture.jours_de_retard = jours_retard
    else:
        facture.est_en_retard = False
        facture.jours_de_retard = 0
    
    return render(request, 'paiements/facture_rappel.html', {
        'facture': facture,
        'rappels': rappels
    })

@login_required
def get_inscription_prix(request, inscription_id):
    """API pour récupérer le prix d'une inscription."""
    try:
        inscription = Inscription.objects.get(pk=inscription_id)
        
        try:
            if hasattr(inscription, 'plan_paiement') and inscription.plan_paiement:
                montant_ht = inscription.plan_paiement.montant_total
            else:
                montant_ht = inscription.seance.prix
        except Exception:
            montant_ht = inscription.seance.prix
        
        montant_ht = Decimal(str(montant_ht))
        
        return JsonResponse({
            'success': True,
            'montant_ht': float(montant_ht)
        })
    except Inscription.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Inscription non trouvée'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def changer_statut_facture(request, facture_id):
    facture = get_object_or_404(Facture, facture_id=facture_id)
    
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        if nouveau_statut in dict(Facture.STATUS_CHOICES):
            ancien_statut = facture.statut
            facture.statut = nouveau_statut
            facture.save()
            
            messages.success(request, f'Statut de la facture modifié de "{dict(Facture.STATUS_CHOICES)[ancien_statut]}" à "{dict(Facture.STATUS_CHOICES)[nouveau_statut]}".')
        else:
            messages.error(request, 'Statut invalide.')
    
    return redirect('paiements:facture-detail', facture_id=facture.facture_id)

@login_required
def modifier_facture(request, facture_id):
    """Vue fonctionnelle pour modifier une facture existante."""
    try:
        # Utiliser une requête directe sans jointure
        facture = Facture.objects.filter(facture_id=facture_id).first()
        
        if not facture:
            messages.error(request, "Cette facture n'existe pas.")
            return redirect('paiements:facture-list')
    except Exception as e:
        messages.error(request, f"Erreur lors de la récupération de la facture: {str(e)}")
        return redirect('paiements:facture-list')
    
    if request.method == 'POST':
        form = FactureForm(request.POST, instance=facture)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facture mise à jour avec succès.')
            return redirect('paiements:facture-detail', facture_id=facture.facture_id)
    else:
        form = FactureForm(instance=facture)
    
    # Utiliser le nouveau template sans référence aux lignes de facture
    return render(request, 'paiements/facture_edit.html', {
        'form': form,
        'titre': f'Modifier la facture {facture.numero_facture}',
        'facture': facture
    })

@login_required
def recreer_facture(request, facture_id):
    """Vue pour recréer une facture à partir d'une facture existante."""
    try:
        # Récupérer la facture originale sans utiliser de requêtes complexes
        facture_originale = None
        for f in Facture.objects.all():
            if str(f.facture_id) == str(facture_id):
                facture_originale = f
                break
                
        if not facture_originale:
            messages.error(request, "La facture originale n'existe pas.")
            return redirect('paiements:facture-list')
    except Exception as e:
        messages.error(request, f"Erreur lors de la récupération de la facture: {str(e)}")
        return redirect('paiements:facture-list')
    
    # Préparer les données initiales pour le formulaire
    initial_data = {
        'inscription': facture_originale.inscription,
        'paiement': facture_originale.paiement,
        'date_emission': facture_originale.date_emission,
        'date_echeance': facture_originale.date_echeance,
        'montant_ht': facture_originale.montant_ht,
        'taux_tva': facture_originale.taux_tva,
        'type_facture': facture_originale.type_facture,
        'statut': facture_originale.statut,
        'destinataire_nom': facture_originale.destinataire_nom,
        'destinataire_adresse': facture_originale.destinataire_adresse,
        'destinataire_email': facture_originale.destinataire_email,
        'destinataire_telephone': facture_originale.destinataire_telephone,
        'destinataire_siret': facture_originale.destinataire_siret,
        'notes': facture_originale.notes,
        'conditions_paiement': facture_originale.conditions_paiement
    }
    
    if request.method == 'POST':
        # Créer une nouvelle facture
        form = FactureForm(request.POST)
        if form.is_valid():
            nouvelle_facture = form.save()
            
            # Recréer les lignes de facture
            try:
                # Récupérer les lignes sans utiliser de requêtes complexes
                lignes_originales = []
                for ligne in LigneFacture.objects.all():
                    if str(ligne.facture.facture_id) == str(facture_id):
                        lignes_originales.append(ligne)
                
                for ligne_originale in lignes_originales:
                    LigneFacture.objects.create(
                        facture=nouvelle_facture,
                        description=ligne_originale.description,
                        quantite=ligne_originale.quantite,
                        prix_unitaire_ht=ligne_originale.prix_unitaire_ht,
                        taux_tva=ligne_originale.taux_tva,
                        montant_ht=ligne_originale.montant_ht,
                        montant_tva=ligne_originale.montant_tva,
                        montant_ttc=ligne_originale.montant_ttc
                    )
                
                # Supprimer l'ancienne facture
                facture_originale.delete()
                
                messages.success(request, 'Facture recréée avec succès.')
                return redirect('paiements:facture-detail', facture_id=nouvelle_facture.facture_id)
            except Exception as e:
                messages.error(request, f"Erreur lors de la recréation des lignes de facture: {str(e)}")
                # En cas d'erreur, supprimer la nouvelle facture pour éviter les doublons
                nouvelle_facture.delete()
                return redirect('paiements:facture-detail', facture_id=facture_id)
    else:
        form = FactureForm(initial=initial_data)
    
    return render(request, 'paiements/facture_edit.html', {
        'form': form,
        'titre': f'Recréer la facture {facture_originale.numero_facture}',
        'facture': facture_originale
    })

@login_required
def emettre_facture(request, facture_id):
    """Vue pour émettre une facture (changer son statut de brouillon à émise)."""
    facture = get_object_or_404(Facture, facture_id=facture_id)
    
    # Vérifier que la facture est en brouillon
    if facture.statut != 'brouillon':
        messages.error(request, "Seules les factures en statut 'Brouillon' peuvent être émises.")
        return redirect('paiements:facture-detail', facture_id=facture.facture_id)
    
    # Changer le statut
    facture.statut = 'emise'
    # Définir la date d'émission à aujourd'hui
    facture.date_emission = timezone.now().date()
    # Définir la date d'échéance à 30 jours plus tard par défaut si elle n'est pas déjà définie
    if not facture.date_echeance:
        facture.date_echeance = facture.date_emission + timezone.timedelta(days=30)
    facture.save()
    
    messages.success(request, f"La facture {facture.numero_facture} a été émise avec succès.")
    return redirect('paiements:facture-detail', facture_id=facture.facture_id)

@login_required
def marquer_facture_payee(request, facture_id):
    """Vue pour marquer une facture comme payée."""
    facture = get_object_or_404(Facture, facture_id=facture_id)
    
    # Vérifier que la facture est émise
    if facture.statut != 'emise':
        messages.error(request, "Seules les factures en statut 'Émise' peuvent être marquées comme payées.")
        return redirect('paiements:facture-detail', facture_id=facture.facture_id)
    
    # Changer le statut
    facture.statut = 'payee'
    facture.save()
    
    messages.success(request, f"La facture {facture.numero_facture} a été marquée comme payée.")
    return redirect('paiements:facture-detail', facture_id=facture.facture_id)

@login_required
def annuler_facture(request, facture_id):
    """Vue pour annuler une facture."""
    facture = get_object_or_404(Facture, facture_id=facture_id)
    
    # Vérifier que la facture n'est pas déjà annulée
    if facture.statut == 'annulee':
        messages.error(request, "Cette facture est déjà annulée.")
        return redirect('paiements:facture-detail', facture_id=facture.facture_id)
    
    # Changer le statut
    ancien_statut = facture.statut
    facture.statut = 'annulee'
    facture.save()
    
    messages.success(request, f"La facture {facture.numero_facture} a été annulée.")
    return redirect('paiements:facture-detail', facture_id=facture.facture_id)
