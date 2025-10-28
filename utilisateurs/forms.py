from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UtilisateurProfile, Role, Permission


class UtilisateurForm(UserCreationForm):
    """Formulaire pour créer/modifier un utilisateur"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False, label="Prénom")
    last_name = forms.CharField(max_length=30, required=False, label="Nom")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les labels
        self.fields['username'].label = "Nom d'utilisateur"
        self.fields['email'].label = "Adresse email"
        self.fields['password1'].label = "Mot de passe"
        self.fields['password2'].label = "Confirmation du mot de passe"
        
        # Ajouter des classes CSS
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UtilisateurProfileForm(forms.ModelForm):
    """Formulaire pour le profil utilisateur"""
    
    class Meta:
        model = UtilisateurProfile
        fields = ('role', 'telephone', 'poste', 'departement', 'date_embauche', 'actif')
        widgets = {
            'date_embauche': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'poste': forms.TextInput(attrs={'class': 'form-control'}),
            'departement': forms.TextInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les rôles actifs
        self.fields['role'].queryset = Role.objects.filter(actif=True)
        self.fields['role'].label = "Rôle"
        self.fields['telephone'].label = "Téléphone"
        self.fields['poste'].label = "Poste occupé"
        self.fields['departement'].label = "Département"
        self.fields['date_embauche'].label = "Date d'embauche"
        self.fields['actif'].label = "Compte actif"


class RoleForm(forms.ModelForm):
    """Formulaire pour créer/modifier un rôle"""
    
    class Meta:
        model = Role
        fields = ('nom', 'description', 'type_role', 'actif')
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'type_role': forms.Select(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nom'].label = "Nom du rôle"
        self.fields['description'].label = "Description"
        self.fields['type_role'].label = "Type de rôle"
        self.fields['actif'].label = "Rôle actif"


class PermissionForm(forms.ModelForm):
    """Formulaire pour créer/modifier une permission"""
    
    class Meta:
        model = Permission
        fields = ('nom', 'code', 'module', 'action', 'description', 'actif')
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'module': forms.Select(attrs={'class': 'form-control'}),
            'action': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nom'].label = "Nom de la permission"
        self.fields['code'].label = "Code de la permission"
        self.fields['module'].label = "Module"
        self.fields['action'].label = "Action"
        self.fields['description'].label = "Description"
        self.fields['actif'].label = "Permission active"


class RolePermissionForm(forms.ModelForm):
    """Formulaire pour gérer les permissions d'un rôle"""
    
    class Meta:
        model = RolePermission
        fields = ('role', 'permission', 'accordee')
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'permission': forms.Select(attrs={'class': 'form-control'}),
            'accordee': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].label = "Rôle"
        self.fields['permission'].label = "Permission"
        self.fields['accordee'].label = "Permission accordée"


class UtilisateurPermissionForm(forms.ModelForm):
    """Formulaire pour gérer les permissions personnalisées d'un utilisateur"""
    
    class Meta:
        model = UtilisateurPermission
        fields = ('utilisateur', 'permission', 'accordee')
        widgets = {
            'utilisateur': forms.Select(attrs={'class': 'form-control'}),
            'permission': forms.Select(attrs={'class': 'form-control'}),
            'accordee': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['utilisateur'].label = "Utilisateur"
        self.fields['permission'].label = "Permission"
        self.fields['accordee'].label = "Permission accordée"


class RechercheUtilisateurForm(forms.Form):
    """Formulaire de recherche d'utilisateurs"""
    
    recherche = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par nom, email, username...'
        }),
        label="Recherche"
    )
    
    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(actif=True),
        required=False,
        empty_label="Tous les rôles",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Rôle"
    )
    
    actif = forms.ChoiceField(
        choices=[('', 'Tous'), ('1', 'Actifs'), ('0', 'Inactifs')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Statut"
    )


class RechercheRoleForm(forms.Form):
    """Formulaire de recherche de rôles"""
    
    recherche = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par nom ou description...'
        }),
        label="Recherche"
    )
    
    type_role = forms.ChoiceField(
        choices=[('', 'Tous les types')] + Role.ROLE_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Type de rôle"
    )
