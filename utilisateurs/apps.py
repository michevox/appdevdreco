from django.apps import AppConfig


class UtilisateursConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utilisateurs'
    verbose_name = 'Gestion des utilisateurs'
    
    def ready(self):
        """Import des signaux lors du démarrage de l'application"""
        import utilisateurs.signals