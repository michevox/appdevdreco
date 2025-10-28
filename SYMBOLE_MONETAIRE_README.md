# Système de Symbole Monétaire Global - DEVDRECO SOFT

## 🎯 Objectif

Ce système permet d'appliquer automatiquement le symbole monétaire choisi dans les paramètres à l'ensemble de l'application, sans avoir à modifier manuellement chaque template ou vue.

## 🏗️ Architecture

### 1. Contexte Global (`context_processors.py`)
- **Fichier**: `parametres/context_processors.py`
- **Fonction**: `parametres_globaux(request)`
- **Disponibilité**: Automatiquement disponible dans tous les templates

### 2. Utilitaires (`utils.py`)
- **Fichier**: `parametres/utils.py`
- **Fonctions**:
  - `get_symbole_monetaire()`: Récupère le symbole actuel
  - `formater_montant(montant, symbole=None)`: Formate un montant avec le symbole
  - `formater_montant_avec_decimaux(montant, symbole=None, decimales=2)`: Formate avec décimales

### 3. Filtres de Template (`parametres_filters.py`)
- **Fichier**: `parametres/templatetags/parametres_filters.py`
- **Filtres disponibles**:
  - `{{ montant|format_montant }}`: Formatage simple
  - `{{ montant|format_montant_simple }}`: Sans décimales
  - `{{ montant|format_montant_decimal }}`: Avec décimales
  - `{{ prix|format_prix:"par kg" }}`: Prix avec unité
  - `{{ quantite|format_quantite:"kg" }}`: Quantité avec unité

## 📱 Utilisation dans les Templates

### Chargement des filtres
```html
{% load parametres_filters %}
```

### Variables globales disponibles
```html
<!-- Symbole monétaire actuel -->
{{ PARAMETRES_GLOBAUX.symbole_monetaire }}

<!-- Nom de l'application -->
{{ PARAMETRES_GLOBAUX.nom_application }}

<!-- Autres paramètres -->
{{ PARAMETRES_GLOBAUX.elements_par_page }}
{{ PARAMETRES_GLOBAUX.format_date }}
```

### Formatage des montants
```html
<!-- Montant simple -->
{{ devis.montant_ht|format_montant_simple }}

<!-- Montant avec décimales -->
{{ devis.montant_ttc|format_montant_decimal }}

<!-- Prix avec unité -->
{{ ligne.prix_unitaire_ht|format_prix:"par kg" }}

<!-- Quantité avec unité -->
{{ ligne.quantite|format_quantite:"kg" }}
```

## 🐍 Utilisation dans les Vues Python

### Import des utilitaires
```python
from parametres.utils import get_symbole_monetaire, formater_montant
```

### Récupération du symbole
```python
symbole = get_symbole_monetaire()  # Retourne 'GNF', 'EUR', etc.
```

### Formatage des montants
```python
# Formatage automatique avec le symbole par défaut
montant_formate = formater_montant(25000)  # "25 000 GNF"

# Formatage avec un symbole spécifique
montant_formate = formater_montant(25000, 'EUR')  # "25 000 EUR"

# Formatage avec décimales
montant_formate = formater_montant_avec_decimaux(25000.50)  # "25 000,50 GNF"
```

## 🔧 Configuration

### 1. Ajout dans `settings.py`
```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ... autres context processors
                'parametres.context_processors.parametres_globaux',
            ],
        },
    },
]
```

### 2. Migration automatique
Le système crée automatiquement les paramètres par défaut si aucun n'existe :
- Symbole monétaire: **GNF** (Franc Guinéen)
- Nom application: **DEVDRECO SOFT**
- Éléments par page: **20**
- Format date: **d/m/Y**

## 📊 Exemples d'Utilisation

### Template de devis
```html
{% load parametres_filters %}

<div class="devis-info">
    <h3>Devis {{ devis.numero }}</h3>
    <p>Montant HT: {{ devis.montant_ht|format_montant_simple }}</p>
    <p>Montant TTC: {{ devis.montant_ttc|format_montant_decimal }}</p>
    <p>Devise: {{ PARAMETRES_GLOBAUX.symbole_monetaire }}</p>
</div>
```

### Vue Django
```python
from parametres.utils import formater_montant

def ma_vue(request):
    montant = 50000
    montant_formate = formater_montant(montant)
    
    context = {
        'montant_formate': montant_formate,
        'symbole': get_symbole_monetaire()
    }
    return render(request, 'template.html', context)
```

### JavaScript (si nécessaire)
```javascript
// Le symbole peut être passé depuis le template
const symboleMonetaire = '{{ PARAMETRES_GLOBAUX.symbole_monetaire }}';

function formaterMontant(montant) {
    return new Intl.NumberFormat('fr-FR').format(montant) + ' ' + symboleMonetaire;
}
```

## 🚀 Avantages

1. **Centralisation**: Un seul endroit pour changer le symbole monétaire
2. **Automatisation**: Changement automatique dans toute l'application
3. **Cohérence**: Même formatage partout
4. **Maintenance**: Facile à maintenir et modifier
5. **Flexibilité**: Support de multiples devises
6. **Performance**: Pas de requêtes supplémentaires dans les templates

## 🔄 Changement de Devise

### Via l'interface d'administration
1. Aller dans **Paramètres > Généraux**
2. Changer le **Symbole monétaire**
3. Sauvegarder

### Via le code
```python
from parametres.models import ParametresGeneraux

parametres = ParametresGeneraux.objects.first()
parametres.symbole_monetaire = 'EUR'
parametres.save()
```

## 🧪 Test

Pour tester le système :
```bash
python manage.py shell
```

```python
from parametres.utils import get_symbole_monetaire, formater_montant

# Test du symbole
print(get_symbole_monetaire())  # Devrait afficher 'GNF'

# Test du formatage
print(formater_montant(100000))  # Devrait afficher '100 000 GNF'
```

## 📝 Notes Importantes

- Le symbole **GNF** est défini par défaut
- Les changements sont appliqués immédiatement
- Tous les templates doivent charger `{% load parametres_filters %}`
- Le système gère automatiquement les erreurs et valeurs nulles
- Support des séparateurs de milliers français (espaces)
- Support des décimales avec virgule

## 🆘 Dépannage

### Problème: Filtres non reconnus
**Solution**: Vérifier que `{% load parametres_filters %}` est présent

### Problème: Variables globales non disponibles
**Solution**: Vérifier que le context processor est dans `settings.py`

### Problème: Symbole incorrect
**Solution**: Vérifier les paramètres dans l'administration Django
