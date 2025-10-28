# Cachet sur les PDF des Devis

## 📋 Description

Cette fonctionnalité permet d'ajouter automatiquement le cachet DEVDRECO sur tous les PDF des devis générés par le système.

## 🎯 Fonctionnalités

- **Cachet automatique** : Le cachet DEVDRECO est ajouté en bas à droite de chaque PDF
- **Taille optimisée** : Cachet de 6cm x 6cm pour une excellente visibilité
- **Position précise** : Le cachet est positionné à 1cm du bas et 1cm du bord droit
- **Textes automatiques** : "Directeur général" et "M. Mensah Kodjo Amélyo" ajoutés sous le cachet
- **Intégration transparente** : Aucune modification manuelle nécessaire
- **Gestion d'erreurs** : Le système continue de fonctionner même si l'image est manquante

## 📁 Structure des fichiers

```
media/
└── cachets_signatures/
    └── cachet_devdreco.png      # Image du cachet
```

## 🚀 Installation

### Étape 1 : Préparer l'image du cachet

1. **Préparer le cachet** :
   - Utilisez un éditeur d'image (Photoshop, GIMP, Paint, etc.)
   - Créez un fichier avec votre cachet DEVDRECO

2. **Format recommandé** :
   - Format : PNG avec transparence
   - Résolution : 300 DPI minimum
   - Taille du cachet : ~6cm x 6cm (sera redimensionné automatiquement)

### Étape 2 : Sauvegarder le fichier

1. Créez le dossier `media/cachets_signatures/` s'il n'existe pas
2. Copiez votre fichier dans ce dossier avec le nom exact :
   - `cachet_devdreco.png`

### Étape 3 : Vérification

Exécutez le script de vérification :
```bash
python setup_cachet_signature.py
```

## 🔧 Configuration

### Positionnement

Le cachet est positionné automatiquement :
- **Cachet** : En bas à droite (6cm x 6cm)
- **Position** : 1cm du bas, 1cm du bord droit
- **Textes automatiques** : "Directeur général" et "M. Mensah Kodjo Amélyo" centrés sous le cachet
- **Visibilité optimisée** : Grande taille pour une excellente visibilité

### Personnalisation

Pour modifier le positionnement, éditez le fichier `devis/utils.py` :

```python
# Dimensions et position du cachet
cachet_width = 6*cm
cachet_height = 6*cm
cachet_x = A4[0] - cachet_width - 1*cm  # Marge droite
cachet_y = 1*cm  # Marge du bas

# Textes sous le cachet
canvas.drawCentredText(text_x, text_y_haut, "Directeur général")
canvas.drawCentredText(text_x, text_y_bas, "M. Mensah Kodjo Amélyo")
```

## 🧪 Test

Pour tester la fonctionnalité :

1. Créez un devis dans le système
2. Générez le PDF (bouton "Imprimer" ou "Télécharger")
3. Vérifiez que le cachet apparaît en bas à droite

## 🐛 Dépannage

### Le cachet n'apparaît pas

1. **Vérifiez les fichiers** :
   ```bash
   python setup_cachet_signature.py
   ```

2. **Vérifiez les permissions** :
   - Assurez-vous que le dossier `media/cachets_signatures/` est accessible en lecture

3. **Vérifiez le format** :
   - Le fichier doit être au format PNG
   - Le nom doit être exact (sensible à la casse)

### Erreur lors de la génération PDF

- Vérifiez les logs du serveur Django
- Assurez-vous que l'image n'est pas corrompue
- Testez avec une image plus petite

## 📝 Notes techniques

- **Format supporté** : PNG avec transparence
- **Taille maximale recommandée** : 1MB
- **Résolution** : 300 DPI pour une qualité optimale
- **Transparence** : Supportée pour un rendu professionnel

## 🔄 Mise à jour

Pour mettre à jour le cachet :

1. Remplacez simplement le fichier dans `media/cachets_signatures/`
2. Aucun redémarrage nécessaire
3. Les nouveaux PDF utiliseront automatiquement la nouvelle image

## 📞 Support

En cas de problème, vérifiez :
1. Le fichier est bien présent dans le bon dossier
2. Le nom de fichier est correct
3. L'image n'est pas corrompue
4. Les permissions de lecture sont correctes
