from django.contrib import admin
from django.utils.html import format_html
from .models import BonCommande, LigneCommande

class LigneCommandeInline(admin.TabularInline):
    """Inline pour les lignes de commande"""
    model = LigneCommande
    extra = 1
    fields = ['description', 'quantite', 'unite', 'prix_unitaire_ht', 'montant_ht']
    readonly_fields = ['montant_ht']
    
    def get_queryset(self, request):
        """Optimiser les requêtes"""
        return super().get_queryset(request).select_related('commande')

@admin.register(BonCommande)
class BonCommandeAdmin(admin.ModelAdmin):
    """Administration des bons de commande"""
    list_display = [
        'numero', 'client', 'objet', 'date_creation', 
        'date_livraison_souhaitee', 'statut', 'montant_ht', 'montant_ttc'
    ]
    list_filter = [
        'statut', 'date_creation', 'date_livraison_souhaitee', 
        'client__actif', 'devis__statut'
    ]
    search_fields = [
        'numero', 'client__nom', 'client__telephone', 'objet', 
        'description', 'adresse_livraison'
    ]
    readonly_fields = [
        'date_creation', 'date_modification', 'montant_ht', 
        'montant_tva', 'montant_ttc'
    ]
    date_hierarchy = 'date_creation'
    ordering = ['-date_creation']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('numero', 'client', 'devis', 'objet', 'description')
        }),
        ('Dates et statut', {
            'fields': ('date_creation', 'date_livraison_souhaitee', 'statut', 'date_confirmation', 'date_livraison')
        }),
        ('Informations commerciales', {
            'fields': ('taux_tva', 'montant_ht', 'montant_tva', 'montant_ttc')
        }),
        ('Livraison et conditions', {
            'fields': ('adresse_livraison', 'conditions_livraison', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('date_modification',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [LigneCommandeInline]
    
    def get_queryset(self, request):
        """Optimiser les requêtes avec select_related"""
        return super().get_queryset(request).select_related(
            'client', 'devis', 'facture'
        ).prefetch_related('lignes')
    
    def save_formset(self, request, form, formset, change):
        """Sauvegarder le formset et recalculer les montants"""
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()
        
        # Recalculer les montants de la commande
        if instances:
            commande = instances[0].commande
            commande.calculer_montants()
    
    def save_model(self, request, obj, form, change):
        """Sauvegarder le modèle et recalculer les montants"""
        super().save_model(request, obj, form, change)
        obj.calculer_montants()
    
    def get_readonly_fields(self, request, obj=None):
        """Champs en lecture seule selon le statut"""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        if obj and obj.statut in ['livre', 'annule']:
            readonly_fields.extend(['statut', 'date_livraison'])
        
        return readonly_fields
    
    def get_actions(self, request):
        """Actions disponibles selon les permissions"""
        actions = super().get_actions(request)
        
        if not request.user.has_perm('commandes.change_boncommande'):
            if 'confirmer_commandes' in actions:
                del actions['confirmer_commandes']
            if 'envoyer_commandes' in actions:
                del actions['envoyer_commandes']
        
        return actions
    
    actions = ['confirmer_commandes', 'envoyer_commandes', 'marquer_en_cours', 'marquer_livrees']
    
    def confirmer_commandes(self, request, queryset):
        """Marquer les commandes comme confirmées"""
        count = 0
        for commande in queryset.filter(statut='envoye'):
            commande.confirmer()
            count += 1
        
        if count == 1:
            message = "1 commande a été confirmée."
        else:
            message = f"{count} commandes ont été confirmées."
        
        self.message_user(request, message)
    confirmer_commandes.short_description = "Confirmer les commandes sélectionnées"
    
    def envoyer_commandes(self, request, queryset):
        """Marquer les commandes comme envoyées"""
        count = 0
        for commande in queryset.filter(statut='brouillon'):
            commande.statut = 'envoye'
            commande.save()
            count += 1
        
        if count == 1:
            message = "1 commande a été envoyée."
        else:
            message = f"{count} commandes ont été envoyées."
        
        self.message_user(request, message)
    envoyer_commandes.short_description = "Envoyer les commandes sélectionnées"
    
    def marquer_en_cours(self, request, queryset):
        """Marquer les commandes comme en cours"""
        count = 0
        for commande in queryset.filter(statut='confirme'):
            commande.statut = 'en_cours'
            commande.save()
            count += 1
        
        if count == 1:
            message = "1 commande a été mise en cours."
        else:
            message = f"{count} commandes ont été mises en cours."
        
        self.message_user(request, message)
    marquer_en_cours.short_description = "Marquer en cours les commandes sélectionnées"
    
    def marquer_livrees(self, request, queryset):
        """Marquer les commandes comme livrées"""
        count = 0
        for commande in queryset.filter(statut='en_cours'):
            commande.livrer()
            count += 1
        
        if count == 1:
            message = "1 commande a été marquée comme livrée."
        else:
            message = f"{count} commandes ont été marquées comme livrées."
        
        self.message_user(request, message)
    marquer_livrees.short_description = "Marquer comme livrées les commandes sélectionnées"

@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):
    """Administration des lignes de commande"""
    list_display = [
        'commande', 'description', 'quantite', 'unite', 
        'prix_unitaire_ht', 'montant_ht'
    ]
    list_filter = ['unite', 'commande__statut', 'commande__client']
    search_fields = [
        'description', 'commande__numero', 'commande__client__nom'
    ]
    readonly_fields = ['montant_ht']
    ordering = ['-commande__date_creation', 'id']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('commande', 'description', 'quantite', 'unite')
        }),
        ('Prix et montants', {
            'fields': ('prix_unitaire_ht', 'montant_ht')
        }),
    )
    
    def get_queryset(self, request):
        """Optimiser les requêtes"""
        return super().get_queryset(request).select_related(
            'commande', 'commande__client'
        )
    
    def save_model(self, request, obj, form, change):
        """Sauvegarder et recalculer les montants"""
        super().save_model(request, obj, form, change)
        obj.commande.calculer_montants()
    
    def has_add_permission(self, request):
        """Empêcher l'ajout direct de lignes"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Autoriser la suppression des lignes"""
        return True
