from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from .models import UtilisateurProfile, Permission, Role


def get_user_permissions(user):
    """
    Retourne toutes les permissions d'un utilisateur
    
    Args:
        user: Instance de User Django
        
    Returns:
        dict: Dictionnaire avec les permissions accordées et refusées
    """
    if not user.is_authenticated:
        return {'accordees': set(), 'refusees': set()}
    
    try:
        profile = user.user_profile
        return {
            'accordees': profile.get_permissions_accordees(),
            'refusees': profile.get_permissions_refusees()
        }
    except UtilisateurProfile.DoesNotExist:
        return {'accordees': set(), 'refusees': set()}


def user_has_permission(user, permission_code):
    """
    Vérifie si un utilisateur a une permission spécifique
    
    Args:
        user: Instance de User Django
        permission_code (str): Code de la permission
        
    Returns:
        bool: True si l'utilisateur a la permission
    """
    if not user.is_authenticated:
        return False
    
    try:
        profile = user.user_profile
        return profile.a_permission(permission_code)
    except UtilisateurProfile.DoesNotExist:
        return False


def user_has_module_permission(user, module, action):
    """
    Vérifie si un utilisateur a une permission pour un module et une action
    
    Args:
        user: Instance de User Django
        module (str): Module concerné
        action (str): Action requise
        
    Returns:
        bool: True si l'utilisateur a la permission
    """
    permission_code = f"{module}.{action}"
    return user_has_permission(user, permission_code)


def is_admin(user):
    """
    Vérifie si un utilisateur est administrateur
    
    Args:
        user: Instance de User Django
        
    Returns:
        bool: True si l'utilisateur est administrateur
    """
    if not user.is_authenticated:
        return False
    
    return user.is_superuser or (hasattr(user, 'user_profile') and user.user_profile.est_administrateur)


def is_manager(user):
    """
    Vérifie si un utilisateur est manager ou administrateur
    
    Args:
        user: Instance de User Django
        
    Returns:
        bool: True si l'utilisateur est manager ou administrateur
    """
    if not user.is_authenticated:
        return False
    
    if is_admin(user):
        return True
    
    try:
        return user.user_profile.est_manager
    except UtilisateurProfile.DoesNotExist:
        return False


def get_accessible_modules(user):
    """
    Retourne la liste des modules accessibles à un utilisateur
    
    Args:
        user: Instance de User Django
        
    Returns:
        list: Liste des modules accessibles
    """
    if not user.is_authenticated:
        return []
    
    if is_admin(user):
        # Les administrateurs ont accès à tous les modules
        return [choice[0] for choice in Permission.MODULES]
    
    try:
        profile = user.user_profile
        permissions = profile.get_permissions_accordees()
        
        modules = set()
        for permission_code in permissions:
            module = permission_code.split('.')[0]
            modules.add(module)
        
        return list(modules)
    except UtilisateurProfile.DoesNotExist:
        return []


def get_module_permissions(user, module):
    """
    Retourne les permissions d'un utilisateur pour un module spécifique
    
    Args:
        user: Instance de User Django
        module (str): Module concerné
        
    Returns:
        dict: Dictionnaire des permissions pour le module
    """
    if not user.is_authenticated:
        return {}
    
    if is_admin(user):
        # Les administrateurs ont toutes les permissions
        return {action: True for action, _ in Permission.ACTIONS}
    
    try:
        profile = user.user_profile
        permissions = {}
        
        for action, _ in Permission.ACTIONS:
            permission_code = f"{module}.{action}"
            permissions[action] = profile.a_permission(permission_code)
        
        return permissions
    except UtilisateurProfile.DoesNotExist:
        return {}


def filter_queryset_by_permissions(user, queryset, model_name):
    """
    Filtre un queryset selon les permissions de l'utilisateur
    
    Args:
        user: Instance de User Django
        queryset: QuerySet à filtrer
        model_name (str): Nom du modèle (pour déterminer les permissions)
        
    Returns:
        QuerySet: QuerySet filtré
    """
    if not user.is_authenticated:
        return queryset.none()
    
    if is_admin(user):
        return queryset
    
    try:
        profile = user.user_profile
        
        # Vérifier les permissions de lecture
        if not profile.a_permission_module(model_name.lower(), 'view'):
            return queryset.none()
        
        # Ici, on pourrait ajouter des filtres plus spécifiques
        # selon les besoins métier (par exemple, filtrer par département)
        
        return queryset
    except UtilisateurProfile.DoesNotExist:
        return queryset.none()


def create_user_with_role(username, email, password, role_name, **kwargs):
    """
    Crée un utilisateur avec un rôle spécifique
    
    Args:
        username (str): Nom d'utilisateur
        email (str): Email
        password (str): Mot de passe
        role_name (str): Nom du rôle
        **kwargs: Arguments supplémentaires pour le profil
        
    Returns:
        User: Instance de l'utilisateur créé
    """
    # Créer l'utilisateur Django
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    # Récupérer le rôle
    try:
        role = Role.objects.get(nom=role_name)
    except Role.DoesNotExist:
        raise ValueError(f"Rôle '{role_name}' non trouvé")
    
    # Créer le profil
    profile = UtilisateurProfile.objects.create(
        user=user,
        role=role,
        **kwargs
    )
    
    return user


def update_user_permissions(user, permissions_dict):
    """
    Met à jour les permissions personnalisées d'un utilisateur
    
    Args:
        user: Instance de User Django
        permissions_dict (dict): Dictionnaire {permission_code: accordee}
    """
    if not user.is_authenticated:
        return
    
    try:
        profile = user.user_profile
        
        for permission_code, accordee in permissions_dict.items():
            try:
                permission = Permission.objects.get(code=permission_code)
                
                # Créer ou mettre à jour la permission personnalisée
                from .models import UtilisateurPermission
                up, created = UtilisateurPermission.objects.get_or_create(
                    utilisateur=profile,
                    permission=permission,
                    defaults={'accordee': accordee}
                )
                
                if not created:
                    up.accordee = accordee
                    up.save()
                    
            except Permission.DoesNotExist:
                continue
                
    except UtilisateurProfile.DoesNotExist:
        return


def get_permission_context(user):
    """
    Retourne un contexte avec toutes les informations de permissions pour les templates
    
    Args:
        user: Instance de User Django
        
    Returns:
        dict: Contexte pour les templates
    """
    if not user.is_authenticated:
        return {
            'is_admin': False,
            'is_manager': False,
            'accessible_modules': [],
            'permissions': {}
        }
    
    try:
        profile = user.user_profile
        return {
            'is_admin': profile.est_administrateur,
            'is_manager': profile.est_manager,
            'accessible_modules': get_accessible_modules(user),
            'permissions': {
                module: get_module_permissions(user, module)
                for module in get_accessible_modules(user)
            },
            'user_profile': profile
        }
    except UtilisateurProfile.DoesNotExist:
        return {
            'is_admin': False,
            'is_manager': False,
            'accessible_modules': [],
            'permissions': {}
        }
