from django import forms
from .models import Paiement, PlanPaiement, PaiementFormateur, Facture, LigneFacture
from inscriptions.models import Inscription
from formateurs.models import Formateur
from django.utils import timezone

class PaiementForm(forms.ModelForm):
    """Formulaire pour la création et la modification des paiements."""
    
    class Meta:
        model = Paiement
        fields = [
            'inscription', 'montant', 'statut', 'date_paiement', 'date_echeance',
            'mode_paiement', 'reference', 'commentaires'
        ]
        widgets = {
            'date_paiement': forms.DateInput(attrs={'type': 'date'}),
            'date_echeance': forms.DateInput(attrs={'type': 'date'}),
            'commentaires': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        inscription_id = kwargs.pop('inscription_id', None)
        super().__init__(*args, **kwargs)
        
        # Appliquer des classes Bootstrap aux champs
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Ajouter l'attribut required aux champs obligatoires
        required_fields = ['inscription', 'montant', 'statut', 'date_paiement']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'required': 'required'})
        
        # Si une inscription_id est fournie, filtrer le queryset
        if inscription_id:
            self.fields['inscription'].initial = inscription_id
            self.fields['inscription'].queryset = Inscription.objects.filter(inscription_id=inscription_id)
        else:
            self.fields['inscription'].queryset = Inscription.objects.all().order_by('-date_inscription')
        
        # Ajouter des labels plus descriptifs
        self.fields['inscription'].label = "Inscription"
        self.fields['montant'].label = "Montant (€)"
        self.fields['statut'].label = "Statut du paiement"
        self.fields['date_paiement'].label = "Date de paiement"
        self.fields['date_echeance'].label = "Date d'échéance"
        self.fields['mode_paiement'].label = "Mode de paiement"
        self.fields['reference'].label = "Référence"
        self.fields['commentaires'].label = "Commentaires"


class PaiementFormateurForm(forms.ModelForm):
    """Formulaire pour la création et la modification des paiements aux formateurs."""
    
    class Meta:
        model = PaiementFormateur
        fields = [
            'formateur', 'montant', 'statut', 'date_paiement', 
            'periode_debut', 'periode_fin', 'heures_travaillees', 'taux_horaire',
            'mode_paiement', 'reference', 'commentaires'
        ]
        widgets = {
            'date_paiement': forms.DateInput(attrs={'type': 'date'}),
            'periode_debut': forms.DateInput(attrs={'type': 'date'}),
            'periode_fin': forms.DateInput(attrs={'type': 'date'}),
            'commentaires': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        formateur_id = kwargs.pop('formateur_id', None)
        super().__init__(*args, **kwargs)
        
        # Appliquer des classes Bootstrap aux champs
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Ajouter l'attribut required aux champs obligatoires
        required_fields = ['formateur', 'montant', 'statut', 'date_paiement', 'periode_debut', 'periode_fin']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'required': 'required'})
        
        # Si un formateur_id est fourni, filtrer le queryset
        if formateur_id:
            self.fields['formateur'].initial = formateur_id
            self.fields['formateur'].queryset = Formateur.objects.filter(formateur_id=formateur_id)
        else:
            self.fields['formateur'].queryset = Formateur.objects.all().order_by('nom', 'prenom')
        
        # Ajouter des labels plus descriptifs
        self.fields['formateur'].label = "Formateur"
        self.fields['montant'].label = "Montant (€)"
        self.fields['statut'].label = "Statut du paiement"
        self.fields['date_paiement'].label = "Date de paiement"
        self.fields['periode_debut'].label = "Début de la période"
        self.fields['periode_fin'].label = "Fin de la période"
        self.fields['heures_travaillees'].label = "Heures travaillées"
        self.fields['taux_horaire'].label = "Taux horaire (€)"
        self.fields['mode_paiement'].label = "Mode de paiement"
        self.fields['reference'].label = "Référence"
        self.fields['commentaires'].label = "Commentaires"
    
    def clean(self):
        cleaned_data = super().clean()
        periode_debut = cleaned_data.get('periode_debut')
        periode_fin = cleaned_data.get('periode_fin')
        
        # Vérifier que la période de début est antérieure à la période de fin
        if periode_debut and periode_fin and periode_debut > periode_fin:
            self.add_error('periode_debut', "La date de début doit être antérieure à la date de fin")
        
        # Recalculer le montant si les heures et le taux sont fournis
        heures_travaillees = cleaned_data.get('heures_travaillees')
        taux_horaire = cleaned_data.get('taux_horaire')
        if heures_travaillees and taux_horaire:
            cleaned_data['montant'] = heures_travaillees * taux_horaire
        
        return cleaned_data


class CalculPaiementFormateurForm(forms.Form):
    """Formulaire pour le calcul automatique des paiements formateurs."""
    
    formateur = forms.ModelChoiceField(
        queryset=Formateur.objects.all().order_by('nom', 'prenom'),
        label="Formateur",
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'})
    )
    
    periode_debut = forms.DateField(
        label="Début de la période",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'})
    )
    
    periode_fin = forms.DateField(
        label="Fin de la période",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'})
    )
    
    taux_horaire = forms.DecimalField(
        label="Taux horaire (€)",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'})
    )
    
    PERIODE_CHOICES = [
        ('personnalise', 'Période personnalisée'),
        ('mois_courant', 'Mois courant'),
        ('mois_precedent', 'Mois précédent'),
        ('trimestre_courant', 'Trimestre courant'),
        ('trimestre_precedent', 'Trimestre précédent'),
    ]
    
    periode_predefinies = forms.ChoiceField(
        choices=PERIODE_CHOICES,
        label="Périodes prédéfinies",
        initial='personnalise',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        formateur_id = kwargs.pop('formateur_id', None)
        super().__init__(*args, **kwargs)
        
        # Si un formateur_id est fourni, filtrer le queryset
        if formateur_id:
            self.fields['formateur'].initial = formateur_id
            self.fields['formateur'].queryset = Formateur.objects.filter(formateur_id=formateur_id)
        
        # Définir les dates par défaut (mois courant)
        today = timezone.now().date()
        first_day = today.replace(day=1)
        last_day = (first_day.replace(month=first_day.month % 12 + 1, day=1) - timezone.timedelta(days=1)) if first_day.month < 12 else first_day.replace(year=first_day.year + 1, month=1, day=1) - timezone.timedelta(days=1)
        
        self.fields['periode_debut'].initial = first_day
        self.fields['periode_fin'].initial = last_day
        
        # Récupérer le taux horaire par défaut du formateur si disponible
        if formateur_id:
            try:
                formateur = Formateur.objects.get(formateur_id=formateur_id)
                if hasattr(formateur, 'taux_horaire') and formateur.taux_horaire:
                    self.fields['taux_horaire'].initial = formateur.taux_horaire
            except Formateur.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        periode_debut = cleaned_data.get('periode_debut')
        periode_fin = cleaned_data.get('periode_fin')
        
        if periode_debut and periode_fin and periode_debut > periode_fin:
            self.add_error('periode_fin', "La date de fin doit être postérieure à la date de début.")
        
        return cleaned_data


class PlanPaiementForm(forms.ModelForm):
    """Formulaire pour la création et la modification des plans de paiement."""
    
    class Meta:
        model = PlanPaiement
        fields = [
            'inscription', 'montant_total', 'nombre_versements', 
            'date_debut', 'intervalle_jours', 'statut', 'commentaires'
        ]
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'commentaires': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        inscription_id = kwargs.pop('inscription_id', None)
        super().__init__(*args, **kwargs)
        
        # Appliquer des classes Bootstrap aux champs
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Ajouter l'attribut required aux champs obligatoires
        required_fields = ['inscription', 'montant_total', 'nombre_versements', 'date_debut', 'intervalle_jours']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'required': 'required'})
        
        # Si une inscription_id est fournie, filtrer le queryset
        if inscription_id:
            self.fields['inscription'].initial = inscription_id
            self.fields['inscription'].queryset = Inscription.objects.filter(inscription_id=inscription_id)
        else:
            self.fields['inscription'].queryset = Inscription.objects.all().order_by('-date_inscription')
        
        # Si c'est une nouvelle instance, définir des valeurs par défaut
        if not self.instance.pk:
            self.fields['nombre_versements'].initial = 3
            self.fields['intervalle_jours'].initial = 30
            # Masquer le statut pour les nouveaux plans
            if 'statut' in self.fields:
                self.fields.pop('statut')
        
        # Ajouter des labels plus descriptifs
        self.fields['inscription'].label = "Inscription"
        self.fields['montant_total'].label = "Montant total (€)"
        self.fields['nombre_versements'].label = "Nombre de versements"
        self.fields['date_debut'].label = "Date du premier versement"
        self.fields['intervalle_jours'].label = "Intervalle entre les versements (jours)"
        if 'statut' in self.fields:
            self.fields['statut'].label = "Statut du plan"
        self.fields['commentaires'].label = "Commentaires"


class FactureForm(forms.ModelForm):
    """Formulaire pour la création et la modification des factures."""
    
    class Meta:
        model = Facture
        fields = [
            'inscription', 'paiement', 'date_emission', 'date_echeance',
            'montant_ht', 'taux_tva', 'type_facture', 'statut',
            'destinataire_nom', 'destinataire_adresse', 'destinataire_email',
            'destinataire_telephone', 'destinataire_siret', 'notes', 'conditions_paiement'
        ]
        widgets = {
            'date_emission': forms.DateInput(attrs={'type': 'date'}),
            'date_echeance': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'conditions_paiement': forms.Textarea(attrs={'rows': 3}),
            'destinataire_adresse': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        inscription_id = kwargs.pop('inscription_id', None)
        paiement_id = kwargs.pop('paiement_id', None)
        super().__init__(*args, **kwargs)
        
        # Appliquer des classes Bootstrap aux champs
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Ajouter l'attribut required aux champs obligatoires
        required_fields = [
            'inscription', 'date_emission', 'montant_ht', 'taux_tva', 
            'type_facture', 'destinataire_nom', 'destinataire_adresse', 'destinataire_email'
        ]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'required': 'required'})
        
        # Si une inscription_id est fournie, filtrer le queryset
        if inscription_id:
            self.fields['inscription'].initial = inscription_id
            self.fields['inscription'].queryset = Inscription.objects.filter(inscription_id=inscription_id)
            
            # Pré-remplir les informations du destinataire
            try:
                inscription = Inscription.objects.get(inscription_id=inscription_id)
                
                # Déterminer le destinataire en fonction du type d'inscription
                if inscription.type_inscription == 'individuelle':
                    destinataire = inscription.client
                elif inscription.type_inscription in ['entreprise', 'groupe']:
                    destinataire = inscription.client
                elif inscription.sponsor:
                    destinataire = inscription.sponsor
                else:
                    destinataire = inscription.client
                
                # Pré-remplir les champs
                self.fields['destinataire_nom'].initial = destinataire.nom_client
                self.fields['destinataire_adresse'].initial = destinataire.adresse
                self.fields['destinataire_email'].initial = destinataire.email
                self.fields['destinataire_telephone'].initial = destinataire.telephone
                
                # SIRET pour les entreprises
                if hasattr(destinataire, 'siret'):
                    self.fields['destinataire_siret'].initial = destinataire.siret
                
                # Déterminer le type de facture
                if inscription.type_inscription == 'individuelle':
                    self.fields['type_facture'].initial = 'individuelle'
                elif inscription.type_inscription in ['entreprise', 'groupe']:
                    self.fields['type_facture'].initial = 'entreprise'
                elif inscription.sponsor:
                    self.fields['type_facture'].initial = 'sponsor'
                
                # Récupérer le montant depuis la séance ou le plan de paiement
                try:
                    plan_paiement = inscription.plan_paiement
                    montant_ttc = plan_paiement.montant_total
                    montant_ht = montant_ttc / 1.2  # Supposant une TVA de 20%
                except:
                    # Si pas de plan de paiement, utiliser le prix de la séance
                    montant_ttc = inscription.seance.prix
                    montant_ht = montant_ttc / 1.2
                
                self.fields['montant_ht'].initial = montant_ht
                self.fields['taux_tva'].initial = 20.00
                
            except Inscription.DoesNotExist:
                pass
        else:
            self.fields['inscription'].queryset = Inscription.objects.all().order_by('-date_inscription')
        
        # Si un paiement_id est fourni, filtrer le queryset
        if paiement_id:
            self.fields['paiement'].initial = paiement_id
            self.fields['paiement'].queryset = Paiement.objects.filter(paiement_id=paiement_id)
            
            # Pré-remplir le montant à partir du paiement
            try:
                paiement = Paiement.objects.get(paiement_id=paiement_id)
                montant_ttc = paiement.montant
                montant_ht = montant_ttc / 1.2  # Supposant une TVA de 20%
                self.fields['montant_ht'].initial = montant_ht
            except Paiement.DoesNotExist:
                pass
        else:
            # Filtrer les paiements sans facture - éviter d'utiliser facture__isnull qui cause l'erreur
            # self.fields['paiement'].queryset = Paiement.objects.filter(facture__isnull=True).order_by('-date_paiement')
            
            # Utiliser une approche alternative pour obtenir les paiements sans facture
            paiements_avec_facture = []
            for facture in Facture.objects.all():
                if facture.paiement:
                    paiements_avec_facture.append(facture.paiement.paiement_id)
            
            self.fields['paiement'].queryset = Paiement.objects.exclude(paiement_id__in=paiements_avec_facture).order_by('-date_paiement')
        
        # Valeurs par défaut
        if not self.instance.pk:
            self.fields['date_emission'].initial = timezone.now().date()
            self.fields['date_echeance'].initial = timezone.now().date() + timezone.timedelta(days=30)
            self.fields['conditions_paiement'].initial = "Paiement à 30 jours à compter de la date d'émission de la facture."
        
        # Ajouter des labels plus descriptifs
        self.fields['inscription'].label = "Inscription"
        self.fields['paiement'].label = "Paiement associé"
        self.fields['date_emission'].label = "Date d'émission"
        self.fields['date_echeance'].label = "Date d'échéance"
        self.fields['montant_ht'].label = "Montant HT (€)"
        self.fields['taux_tva'].label = "Taux de TVA (%)"
        self.fields['type_facture'].label = "Type de facture"
        self.fields['statut'].label = "Statut de la facture"
        self.fields['destinataire_nom'].label = "Nom du destinataire"
        self.fields['destinataire_adresse'].label = "Adresse du destinataire"
        self.fields['destinataire_email'].label = "Email du destinataire"
        self.fields['destinataire_telephone'].label = "Téléphone du destinataire"
        self.fields['destinataire_siret'].label = "SIRET (pour les entreprises)"
        self.fields['notes'].label = "Notes"
        self.fields['conditions_paiement'].label = "Conditions de paiement"
    
    def clean(self):
        cleaned_data = super().clean()
        montant_ht = cleaned_data.get('montant_ht')
        taux_tva = cleaned_data.get('taux_tva')
        
        # Calculer les montants TVA et TTC
        if montant_ht and taux_tva:
            montant_tva = montant_ht * (taux_tva / 100)
            montant_ttc = montant_ht + montant_tva
            
            # Ajouter ces valeurs aux données nettoyées
            cleaned_data['montant_tva'] = montant_tva
            cleaned_data['montant_ttc'] = montant_ttc
        
        return cleaned_data


class LigneFactureForm(forms.ModelForm):
    """Formulaire pour la création et la modification des lignes de facture."""
    
    class Meta:
        model = LigneFacture
        fields = [
            'description', 'quantite', 'prix_unitaire_ht', 'taux_tva'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Appliquer des classes Bootstrap aux champs
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Ajouter l'attribut required aux champs obligatoires
        required_fields = ['description', 'quantite', 'prix_unitaire_ht', 'taux_tva']
        for field_name in required_fields:
            self.fields[field_name].widget.attrs.update({'required': 'required'})
        
        # Valeurs par défaut
        if not self.instance.pk:
            self.fields['quantite'].initial = 1
            self.fields['taux_tva'].initial = 20.00
        
        # Ajouter des labels plus descriptifs
        self.fields['description'].label = "Description"
        self.fields['quantite'].label = "Quantité"
        self.fields['prix_unitaire_ht'].label = "Prix unitaire HT (€)"
        self.fields['taux_tva'].label = "Taux de TVA (%)"
    
    def clean(self):
        cleaned_data = super().clean()
        quantite = cleaned_data.get('quantite')
        prix_unitaire_ht = cleaned_data.get('prix_unitaire_ht')
        taux_tva = cleaned_data.get('taux_tva')
        
        # Calculer les montants
        if quantite and prix_unitaire_ht and taux_tva:
            montant_ht = quantite * prix_unitaire_ht
            montant_tva = montant_ht * (taux_tva / 100)
            montant_ttc = montant_ht + montant_tva
            
            # Ajouter ces valeurs aux données nettoyées
            cleaned_data['montant_ht'] = montant_ht
            cleaned_data['montant_tva'] = montant_tva
            cleaned_data['montant_ttc'] = montant_ttc
        
        return cleaned_data


class GenerationFactureForm(forms.Form):
    """Formulaire pour la génération automatique de factures."""
    
    inscription = forms.ModelChoiceField(
        queryset=Inscription.objects.all().order_by('-date_inscription'),
        label="Inscription",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    montant_ht = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Montant HT (€)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    taux_tva = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        initial=0.0,
        label="Taux de TVA (%)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
    )
    
    type_facture = forms.ChoiceField(
        choices=Facture.INVOICE_TYPE_CHOICES,
        label="Type de facture",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    statut_initial = forms.ChoiceField(
        choices=Facture.STATUS_CHOICES,
        label="Statut initial",
        initial='brouillon',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    generer_pdf = forms.BooleanField(
        required=False,
        initial=True,
        label="Générer le PDF",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Ajouter un événement JavaScript pour mettre à jour le montant quand l'inscription change
        self.fields['inscription'].widget.attrs.update({
            'onchange': 'updateMontantFromInscription(this.value)'
        })
