from django import forms
from django.forms import inlineformset_factory
from .models import Facture, LigneFacture
from fournisseurs.models import Fournisseur

class FactureForm(forms.ModelForm):
    """Formulaire pour la création et modification des factures"""
    
    class Meta:
        model = Facture
        fields = [
            'numero', 'fournisseur', 'statut', 'date_emission', 'date_echeance', 
            'objet', 'description', 'taux_tva', 'conditions_paiement', 'notes'
        ]
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de facture'
            }),
            'fournisseur': forms.Select(attrs={
                'class': 'form-control'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date_emission': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_echeance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'objet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Objet de la facture'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description détaillée'
            }),
            'taux_tva': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'conditions_paiement': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Conditions de paiement'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes supplémentaires'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les fournisseurs actifs
        self.fields['fournisseur'].queryset = Fournisseur.objects.filter(actif=True)
    
    def clean_numero(self):
        """Validation du numéro de facture"""
        numero = self.cleaned_data.get('numero')
        if numero:
            # Vérifier l'unicité
            if Facture.objects.filter(numero=numero).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("Ce numéro de facture existe déjà.")
        return numero

class LigneFactureForm(forms.ModelForm):
    """Formulaire pour les lignes de facture"""
    
    class Meta:
        model = LigneFacture
        fields = ['description', 'quantite', 'unite', 'prix_unitaire_ht']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Description de l\'article ou service'
            }),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'unite': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unité (pièce, kg, m², etc.)'
            }),
            'prix_unitaire_ht': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }

# Formset pour les lignes de facture
LigneFactureFormSet = inlineformset_factory(
    Facture,
    LigneFacture,
    form=LigneFactureForm,
    extra=0,  # Pas de ligne vide par défaut
    can_delete=True,
    fields=['description', 'quantite', 'unite', 'prix_unitaire_ht']
)
