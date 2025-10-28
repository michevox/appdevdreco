from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Permission, Role, RolePermission, UtilisateurProfile


@receiver(post_migrate)
def creer_permissions_par_defaut(sender, **kwargs):
    """Crée les permissions par défaut après les migrations"""
    if sender.name == 'utilisateurs':
        creer_permissions_systeme()
        creer_roles_par_defaut()


def creer_permissions_systeme():
    """Crée toutes les permissions du système"""
    
    # Définir toutes les permissions par module
    permissions_data = {
        'clients': ['view', 'add', 'change', 'delete', 'export', 'print'],
        'devis': ['view', 'add', 'change', 'delete', 'export', 'print'],
        'factures': ['view', 'add', 'change', 'delete', 'export', 'print'],
        'commandes': ['view', 'add', 'change', 'delete', 'export', 'print'],
        'articles': ['view', 'add', 'change', 'delete', 'export', 'import'],
        'fournisseurs': ['view', 'add', 'change', 'delete', 'export', 'print'],
        'rapports': ['view', 'export', 'print'],
        'parametres': ['view', 'change'],
        'utilisateurs': ['view', 'add', 'change', 'delete'],
    }
    
    for module, actions in permissions_data.items():
        for action in actions:
            code = f"{module}.{action}"
            nom = f"{module.title()} - {action.title()}"
            
            permission, created = Permission.objects.get_or_create(
                code=code,
                defaults={
                    'nom': nom,
                    'module': module,
                    'action': action,
                    'description': f"Permission pour {action} dans le module {module}"
                }
            )
            
            if created:
                print(f"Permission créée: {permission}")


def creer_roles_par_defaut():
    """Crée les rôles par défaut avec leurs permissions"""
    
    # Rôle Administrateur
    role_admin, created = Role.objects.get_or_create(
        nom='Administrateur',
        defaults={
            'description': 'Accès complet à toutes les fonctionnalités',
            'type_role': 'admin'
        }
    )
    
    if created:
        # L'administrateur a toutes les permissions
        for permission in Permission.objects.all():
            RolePermission.objects.create(
                role=role_admin,
                permission=permission,
                accordee=True
            )
        print(f"Rôle créé: {role_admin}")
    
    # Rôle Manager
    role_manager, created = Role.objects.get_or_create(
        nom='Manager',
        defaults={
            'description': 'Accès à la gestion et aux rapports',
            'type_role': 'manager'
        }
    )
    
    if created:
        # Le manager a accès à tout sauf la gestion des utilisateurs
        permissions_manager = Permission.objects.exclude(module='utilisateurs')
        for permission in permissions_manager:
            RolePermission.objects.create(
                role=role_manager,
                permission=permission,
                accordee=True
            )
        print(f"Rôle créé: {role_manager}")
    
    # Rôle Utilisateur Standard
    role_standard, created = Role.objects.get_or_create(
        nom='Utilisateur Standard',
        defaults={
            'description': 'Accès de base aux fonctionnalités principales',
            'type_role': 'standard'
        }
    )
    
    if created:
        # L'utilisateur standard a accès en lecture et création pour les modules principaux
        modules_standard = ['clients', 'devis', 'articles']
        actions_standard = ['view', 'add']
        
        for module in modules_standard:
            for action in actions_standard:
                try:
                    permission = Permission.objects.get(module=module, action=action)
                    RolePermission.objects.create(
                        role=role_standard,
                        permission=permission,
                        accordee=True
                    )
                except Permission.DoesNotExist:
                    pass
        
        print(f"Rôle créé: {role_standard}")
    
    # Rôle Lecture Seule
    role_readonly, created = Role.objects.get_or_create(
        nom='Lecture Seule',
        defaults={
            'description': 'Accès en lecture seule',
            'type_role': 'readonly'
        }
    )
    
    if created:
        # Lecture seule pour tous les modules
        permissions_readonly = Permission.objects.filter(action='view')
        for permission in permissions_readonly:
            RolePermission.objects.create(
                role=role_readonly,
                permission=permission,
                accordee=True
            )
        print(f"Rôle créé: {role_readonly}")


def creer_profil_utilisateur(sender, instance, created, **kwargs):
    """Crée automatiquement un profil utilisateur lors de la création d'un utilisateur"""
    if created:
        # Récupérer le rôle par défaut (Utilisateur Standard)
        role_default = Role.objects.filter(nom='Utilisateur Standard').first()
        
        UtilisateurProfile.objects.create(
            user=instance,
            role=role_default
        )


# Connecter le signal
from django.db.models.signals import post_save
post_save.connect(creer_profil_utilisateur, sender=User)
