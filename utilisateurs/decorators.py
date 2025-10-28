from functools import wraps
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import UtilisateurProfile


def permission_required(permission_code, redirect_url=None, message="Vous n'avez pas les permissions nécessaires pour accéder à cette page."):
    """
    Décorateur pour vérifier les permissions utilisateur
    
    Args:
        permission_code (str): Code de la permission requise
        redirect_url (str): URL de redirection en cas de refus
        message (str): Message d'erreur à afficher
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('core:home')
            
            # Récupérer le profil utilisateur
            try:
                profile = request.user.user_profile
            except UtilisateurProfile.DoesNotExist:
                messages.error(request, "Profil utilisateur non trouvé.")
                return redirect('core:home')
            
            # Vérifier la permission
            if not profile.a_permission(permission_code):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': True,
                        'message': message
                    }, status=403)
                
                if redirect_url:
                    messages.error(request, message)
                    return redirect(redirect_url)
                else:
                    return render(request, 'utilisateurs/403.html', {
                        'message': message,
                        'permission_requise': permission_code
                    }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def permission_module_required(module, action, redirect_url=None, message=None):
    """
    Décorateur pour vérifier les permissions par module et action
    
    Args:
        module (str): Module concerné
        action (str): Action requise
        redirect_url (str): URL de redirection en cas de refus
        message (str): Message d'erreur personnalisé
    """
    if message is None:
        message = f"Vous n'avez pas les permissions pour {action} dans le module {module}."
    
    permission_code = f"{module}.{action}"
    return permission_required(permission_code, redirect_url, message)


def admin_required(redirect_url=None):
    """
    Décorateur pour vérifier que l'utilisateur est administrateur
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('core:home')
            
            try:
                profile = request.user.user_profile
            except UtilisateurProfile.DoesNotExist:
                messages.error(request, "Profil utilisateur non trouvé.")
                return redirect('core:home')
            
            if not profile.est_administrateur:
                message = "Accès réservé aux administrateurs."
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': True,
                        'message': message
                    }, status=403)
                
                if redirect_url:
                    messages.error(request, message)
                    return redirect(redirect_url)
                else:
                    return render(request, 'utilisateurs/403.html', {
                        'message': message
                    }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def manager_required(redirect_url=None):
    """
    Décorateur pour vérifier que l'utilisateur est manager ou administrateur
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('core:home')
            
            try:
                profile = request.user.user_profile
            except UtilisateurProfile.DoesNotExist:
                messages.error(request, "Profil utilisateur non trouvé.")
                return redirect('core:home')
            
            if not (profile.est_administrateur or profile.est_manager):
                message = "Accès réservé aux managers et administrateurs."
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': True,
                        'message': message
                    }, status=403)
                
                if redirect_url:
                    messages.error(request, message)
                    return redirect(redirect_url)
                else:
                    return render(request, 'utilisateurs/403.html', {
                        'message': message
                    }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def ajax_permission_required(permission_code):
    """
    Décorateur pour les requêtes AJAX avec vérification de permission
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'error': True,
                    'message': 'Authentification requise'
                }, status=401)
            
            try:
                profile = request.user.user_profile
            except UtilisateurProfile.DoesNotExist:
                return JsonResponse({
                    'error': True,
                    'message': 'Profil utilisateur non trouvé'
                }, status=403)
            
            if not profile.a_permission(permission_code):
                return JsonResponse({
                    'error': True,
                    'message': 'Permissions insuffisantes'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def class_permission_required(permission_code):
    """
    Décorateur de classe pour les vues basées sur les classes
    """
    def decorator(cls):
        original_dispatch = cls.dispatch
        
        def dispatch(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('core:home')
            
            try:
                profile = request.user.user_profile
            except UtilisateurProfile.DoesNotExist:
                messages.error(request, "Profil utilisateur non trouvé.")
                return redirect('core:home')
            
            if not profile.a_permission(permission_code):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': True,
                        'message': 'Permissions insuffisantes'
                    }, status=403)
                
                return render(request, 'utilisateurs/403.html', {
                    'message': 'Vous n\'avez pas les permissions nécessaires.',
                    'permission_requise': permission_code
                }, status=403)
            
            return original_dispatch(self, request, *args, **kwargs)
        
        cls.dispatch = dispatch
        return cls
    return decorator