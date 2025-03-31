from django.db import models
from django.utils import timezone
import uuid
from django.db.models import Sum
from decimal import Decimal

# Create your models here.

class Paiement(models.Model):
    """Model to track all received and due payments."""
    
    STATUS_CHOICES = [
        ('recu', 'Received'),
        ('en_attente', 'Pending'),
        ('retard', 'Late'),
        ('annule', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('especes', 'Cash'),
        ('cheque', 'Check'),
        ('virement', 'Bank Transfer'),
        ('carte', 'Credit/Debit Card'),
        ('autre', 'Other'),
    ]
    
    paiement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscription = models.ForeignKey('inscriptions.Inscription', on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateField(default=timezone.now)
    date_echeance = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    mode_paiement = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    reference = models.CharField(max_length=100, blank=True, null=True, help_text="Payment reference number (e.g., check number)")
    commentaires = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-date_paiement']
    
    def __str__(self):
        return f"Payment {self.paiement_id} - {self.montant} €"
    
    def is_late(self):
        """Check if the payment is late."""
        if self.statut == 'en_attente' and self.date_echeance:
            return self.date_echeance < timezone.now().date()
        return False
    
    def days_overdue(self):
        """Return the number of days payment is overdue."""
        if self.is_late():
            return (timezone.now().date() - self.date_echeance).days
        return 0


class PaiementFormateur(models.Model):
    """Model to manage trainer payments."""
    
    STATUS_CHOICES = [
        ('paye', 'Paid'),
        ('en_attente', 'Pending'),
        ('planifie', 'Scheduled'),
        ('annule', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('virement', 'Bank Transfer'),
        ('cheque', 'Check'),
        ('especes', 'Cash'),
        ('autre', 'Other'),
    ]
    
    paiement_formateur_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    formateur = models.ForeignKey('formateurs.Formateur', on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateField(default=timezone.now)
    periode_debut = models.DateField(help_text="Start of work period covered by this payment")
    periode_fin = models.DateField(help_text="End of work period covered by this payment")
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    mode_paiement = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='virement')
    reference = models.CharField(max_length=100, blank=True, null=True, help_text="Payment reference (e.g., transaction number)")
    heures_travaillees = models.DecimalField(max_digits=6, decimal_places=2, help_text="Number of hours worked during the period")
    taux_horaire = models.DecimalField(max_digits=8, decimal_places=2, help_text="Hourly rate applied")
    commentaires = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Trainer Payment"
        verbose_name_plural = "Trainer Payments"
        ordering = ['-date_paiement']
    
    def __str__(self):
        return f"Payment to {self.formateur} - {self.montant} €"
    
    def calculate_amount(self):
        """Calculate payment amount based on hours worked and hourly rate."""
        return self.heures_travaillees * self.taux_horaire
    
    def save(self, *args, **kwargs):
        # Recalculate amount if hours or rate have changed
        if self.heures_travaillees and self.taux_horaire:
            self.montant = self.calculate_amount()
        super().save(*args, **kwargs)


class PlanPaiement(models.Model):
    """Model to manage installment payment plans."""
    
    STATUS_CHOICES = [
        ('actif', 'Active'),
        ('complete', 'Completed'),
        ('annule', 'Cancelled'),
    ]
    
    plan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscription = models.OneToOneField('inscriptions.Inscription', on_delete=models.CASCADE, related_name='plan_paiement')
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    nombre_versements = models.PositiveIntegerField(default=1)
    date_debut = models.DateField(default=timezone.now)
    intervalle_jours = models.PositiveIntegerField(default=30, help_text="Interval in days between installments")
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='actif')
    commentaires = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Payment Plan"
        verbose_name_plural = "Payment Plans"
    
    def __str__(self):
        return f"Payment plan for {self.inscription}"
    
    def amount_paid(self):
        """Calculate the total amount already paid."""
        return self.inscription.paiements.filter(statut='recu').aggregate(total=models.Sum('montant'))['total'] or 0
    
    def remaining_amount(self):
        """Calculate the remaining amount to be paid."""
        return self.montant_total - self.amount_paid()
    
    def progress(self):
        """Calculate the percentage progress of the payment plan."""
        if self.montant_total > 0:
            return (self.amount_paid() / self.montant_total) * 100
        return 0
    
    def generate_schedule(self):
        """Generate the schedule of upcoming payments."""
        schedule = []
        montant_par_versement = self.montant_total / self.nombre_versements
        
        for i in range(self.nombre_versements):
            date_versement = self.date_debut + timezone.timedelta(days=i * self.intervalle_jours)
            schedule.append({
                'numero': i + 1,
                'date': date_versement,
                'montant': montant_par_versement,
            })
        
        return schedule


class Facture(models.Model):
    """Model for invoices generated for payments."""
    
    STATUS_CHOICES = [
        ('brouillon', 'Draft'),
        ('emise', 'Issued'),
        ('payee', 'Paid'),
        ('annulee', 'Cancelled'),
    ]
    
    INVOICE_TYPE_CHOICES = [
        ('individuelle', 'Individual'),
        ('entreprise', 'Company'),
        ('sponsor', 'Sponsor'),
    ]
    
    facture_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_facture = models.CharField(max_length=20, unique=True, blank=True)
    inscription = models.ForeignKey('inscriptions.Inscription', on_delete=models.SET_NULL, null=True, blank=True, related_name='factures')
    paiement = models.ForeignKey('Paiement', on_delete=models.SET_NULL, null=True, blank=True, related_name='factures')
    
    # Invoice type (individual, company, sponsor)
    type_facture = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES, default='individuelle')
    
    # Invoice status
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='brouillon')
    
    # Dates
    date_emission = models.DateField(default=timezone.now)
    date_echeance = models.DateField(null=True, blank=True)
    
    # Amounts
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=20.0)
    montant_tva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Recipient information
    destinataire_nom = models.CharField(max_length=255)
    destinataire_adresse = models.TextField()
    destinataire_email = models.EmailField()
    destinataire_telephone = models.CharField(max_length=20, blank=True, null=True)
    destinataire_siret = models.CharField(max_length=14, blank=True, null=True)
    
    # Additional information
    conditions_paiement = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Metadata
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ['-date_emission']
    
    def __str__(self):
        return f"Facture {self.numero_facture} - {self.get_type_facture_display()}"
    
    def save(self, *args, **kwargs):
        # Generate invoice number if not already set
        if not self.numero_facture:
            today = timezone.now().date()
            count = Facture.objects.filter(date_emission__year=today.year).count() + 1
            self.numero_facture = f"F{today.year}{count:04d}"
        super().save(*args, **kwargs)
    
    def recalculate_amounts(self):
        """Recalculate invoice amounts based on line items."""
        # Reset amounts
        self.montant_ht = 0
        self.montant_tva = 0
        self.montant_ttc = 0
        
        # Sum from line items if they exist
        if hasattr(self, 'lignes'):
            lines = self.lignes.all()
            if lines:
                for line in lines:
                    self.montant_ht += line.montant_ht
                    self.montant_tva += line.montant_tva
                    self.montant_ttc += line.montant_ttc
            else:
                # Calculate based on tax rate if there are no line items
                if self.montant_ht > 0:
                    self.montant_tva = self.montant_ht * (self.taux_tva / 100)
                    self.montant_ttc = self.montant_ht + self.montant_tva
    
    @classmethod
    def generer_facture_pour_inscription(cls, inscription_id, statut='brouillon'):
        """
        Génère une facture pour une inscription donnée.
        
        Args:
            inscription_id: ID de l'inscription
            statut: Statut initial de la facture
            
        Returns:
            Facture: L'objet facture créé
        """
        from inscriptions.models import Inscription
        from decimal import Decimal
        
        try:
            inscription = Inscription.objects.get(inscription_id=inscription_id)
        except Inscription.DoesNotExist:
            raise ValueError("L'inscription spécifiée n'existe pas")
            
        # Déterminer le destinataire en fonction du type d'inscription
        if inscription.type_inscription == 'individuelle':
            destinataire = inscription.client
        elif inscription.type_inscription in ['entreprise', 'groupe']:
            destinataire = inscription.client
        elif inscription.sponsor:
            destinataire = inscription.sponsor
        else:
            destinataire = inscription.client
            
        # Déterminer le type de facture
        if inscription.type_inscription == 'individuelle':
            type_facture = 'individuelle'
        elif inscription.type_inscription in ['entreprise', 'groupe']:
            type_facture = 'entreprise'
        elif inscription.sponsor:
            type_facture = 'sponsor'
        else:
            type_facture = 'individuelle'
            
        # Calculer le montant à partir de la séance ou du plan de paiement
        try:
            plan_paiement = inscription.plan_paiement
            montant_ttc = plan_paiement.montant_total
            montant_ht = montant_ttc / Decimal('1.2')  # Supposant une TVA de 20%
        except:
            # Si pas de plan de paiement, utiliser le prix de la séance
            montant_ttc = inscription.seance.prix
            montant_ht = montant_ttc / Decimal('1.2')
            
        # Créer la facture
        facture = cls(
            inscription=inscription,
            type_facture=type_facture,
            statut=statut,
            date_emission=timezone.now().date(),
            date_echeance=timezone.now().date() + timezone.timedelta(days=30),
            montant_ht=montant_ht,
            taux_tva=Decimal('20.0'),
            montant_tva=montant_ht * Decimal('0.2'),
            montant_ttc=montant_ttc,
            destinataire_nom=destinataire.nom_entite,
            destinataire_adresse=destinataire.adresse_siege or "",
            destinataire_email=destinataire.email or "",
            destinataire_telephone=destinataire.telephone or "",
        )
        
        # Ajouter le SIRET si c'est une entreprise
        if hasattr(destinataire, 'numero_immatriculation') and destinataire.numero_immatriculation:
            facture.destinataire_siret = destinataire.numero_immatriculation
            
        facture.save()
        
        # Créer une ligne de facture par défaut
        from .models import LigneFacture
        LigneFacture.objects.create(
            facture=facture,
            description=f"Formation: {inscription.seance.cours.nom_cours}",
            quantite=1,
            prix_unitaire_ht=montant_ht,
            taux_tva=Decimal('20.0'),
            montant_ht=montant_ht,
            montant_tva=montant_ht * Decimal('0.2'),
            montant_ttc=montant_ttc
        )
        
        return facture


class LigneFacture(models.Model):
    """Model for detailed invoice line items."""
    
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
        verbose_name = "Invoice Line"
        verbose_name_plural = "Invoice Lines"
    
    def __str__(self):
        return f"{self.description} - {self.montant_ttc}€"
    
    def save(self, *args, **kwargs):
        # Calculate amounts
        self.montant_ht = self.quantite * self.prix_unitaire_ht
        self.montant_tva = self.montant_ht * (self.taux_tva / 100)
        self.montant_ttc = self.montant_ht + self.montant_tva
        
        super().save(*args, **kwargs)
        
        # Update the parent invoice
        self.facture.recalculate_amounts()
        self.facture.save()
