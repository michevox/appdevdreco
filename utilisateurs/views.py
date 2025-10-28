from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods

from .models import (
    UtilisateurProfile, Role, Permission, RolePermission, 
    UtilisateurPermission, ConnexionUtilisateur
)
from .decorators import admin_required, permission_required, ajax_permission_required
from .utils import create_user_with_role, update_user_permissions


@login_required
@admin_required()
def liste_utilisateurs(request):
    """Liste tous les utilisateurs avec leurs rôles"""
    utilisateurs = UtilisateurProfile.objects.select_related('user', 'role').all()
    
    # Filtrage
    recherche = request.GET.get('recherche', '')
    role_filter = request.GET.get('role', '')
    actif_filter = request.GET.get('actif', '')
    
    if recherche:
        utilisateurs = utilisateurs.filter(
            Q(user__username__icontains=recherche) |
            Q(user__first_name__icontains=recherche) |
            Q(user__last_name__icontains=recherche) |
            Q(user__email__icontains=recherche)
        )
    
    if role_filter:
        utilisateurs = utilisateurs.filter(role__id=role_filter)
    
    if actif_filter != '':
        actif = actif_filter == '1'
        utilisateurs = utilisateurs.filter(actif=actif)
    
    # Pagination
    paginator = Paginator(utilisateurs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Contexte
    roles = Role.objects.filter(actif=True)
    
    context = {
        'page_obj': page_obj,
        'roles': roles,
        'recherche': recherche,
        'role_filter': role_filter,
        'actif_filter': actif_filter,
    }
    
    return render(request, 'utilisateurs/liste_utilisateurs.html', context)


@login_required
@admin_required()
def detail_utilisateur(request, user_id):
    """Détail d'un utilisateur avec ses permissions"""
    utilisateur = get_object_or_404(UtilisateurProfile, user__id=user_id)
    
    # Récupérer les permissions accordées et refusées
    permissions_accordees = utilisateur.get_permissions_accordees()
    permissions_refusees = utilisateur.get_permissions_refusees()
    
    # Récupérer l'historique des connexions
    connexions = ConnexionUtilisateur.objects.filter(
        utilisateur=utilisateur.user
    ).order_by('-date_connexion')[:10]
    
    context = {
        'utilisateur': utilisateur,
        'permissions_accordees': permissions_accordees,
        'permissions_refusees': permissions_refusees,
        'connexions': connexions,
    }
    
    return render(request, 'utilisateurs/detail_utilisateur.html', context)


@login_required
def mon_profil(request):
    """Afficher le profil de l'utilisateur connecté"""
    try:
        profile = request.user.user_profile
    except UtilisateurProfile.DoesNotExist:
        messages.error(request, "Profil utilisateur non trouvé.")
        return redirect('core:dashboard')
    
    # Récupérer les permissions
    permissions_accordees = profile.get_permissions_accordees()
    permissions_refusees = profile.get_permissions_refusees()
    
    # Récupérer l'historique des connexions
    connexions = ConnexionUtilisateur.objects.filter(
        utilisateur=request.user
    ).order_by('-date_connexion')[:5]
    
    context = {
        'profile': profile,
        'permissions_accordees': permissions_accordees,
        'permissions_refusees': permissions_refusees,
        'connexions': connexions,
    }
    
    return render(request, 'utilisateurs/mon_profil.html', context)