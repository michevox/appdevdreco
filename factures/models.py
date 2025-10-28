from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from fournisseurs.models import Fournisseur

class Facture(models.Model):
    """Modèle pour les factures des fournisseurs"""
    
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]
    
    # Informations de base
    numero = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Numéro de facture",
        help_text="Numéro de facture du fournisseur"
    )
    fournisseur = models.ForeignKey(
        Fournisseur, 
        on_delete=models.CASCADE, 
        verbose_name="Fournisseur",
        help_text="Fournisseur qui a émis la facture"
    )
    objet = models.CharField(
        max_length=200, 
        verbose_name="Objet",
        help_text="Objet de la facture"
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Description",
        help_text="Description détaillée de la facture"
    )
    
    # Dates
    date_emission = models.DateField(
        verbose_name="Date d'émission",
        help_text="Date d'émission de la facture"
    )
    date_reception = models.DateField(
        default=timezone.now,
        verbose_name="Date de réception",
        help_text="Date de réception de la facture"
    )
    date_echeance = models.DateField(
        verbose_name="Date d'échéance",
        help_text="Date d'échéance de paiement"
    )
    
    # Statut
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='brouillon',
        verbose_name="Statut",
        help_text="Statut actuel de la facture"
    )
    
    # Montants
    montant_ht = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Montant HT",
        help_text="Montant hors taxes"
    )
    taux_tva = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('18.00'),
        verbose_name="Taux TVA (%)",
        help_text="Taux de TVA en pourcentage"
    )
    montant_tva = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Montant TVA",
        help_text="Montant de la TVA"
    )
    montant_ttc = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Montant TTC",
        help_text="Montant toutes taxes comprises"
    )
    
    # Conditions et notes
    conditions_paiement = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Conditions de paiement",
        help_text="Conditions de paiement spécifiées"
    )
    notes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Notes",
        help_text="Notes additionnelles"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-date_emission']
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['fournisseur']),
            models.Index(fields=['date_emission']),
            models.Index(fields=['statut']),
        ]
    
    def __str__(self):
        return f"Facture {self.numero} - {self.fournisseur.nom}"
    
    def save(self, *args, **kwargs):
        """Sauvegarde avec préservation des champs automatiques"""
        # Si c'est une mise à jour (l'objet a déjà un ID)
        if self.pk:
            try:
                # Récupérer l'objet existant pour préserver les champs automatiques
                existing = Facture.objects.get(pk=self.pk)
                if not self.date_creation:
                    self.date_creation = existing.date_creation
            except Facture.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    def calculer_montants(self):
        """Calcule automatiquement les montants HT, TVA et TTC"""
        try:
            print(f"Calcul des montants pour la facture {self.numero}")
            
            # Calculer le total HT de manière sécurisée
            total_ht = Decimal('0.00')
            lignes_count = 0
            
            for ligne in self.lignes.all():
                try:
                    if ligne.quantite and ligne.prix_unitaire_ht:
                        # Seulement limiter la quantité, pas les prix
                        quantite = min(Decimal(str(ligne.quantite)), Decimal('999999.99'))
                        prix = Decimal(str(ligne.prix_unitaire_ht))
                        ligne_montant = quantite * prix
                        total_ht += ligne_montant
                        lignes_count += 1
                        print(f"Ligne {ligne.id}: {quantite} x {prix} = {ligne_montant}")
                        
                except (TypeError, ValueError, InvalidOperation):
                    print(f"Problème avec la ligne {ligne.id}, utilisation de valeurs par défaut")
                    continue
            
            print(f"Total HT calculé: {total_ht} (basé sur {lignes_count} lignes)")
            self.montant_ht = total_ht
            
            # Calculer la TVA
            try:
                if self.taux_tva:
                    taux_tva_limite = min(Decimal(str(self.taux_tva)), Decimal('100.00'))
                    self.montant_tva = self.montant_ht * (taux_tva_limite / Decimal('100'))
                    print(f"TVA calculée: {self.montant_ht} x {taux_tva_limite}% = {self.montant_tva}")
                else:
                    self.montant_tva = Decimal('0.00')
                    print("Taux TVA à 0, montant TVA = 0")
            except (TypeError, ValueError, InvalidOperation):
                self.montant_tva = Decimal('0.00')
                print("Erreur calcul TVA, montant TVA = 0")
            
            # Calculer le TTC
            try:
                self.montant_ttc = self.montant_ht + self.montant_tva
                print(f"TTC calculé: {self.montant_ht} + {self.montant_tva} = {self.montant_ttc}")
            except (TypeError, ValueError, InvalidOperation):
                self.montant_ttc = self.montant_ht
                print("Erreur calcul TTC, TTC = HT")
            
            # Sauvegarder sans déclencher les signaux
            super().save(update_fields=['montant_ht', 'montant_tva', 'montant_ttc'])
            print(f"Montants sauvegardés: HT={self.montant_ht}, TVA={self.montant_tva}, TTC={self.montant_ttc}")
            
        except Exception as e:
            print(f"Erreur lors du calcul des montants: {e}")
            # En cas d'erreur, utiliser des valeurs par défaut
            self.montant_ht = Decimal('0.00')
            self.montant_tva = Decimal('0.00')
            self.montant_ttc = Decimal('0.00')
            super().save(update_fields=['montant_ht', 'montant_tva', 'montant_ttc'])
    
    def valider(self):
        """Marque la facture comme validée"""
        self.statut = 'validee'
        self.save()
    
    def payer(self):
        """Marque la facture comme payée"""
        self.statut = 'payee'
        self.save()
    
    def annuler(self):
        """Marque la facture comme annulée"""
        self.statut = 'annulee'
        self.save()


class LigneFacture(models.Model):
    """Modèle pour les lignes de facture"""
    
    facture = models.ForeignKey(
        Facture, 
        on_delete=models.CASCADE, 
        related_name='lignes',
        verbose_name="Facture"
    )
    description = models.CharField(
        max_length=200, 
        verbose_name="Description",
        help_text="Description de l'article ou service"
    )
    quantite = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('1.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Quantité",
        help_text="Quantité commandée"
    )
    unite = models.CharField(
        max_length=20, 
        default="unité", 
        verbose_name="Unité",
        help_text="Unité de mesure"
    )
    prix_unitaire_ht = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Prix unitaire HT",
        help_text="Prix unitaire hors taxes"
    )
    montant_ht = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant HT",
        help_text="Montant total de la ligne hors taxes"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    class Meta:
        verbose_name = "Ligne de facture"
        verbose_name_plural = "Lignes de facture"
        ordering = ['id']
    
    def __str__(self):
        return f"{self.description} - {self.quantite} {self.unite}"
    
    def save(self, *args, **kwargs):
        """Calcule automatiquement le montant HT et sauvegarde"""
        try:
            # S'assurer que les valeurs sont des Decimal valides
            if not isinstance(self.quantite, Decimal):
                try:
                    self.quantite = Decimal(str(self.quantite))
                except (ValueError, InvalidOperation):
                    self.quantite = Decimal('1.00')
            
            # Limiter seulement la quantité (pas les prix)
            self.quantite = min(self.quantite, Decimal('999999.99'))
            
            if not isinstance(self.prix_unitaire_ht, Decimal):
                try:
                    self.prix_unitaire_ht = Decimal(str(self.prix_unitaire_ht))
                except (ValueError, InvalidOperation):
                    self.prix_unitaire_ht = Decimal('0.00')
            
            # Calculer le montant HT sans limitation
            try:
                self.montant_ht = self.quantite * self.prix_unitaire_ht
            except (TypeError, ValueError, InvalidOperation):
                self.montant_ht = Decimal('0.00')
            
            # Sauvegarder la ligne
            super().save(*args, **kwargs)
            
            # Recalculer les montants de la facture après sauvegarde
            if hasattr(self, 'facture') and self.facture:
                try:
                    self.facture.calculer_montants()
                except Exception as e:
                    print(f"Erreur lors du recalcul des montants de la facture: {e}")
                
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la ligne: {e}")
            # En cas d'erreur critique, utiliser des valeurs par défaut
            self.quantite = Decimal('1.00')
            self.prix_unitaire_ht = Decimal('0.00')
            self.montant_ht = Decimal('0.00')
            super().save(*args, **kwargs)
            
            # Recalculer les montants de la facture même en cas d'erreur
            if hasattr(self, 'facture') and self.facture:
                try:
                    self.facture.calculer_montants()
                except Exception as e:
                    print(f"Erreur lors du recalcul des montants de la facture: {e}")
    
    def delete(self, *args, **kwargs):
        """Supprime la ligne et recalcule les montants de la facture"""
        facture = self.facture
        super().delete(*args, **kwargs)
        
        # Recalculer les montants de la facture après suppression
        if facture:
            try:
                facture.calculer_montants()
            except Exception as e:
                print(f"Erreur lors du recalcul des montants après suppression: {e}")