from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    UtilisateurProfile, Role, Permission, RolePermission,
    UtilisateurPermission, ConnexionUtilisateur
)


class UtilisateurProfileInline(admin.StackedInline):
    """Inline pour le profil utilisateur dans l'admin Django"""
    model = UtilisateurProfile
    can_delete = False
    verbose_name_plural = 'Profil utilisateur (nouveau système)'
    fields = ('role', 'telephone', 'poste', 'departement', 'date_embauche', 'actif')


class UserAdmin(BaseUserAdmin):
    """Admin personnalisé pour les utilisateurs"""
    inlines = (UtilisateurProfileInline,)
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'get_role')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'user_profile__role', 'user_profile__actif')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_role(self, obj):
        try:
            return obj.user_profile.role.nom if obj.user_profile.role else 'Sans rôle'
        except UtilisateurProfile.DoesNotExist:
            return 'Profil manquant'
    get_role.short_description = 'Rôle'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user_profile__role')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin pour les rôles"""
    list_display = ('nom', 'type_role', 'actif', 'nombre_utilisateurs', 'date_creation')
    list_filter = ('type_role', 'actif', 'date_creation')
    search_fields = ('nom', 'description')
    readonly_fields = ('date_creation', 'date_modification')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description', 'type_role', 'actif')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def nombre_utilisateurs(self, obj):
        return obj.utilisateurs.count()
    nombre_utilisateurs.short_description = 'Nombre d\'utilisateurs'


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin pour les permissions"""
    list_display = ('nom', 'code', 'module', 'action', 'actif', 'date_creation')
    list_filter = ('module', 'action', 'actif', 'date_creation')
    search_fields = ('nom', 'code', 'description')
    readonly_fields = ('date_creation', 'date_modification')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'code', 'module', 'action', 'description', 'actif')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """Admin pour les permissions des rôles"""
    list_display = ('role', 'permission', 'accordee', 'date_creation')
    list_filter = ('accordee', 'role', 'permission__module', 'date_creation')
    search_fields = ('role__nom', 'permission__nom', 'permission__code')
    readonly_fields = ('date_creation', 'date_modification')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('role', 'permission', 'accordee')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UtilisateurPermission)
class UtilisateurPermissionAdmin(admin.ModelAdmin):
    """Admin pour les permissions personnalisées des utilisateurs"""
    list_display = ('utilisateur', 'permission', 'accordee', 'date_creation')
    list_filter = ('accordee', 'permission__module', 'date_creation')
    search_fields = ('utilisateur__user__username', 'permission__nom', 'permission__code')
    readonly_fields = ('date_creation', 'date_modification')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('utilisateur', 'permission', 'accordee')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ConnexionUtilisateur)
class ConnexionUtilisateurAdmin(admin.ModelAdmin):
    """Admin pour l'historique des connexions"""
    list_display = ('utilisateur', 'adresse_ip', 'date_connexion', 'date_deconnexion', 'reussie')
    list_filter = ('reussie', 'date_connexion')
    search_fields = ('utilisateur__username', 'adresse_ip')
    readonly_fields = ('date_connexion', 'date_deconnexion')
    
    fieldsets = (
        ('Informations de connexion', {
            'fields': ('utilisateur', 'adresse_ip', 'user_agent', 'reussie')
        }),
        ('Dates', {
            'fields': ('date_connexion', 'date_deconnexion'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# Désenregistrer l'admin par défaut de User et enregistrer le nôtre
admin.site.unregister(User)
admin.site.register(User, UserAdmin)