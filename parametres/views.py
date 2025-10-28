from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from .models import ParametresGeneraux, InformationsSociete, UtilisateurCustom
from .forms import (
    ParametresGenerauxForm, 
    InformationsSocieteForm, 
    UtilisateurCreationForm,
    UtilisateurModificationForm
)
from utilisateurs.models import UtilisateurProfile, Role, Permission, UtilisateurPermission
from utilisateurs.decorators import admin_required

def est_administrateur(user):
    """Vérifie si l'utilisateur est administrateur"""
    try:
        profile = user.profile
        return profile.est_administrateur
    except:
        return user.is_superuser

@login_required
@user_passes_test(est_administrateur)
def parametres_generaux(request):
    """Vue pour gérer les paramètres généraux"""
    
    # Récupérer ou créer les paramètres
    parametres, created = ParametresGeneraux.objects.get_or_create(
        defaults={
            'symbole_monetaire': 'GNF',
            'nom_application': 'DEVDRECO SOFT',
            'elements_par_page': 20,
            'format_date': 'd/m/Y',
            'notifications_email': True,
            'notifications_sms': False
        }
    )
    
    if request.method == 'POST':
        form = ParametresGenerauxForm(request.POST, instance=parametres)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paramètres généraux mis à jour avec succès.')
            return redirect('parametres:parametres_generaux')
    else:
        form = ParametresGenerauxForm(instance=parametres)
    
    context = {
        'form': form,
        'parametres': parametres,
        'active_tab': 'generaux'
    }
    return render(request, 'parametres/parametres_generaux.html', context)

@login_required
@user_passes_test(est_administrateur)
def informations_societe(request):
    """Vue pour gérer les informations de la société"""
    
    # Récupérer ou créer les informations de société
    societe, created = InformationsSociete.objects.get_or_create(
        defaults={
            'nom_raison_sociale': 'DEVDRECO SOFT',
            'pays': 'Guinée'
        }
    )
    
    if request.method == 'POST':
        form = InformationsSocieteForm(request.POST, request.FILES, instance=societe)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informations de la société mises à jour avec succès.')
            return redirect('parametres:informations_societe')
    else:
        form = InformationsSocieteForm(instance=societe)
    
    context = {
        'form': form,
        'societe': societe,
        'active_tab': 'societe'
    }
    return render(request, 'parametres/informations_societe.html', context)

class UtilisateurListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vue pour lister les utilisateurs"""
    model = UtilisateurCustom
    template_name = 'parametres/utilisateur_list.html'
    context_object_name = 'utilisateurs'
    paginate_by = 20
    
    def test_func(self):
        return est_administrateur(self.request.user)
    
    def get_queryset(self):
        queryset = UtilisateurCustom.objects.select_related('user').all()
        
        # Recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(poste__icontains=search_query) |
                Q(departement__icontains=search_query)
            )
        
        # Filtre par rôle
        role_filter = self.request.GET.get('role', '')
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        
        # Filtre par statut
        statut_filter = self.request.GET.get('statut', '')
        if statut_filter == 'actif':
            queryset = queryset.filter(actif=True)
        elif statut_filter == 'inactif':
            queryset = queryset.filter(actif=False)
        
        return queryset.order_by('user__username')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'utilisateurs'
        context['search_query'] = self.request.GET.get('search', '')
        context['role_filter'] = self.request.GET.get('role', '')
        context['statut_filter'] = self.request.GET.get('statut', '')
        context['role_choices'] = UtilisateurCustom.ROLE_CHOICES
        return context

class UtilisateurCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Vue pour créer un nouvel utilisateur"""
    form_class = UtilisateurCreationForm
    template_name = 'parametres/utilisateur_form.html'
    success_url = reverse_lazy('parametres:utilisateur_list')
    
    def test_func(self):
        return est_administrateur(self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Utilisateur {form.instance.username} créé avec succès.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'utilisateurs'
        context['title'] = 'Créer un nouvel utilisateur'
        context['submit_text'] = 'Créer l\'utilisateur'
        return context

class UtilisateurUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vue pour modifier un utilisateur"""
    model = UtilisateurCustom
    form_class = UtilisateurModificationForm
    template_name = 'parametres/utilisateur_form.html'
    success_url = reverse_lazy('parametres:utilisateur_list')
    
    def test_func(self):
        return est_administrateur(self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Utilisateur {self.object.user.username} modifié avec succès.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'utilisateurs'
        context['title'] = f'Modifier l\'utilisateur {self.object.user.username}'
        context['submit_text'] = 'Mettre à jour'
        return context

class UtilisateurDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vue pour supprimer un utilisateur"""
    model = UtilisateurCustom
    template_name = 'parametres/utilisateur_confirm_delete.html'
    success_url = reverse_lazy('parametres:utilisateur_list')
    
    def test_func(self):
        return est_administrateur(self.request.user)
    
    def delete(self, request, *args, **kwargs):
        username = self.get_object().user.username
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Utilisateur {username} supprimé avec succès.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'utilisateurs'
        return context

@login_required
@user_passes_test(est_administrateur)
def utilisateur_activer_desactiver(request, pk):
    """Vue pour activer/désactiver un utilisateur"""
    utilisateur = get_object_or_404(UtilisateurCustom, pk=pk)
    
    if request.method == 'POST':
        utilisateur.actif = not utilisateur.actif
        utilisateur.save()
        
        action = "activé" if utilisateur.actif else "désactivé"
        messages.success(request, f'Utilisateur {utilisateur.user.username} {action} avec succès.')
        
        return redirect('parametres:utilisateur_list')
    
    context = {
        'utilisateur': utilisateur,
        'active_tab': 'utilisateurs'
    }
    return render(request, 'parametres/utilisateur_activer_desactiver.html', context)

@login_required
@user_passes_test(est_administrateur)
def utilisateur_changer_mot_de_passe(request, pk):
    """Vue pour changer le mot de passe d'un utilisateur"""
    utilisateur = get_object_or_404(UtilisateurCustom, pk=pk)
    
    if request.method == 'POST':
        form = PasswordChangeForm(utilisateur.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, f'Mot de passe de {utilisateur.user.username} changé avec succès.')
            return redirect('parametres:utilisateur_list')
    else:
        form = PasswordChangeForm(utilisateur.user)
    
    context = {
        'form': form,
        'utilisateur': utilisateur,
        'active_tab': 'utilisateurs'
    }
    return render(request, 'parametres/utilisateur_changer_mot_de_passe.html', context)

@login_required
@user_passes_test(est_administrateur)
def tableau_bord_parametres(request):
    """Vue pour le tableau de bord des paramètres"""
    
    # Statistiques des utilisateurs
    total_utilisateurs = UtilisateurCustom.objects.count()
    utilisateurs_actifs = UtilisateurCustom.objects.filter(actif=True).count()
    utilisateurs_inactifs = total_utilisateurs - utilisateurs_actifs
    administrateurs = UtilisateurCustom.objects.filter(role='admin').count()
    utilisateurs_standard = UtilisateurCustom.objects.filter(role='standard').count()
    
    # Vérifier si les paramètres sont configurés
    parametres_configures = ParametresGeneraux.objects.exists()
    societe_configuree = InformationsSociete.objects.exists()
    
    # Derniers utilisateurs créés
    derniers_utilisateurs = UtilisateurCustom.objects.select_related('user').order_by('-date_creation')[:5]
    
    context = {
        'total_utilisateurs': total_utilisateurs,
        'utilisateurs_actifs': utilisateurs_actifs,
        'utilisateurs_inactifs': utilisateurs_inactifs,
        'administrateurs': administrateurs,
        'utilisateurs_standard': utilisateurs_standard,
        'parametres_configures': parametres_configures,
        'societe_configuree': societe_configuree,
        'derniers_utilisateurs': derniers_utilisateurs,
        'active_tab': 'tableau_bord'
    }
    
    return render(request, 'parametres/tableau_bord.html', context)


@login_required
@admin_required()
def gestion_permissions(request):
    """Vue pour gérer les permissions des utilisateurs"""
    
    # Récupérer tous les utilisateurs avec leurs profils
    utilisateurs = User.objects.select_related('user_profile').all()
    
    # Récupérer tous les rôles
    roles = Role.objects.all()
    
    # Récupérer toutes les permissions groupées par module
    permissions = Permission.objects.all().order_by('module', 'code')
    permissions_par_module = {}
    for permission in permissions:
        if permission.module not in permissions_par_module:
            permissions_par_module[permission.module] = []
        permissions_par_module[permission.module].append(permission)
    
    context = {
        'utilisateurs': utilisateurs,
        'roles': roles,
        'permissions_par_module': permissions_par_module,
        'active_tab': 'permissions'
    }
    
    return render(request, 'parametres/gestion_permissions.html', context)


@login_required
@admin_required()
def modifier_permissions_utilisateur(request, user_id):
    """Vue pour modifier les permissions d'un utilisateur spécifique"""
    
    user = get_object_or_404(User, id=user_id)
    
    try:
        profile = user.user_profile
    except UtilisateurProfile.DoesNotExist:
        messages.error(request, "Profil utilisateur non trouvé.")
        return redirect('parametres:gestion_permissions')
    
    # Récupérer toutes les permissions
    permissions = Permission.objects.all().order_by('module', 'code')
    permissions_par_module = {}
    for permission in permissions:
        if permission.module not in permissions_par_module:
            permissions_par_module[permission.module] = []
        permissions_par_module[permission.module].append(permission)
    
    # Récupérer les permissions actuelles de l'utilisateur
    permissions_utilisateur = UtilisateurPermission.objects.filter(utilisateur=profile)
    permissions_actuelles = {p.permission.code: p for p in permissions_utilisateur}
    
    if request.method == 'POST':
        # Traiter les permissions cochées
        permissions_selectionnees = request.POST.getlist('permissions')
        
        # Supprimer toutes les permissions actuelles
        UtilisateurPermission.objects.filter(utilisateur=profile).delete()
        
        # Ajouter les nouvelles permissions
        for permission_code in permissions_selectionnees:
            try:
                permission = Permission.objects.get(code=permission_code)
                UtilisateurPermission.objects.create(
                    utilisateur=profile,
                    permission=permission
                )
            except Permission.DoesNotExist:
                continue
        
        messages.success(request, f'Permissions mises à jour pour {user.get_full_name() or user.username}.')
        return redirect('parametres:gestion_permissions')
    
    context = {
        'user': user,
        'profile': profile,
        'permissions_par_module': permissions_par_module,
        'permissions_actuelles': permissions_actuelles,
        'active_tab': 'permissions'
    }
    
    return render(request, 'parametres/modifier_permissions.html', context)


@login_required
@admin_required()
def modifier_role_utilisateur(request, user_id):
    """Vue pour modifier le rôle d'un utilisateur"""
    
    user = get_object_or_404(User, id=user_id)
    
    try:
        profile = user.user_profile
    except UtilisateurProfile.DoesNotExist:
        messages.error(request, "Profil utilisateur non trouvé.")
        return redirect('parametres:gestion_permissions')
    
    roles = Role.objects.all()
    
    if request.method == 'POST':
        role_id = request.POST.get('role')
        
        if role_id:
            try:
                role = Role.objects.get(id=role_id)
                profile.role = role
                profile.save()
                messages.success(request, f'Rôle mis à jour pour {user.get_full_name() or user.username}.')
            except Role.DoesNotExist:
                messages.error(request, "Rôle non trouvé.")
        else:
            profile.role = None
            profile.save()
            messages.success(request, f'Rôle supprimé pour {user.get_full_name() or user.username}.')
        
        return redirect('parametres:gestion_permissions')
    
    context = {
        'user': user,
        'profile': profile,
        'roles': roles,
        'active_tab': 'permissions'
    }
    
    return render(request, 'parametres/modifier_role.html', context)


@login_required
@admin_required()
def activer_desactiver_utilisateur(request, user_id):
    """Vue pour activer/désactiver un utilisateur"""
    
    user = get_object_or_404(User, id=user_id)
    
    try:
        profile = user.user_profile
    except UtilisateurProfile.DoesNotExist:
        messages.error(request, "Profil utilisateur non trouvé.")
        return redirect('parametres:gestion_permissions')
    
    # Basculer le statut actif
    profile.actif = not profile.actif
    profile.save()
    
    statut = "activé" if profile.actif else "désactivé"
    messages.success(request, f'Utilisateur {user.get_full_name() or user.username} {statut} avec succès.')
    
    return redirect('parametres:gestion_permissions')


@login_required
@admin_required()
def ajouter_permission_utilisateur(request):
    """Vue AJAX pour ajouter une permission à un utilisateur"""
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        permission_code = request.POST.get('permission_code')
        
        try:
            user = User.objects.get(id=user_id)
            profile = user.user_profile
            permission = Permission.objects.get(code=permission_code)
            
            # Vérifier si la permission n'existe pas déjà
            if not UtilisateurPermission.objects.filter(utilisateur=profile, permission=permission).exists():
                UtilisateurPermission.objects.create(utilisateur=profile, permission=permission)
                return JsonResponse({'success': True, 'message': 'Permission ajoutée avec succès.'})
            else:
                return JsonResponse({'success': False, 'message': 'Cette permission existe déjà.'})
                
        except (User.DoesNotExist, UtilisateurProfile.DoesNotExist, Permission.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Utilisateur ou permission non trouvé.'})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})


@login_required
@admin_required()
def supprimer_permission_utilisateur(request):
    """Vue AJAX pour supprimer une permission d'un utilisateur"""
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        permission_code = request.POST.get('permission_code')
        
        try:
            user = User.objects.get(id=user_id)
            profile = user.user_profile
            permission = Permission.objects.get(code=permission_code)
            
            UtilisateurPermission.objects.filter(utilisateur=profile, permission=permission).delete()
            return JsonResponse({'success': True, 'message': 'Permission supprimée avec succès.'})
                
        except (User.DoesNotExist, UtilisateurProfile.DoesNotExist, Permission.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Utilisateur ou permission non trouvé.'})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})
