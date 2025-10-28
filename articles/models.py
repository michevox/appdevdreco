from django.db import models
from django.utils import timezone


class Categorie(models.Model):
    """Modèle pour gérer les catégories d'articles"""
    
    libelle = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Libellé",
        help_text="Nom de la catégorie"
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
    actif = models.BooleanField(
        default=True,
        verbose_name="Catégorie active"
    )
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['libelle']
        indexes = [
            models.Index(fields=['libelle']),
            models.Index(fields=['actif']),
        ]
    
    def __str__(self):
        return self.libelle


class Article(models.Model):
    """Modèle pour gérer les articles"""
    
    designation = models.CharField(
        max_length=200,
        verbose_name="Désignation",
        help_text="Nom de l'article"
    )
    
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.CASCADE,
        verbose_name="Catégorie",
        help_text="Catégorie de l'article"
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
    actif = models.BooleanField(
        default=True,
        verbose_name="Article actif"
    )
    
    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['designation']
        indexes = [
            models.Index(fields=['designation']),
            models.Index(fields=['categorie']),
            models.Index(fields=['actif']),
        ]
    
    def __str__(self):
        return f"{self.designation} ({self.categorie.libelle})"