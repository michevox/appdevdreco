from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.core.exceptions import ValidationError
from articles.models import Article
import re


class Fournisseur(models.Model):
    """Modèle pour gérer les fournisseurs"""
    
    TYPE_FOURNISSEUR_CHOICES = [
        ('particulier', 'Particulier'),
        ('entreprise', 'Entreprise'),
        ('grossiste', 'Grossiste'),
        ('fabricant', 'Fabricant'),
        ('importateur', 'Importateur'),
    ]
    
    # Informations de base
    nom_complet = models.CharField(
        max_length=200,
        verbose_name="Nom complet ou raison sociale",
        help_text="Nom du fournisseur ou raison sociale de l'entreprise"
    )
    
    type_fournisseur = models.CharField(
        max_length=20,
        choices=TYPE_FOURNISSEUR_CHOICES,
        default='entreprise',
        verbose_name="Type de fournisseur"
    )
    
    # Informations de contact
    telephone = models.CharField(
        max_length=20,
        default="+224 ",
        verbose_name="Téléphone",
        help_text="Numéro de téléphone avec indicatif pays"
    )
    
    email = models.EmailField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Email",
        validators=[EmailValidator()]
    )
    
    adresse = models.TextField(
        blank=True,
        null=True,
        verbose_name="Adresse complète"
    )
    
    ville = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ville"
    )
    
    pays = models.CharField(
        max_length=100,
        default="Guinée",
        verbose_name="Pays"
    )
    
    # Informations commerciales
    site_web = models.URLField(
        blank=True,
        null=True,
        verbose_name="Site web"
    )
    
    contact_principal = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Contact principal"
    )
    
    fonction_contact = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Fonction du contact"
    )
    
    # Informations financières
    conditions_paiement = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Conditions de paiement",
        help_text="Ex: 30 jours net, 2% 10 jours, etc."
    )
    
    delai_livraison = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Délai de livraison",
        help_text="Ex: 5-7 jours ouvrés"
    )
    
    # Statut et métadonnées
    actif = models.BooleanField(
        default=True,
        verbose_name="Fournisseur actif"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes internes"
    )
    
    # Timestamps
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['nom_complet']
        indexes = [
            models.Index(fields=['nom_complet']),
            models.Index(fields=['type_fournisseur']),
            models.Index(fields=['actif']),
        ]
    
    def __str__(self):
        return self.nom_complet
    
    def clean(self):
        super().clean()
        
        # Validation du nom complet
        if not self.nom_complet or not self.nom_complet.strip():
            raise ValidationError({'nom_complet': 'Le nom complet est obligatoire.'})
        
        # Validation de l'email si fourni
        if self.email:
            # Vérifier l'unicité de l'email
            queryset = Fournisseur.objects.filter(email=self.email)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError({'email': 'Cette adresse email est déjà utilisée par un autre fournisseur.'})
        
        # Validation du nom complet (unicité)
        queryset = Fournisseur.objects.filter(nom_complet=self.nom_complet)
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        if queryset.exists():
            raise ValidationError({'nom_complet': 'Un fournisseur avec ce nom existe déjà.'})
    
    def get_telephone_formate(self):
        """Retourne le téléphone formaté pour l'affichage"""
        if not self.telephone:
            return ""
        
        # Formatage basique du téléphone
        phone = re.sub(r'[^\d+]', '', self.telephone)
        if phone.startswith('+'):
            return phone
        elif phone.startswith('225'):
            return f"+{phone}"
        else:
            return f"+225 {phone}"
    
    def get_adresse_complete(self):
        """Retourne l'adresse complète formatée"""
        adresse_parts = []
        if self.adresse:
            adresse_parts.append(self.adresse)
        if self.ville:
            adresse_parts.append(self.ville)
        if self.pays:
            adresse_parts.append(self.pays)
        return ", ".join(adresse_parts) if adresse_parts else "Non renseignée"


class ProduitFournisseur(models.Model):
    """Modèle pour gérer les produits fournis par les fournisseurs"""
    
    fournisseur = models.ForeignKey(
        Fournisseur,
        on_delete=models.CASCADE,
        related_name='produits',
        verbose_name="Fournisseur"
    )
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='fournisseurs',
        verbose_name="Article"
    )
    
    # Informations commerciales
    reference_fournisseur = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Référence fournisseur",
        help_text="Référence du produit chez le fournisseur"
    )
    
    prix_achat_ht = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Prix d'achat HT",
        help_text="Prix d'achat hors taxes"
    )
    
    devise = models.CharField(
        max_length=3,
        default='XOF',
        verbose_name="Devise",
        help_text="Code devise (XOF, EUR, USD, etc.)"
    )
    
    # Conditions commerciales
    delai_livraison = models.PositiveIntegerField(
        default=0,
        verbose_name="Délai de livraison (jours)",
        help_text="Délai de livraison en jours"
    )
    
    quantite_minimale = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantité minimale de commande"
    )
    
    stock_disponible = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock disponible",
        help_text="Stock disponible chez le fournisseur"
    )
    
    # Statut
    actif = models.BooleanField(
        default=True,
        verbose_name="Produit actif"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes"
    )
    
    # Timestamps
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    class Meta:
        verbose_name = "Produit fournisseur"
        verbose_name_plural = "Produits fournisseurs"
        unique_together = ['fournisseur', 'article']
        ordering = ['fournisseur__nom_complet', 'article__designation']
        indexes = [
            models.Index(fields=['fournisseur', 'actif']),
            models.Index(fields=['article', 'actif']),
            models.Index(fields=['prix_achat_ht']),
        ]
    
    def __str__(self):
        return f"{self.fournisseur.nom_complet} - {self.article.designation}"
    
    def get_prix_achat_formate(self):
        """Retourne le prix d'achat formaté"""
        return f"{self.prix_achat_ht:,.2f} {self.devise}"
    
    def get_marge_brute(self):
        """Calcule la marge brute si le prix de vente est défini"""
        if hasattr(self.article, 'prix_unitaire_ht') and self.article.prix_unitaire_ht:
            marge = self.article.prix_unitaire_ht - self.prix_achat_ht
            return max(0, marge)  # Marge ne peut pas être négative
        return None
    
    def get_taux_marge(self):
        """Calcule le taux de marge en pourcentage"""
        marge = self.get_marge_brute()
        if marge is not None and self.prix_achat_ht > 0:
            return (marge / self.prix_achat_ht) * 100
        return None