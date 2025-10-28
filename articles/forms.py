from django import forms
from .models import Categorie, Article


class CategorieForm(forms.ModelForm):
    """Formulaire pour les catégories"""
    
    class Meta:
        model = Categorie
        fields = ['libelle']
        widgets = {
            'libelle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le libellé de la catégorie',
                'required': True
            })
        }
        labels = {
            'libelle': 'Libellé de la catégorie'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['libelle'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Entrez le libellé de la catégorie'
        })


class ArticleForm(forms.ModelForm):
    """Formulaire pour les articles"""
    
    class Meta:
        model = Article
        fields = ['designation', 'categorie']
        widgets = {
            'designation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez la désignation de l\'article',
                'required': True
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            })
        }
        labels = {
            'designation': 'Désignation de l\'article',
            'categorie': 'Catégorie'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer seulement les catégories actives
        self.fields['categorie'].queryset = Categorie.objects.filter(actif=True)
        self.fields['categorie'].empty_label = "Sélectionnez une catégorie"
        
        self.fields['designation'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Entrez la désignation de l\'article'
        })
        self.fields['categorie'].widget.attrs.update({
            'class': 'form-control'
        })

