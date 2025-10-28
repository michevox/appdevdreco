from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, date


class RapportVentes(models.Model):
    """Rapport de ventes par période"""
    TYPE_RAPPORT_CHOICES = [
        ('journalier', 'Journalier'),
        ('hebdomadaire', 'Hebdomadaire'),
        ('mensuel', 'Mensuel'),
        ('annuel', 'Annuel'),
        ('personnalise', 'Période personnalisée'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    nom = models.CharField(max_length=200, verbose_name="Nom du rapport")
    type_rapport = models.CharField(max_length=20, choices=TYPE_RAPPORT_CHOICES, default='mensuel')
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    format_sortie = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    inclure_devis = models.BooleanField(default=True, verbose_name="Inclure les devis")
    inclure_factures = models.BooleanField(default=True, verbose_name="Inclure les factures")
    inclure_commandes = models.BooleanField(default=True, verbose_name="Inclure les commandes")
    groupe_par_client = models.BooleanField(default=False, verbose_name="Grouper par client")
    groupe_par_article = models.BooleanField(default=False, verbose_name="Grouper par article")
    creer_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    date_creation = models.DateTimeField(auto_now_add=True)
    fichier_genere = models.FileField(upload_to='rapports/ventes/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Rapport de ventes"
        verbose_name_plural = "Rapports de ventes"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom} - {self.get_type_rapport_display()} ({self.date_debut} à {self.date_fin})"


class RapportClients(models.Model):
    """Rapport sur les clients"""
    TYPE_RAPPORT_CHOICES = [
        ('actifs', 'Clients actifs'),
        ('inactifs', 'Clients inactifs'),
        ('tous', 'Tous les clients'),
        ('nouveaux', 'Nouveaux clients'),
        ('fideles', 'Clients fidèles'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    nom = models.CharField(max_length=200, verbose_name="Nom du rapport")
    type_rapport = models.CharField(max_length=20, choices=TYPE_RAPPORT_CHOICES, default='tous')
    periode_debut = models.DateField(blank=True, null=True, verbose_name="Période début")
    periode_fin = models.DateField(blank=True, null=True, verbose_name="Période fin")
    format_sortie = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    inclure_statistiques = models.BooleanField(default=True, verbose_name="Inclure les statistiques")
    inclure_historique_achats = models.BooleanField(default=False, verbose_name="Inclure l'historique des achats")
    creer_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    date_creation = models.DateTimeField(auto_now_add=True)
    fichier_genere = models.FileField(upload_to='rapports/clients/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Rapport clients"
        verbose_name_plural = "Rapports clients"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom} - {self.get_type_rapport_display()}"


class RapportArticles(models.Model):
    """Rapport sur les articles"""
    TYPE_RAPPORT_CHOICES = [
        ('stock', 'État des stocks'),
        ('ventes', 'Articles les plus vendus'),
        ('moins_vendus', 'Articles moins vendus'),
        ('categorie', 'Par catégorie'),
        ('prix', 'Analyse des prix'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    nom = models.CharField(max_length=200, verbose_name="Nom du rapport")
    type_rapport = models.CharField(max_length=20, choices=TYPE_RAPPORT_CHOICES, default='stock')
    periode_debut = models.DateField(blank=True, null=True, verbose_name="Période début")
    periode_fin = models.DateField(blank=True, null=True, verbose_name="Période fin")
    format_sortie = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    inclure_categories = models.BooleanField(default=True, verbose_name="Inclure les catégories")
    inclure_prix = models.BooleanField(default=True, verbose_name="Inclure les prix")
    inclure_statistiques = models.BooleanField(default=True, verbose_name="Inclure les statistiques")
    creer_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    date_creation = models.DateTimeField(auto_now_add=True)
    fichier_genere = models.FileField(upload_to='rapports/articles/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Rapport articles"
        verbose_name_plural = "Rapports articles"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom} - {self.get_type_rapport_display()}"


class RapportFinancier(models.Model):
    """Rapport financier global"""
    TYPE_RAPPORT_CHOICES = [
        ('ca', 'Chiffre d\'affaires'),
        ('benefices', 'Bénéfices'),
        ('tresorerie', 'Trésorerie'),
        ('complet', 'Rapport financier complet'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    nom = models.CharField(max_length=200, verbose_name="Nom du rapport")
    type_rapport = models.CharField(max_length=20, choices=TYPE_RAPPORT_CHOICES, default='complet')
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    format_sortie = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    inclure_graphiques = models.BooleanField(default=True, verbose_name="Inclure les graphiques")
    inclure_details = models.BooleanField(default=True, verbose_name="Inclure les détails")
    creer_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    date_creation = models.DateTimeField(auto_now_add=True)
    fichier_genere = models.FileField(upload_to='rapports/financiers/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Rapport financier"
        verbose_name_plural = "Rapports financiers"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom} - {self.get_type_rapport_display()} ({self.date_debut} à {self.date_fin})"


class ConfigurationRapport(models.Model):
    """Configuration globale des rapports"""
    nom_societe = models.CharField(max_length=200, default="DEVDRECO SOFT", verbose_name="Nom de la société")
    logo_rapport = models.ImageField(upload_to='rapports/logos/', blank=True, null=True, verbose_name="Logo pour les rapports")
    couleur_principale = models.CharField(max_length=7, default="#007bff", verbose_name="Couleur principale")
    couleur_secondaire = models.CharField(max_length=7, default="#6c757d", verbose_name="Couleur secondaire")
    inclure_entete = models.BooleanField(default=True, verbose_name="Inclure l'en-tête")
    inclure_pied = models.BooleanField(default=True, verbose_name="Inclure le pied de page")
    format_date = models.CharField(max_length=20, default="%d/%m/%Y", verbose_name="Format de date")
    devise = models.CharField(max_length=10, default="GNF", verbose_name="Devise")
    
    class Meta:
        verbose_name = "Configuration des rapports"
        verbose_name_plural = "Configurations des rapports"
    
    def __str__(self):
        return f"Configuration - {self.nom_societe}"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule configuration
        if not self.pk and ConfigurationRapport.objects.exists():
            # Si c'est un nouvel objet et qu'il existe déjà une configuration, ne pas créer
            return
        super().save(*args, **kwargs)