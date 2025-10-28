from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class CustomUserAdmin(UserAdmin):
    """Administration personnalisée pour les utilisateurs"""
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'is_staff', 'is_superuser', 'is_active', 'date_joined'
    ]
    list_filter = [
        'is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined'
    ]
    search_fields = [
        'username', 'first_name', 'last_name', 'email'
    ]
    ordering = ['username']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    def get_queryset(self, request):
        """Seuls les superutilisateurs peuvent voir tous les utilisateurs"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            # Les utilisateurs non-superuser ne voient que leur propre profil
            return qs.filter(id=request.user.id)
    
    def has_add_permission(self, request):
        """Seuls les superutilisateurs peuvent créer des utilisateurs"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Seuls les superutilisateurs peuvent modifier les utilisateurs"""
        if request.user.is_superuser:
            return True
        # Les utilisateurs peuvent modifier leur propre profil
        return obj and obj.id == request.user.id
    
    def has_delete_permission(self, request, obj=None):
        """Seuls les superutilisateurs peuvent supprimer des utilisateurs"""
        return request.user.is_superuser

# Désenregistrer l'admin par défaut et enregistrer notre version personnalisée
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
