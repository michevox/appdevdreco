from django import forms
from django.forms import inlineformset_factory
from .models import Devis, LigneDevis
from clients.models import Client

class DevisForm(forms.ModelForm):
    """Formulaire pour la création et modification des devis"""
    
    class Meta:
        model = Devis
        fields = [
            'numero', 'client', 'statut', 'date_validite', 'objet', 'description',
            'taux_tva', 'conditions_paiement', 'notes'
        ]
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de devis'
            }),
            'client': forms.Select(attrs={
                'class': 'form-control'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date_validite': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'objet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Objet du devis'
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
        # Filtrer les clients actifs
        self.fields['client'].queryset = Client.objects.filter(actif=True)
    
    def clean_numero(self):
        """Validation du numéro de devis"""
        numero = self.cleaned_data.get('numero')
        if numero:
            # Vérifier l'unicité
            if Devis.objects.filter(numero=numero).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("Ce numéro de devis existe déjà.")
        return numero

class LigneDevisForm(forms.ModelForm):
    """Formulaire pour les lignes de devis"""
    
    class Meta:
        model = LigneDevis
        fields = ['description', 'quantite', 'unite', 'prix_unitaire_ht']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Description de la prestation'
            }),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'unite': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unité (heure, m², etc.)'
            }),
            'prix_unitaire_ht': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }

# Formset pour les lignes de devis
LigneDevisFormSet = inlineformset_factory(
    Devis,
    LigneDevis,
    form=LigneDevisForm,
    extra=1,
    can_delete=True,
    fields=['description', 'quantite', 'unite', 'prix_unitaire_ht']
) 