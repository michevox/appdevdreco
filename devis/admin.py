from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Devis, LigneDevis

class LigneDevisInline(admin.TabularInline):
    """Inline pour les lignes de devis"""
    model = LigneDevis
    extra = 1
    fields = ['description', 'quantite', 'unite', 'prix_unitaire_ht', 'montant_ht']
    readonly_fields = ['montant_ht']

@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    """Configuration de l'interface d'administration pour les devis"""
    
    list_display = [
        'numero', 'client', 'objet', 'montant_ttc', 'statut', 
        'date_creation', 'date_validite'
    ]
    list_filter = [
        'statut', 'date_creation', 'date_validite', 'client__type_client'
    ]
    search_fields = [
        'numero', 'client__nom', 'objet'
    ]
    readonly_fields = [
        'montant_ht', 'montant_tva', 'montant_ttc', 
        'date_creation', 'date_modification'
    ]
    inlines = [LigneDevisInline]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('numero', 'client', 'objet', 'description')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_validite', 'date_envoi', 'date_reponse')
        }),
        ('Statut', {
            'fields': ('statut',)
        }),
        ('Calculs', {
            'fields': ('taux_tva', 'montant_ht', 'montant_tva', 'montant_ttc'),
            'classes': ('collapse',)
        }),
        ('Conditions', {
            'fields': ('conditions_paiement', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimise les requêtes avec select_related"""
        return super().get_queryset(request).select_related('client')
    
    def montant_ttc_colore(self, obj):
        """Affiche le montant TTC avec une couleur selon le statut"""
        if obj.statut == 'accepte':
            color = 'green'
        elif obj.statut == 'refuse':
            color = 'red'
        elif obj.statut == 'envoye':
            color = 'orange'
        else:
            color = 'black'
        
        return format_html(
            '<span style="color: {};">{:.2f} €</span>',
            color, obj.montant_ttc
        )
    montant_ttc_colore.short_description = 'Montant TTC'
    
    def lien_client(self, obj):
        """Affiche un lien vers le client"""
        if obj.client:
            url = reverse('admin:clients_client_change', args=[obj.client.pk])
            return format_html('<a href="{}">{}</a>', url, obj.client.nom_complet)
        return '-'
    lien_client.short_description = 'Client'
    
    actions = ['marquer_envoye', 'marquer_accepte', 'marquer_refuse']
    
    def marquer_envoye(self, request, queryset):
        """Action pour marquer les devis comme envoyés"""
        count = 0
        for devis in queryset:
            if devis.statut == 'brouillon':
                devis.envoyer()
                count += 1
        self.message_user(request, f'{count} devis marqués comme envoyés.')
    marquer_envoye.short_description = 'Marquer comme envoyé'
    
    def marquer_accepte(self, request, queryset):
        """Action pour marquer les devis comme acceptés"""
        count = 0
        for devis in queryset:
            if devis.statut == 'envoye':
                devis.accepter()
                count += 1
        self.message_user(request, f'{count} devis marqués comme acceptés.')
    marquer_accepte.short_description = 'Marquer comme accepté'
    
    def marquer_refuse(self, request, queryset):
        """Action pour marquer les devis comme refusés"""
        count = 0
        for devis in queryset:
            if devis.statut == 'envoye':
                devis.refuser()
                count += 1
        self.message_user(request, f'{count} devis marqués comme refusés.')
    marquer_refuse.short_description = 'Marquer comme refusé'
