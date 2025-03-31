from django.db import models
from django.utils import timezone
import uuid
from django.db.models import Sum
from decimal import Decimal

# Create your models here.

class Paiement(models.Model):
    """Modèle pour suivre tous les paiements reçus et dus."""
    
    STATUT_CHOICES = [
        ('recu', 'Reçu'),
        ('en_attente', 'En attente'),
        ('retard', 'En retard'),
        ('annule', 'Annulé'),
    ]
    
    MODE_PAIEMENT_CHOICES = [
        ('especes', 'Espèces'),
        ('cheque', 'Chèque'),
        ('virement', 'Virement bancaire'),
        ('carte', 'Carte de crédit/débit'),
        ('autre', 'Autre'),
    ]
    
    paiement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscription = models.ForeignKey('inscriptions.Inscription', on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateField(default=timezone.now)
    date_echeance = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, null=True, blank=True)
    reference = models.CharField(max_length=100, blank=True, null=True, help_text="Numéro de référence du paiement (ex: numéro de chèque)")
    commentaires = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-date_paiement']
    
    def __str__(self):
        return f"Paiement {self.paiement_id} - {self.montant} €"
    
    def est_en_retard(self):
        """Vérifie si le paiement est en retard."""
        if self.statut == 'en_attente' and self.date_echeance:
            return self.date_echeance < timezone.now().date()
        return False
    
    def jours_de_retard(self):
        """Retourne le nombre de jours de retard."""
        if self.est_en_retard():
            return (timezone.now().date() - self.date_echeance).days
        return 0


class PaiementFormateur(models.Model):
    """Modèle pour gérer les paiements aux formateurs."""
    
    STATUT_CHOICES = [
        ('paye', 'Payé'),
        ('en_attente', 'En attente'),
        ('planifie', 'Planifié'),
        ('annule', 'Annulé'),
    ]
    
    MODE_PAIEMENT_CHOICES = [
        ('virement', 'Virement bancaire'),
        ('cheque', 'Chèque'),
        ('especes', 'Espèces'),
        ('autre', 'Autre'),
    ]
    
    paiement_formateur_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    formateur = models.ForeignKey('formateurs.Formateur', on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateField(default=timezone.now)
    periode_debut = models.DateField(help_text="Début de la période de travail concernée par ce paiement")
    periode_fin = models.DateField(help_text="Fin de la période de travail concernée par ce paiement")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, default='virement')
    reference = models.CharField(max_length=100, blank=True, null=True, help_text="Référence du paiement (ex: numéro de transaction)")
    heures_travaillees = models.DecimalField(max_digits=6, decimal_places=2, help_text="Nombre d'heures travaillées sur la période")
    taux_horaire = models.DecimalField(max_digits=8, decimal_places=2, help_text="Taux horaire appliqué")
    commentaires = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paiement Formateur"
        verbose_name_plural = "Paiements Formateurs"
        ordering = ['-date_paiement']
    
    def __str__(self):
        return f"Paiement à {self.formateur} - {self.montant} €"
    
    def calculer_montant(self):
        """Calcule le montant du paiement basé sur les heures travaillées et le taux horaire."""
        return self.heures_travaillees * self.taux_horaire
    
    def save(self, *args, **kwargs):
        # Recalculer le montant si les heures ou le taux ont changé
        if self.heures_travaillees and self.taux_horaire:
            self.montant = self.calculer_montant()
        super().save(*args, **kwargs)


class PlanPaiement(models.Model):
    """Modèle pour gérer les plans de paiement échelonnés."""
    
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('complete', 'Complété'),
        ('annule', 'Annulé'),
    ]
    
    plan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscription = models.OneToOneField('inscriptions.Inscription', on_delete=models.CASCADE, related_name='plan_paiement')
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    nombre_versements = models.PositiveIntegerField(default=1)
    date_debut = models.DateField(default=timezone.now)
    intervalle_jours = models.PositiveIntegerField(default=30, help_text="Intervalle en jours entre les versements")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    commentaires = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Plan de paiement"
        verbose_name_plural = "Plans de paiement"
    
    def __str__(self):
        return f"Plan de paiement pour {self.inscription}"
    
    def montant_verse(self):
        """Calcule le montant total déjà versé."""
        return self.inscription.paiements.filter(statut='recu').aggregate(total=models.Sum('montant'))['total'] or 0
    
    def montant_restant(self):
        """Calcule le montant restant à payer."""
        return self.montant_total - self.montant_verse()
    
    def progression(self):
        """Calcule le pourcentage de progression du plan de paiement."""
        if self.montant_total > 0:
            return (self.montant_verse() / self.montant_total) * 100
        return 0
    
    def generer_echeancier(self):
        """Génère l'échéancier des paiements à venir."""
        echeancier = []
        montant_par_versement = self.montant_total / self.nombre_versements
        
        for i in range(self.nombre_versements):
            date_versement = self.date_debut + timezone.timedelta(days=i * self.intervalle_jours)
            echeancier.append({
                'numero': i + 1,
                'date': date_versement,
                'montant': montant_par_versement,
            })
        
        return echeancier


class Facture(models.Model):
    """Modèle pour les factures générées pour les paiements."""
    
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('emise', 'Émise'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]
    
    TYPE_FACTURE_CHOICES = [
        ('individuelle', 'Individuelle'),
        ('entreprise', 'Entreprise'),
        ('sponsor', 'Sponsor'),
    ]
    
    facture_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_facture = models.CharField(max_length=20, unique=True, blank=True)
    inscription = models.ForeignKey('inscriptions.Inscription', on_delete=models.SET_NULL, null=True, blank=True, related_name='factures')
    paiement = models.ForeignKey('Paiement', on_delete=models.SET_NULL, null=True, blank=True, related_name='factures')
    
    # Type de facture (individuelle, entreprise, sponsor)
    type_facture = models.CharField(max_length=20, choices=TYPE_FACTURE_CHOICES, default='individuelle')
    
    # Statut de la facture
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    
    # Dates
    date_emission = models.DateField(default=timezone.now)
    date_echeance = models.DateField(null=True, blank=True)
    
    # Montants
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=20.0)
    montant_tva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Informations du destinataire
    destinataire_nom = models.CharField(max_length=255)
    destinataire_adresse = models.TextField()
    destinataire_email = models.EmailField()
    destinataire_telephone = models.CharField(max_length=20, blank=True, null=True)
    destinataire_siret = models.CharField(max_length=14, blank=True, null=True)
    
    # Informations complémentaires
    conditions_paiement = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-date_emission']
    
    def __str__(self):
        return f"Facture {self.numero_facture}"
    
    def save(self, *args, **kwargs):
        # Générer un numéro de facture unique s'il n'existe pas déjà
        if not self.numero_facture:
            annee = timezone.now().year
            # Compter les factures existantes pour cette année
            count = Facture.objects.filter(
                numero_facture__startswith=f"F{annee}"
            ).count()
            # Générer le numéro de facture (format: F2023-0001)
            self.numero_facture = f"F{annee}-{count+1:04d}"
        
        # Calculer les montants TVA et TTC si le montant HT est défini
        if self.montant_ht and self.taux_tva:
            self.montant_tva = self.montant_ht * (self.taux_tva / Decimal('100.0'))
            self.montant_ttc = self.montant_ht + self.montant_tva
        
        super().save(*args, **kwargs)
    
    def recalculer_montants(self):
        """Recalcule les montants de la facture en fonction des lignes de facture."""
        from django.db.models import Sum
        
        # Récupérer les lignes de facture
        lignes = LigneFacture.objects.filter(facture=self)
        
        # Calculer les totaux
        if lignes.exists():
            total_ht = lignes.aggregate(total=Sum('montant_ht'))['total'] or 0
            total_tva = lignes.aggregate(total=Sum('montant_tva'))['total'] or 0
            total_ttc = lignes.aggregate(total=Sum('montant_ttc'))['total'] or 0
            
            self.montant_ht = total_ht
            self.montant_tva = total_tva
            self.montant_ttc = total_ttc
            self.save()
        
        return self.montant_ttc
    
    @classmethod
    def generer_facture_pour_inscription(cls, inscription_id, statut='brouillon'):
        """
        Génère une facture pour une inscription donnée.
        Le type de facture est déterminé en fonction du type d'inscription.
        """
        from inscriptions.models import Inscription
        
        # Récupérer l'inscription
        inscription = Inscription.objects.get(pk=inscription_id)
        
        # Déterminer le type de facture en fonction du type d'inscription
        if inscription.type_inscription == 'individuelle':
            type_facture = 'individuelle'
            # Utiliser uniquement le nom complet de l'apprenant pour éviter des erreurs
            # d'attributs manquants comme 'prenom'
            destinataire_nom = str(inscription.apprenant)
            destinataire_adresse = getattr(inscription.apprenant, 'adresse', 'Adresse non spécifiée')
            destinataire_email = getattr(inscription.apprenant, 'email', '')
            destinataire_telephone = getattr(inscription.apprenant, 'telephone', '')
            destinataire_siret = None
        elif inscription.type_inscription in ['entreprise', 'groupe']:
            type_facture = 'entreprise'
            if inscription.client:
                destinataire_nom = inscription.client.nom_entite
                destinataire_adresse = getattr(inscription.client, 'adresse_siege', 'Adresse non spécifiée')
                destinataire_email = getattr(inscription.client, 'email', '')
                destinataire_telephone = getattr(inscription.client, 'telephone', '')
                destinataire_siret = getattr(inscription.client, 'numero_immatriculation', '')
            else:
                # Fallback si pas d'entreprise
                destinataire_nom = str(inscription.apprenant)
                destinataire_adresse = getattr(inscription.apprenant, 'adresse', 'Adresse non spécifiée')
                destinataire_email = getattr(inscription.apprenant, 'email', '')
                destinataire_telephone = getattr(inscription.apprenant, 'telephone', '')
                destinataire_siret = None
        elif inscription.sponsor:
            type_facture = 'sponsor'
            destinataire_nom = inscription.sponsor.nom_entite
            destinataire_adresse = getattr(inscription.sponsor, 'adresse_siege', 'Adresse non spécifiée')
            destinataire_email = getattr(inscription.sponsor, 'email', '')
            destinataire_telephone = getattr(inscription.sponsor, 'telephone', '')
            destinataire_siret = getattr(inscription.sponsor, 'numero_immatriculation', '')
        else:
            # Par défaut, facturer à l'apprenant
            type_facture = 'individuelle'
            destinataire_nom = str(inscription.apprenant)
            destinataire_adresse = getattr(inscription.apprenant, 'adresse', 'Adresse non spécifiée')
            destinataire_email = getattr(inscription.apprenant, 'email', '')
            destinataire_telephone = getattr(inscription.apprenant, 'telephone', '')
            destinataire_siret = None
        
        # Déterminer le montant à facturer
        try:
            if hasattr(inscription, 'plan_paiement') and inscription.plan_paiement:
                # Si un plan de paiement est défini, utiliser le montant total du plan
                montant_ht = Decimal(str(inscription.plan_paiement.montant_total))
            else:
                # Sinon, utiliser le prix de la séance
                montant_ht = Decimal(str(inscription.seance.prix))
        except Exception as e:
            # En cas d'erreur, utiliser le prix de la séance
            montant_ht = Decimal(str(inscription.seance.prix))
        
        # Créer la facture
        facture = cls.objects.create(
            inscription=inscription,
            paiement=None,  # Pas de paiement associé initialement
            type_facture=type_facture,
            statut=statut,
            date_emission=timezone.now().date(),
            date_echeance=timezone.now().date() + timezone.timedelta(days=30),  # Échéance à 30 jours par défaut
            montant_ht=montant_ht,
            taux_tva=Decimal('20.0'),  # TVA à 20% par défaut
            destinataire_nom=destinataire_nom,
            destinataire_adresse=destinataire_adresse,
            destinataire_email=destinataire_email,
            destinataire_telephone=destinataire_telephone,
            destinataire_siret=destinataire_siret,
            conditions_paiement="Paiement à réception de facture.\nMerci d'indiquer le numéro de facture dans votre référence de paiement."
        )
        
        # Créer une ligne de facture par défaut
        LigneFacture.objects.create(
            facture=facture,
            description=f"Formation: {inscription.seance.cours.nom_cours}",
            quantite=1,
            prix_unitaire_ht=montant_ht,
            taux_tva=Decimal('20.0'),
            montant_ht=montant_ht,
            montant_tva=montant_ht * Decimal('0.2'),
            montant_ttc=montant_ht * Decimal('1.2')
        )
        
        return facture


class LigneFacture(models.Model):
    """Modèle pour les lignes détaillées d'une facture."""
    
    ligne_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    facture = models.ForeignKey('Facture', on_delete=models.CASCADE, related_name='lignes')
    
    description = models.CharField(max_length=255)
    quantite = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    prix_unitaire_ht = models.DecimalField(max_digits=10, decimal_places=2)
    
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2)
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=20.0)
    montant_tva = models.DecimalField(max_digits=10, decimal_places=2)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ligne de facture"
        verbose_name_plural = "Lignes de facture"
    
    def __str__(self):
        return f"{self.description} ({self.facture.numero_facture})"
    
    def save(self, *args, **kwargs):
        # Calculer les montants
        self.montant_ht = self.quantite * self.prix_unitaire_ht
        self.montant_tva = self.montant_ht * (self.taux_tva / Decimal('100.0'))
        self.montant_ttc = self.montant_ht + self.montant_tva
        
        super().save(*args, **kwargs)
