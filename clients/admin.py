from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'nom_complet', 
        'type_client_display', 
        'telephone_formatted', 
        'email_display', 
        'statut_badge', 
        'date_creation'
    ]
    list_filter = [
        'type_client', 
        'actif', 
        'date_creation', 
        'date_modification'
    ]
    search_fields = [
        'nom_complet', 
        'telephone', 
        'email', 
        'adresse'
    ]
    readonly_fields = [
        'date_creation', 
        'date_modification'
    ]
    list_per_page = 20
    ordering = ['-date_creation']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('nom_complet', 'type_client', 'actif')
        }),
        ('Coordonnées', {
            'fields': ('telephone', 'email', 'adresse')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def type_client_display(self, obj):
        """Affichage du type de client avec icône"""
        icon = "👤" if obj.type_client == 'particulier' else "🏢"
        return format_html('{} {}', icon, obj.get_type_display_short())
    type_client_display.short_description = 'Type'
    type_client_display.admin_order_field = 'type_client'
    
    def telephone_formatted(self, obj):
        """Affichage du téléphone formaté"""
        if obj.telephone:
            return format_html(
                '<a href="tel:{}">{}</a>', 
                obj.telephone, 
                obj.get_telephone_formatted()
            )
        return '-'
    telephone_formatted.short_description = 'Téléphone'
    
    def email_display(self, obj):
        """Affichage de l'email avec lien"""
        if obj.email:
            return format_html(
                '<a href="mailto:{}">{}</a>', 
                obj.email, 
                obj.email
            )
        return '-'
    email_display.short_description = 'Email'
    
    def statut_badge(self, obj):
        """Affichage du statut avec badge coloré"""
        if obj.actif:
            return format_html(
                '<span class="badge bg-success">Actif</span>'
            )
        else:
            return format_html(
                '<span class="badge bg-secondary">Inactif</span>'
            )
    statut_badge.short_description = 'Statut'
    statut_badge.admin_order_field = 'actif'
    
    def get_queryset(self, request):
        """Optimisation des requêtes"""
        return super().get_queryset(request).select_related()
    
    def get_readonly_fields(self, request, obj=None):
        """Champs en lecture seule selon le contexte"""
        if obj:  # Mode édition
            return self.readonly_fields + ('date_creation',)
        return self.readonly_fields
    
    actions = ['activer_clients', 'desactiver_clients', 'exporter_clients']
    
    def activer_clients(self, request, queryset):
        """Action pour activer plusieurs clients"""
        updated = queryset.update(actif=True)
        self.message_user(
            request, 
            f'{updated} client(s) ont été activé(s) avec succès.'
        )
    activer_clients.short_description = "Activer les clients sélectionnés"
    
    def desactiver_clients(self, request, queryset):
        """Action pour désactiver plusieurs clients"""
        updated = queryset.update(actif=False)
        self.message_user(
            request, 
            f'{updated} client(s) ont été désactivé(s) avec succès.'
        )
    desactiver_clients.short_description = "Désactiver les clients sélectionnés"
    
    def exporter_clients(self, request, queryset):
        """Action pour exporter les clients sélectionnés"""
        import csv
        from django.http import HttpResponse
        from django.utils import timezone
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="clients_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Nom complet/Raison sociale',
            'Type',
            'Téléphone',
            'Email',
            'Adresse',
            'Statut',
            'Date de création',
            'Dernière modification'
        ])
        
        for client in queryset:
            writer.writerow([
                client.nom_complet,
                client.get_type_display_short(),
                client.telephone,
                client.email or '',
                client.adresse or '',
                'Actif' if client.actif else 'Inactif',
                client.date_creation.strftime('%d/%m/%Y %H:%M'),
                client.date_modification.strftime('%d/%m/%Y %H:%M')
            ])
        
        return response
    exporter_clients.short_description = "Exporter les clients sélectionnés"
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
