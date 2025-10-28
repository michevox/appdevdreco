from django.db import models
from django.core.validators import MinValueValidator
from clients.models import Client
from devis.models import Devis
from fournisseurs.models import Fournisseur
from decimal import Decimal, InvalidOperation
from django.utils import timezone

class BonCommande(models.Model):
    """Modèle pour gérer les bons de commande (achats fournisseurs)"""
    
    TYPE_CHOICES = [
        ('achat', 'Achat fournisseur'),
        ('vente', 'Vente client'),
    ]
    
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoye', 'Envoyé'),
        ('confirme', 'Confirmé'),
        ('en_cours', 'En cours'),
        ('livre', 'Livré'),
        ('annule', 'Annulé'),
    ]
    
    # Informations de base
    numero = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Numéro de commande")
    type_commande = models.CharField(
        max_length=10, 
        choices=TYPE_CHOICES, 
        default='achat',
        verbose_name="Type de commande"
    )
    
    # Relations selon le type
    fournisseur = models.ForeignKey(
        Fournisseur, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        verbose_name="Fournisseur"
    )
    client = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        verbose_name="Client"
    )
    devis = models.ForeignKey(
        Devis, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        verbose_name="Devis associé"
    )
    # facture = models.ForeignKey(
    #     Facture, 
    #     on_delete=models.SET_NULL, 
    #     blank=True, 
    #     null=True,
    #     verbose_name="Facture associée"
    # )
    date_creation = models.DateField(auto_now_add=True, verbose_name="Date de création")
    date_livraison_souhaitee = models.DateField(verbose_name="Date de livraison souhaitée")
    
    # Statut et suivi
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='brouillon',
        verbose_name="Statut"
    )
    date_confirmation = models.DateTimeField(blank=True, null=True, verbose_name="Date de confirmation")
    date_livraison = models.DateField(blank=True, null=True, verbose_name="Date de livraison")
    
    # Informations commerciales
    objet = models.CharField(max_length=200, verbose_name="Objet de la commande")
    description = models.TextField(blank=True, null=True, verbose_name="Description détaillée")
    
    # Calculs
    montant_ht = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Montant HT"
    )
    taux_tva = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('18.00'),
        verbose_name="Taux TVA (%)"
    )
    montant_tva = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Montant TVA"
    )
    montant_ttc = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Montant TTC"
    )
    
    # Conditions
    conditions_livraison = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Conditions de livraison"
    )
    adresse_livraison = models.TextField(verbose_name="Adresse de livraison")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    
    # Métadonnées
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Bon de commande"
        verbose_name_plural = "Bons de commande"
        ordering = ['-date_creation']
    
    def __str__(self):
        if self.type_commande == 'achat' and self.fournisseur:
            return f"Commande {self.numero} - {self.fournisseur.nom}"
        elif self.type_commande == 'vente' and self.client:
            return f"Commande {self.numero} - {self.client.nom_complet}"
        else:
            return f"Commande {self.numero}"
    
    def generer_numero(self):
        """Génère automatiquement un numéro de commande unique"""
        from datetime import datetime
        
        # Format: CMD-AAAAMMJJ-XXX
        date_str = datetime.now().strftime('%Y%m%d')
        prefix = f"CMD-{date_str}"
        
        # Trouver le dernier numéro pour aujourd'hui
        derniere_commande = BonCommande.objects.filter(
            numero__startswith=prefix
        ).order_by('-numero').first()
        
        if derniere_commande:
            # Extraire le numéro séquentiel
            try:
                dernier_numero = int(derniere_commande.numero.split('-')[-1])
                nouveau_numero = dernier_numero + 1
            except (ValueError, IndexError):
                nouveau_numero = 1
        else:
            nouveau_numero = 1
        
        return f"{prefix}-{nouveau_numero:03d}"
    
    def save(self, *args, **kwargs):
        """Surcharge de la méthode save pour générer le numéro automatiquement"""
        if not self.numero:
            self.numero = self.generer_numero()
        super().save(*args, **kwargs)
    
    def calculer_montants(self):
        """Calcule automatiquement les montants HT, TVA et TTC"""
        try:
            print(f"Calcul des montants pour la commande {self.numero}")
            
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
    
    def confirmer(self):
        """Marque la commande comme confirmée"""
        from django.utils import timezone
        self.statut = 'confirme'
        self.date_confirmation = timezone.now()
        self.save()
    
    def livrer(self):
        """Marque la commande comme livrée"""
        from django.utils import timezone
        self.statut = 'livre'
        self.date_livraison = timezone.now().date()
        self.save()
    
    def annuler(self):
        """Marque la commande comme annulée"""
        self.statut = 'annule'
        self.save()

class LigneCommande(models.Model):
    """Modèle pour les lignes de commande"""
    
    commande = models.ForeignKey(
        BonCommande, 
        on_delete=models.CASCADE, 
        related_name='lignes',
        verbose_name="Commande"
    )
    description = models.CharField(max_length=200, verbose_name="Description")
    quantite = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Quantité"
    )
    unite = models.CharField(max_length=20, default="unité", verbose_name="Unité")
    prix_unitaire_ht = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Prix unitaire HT"
    )
    montant_ht = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        verbose_name="Montant HT"
    )
    
    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"
    
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
            
            # Limiter la quantité pour éviter les débordements
            self.quantite = min(self.quantite, Decimal('999999.99'))
            
            if not isinstance(self.prix_unitaire_ht, Decimal):
                try:
                    self.prix_unitaire_ht = Decimal(str(self.prix_unitaire_ht))
                except (ValueError, InvalidOperation):
                    self.prix_unitaire_ht = Decimal('0.00')
            
            # Limiter le prix unitaire pour éviter les débordements (max 9999999999999.99 = 15 digits)
            self.prix_unitaire_ht = min(self.prix_unitaire_ht, Decimal('9999999999999.99'))
            
            # Calculer le montant HT et le limiter aussi
            try:
                montant_calcule = self.quantite * self.prix_unitaire_ht
                self.montant_ht = min(montant_calcule, Decimal('9999999999999.99'))
            except (TypeError, ValueError, InvalidOperation):
                self.montant_ht = Decimal('0.00')
            
            # Sauvegarder la ligne
            super().save(*args, **kwargs)
            
            # Recalculer les montants de la commande après sauvegarde
            if hasattr(self, 'commande') and self.commande:
                try:
                    self.commande.calculer_montants()
                except Exception as e:
                    print(f"Erreur lors du recalcul des montants de la commande: {e}")
                
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la ligne: {e}")
            # En cas d'erreur critique, utiliser des valeurs par défaut
            self.quantite = Decimal('1.00')
            self.prix_unitaire_ht = Decimal('0.00')
            self.montant_ht = Decimal('0.00')
            super().save(*args, **kwargs)
            
            # Recalculer les montants de la commande même en cas d'erreur
            if hasattr(self, 'commande') and self.commande:
                try:
                    self.commande.calculer_montants()
                except Exception as e:
                    print(f"Erreur lors du recalcul des montants de la commande: {e}")
    
    def delete(self, *args, **kwargs):
        """Supprime la ligne et recalcule les montants de la commande"""
        commande = self.commande
        super().delete(*args, **kwargs)
        
        # Recalculer les montants de la commande après suppression
        if commande:
            try:
                commande.calculer_montants()
            except Exception as e:
                print(f"Erreur lors du recalcul des montants après suppression: {e}")
