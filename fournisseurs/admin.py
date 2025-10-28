from django.contrib import admin
from .models import Fournisseur, ProduitFournisseur


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = [
        'nom_complet', 'type_fournisseur', 'telephone', 'email', 
        'ville', 'pays', 'actif', 'date_creation'
    ]
    list_filter = [
        'type_fournisseur', 'actif', 'pays', 'date_creation'
    ]
    search_fields = [
        'nom_complet', 'email', 'telephone', 'contact_principal', 'ville'
    ]
    list_editable = ['actif']
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations générales', {
            'fields': (
                'nom_complet', 'type_fournisseur', 'actif'
            )
        }),
        ('Contact', {
            'fields': (
                'telephone', 'email', 'contact_principal', 'fonction_contact'
            )
        }),
        ('Adresse', {
            'fields': (
                'adresse', 'ville', 'pays', 'site_web'
            )
        }),
        ('Conditions commerciales', {
            'fields': (
                'conditions_paiement', 'delai_livraison'
            )
        }),
        ('Métadonnées', {
            'fields': (
                'notes', 'date_creation', 'date_modification'
            ),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['nom_complet']
    date_hierarchy = 'date_creation'


@admin.register(ProduitFournisseur)
class ProduitFournisseurAdmin(admin.ModelAdmin):
    list_display = [
        'fournisseur', 'article', 'reference_fournisseur', 
        'prix_achat_ht', 'devise', 'delai_livraison', 'actif'
    ]
    list_filter = [
        'fournisseur', 'devise', 'actif', 'date_creation'
    ]
    search_fields = [
        'fournisseur__nom_complet', 'article__designation', 
        'reference_fournisseur'
    ]
    list_editable = ['prix_achat_ht', 'actif']
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations générales', {
            'fields': (
                'fournisseur', 'article', 'reference_fournisseur', 'actif'
            )
        }),
        ('Prix et conditions', {
            'fields': (
                'prix_achat_ht', 'devise', 'delai_livraison', 
                'quantite_minimale', 'stock_disponible'
            )
        }),
        ('Métadonnées', {
            'fields': (
                'notes', 'date_creation', 'date_modification'
            ),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['fournisseur__nom_complet', 'article__designation']
    date_hierarchy = 'date_creation'