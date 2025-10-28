from django.contrib import admin
from .models import RapportVentes, RapportClients, RapportArticles, RapportFinancier, ConfigurationRapport


@admin.register(RapportVentes)
class RapportVentesAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_rapport', 'date_debut', 'date_fin', 'format_sortie', 'creer_par', 'date_creation']
    list_filter = ['type_rapport', 'format_sortie', 'date_creation', 'creer_par']
    search_fields = ['nom', 'creer_par__username', 'creer_par__first_name', 'creer_par__last_name']
    readonly_fields = ['date_creation', 'fichier_genere']
    ordering = ['-date_creation']


@admin.register(RapportClients)
class RapportClientsAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_rapport', 'periode_debut', 'periode_fin', 'format_sortie', 'creer_par', 'date_creation']
    list_filter = ['type_rapport', 'format_sortie', 'date_creation', 'creer_par']
    search_fields = ['nom', 'creer_par__username', 'creer_par__first_name', 'creer_par__last_name']
    readonly_fields = ['date_creation', 'fichier_genere']
    ordering = ['-date_creation']


@admin.register(RapportArticles)
class RapportArticlesAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_rapport', 'periode_debut', 'periode_fin', 'format_sortie', 'creer_par', 'date_creation']
    list_filter = ['type_rapport', 'format_sortie', 'date_creation', 'creer_par']
    search_fields = ['nom', 'creer_par__username', 'creer_par__first_name', 'creer_par__last_name']
    readonly_fields = ['date_creation', 'fichier_genere']
    ordering = ['-date_creation']


@admin.register(RapportFinancier)
class RapportFinancierAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_rapport', 'date_debut', 'date_fin', 'format_sortie', 'creer_par', 'date_creation']
    list_filter = ['type_rapport', 'format_sortie', 'date_creation', 'creer_par']
    search_fields = ['nom', 'creer_par__username', 'creer_par__first_name', 'creer_par__last_name']
    readonly_fields = ['date_creation', 'fichier_genere']
    ordering = ['-date_creation']


@admin.register(ConfigurationRapport)
class ConfigurationRapportAdmin(admin.ModelAdmin):
    list_display = ['nom_societe', 'devise', 'couleur_principale', 'couleur_secondaire']
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom_societe', 'logo_rapport', 'devise')
        }),
        ('Apparence', {
            'fields': ('couleur_principale', 'couleur_secondaire')
        }),
        ('Options', {
            'fields': ('inclure_entete', 'inclure_pied', 'format_date')
        }),
    )
    
    def has_add_permission(self, request):
        # Permettre seulement une configuration
        return not ConfigurationRapport.objects.exists()