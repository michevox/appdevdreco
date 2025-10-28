from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import ParametresGeneraux, InformationsSociete, UtilisateurCustom

@admin.register(ParametresGeneraux)
class ParametresGenerauxAdmin(admin.ModelAdmin):
    """Admin pour les paramètres généraux"""
    list_display = ['nom_application', 'symbole_monetaire', 'elements_par_page', 'format_date', 'date_modification']
    list_editable = ['symbole_monetaire', 'elements_par_page', 'format_date']
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Paramètres monétaires', {
            'fields': ('symbole_monetaire',)
        }),
        ('Paramètres de l\'application', {
            'fields': ('nom_application', 'elements_par_page', 'format_date')
        }),
        ('Notifications', {
            'fields': ('notifications_email', 'notifications_sms')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Empêcher la création de plusieurs instances"""
        return not ParametresGeneraux.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Empêcher la suppression"""
        return False

@admin.register(InformationsSociete)
class InformationsSocieteAdmin(admin.ModelAdmin):
    """Admin pour les informations de la société"""
    list_display = ['nom_raison_sociale', 'ville', 'pays', 'email', 'telephone_fixe', 'date_modification']
    list_editable = ['ville', 'pays', 'email', 'telephone_fixe']
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('nom_raison_sociale', 'telephone_fixe', 'telephone_portable', 'email')
        }),
        ('Adresse', {
            'fields': ('adresse', 'ville', 'code_postal', 'pays')
        }),
        ('Web et documents', {
            'fields': ('url_site', 'en_tete_document', 'pied_page_document')
        }),
        ('Logo et images', {
            'fields': ('logo',)
        }),
        ('Informations légales', {
            'fields': ('numero_registre_commerce', 'numero_contribuable')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Empêcher la création de plusieurs instances"""
        return not InformationsSociete.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Empêcher la suppression"""
        return False

class UtilisateurCustomInline(admin.StackedInline):
    """Inline pour le profil utilisateur personnalisé"""
    model = UtilisateurCustom
    can_delete = False
    verbose_name_plural = 'Profil personnalisé'
    fields = ['role', 'telephone', 'poste', 'departement', 'date_embauche', 'actif']

class UserAdminCustom(UserAdmin):
    """Admin personnalisé pour les utilisateurs avec profil étendu"""
    inlines = [UtilisateurCustomInline]
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'get_actif', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'profile__role', 'profile__actif']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'profile__poste', 'profile__departement']
    
    def get_role(self, obj):
        """Obtenir le rôle de l'utilisateur"""
        try:
            return obj.profile.get_role_display()
        except:
            return 'Non défini'
    get_role.short_description = 'Rôle'
    
    def get_actif(self, obj):
        """Obtenir le statut actif de l'utilisateur"""
        try:
            return obj.profile.actif
        except:
            return False
    get_actif.boolean = True
    get_actif.short_description = 'Actif'

# Désenregistrer l'admin par défaut et enregistrer le personnalisé
admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)

@admin.register(UtilisateurCustom)
class UtilisateurCustomAdmin(admin.ModelAdmin):
    """Admin pour les profils utilisateurs personnalisés"""
    list_display = ['user', 'role', 'poste', 'departement', 'telephone', 'actif', 'date_creation']
    list_filter = ['role', 'actif', 'departement', 'date_creation']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'poste', 'departement']
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Profil', {
            'fields': ('role', 'telephone', 'poste', 'departement', 'date_embauche')
        }),
        ('Statut', {
            'fields': ('actif',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Empêcher l'ajout direct - utiliser l'admin User à la place"""
        return False
