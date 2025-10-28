from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from clients.models import Client

class Devis(models.Model):
    """Modèle pour les devis"""
    
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoye', 'Envoyé'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
        ('expire', 'Expiré'),
    ]
    
    numero = models.CharField(max_length=20, unique=True, verbose_name="Numéro")
    client = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE, 
        verbose_name="Client"
    )
    objet = models.CharField(max_length=200, verbose_name="Objet")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Montants
    montant_ht = models.DecimalField(
        max_digits=18, 
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
        max_digits=18, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Montant TVA"
    )
    montant_ttc = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Montant TTC"
    )
    
    # Statut et dates
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='brouillon',
        verbose_name="Statut"
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_validite = models.DateField(verbose_name="Date de validité")
    date_envoi = models.DateTimeField(null=True, blank=True, verbose_name="Date d'envoi")
    date_reponse = models.DateTimeField(null=True, blank=True, verbose_name="Date de réponse")
    
    # Conditions et notes
    conditions_paiement = models.TextField(blank=True, verbose_name="Conditions de paiement")
    notes = models.TextField(blank=True, verbose_name="Notes")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Devis"
        verbose_name_plural = "Devis"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Devis {self.numero} - {self.client.nom_complet}"
    
    def save(self, *args, **kwargs):
        """Sauvegarde avec préservation des champs automatiques"""
        # Si c'est une mise à jour (l'objet a déjà un ID)
        if self.pk:
            try:
                # Récupérer l'objet existant pour préserver les champs automatiques
                existing = Devis.objects.get(pk=self.pk)
                if not self.date_creation:
                    self.date_creation = existing.date_creation
            except Devis.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    def calculer_montants(self):
        """Calcule automatiquement les montants HT, TVA et TTC"""
        try:
            # Calculer le total HT de manière sécurisée
            total_ht = Decimal('0.00')
            for ligne in self.lignes.all():
                try:
                    if ligne.quantite and ligne.prix_unitaire_ht:
                        # Seulement limiter la quantité, pas les prix
                        quantite = min(Decimal(str(ligne.quantite)), Decimal('999999.99'))
                        prix = Decimal(str(ligne.prix_unitaire_ht))
                        ligne_montant = quantite * prix
                        total_ht += ligne_montant
                        
                except (TypeError, ValueError, InvalidOperation):
                    print(f"Problème avec la ligne {ligne.id}, utilisation de valeurs par défaut")
                    continue
            
            self.montant_ht = total_ht
            
            # Calculer la TVA
            try:
                if self.taux_tva:
                    taux_tva_limite = min(Decimal(str(self.taux_tva)), Decimal('100.00'))
                    self.montant_tva = self.montant_ht * (taux_tva_limite / Decimal('100'))
                else:
                    self.montant_tva = Decimal('0.00')
            except (TypeError, ValueError, InvalidOperation):
                self.montant_tva = Decimal('0.00')
            
            # Calculer le TTC
            try:
                self.montant_ttc = self.montant_ht + self.montant_tva
            except (TypeError, ValueError, InvalidOperation):
                self.montant_ttc = self.montant_ht
            
            # Sauvegarder sans déclencher les signaux
            self.save(update_fields=['montant_ht', 'montant_tva', 'montant_ttc'])
            
        except Exception as e:
            print(f"Erreur lors du calcul des montants: {e}")
            # En cas d'erreur, utiliser des valeurs par défaut
            self.montant_ht = Decimal('0.00')
            self.montant_tva = Decimal('0.00')
            self.montant_ttc = Decimal('0.00')
            self.save(update_fields=['montant_ht', 'montant_tva', 'montant_ttc'])
    
    def envoyer(self):
        """Marque le devis comme envoyé"""
        from django.utils import timezone
        self.statut = 'envoye'
        self.date_envoi = timezone.now()
        self.save()
    
    def accepter(self):
        """Marque le devis comme accepté"""
        from django.utils import timezone
        self.statut = 'accepte'
        self.date_reponse = timezone.now()
        self.save()
    
    def refuser(self):
        """Marque le devis comme refusé"""
        from django.utils import timezone
        self.statut = 'refuse'
        self.date_reponse = timezone.now()
        self.save()

class LigneDevis(models.Model):
    """Modèle pour les lignes de devis"""
    
    devis = models.ForeignKey(
        Devis, 
        on_delete=models.CASCADE, 
        related_name='lignes',
        verbose_name="Devis"
    )
    description = models.CharField(max_length=200, verbose_name="Description")
    quantite = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('1.00'),
        verbose_name="Quantité"
    )
    unite = models.CharField(max_length=20, default="unité", verbose_name="Unité")
    prix_unitaire_ht = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Prix unitaire HT"
    )
    montant_ht = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant HT"
    )
    
    class Meta:
        verbose_name = "Ligne de devis"
        verbose_name_plural = "Lignes de devis"
    
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
            
            # Sauvegarder la ligne SANS recalculer les montants du devis
            # pour éviter les boucles infinies et les erreurs de conversion
            super().save(*args, **kwargs)
                
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la ligne: {e}")
            # En cas d'erreur critique, utiliser des valeurs par défaut
            self.quantite = Decimal('1.00')
            self.prix_unitaire_ht = Decimal('0.00')
            self.montant_ht = Decimal('0.00')
            super().save(*args, **kwargs)
