from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import UtilisateurProfile, ConnexionUtilisateur
from .utils import get_permission_context
import time


class PermissionMiddleware(MiddlewareMixin):
    """
    Middleware pour vérifier les permissions utilisateur sur toutes les requêtes
    """
    
    # URLs qui ne nécessitent pas de vérification de permissions
    EXEMPT_URLS = [
        '/login/',
        '/logout/',
        '/admin/',
        '/static/',
        '/media/',
        '/favicon.ico',
        '/home/',
        '/ajax-login/',
    ]
    
    # URLs qui nécessitent une authentification mais pas de permissions spécifiques
    AUTH_REQUIRED_URLS = [
        '/dashboard/',
        '/profile/',
    ]
    
    def process_request(self, request):
        """
        Traite chaque requête pour vérifier les permissions
        """
        # Ignorer les requêtes pour les fichiers statiques et les URLs exemptées
        if any(request.path.startswith(url) for url in self.EXEMPT_URLS):
            return None
        
        # Vérifier l'authentification pour les URLs protégées
        if not request.user.is_authenticated:
            if request.path not in ['/', '/home/']:
                return redirect('core:home')
            return None
        
        # Ajouter les informations de permissions au contexte de la requête
        request.permissions = get_permission_context(request.user)
        
        # Vérifier les permissions spécifiques selon l'URL
        return self.check_url_permissions(request)
    
    def check_url_permissions(self, request):
        """
        Vérifie les permissions selon l'URL demandée
        """
        path = request.path
        
        # Mapping des URLs vers les permissions requises
        url_permissions = {
            '/clients/': 'clients.view',
            '/clients/ajouter/': 'clients.add',
            '/clients/modifier/': 'clients.change',
            '/clients/supprimer/': 'clients.delete',
            '/clients/exporter/': 'clients.export',
            
            '/devis/': 'devis.view',
            '/devis/ajouter/': 'devis.add',
            '/devis/modifier/': 'devis.change',
            '/devis/supprimer/': 'devis.delete',
            '/devis/exporter/': 'devis.export',
            '/devis/imprimer/': 'devis.print',
            
            '/factures/': 'factures.view',
            '/factures/ajouter/': 'factures.add',
            '/factures/modifier/': 'factures.change',
            '/factures/supprimer/': 'factures.delete',
            '/factures/exporter/': 'factures.export',
            '/factures/imprimer/': 'factures.print',
            
            '/commandes/': 'commandes.view',
            '/commandes/ajouter/': 'commandes.add',
            '/commandes/modifier/': 'commandes.change',
            '/commandes/supprimer/': 'commandes.delete',
            '/commandes/exporter/': 'commandes.export',
            '/commandes/imprimer/': 'commandes.print',
            
            '/articles/': 'articles.view',
            '/articles/ajouter/': 'articles.add',
            '/articles/modifier/': 'articles.change',
            '/articles/supprimer/': 'articles.delete',
            '/articles/exporter/': 'articles.export',
            '/articles/importer/': 'articles.import',
            
            '/fournisseurs/': 'fournisseurs.view',
            '/fournisseurs/ajouter/': 'fournisseurs.add',
            '/fournisseurs/modifier/': 'fournisseurs.change',
            '/fournisseurs/supprimer/': 'fournisseurs.delete',
            '/fournisseurs/exporter/': 'fournisseurs.export',
            
            '/rapports/': 'rapports.view',
            '/rapports/exporter/': 'rapports.export',
            '/rapports/imprimer/': 'rapports.print',
            
            '/parametres/': 'parametres.view',
            '/parametres/modifier/': 'parametres.change',
            
            '/utilisateurs/': 'utilisateurs.view',
            '/utilisateurs/ajouter/': 'utilisateurs.add',
            '/utilisateurs/modifier/': 'utilisateurs.change',
            '/utilisateurs/supprimer/': 'utilisateurs.delete',
        }
        
        # Vérifier les permissions pour l'URL actuelle
        for url_pattern, required_permission in url_permissions.items():
            if path.startswith(url_pattern):
                if not self.has_permission(request.user, required_permission):
                    return self.handle_permission_denied(request, required_permission)
                break
        
        return None
    
    def has_permission(self, user, permission_code):
        """
        Vérifie si l'utilisateur a une permission spécifique
        """
        if not user.is_authenticated:
            return False
        
        try:
            profile = user.user_profile
            return profile.a_permission(permission_code)
        except UtilisateurProfile.DoesNotExist:
            return False
    
    def handle_permission_denied(self, request, permission_code):
        """
        Gère le refus de permission
        """
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponseForbidden('Permissions insuffisantes')
        
        messages.error(request, f"Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('core:dashboard')


class ConnexionMiddleware(MiddlewareMixin):
    """
    Middleware pour tracer les connexions utilisateur
    """
    
    def process_request(self, request):
        """
        Enregistre les informations de connexion
        """
        if request.user.is_authenticated:
            # Mettre à jour la dernière connexion
            try:
                profile = request.user.user_profile
                profile.derniere_connexion = timezone.now()
                profile.save(update_fields=['derniere_connexion'])
            except UtilisateurProfile.DoesNotExist:
                pass
            
            # Enregistrer la connexion si c'est une nouvelle session
            if not hasattr(request.session, 'connexion_enregistree'):
                ConnexionUtilisateur.objects.create(
                    utilisateur=request.user,
                    adresse_ip=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    reussie=True
                )
                request.session['connexion_enregistree'] = True
        
        return None
    
    def get_client_ip(self, request):
        """
        Récupère l'adresse IP du client
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class NavigationMiddleware(MiddlewareMixin):
    """
    Middleware pour ajouter les informations de navigation selon les permissions
    """
    
    def process_request(self, request):
        """
        Ajoute les informations de navigation au contexte
        """
        if request.user.is_authenticated:
            try:
                profile = request.user.user_profile
                
                # Définir les éléments de navigation selon les permissions
                navigation_items = []
                
                # Dashboard (toujours accessible)
                navigation_items.append({
                    'name': 'Tableau de bord',
                    'url': '/dashboard/',
                    'icon': 'fas fa-tachometer-alt',
                    'active': request.path == '/dashboard/'
                })
                
                # Clients
                if profile.a_permission('clients.view'):
                    navigation_items.append({
                        'name': 'Clients',
                        'url': '/clients/',
                        'icon': 'fas fa-users',
                        'active': request.path.startswith('/clients/')
                    })
                
                # Devis
                if profile.a_permission('devis.view'):
                    navigation_items.append({
                        'name': 'Devis',
                        'url': '/devis/',
                        'icon': 'fas fa-file-invoice',
                        'active': request.path.startswith('/devis/')
                    })
                
                # Factures
                if profile.a_permission('factures.view'):
                    navigation_items.append({
                        'name': 'Factures',
                        'url': '/factures/',
                        'icon': 'fas fa-file-invoice-dollar',
                        'active': request.path.startswith('/factures/')
                    })
                
                # Commandes
                if profile.a_permission('commandes.view'):
                    navigation_items.append({
                        'name': 'Commandes',
                        'url': '/commandes/',
                        'icon': 'fas fa-shopping-cart',
                        'active': request.path.startswith('/commandes/')
                    })
                
                # Articles
                if profile.a_permission('articles.view'):
                    navigation_items.append({
                        'name': 'Articles',
                        'url': '/articles/',
                        'icon': 'fas fa-boxes',
                        'active': request.path.startswith('/articles/')
                    })
                
                # Fournisseurs
                if profile.a_permission('fournisseurs.view'):
                    navigation_items.append({
                        'name': 'Fournisseurs',
                        'url': '/fournisseurs/',
                        'icon': 'fas fa-truck',
                        'active': request.path.startswith('/fournisseurs/')
                    })
                
                # Rapports
                if profile.a_permission('rapports.view'):
                    navigation_items.append({
                        'name': 'Rapports',
                        'url': '/rapports/',
                        'icon': 'fas fa-chart-bar',
                        'active': request.path.startswith('/rapports/')
                    })
                
                # Paramètres (pour les managers et admins)
                if profile.est_administrateur or profile.est_manager:
                    navigation_items.append({
                        'name': 'Paramètres',
                        'url': '/parametres/',
                        'icon': 'fas fa-cog',
                        'active': request.path.startswith('/parametres/')
                    })
                
                # Utilisateurs (pour les admins uniquement)
                if profile.est_administrateur:
                    navigation_items.append({
                        'name': 'Utilisateurs',
                        'url': '/utilisateurs/',
                        'icon': 'fas fa-user-cog',
                        'active': request.path.startswith('/utilisateurs/')
                    })
                
                request.navigation_items = navigation_items
                
            except UtilisateurProfile.DoesNotExist:
                request.navigation_items = []
        else:
            request.navigation_items = []
        
        return None
