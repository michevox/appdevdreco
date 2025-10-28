from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

class ParametresGeneraux(models.Model):
    """Paramètres généraux de l'application"""
    
    # Paramètres monétaires
    SYMBOLES_MONETAIRES = [
        ('GNF', 'GNF (Franc Guinéen)'),
        ('FCFA', 'FCFA (Franc CFA)'),
        ('EUR', 'EUR (Euro)'),
        ('USD', 'USD (Dollar US)'),
        ('GBP', 'GBP (Livre Sterling)'),
        ('JPY', 'JPY (Yen Japonais)'),
        ('CHF', 'CHF (Franc Suisse)'),
        ('CAD', 'CAD (Dollar Canadien)'),
        ('AUD', 'AUD (Dollar Australien)'),
    ]
    
    symbole_monetaire = models.CharField(
        max_length=10,
        choices=SYMBOLES_MONETAIRES,
        default='GNF',
        verbose_name="Symbole monétaire"
    )
    
    # Paramètres de l'application
    nom_application = models.CharField(
        max_length=100,
        default='DEVDRECO SOFT',
        verbose_name="Nom de l'application"
    )
    
    # Paramètres de pagination
    elements_par_page = models.PositiveIntegerField(
        default=20,
        verbose_name="Éléments par page"
    )
    
    # Paramètres de date
    format_date = models.CharField(
        max_length=20,
        default='d/m/Y',
        verbose_name="Format de date"
    )
    
    # Paramètres de notification
    notifications_email = models.BooleanField(
        default=True,
        verbose_name="Notifications par email"
    )
    
    notifications_sms = models.BooleanField(
        default=False,
        verbose_name="Notifications par SMS"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paramètres généraux"
        verbose_name_plural = "Paramètres généraux"
    
    def __str__(self):
        return f"Paramètres - {self.nom_application}"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule instance
        if not self.pk and ParametresGeneraux.objects.exists():
            raise ValidationError("Il ne peut y avoir qu'une seule instance de paramètres généraux")
        super().save(*args, **kwargs)

class InformationsSociete(models.Model):
    """Informations de la société"""
    
    # Informations de base
    nom_raison_sociale = models.CharField(
        max_length=200,
        verbose_name="Nom ou raison sociale"
    )
    
    telephone_fixe = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone fixe"
    )
    
    telephone_portable = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone portable"
    )
    
    email = models.EmailField(
        verbose_name="Adresse email"
    )
    
    adresse = models.TextField(
        verbose_name="Adresse complète"
    )
    
    ville = models.CharField(
        max_length=100,
        verbose_name="Ville"
    )
    
    code_postal = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Code postal"
    )
    
    pays = models.CharField(
        max_length=100,
        default='Guinée',
        verbose_name="Pays"
    )
    
    # Informations web
    url_site = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL du site web"
    )
    
    # Documents
    en_tete_document = models.TextField(
        blank=True,
        null=True,
        verbose_name="En-tête pour documents (texte)"
    )
    
    pied_page_document = models.TextField(
        blank=True,
        null=True,
        verbose_name="Pied de page pour documents (texte)"
    )
    
    # Logo et images
    logo = models.ImageField(
        upload_to='logos/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])],
        verbose_name="Logo de la société"
    )
    bandeau_entete = models.ImageField(
        upload_to='bandeaux/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        verbose_name="Image d'entête (bandeau)"
    )
    bandeau_pied = models.ImageField(
        upload_to='bandeaux/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        verbose_name="Image de pied de page (bandeau)"
    )
    
    # Informations légales
    numero_registre_commerce = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Numéro de registre de commerce"
    )
    
    numero_contribuable = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Numéro de contribuable"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Informations de la société"
        verbose_name_plural = "Informations de la société"
    
    def __str__(self):
        return self.nom_raison_sociale
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule instance
        if not self.pk and InformationsSociete.objects.exists():
            raise ValidationError("Il ne peut y avoir qu'une seule instance d'informations de société")
        super().save(*args, **kwargs)

class UtilisateurCustom(models.Model):
    """Extension du modèle utilisateur Django pour les rôles personnalisés"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('standard', 'Utilisateur standard'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Utilisateur Django"
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='standard',
        verbose_name="Rôle utilisateur"
    )
    
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
    
    actif = models.BooleanField(
        default=True,
        verbose_name="Compte actif"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"
    
    @property
    def est_administrateur(self):
        """Vérifie si l'utilisateur est administrateur"""
        return self.role == 'admin' or self.user.is_superuser
    
    @property
    def est_utilisateur_standard(self):
        """Vérifie si l'utilisateur est standard"""
        return self.role == 'standard' and not self.user.is_superuser
