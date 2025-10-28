#!/usr/bin/env python3
"""
Script pour nettoyer les fichiers de test
"""

import os

def cleanup_test_files():
    """Nettoie les fichiers de test créés"""
    
    print("=== Nettoyage des fichiers de test ===")
    
    # Fichiers à supprimer
    test_files = [
        "test_devis_avec_cachet.pdf",
        "create_test_images.py",
        "setup_cachet_signature.py", 
        "test_cachet_signature.py",
        "process_cachet_signature.py",
        "cleanup_test_files.py"
    ]
    
    # Dossier de test à supprimer (optionnel)
    test_dir = "media/cachets_signatures"
    
    deleted_count = 0
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Supprimé: {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Erreur suppression {file_path}: {e}")
        else:
            print(f"ℹ️  Non trouvé: {file_path}")
    
    # Optionnel: supprimer le dossier de test s'il est vide
    if os.path.exists(test_dir):
        try:
            if not os.listdir(test_dir):  # Si le dossier est vide
                os.rmdir(test_dir)
                print(f"✅ Dossier vide supprimé: {test_dir}")
            else:
                print(f"ℹ️  Dossier non vide, conservé: {test_dir}")
        except Exception as e:
            print(f"❌ Erreur suppression dossier {test_dir}: {e}")
    
    print(f"\n🎉 Nettoyage terminé: {deleted_count} fichier(s) supprimé(s)")
    
    return deleted_count

if __name__ == "__main__":
    cleanup_test_files()
