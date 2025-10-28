#!/usr/bin/env python3
"""
Script simple pour configurer le cachet et la signature DEVDRECO
"""

import os
import shutil

def setup_cachet_signature():
    """
    Configure le cachet et la signature pour les PDF des devis
    """
    
    # Créer le dossier de destination
    output_dir = "media/cachets_signatures"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== Configuration du cachet et de la signature DEVDRECO ===")
    print(f"Dossier de destination: {output_dir}")
    
    # Chemins des fichiers
    cachet_path = os.path.join(output_dir, "cachet_devdreco.png")
    signature_path = os.path.join(output_dir, "signature_devdreco.png")
    
    print("\n📋 Instructions pour ajouter votre cachet et signature:")
    print("1. Sauvegardez votre image du cachet et signature dans le dossier:")
    print(f"   {output_dir}")
    print("2. Nommez les fichiers:")
    print(f"   - Cachet: cachet_devdreco.png")
    print(f"   - Signature: signature_devdreco.png")
    print("\n💡 Conseil: Utilisez un éditeur d'image pour séparer le cachet et la signature")
    print("   en deux fichiers distincts pour un meilleur contrôle.")
    
    # Vérifier si les fichiers existent
    cachet_exists = os.path.exists(cachet_path)
    signature_exists = os.path.exists(signature_path)
    
    print(f"\n📊 État actuel:")
    print(f"   Cachet: {'✅ Trouvé' if cachet_exists else '❌ Manquant'}")
    print(f"   Signature: {'✅ Trouvée' if signature_exists else '❌ Manquante'}")
    
    if cachet_exists and signature_exists:
        print("\n🎉 Configuration terminée! Le cachet et la signature seront automatiquement")
        print("   ajoutés aux PDF des devis.")
    else:
        print("\n⚠️  Veuillez ajouter les fichiers manquants pour activer le cachet et la signature.")
    
    return cachet_exists and signature_exists

if __name__ == "__main__":
    setup_cachet_signature()
