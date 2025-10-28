from django import forms
from django.forms import inlineformset_factory
from .models import BonCommande, LigneCommande
from clients.models import Client
from devis.models import Devis
from fournisseurs.models import Fournisseur

class BonCommandeForm(forms.ModelForm):
    """Formulaire pour créer/modifier un bon de commande"""
    
    class Meta:
        model = BonCommande
        fields = [
            'numero', 'type_commande', 'fournisseur', 'client', 'devis', 'objet', 'description',
            'date_livraison_souhaitee', 'adresse_livraison',
            'conditions_livraison', 'notes', 'taux_tva'
        ]
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de commande'
            }),
            'type_commande': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'toggleCommandeType()'
            }),
            'fournisseur': forms.Select(attrs={
                'class': 'form-control',
                'data-placeholder': 'Sélectionner un fournisseur'
            }),
            'client': forms.Select(attrs={
                'class': 'form-control',
                'data-placeholder': 'Sélectionner un client'
            }),
            'devis': forms.Select(attrs={
                'class': 'form-control',
                'data-placeholder': 'Devis associé (optionnel)'
            }),
            'objet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Objet de la commande'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description détaillée de la commande'
            }),
            'date_livraison_souhaitee': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'adresse_livraison': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adresse complète de livraison'
            }),
            'conditions_livraison': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Conditions de livraison'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes additionnelles'
            }),
            'taux_tva': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les fournisseurs actifs
        self.fields['fournisseur'].queryset = Fournisseur.objects.filter(actif=True)
        # Filtrer les clients actifs
        self.fields['client'].queryset = Client.objects.filter(actif=True)
        # Filtrer les devis acceptés
        self.fields['devis'].queryset = Devis.objects.filter(statut='accepte')
        
        # Rendre le champ numéro non requis (sera généré automatiquement)
        self.fields['numero'].required = False
        
        # Ajouter des classes Bootstrap pour la validation
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

class LigneCommandeForm(forms.ModelForm):
    """Formulaire pour une ligne de commande"""
    
    class Meta:
        model = LigneCommande
        fields = ['description', 'quantite', 'unite', 'prix_unitaire_ht']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Description du produit/service'
            }),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'max': '999999.99',
                'placeholder': 'Quantité'
            }),
            'unite': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unité (kg, m, unité, etc.)'
            }),
            'prix_unitaire_ht': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '9999999999999.99',
                'placeholder': 'Prix unitaire HT'
            })
        }
    
    def clean_quantite(self):
        """Valider que la quantité ne dépasse pas la limite"""
        from decimal import Decimal
        quantite = self.cleaned_data.get('quantite')
        if quantite and quantite > Decimal('999999.99'):
            raise forms.ValidationError("La quantité ne peut pas dépasser 999 999.99")
        return quantite
    
    def clean_prix_unitaire_ht(self):
        """Valider que le prix ne dépasse pas la limite"""
        from decimal import Decimal
        prix = self.cleaned_data.get('prix_unitaire_ht')
        if prix and prix > Decimal('9999999999999.99'):
            raise forms.ValidationError("Le prix unitaire ne peut pas dépasser 9 999 999 999 999.99 GNF")
        return prix

# Formset pour les lignes de commande
LigneCommandeFormSet = inlineformset_factory(
    BonCommande,
    LigneCommande,
    form=LigneCommandeForm,
    extra=0,  # Pas de ligne vide par défaut
    can_delete=True,
    fields=['description', 'quantite', 'unite', 'prix_unitaire_ht']
)

class BonCommandeSearchForm(forms.Form):
    """Formulaire de recherche pour les commandes"""
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par numéro, client, objet...'
        }),
        label="Recherche"
    )
    
    statut = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + BonCommande.STATUT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Statut"
    )
    
    type_commande = forms.ChoiceField(
        choices=[('', 'Tous les types')] + BonCommande.TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Type de commande"
    )
    
    fournisseur = forms.ModelChoiceField(
        queryset=Fournisseur.objects.filter(actif=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Fournisseur"
    )
    
    client = forms.ModelChoiceField(
        queryset=Client.objects.filter(actif=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Client"
    )
    
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Date de début"
    )
    
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Date de fin"
    )
