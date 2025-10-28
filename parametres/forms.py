from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ParametresGeneraux, InformationsSociete, UtilisateurCustom

class ParametresGenerauxForm(forms.ModelForm):
    """Formulaire pour les paramètres généraux"""
    
    class Meta:
        model = ParametresGeneraux
        fields = [
            'symbole_monetaire',
            'nom_application',
            'elements_par_page',
            'format_date',
            'notifications_email',
            'notifications_sms'
        ]
        widgets = {
            'symbole_monetaire': forms.Select(attrs={'class': 'form-select'}),
            'nom_application': forms.TextInput(attrs={'class': 'form-control'}),
            'elements_par_page': forms.NumberInput(attrs={'class': 'form-control'}),
            'format_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'd/m/Y'}),
            'notifications_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notifications_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class InformationsSocieteForm(forms.ModelForm):
    """Formulaire pour les informations de la société"""
    
    class Meta:
        model = InformationsSociete
        fields = [
            'nom_raison_sociale',
            'telephone_fixe',
            'telephone_portable',
            'email',
            'adresse',
            'ville',
            'code_postal',
            'pays',
            'url_site',
            'logo',
            'bandeau_entete',
            'bandeau_pied',
            'numero_registre_commerce',
            'numero_contribuable'
        ]
        widgets = {
            'nom_raison_sociale': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone_fixe': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone_portable': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'url_site': forms.URLInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'bandeau_entete': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'bandeau_pied': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'numero_registre_commerce': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_contribuable': forms.TextInput(attrs={'class': 'form-control'})
        }

class UtilisateurCustomForm(forms.ModelForm):
    """Formulaire pour le profil utilisateur personnalisé"""
    
    class Meta:
        model = UtilisateurCustom
        fields = [
            'role',
            'telephone',
            'poste',
            'departement',
            'date_embauche',
            'actif'
        ]
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'poste': forms.TextInput(attrs={'class': 'form-control'}),
            'departement': forms.TextInput(attrs={'class': 'form-control'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class UtilisateurCreationForm(UserCreationForm):
    """Formulaire pour créer un nouvel utilisateur avec profil personnalisé"""
    
    # Champs du profil personnalisé
    role = forms.ChoiceField(
        choices=UtilisateurCustom.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Rôle utilisateur"
    )
    
    telephone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Téléphone"
    )
    
    poste = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Poste occupé"
    )
    
    departement = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Département"
    )
    
    date_embauche = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date d'embauche"
    )
    
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les labels des champs de mot de passe
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].label = "Mot de passe"
        self.fields['password2'].label = "Confirmation du mot de passe"
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Créer le profil personnalisé
            UtilisateurCustom.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                telephone=self.cleaned_data['telephone'],
                poste=self.cleaned_data['poste'],
                departement=self.cleaned_data['departement'],
                date_embauche=self.cleaned_data['date_embauche']
            )
        return user

class UtilisateurModificationForm(forms.ModelForm):
    """Formulaire pour modifier un utilisateur existant"""
    
    # Champs de base de l'utilisateur Django
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Prénom"
    )
    
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Nom"
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Email"
    )
    
    class Meta:
        model = UtilisateurCustom
        fields = [
            'role',
            'telephone',
            'poste',
            'departement',
            'date_embauche',
            'actif'
        ]
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'poste': forms.TextInput(attrs={'class': 'form-control'}),
            'departement': forms.TextInput(attrs={'class': 'form-control'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            # Pré-remplir les champs de base de l'utilisateur
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Mettre à jour l'utilisateur Django
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            
            # Sauvegarder le profil
            profile.save()
        return profile


class GestionPermissionsForm(forms.Form):
    """Formulaire pour la gestion des permissions utilisateur"""
    
    def __init__(self, *args, **kwargs):
        permissions_par_module = kwargs.pop('permissions_par_module', {})
        permissions_actuelles = kwargs.pop('permissions_actuelles', {})
        super().__init__(*args, **kwargs)
        
        # Créer des champs checkbox pour chaque permission
        for module, permissions in permissions_par_module.items():
            for permission in permissions:
                field_name = f'permission_{permission.code}'
                self.fields[field_name] = forms.BooleanField(
                    required=False,
                    label=permission.nom,
                    help_text=permission.description,
                    initial=permission.code in permissions_actuelles,
                    widget=forms.CheckboxInput(attrs={
                        'class': 'form-check-input permission-checkbox',
                        'data-module': module,
                        'data-permission': permission.code
                    })
                )


class ModifierRoleForm(forms.Form):
    """Formulaire pour modifier le rôle d'un utilisateur"""
    
    role = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Aucun rôle",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        roles_queryset = kwargs.pop('roles_queryset', None)
        super().__init__(*args, **kwargs)
        
        if roles_queryset:
            self.fields['role'].queryset = roles_queryset


class FiltreUtilisateursForm(forms.Form):
    """Formulaire pour filtrer les utilisateurs"""
    
    RECHERCHE_CHOICES = [
        ('', 'Tous les utilisateurs'),
        ('actifs', 'Utilisateurs actifs'),
        ('inactifs', 'Utilisateurs inactifs'),
        ('administrateurs', 'Administrateurs'),
        ('managers', 'Managers'),
        ('utilisateurs_standard', 'Utilisateurs standard'),
    ]
    
    filtre = forms.ChoiceField(
        choices=RECHERCHE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    recherche = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par nom, email...'
        })
    )
