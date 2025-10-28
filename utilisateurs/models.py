from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Role(models.Model):
    """Modèle pour définir les rôles utilisateur"""
    
    ROLE_TYPES = [
        ('admin', 'Administrateur'),
        ('manager', 'Manager'),
        ('standard', 'Utilisateur standard'),
        ('readonly', 'Lecture seule'),
    ]
    
    nom = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom du rôle"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Description du rôle"
    )
    
    type_role = models.CharField(
        max_length=20,
        choices=ROLE_TYPES,
        default='standard',
        verbose_name="Type de rôle"
    )
    
    actif = models.BooleanField(
        default=True,
        verbose_name="Rôle actif"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom
    
    @property
    def est_administrateur(self):
        """Vérifie si c'est un rôle administrateur"""
        return self.type_role == 'admin'
    
    @property
    def est_manager(self):
        """Vérifie si c'est un rôle manager"""
        return self.type_role == 'manager'


class Permission(models.Model):
    """Modèle pour définir les permissions spécifiques"""
    
    MODULES = [
        ('clients', 'Clients'),
        ('devis', 'Devis'),
        ('factures', 'Factures'),
        ('commandes', 'Commandes'),
        ('articles', 'Articles'),
        ('fournisseurs', 'Fournisseurs'),
        ('rapports', 'Rapports'),
        ('parametres', 'Paramètres'),
        ('utilisateurs', 'Utilisateurs'),
    ]
    
    ACTIONS = [
        ('view', 'Voir'),
        ('add', 'Ajouter'),
        ('change', 'Modifier'),
        ('delete', 'Supprimer'),
        ('export', 'Exporter'),
        ('import', 'Importer'),
        ('print', 'Imprimer'),
    ]
    
    nom = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom de la permission"
    )
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Code de la permission"
    )
    
    module = models.CharField(
        max_length=20,
        choices=MODULES,
        verbose_name="Module"
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTIONS,
        verbose_name="Action"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    actif = models.BooleanField(
        default=True,
        verbose_name="Permission active"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ['module', 'action']
        unique_together = ['module', 'action']
    
    def __str__(self):
        return f"{self.get_module_display()} - {self.get_action_display()}"
    
    def save(self, *args, **kwargs):
        # Générer automatiquement le code si non fourni
        if not self.code:
            self.code = f"{self.module}.{self.action}"
        super().save(*args, **kwargs)


class RolePermission(models.Model):
    """Modèle pour associer les permissions aux rôles"""
    
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='permissions',
        verbose_name="Rôle"
    )
    
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name="Permission"
    )
    
    accordee = models.BooleanField(
        default=True,
        verbose_name="Permission accordée"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Permission de rôle"
        verbose_name_plural = "Permissions de rôles"
        unique_together = ['role', 'permission']
        ordering = ['role', 'permission']
    
    def __str__(self):
        status = "✓" if self.accordee else "✗"
        return f"{self.role.nom} - {self.permission} {status}"


class UtilisateurProfile(models.Model):
    """Extension du modèle utilisateur Django avec système de rôles"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='user_profile',
        verbose_name="Utilisateur Django"
    )
    
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utilisateurs',
        verbose_name="Rôle principal"
    )
    
    # Informations personnelles
    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone"
    )
    
    poste = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Poste occupé"
    )
    
    departement = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Département"
    )
    
    date_embauche = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date d'embauche"
    )
    
    # Statut
    actif = models.BooleanField(
        default=True,
        verbose_name="Compte actif"
    )
    
    # Permissions personnalisées (override du rôle)
    permissions_personnalisees = models.ManyToManyField(
        Permission,
        through='UtilisateurPermission',
        blank=True,
        verbose_name="Permissions personnalisées"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    derniere_connexion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière connexion"
    )
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role.nom if self.role else 'Sans rôle'})"
    
    @property
    def est_administrateur(self):
        """Vérifie si l'utilisateur est administrateur"""
        return (self.user.is_superuser or 
                (self.role and self.role.est_administrateur))
    
    @property
    def est_manager(self):
        """Vérifie si l'utilisateur est manager"""
        return (self.role and self.role.est_manager)
    
    def a_permission(self, code_permission):
        """Vérifie si l'utilisateur a une permission spécifique"""
        # Vérifier les permissions personnalisées d'abord (même pour les administrateurs)
        permission_perso = self.utilisateurpermission_set.filter(
            permission__code=code_permission
        ).first()
        
        if permission_perso:
            return permission_perso.accordee
        
        # Si pas de permission personnalisée, vérifier les permissions du rôle
        if self.role:
            role_permission = self.role.permissions.filter(
                permission__code=code_permission
            ).first()
            
            if role_permission:
                return role_permission.accordee
        
        # Si l'utilisateur est administrateur et qu'aucune permission spécifique n'est définie,
        # alors il a accès par défaut (comportement de fallback)
        if self.est_administrateur:
            return True
        
        return False
    
    def a_permission_module(self, module, action):
        """Vérifie si l'utilisateur a une permission pour un module et une action"""
        code_permission = f"{module}.{action}"
        return self.a_permission(code_permission)
    
    def get_permissions_accordees(self):
        """Retourne toutes les permissions accordées à l'utilisateur"""
        permissions = set()
        
        # Permissions personnalisées accordées
        for up in self.utilisateurpermission_set.filter(accordee=True):
            permissions.add(up.permission.code)
        
        # Permissions du rôle accordées
        if self.role:
            for rp in self.role.permissions.filter(accordee=True):
                permissions.add(rp.permission.code)
        
        return permissions
    
    def get_permissions_refusees(self):
        """Retourne toutes les permissions refusées à l'utilisateur"""
        permissions = set()
        
        # Permissions personnalisées refusées
        for up in self.utilisateurpermission_set.filter(accordee=False):
            permissions.add(up.permission.code)
        
        # Permissions du rôle refusées
        if self.role:
            for rp in self.role.permissions.filter(accordee=False):
                permissions.add(rp.permission.code)
        
        return permissions


class UtilisateurPermission(models.Model):
    """Modèle pour les permissions personnalisées des utilisateurs"""
    
    utilisateur = models.ForeignKey(
        UtilisateurProfile,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur"
    )
    
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        verbose_name="Permission"
    )
    
    accordee = models.BooleanField(
        default=True,
        verbose_name="Permission accordée"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Permission utilisateur"
        verbose_name_plural = "Permissions utilisateurs"
        unique_together = ['utilisateur', 'permission']
        ordering = ['utilisateur', 'permission']
    
    def __str__(self):
        status = "✓" if self.accordee else "✗"
        return f"{self.utilisateur.user.username} - {self.permission} {status}"


class ConnexionUtilisateur(models.Model):
    """Modèle pour tracer les connexions utilisateur"""
    
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='connexions',
        verbose_name="Utilisateur"
    )
    
    adresse_ip = models.GenericIPAddressField(
        verbose_name="Adresse IP"
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    
    date_connexion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de connexion"
    )
    
    date_deconnexion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de déconnexion"
    )
    
    reussie = models.BooleanField(
        default=True,
        verbose_name="Connexion réussie"
    )
    
    class Meta:
        verbose_name = "Connexion utilisateur"
        verbose_name_plural = "Connexions utilisateurs"
        ordering = ['-date_connexion']
    
    def __str__(self):
        status = "✓" if self.reussie else "✗"
        return f"{self.utilisateur.username} - {self.date_connexion.strftime('%d/%m/%Y %H:%M')} {status}"