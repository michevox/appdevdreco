#!/usr/bin/env python3
"""
Script pour traiter l'image du cachet et de la signature DEVDRECO
et la séparer en deux fichiers distincts.
"""

import os
from PIL import Image
import sys

def process_cachet_signature():
    """
    Traite l'image du cachet et de la signature pour les séparer
    et les sauvegarder dans le dossier approprié.
    """
    
    # Créer le dossier de destination s'il n'existe pas
    output_dir = "media/cachets_signatures"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== Traitement du cachet et de la signature DEVDRECO ===")
    print(f"Dossier de destination: {output_dir}")
    
    # Instructions pour l'utilisateur
    print("\n📋 Instructions:")
    print("1. Sauvegardez votre image du cachet et signature dans ce dossier")
    print("2. Nommez-la 'cachet_signature_original.png'")
    print("3. Le script la traitera automatiquement")
    
    # Chemin vers l'image originale
    original_path = os.path.join(output_dir, "cachet_signature_original.png")
    
    if not os.path.exists(original_path):
        print(f"\n❌ Fichier non trouvé: {original_path}")
        print("Veuillez d'abord sauvegarder votre image dans ce fichier.")
        return False
    
    try:
        # Ouvrir l'image originale
        img = Image.open(original_path)
        print(f"\n✅ Image chargée: {img.size[0]}x{img.size[1]} pixels")
        
        # Convertir en RGBA si nécessaire
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Dimensions de l'image
        width, height = img.size
        
        # Séparer le cachet (côté gauche) et la signature (côté droit)
        # Ajustez ces valeurs selon votre image
        cachet_width = int(width * 0.6)  # 60% de la largeur pour le cachet
        signature_width = width - cachet_width  # Le reste pour la signature
        
        # Extraire le cachet (côté gauche)
        cachet_box = (0, 0, cachet_width, height)
        cachet_img = img.crop(cachet_box)
        
        # Extraire la signature (côté droit)
        signature_box = (cachet_width, 0, width, height)
        signature_img = img.crop(signature_box)
        
        # Sauvegarder le cachet
        cachet_path = os.path.join(output_dir, "cachet_devdreco.png")
        cachet_img.save(cachet_path, "PNG")
        print(f"✅ Cachet sauvegardé: {cachet_path}")
        
        # Sauvegarder la signature
        signature_path = os.path.join(output_dir, "signature_devdreco.png")
        signature_img.save(signature_path, "PNG")
        print(f"✅ Signature sauvegardée: {signature_path}")
        
        print("\n🎉 Traitement terminé avec succès!")
        print("Les fichiers sont maintenant prêts pour être utilisés dans les PDF.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du traitement: {e}")
        return False

if __name__ == "__main__":
    success = process_cachet_signature()
    if success:
        print("\n✅ Le cachet et la signature sont maintenant intégrés dans les PDF des devis!")
    else:
        print("\n❌ Échec du traitement. Veuillez vérifier les fichiers.")
