from django.contrib import admin
from django.contrib.admin import AdminSite

class DevdrecoSoftAdminSite(AdminSite):
    """Site d'administration personnalisé pour DEVDRECO SOFT"""
    
    site_header = "DEVDRECO SOFT - Administration"
    site_title = "DEVDRECO SOFT Admin"
    index_title = "Tableau de bord DEVDRECO SOFT"
    
    def get_app_list(self, request):
        """Personnalise l'ordre des applications dans l'admin"""
        app_list = super().get_app_list(request)
        
        # Réorganiser les applications
        app_ordering = {
            'core': 1,
            'clients': 2,
            'devis': 3,
            'factures': 4,
            'commandes': 5,
            'auth': 6,
        }
        
        # Trier les applications selon l'ordre défini
        app_list.sort(key=lambda x: app_ordering.get(x['app_label'], 999))
        
        return app_list

# Personnaliser l'admin par défaut
admin.site.site_header = "DEVDRECO SOFT - Administration"
admin.site.site_title = "DEVDRECO SOFT Admin"
admin.site.index_title = "Tableau de bord DEVDRECO SOFT"

# Personnaliser les couleurs de l'admin
admin.site.site_url = "/" 