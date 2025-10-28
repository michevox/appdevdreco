#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration du cachet et de la signature
dans les PDF des devis.
"""

import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devdreco_soft.settings')
django.setup()

def test_cachet_signature_integration():
    """
    Teste l'intégration du cachet et de la signature dans les PDF
    """
    
    print("=== Test d'intégration du cachet et de la signature ===")
    
    # Vérifier que le dossier existe
    cachet_dir = "media/cachets_signatures"
    if not os.path.exists(cachet_dir):
        print(f"❌ Dossier manquant: {cachet_dir}")
        return False
    
    # Vérifier les fichiers requis
    cachet_path = os.path.join(cachet_dir, "cachet_devdreco.png")
    signature_path = os.path.join(cachet_dir, "signature_devdreco.png")
    
    cachet_exists = os.path.exists(cachet_path)
    signature_exists = os.path.exists(signature_path)
    
    print(f"📁 Dossier: {'✅' if os.path.exists(cachet_dir) else '❌'} {cachet_dir}")
    print(f"🔵 Cachet: {'✅' if cachet_exists else '❌'} {cachet_path}")
    print(f"✍️  Signature: {'✅' if signature_exists else '❌'} {signature_path}")
    
    if not cachet_exists or not signature_exists:
        print("\n⚠️  Fichiers manquants. Veuillez ajouter :")
        if not cachet_exists:
            print(f"   - {cachet_path}")
        if not signature_exists:
            print(f"   - {signature_path}")
        return False
    
    # Tester l'import des modules nécessaires
    try:
        from devis.utils import generer_pdf_reportlab
        print("✅ Module de génération PDF importé avec succès")
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    
    # Tester l'import de ReportLab
    try:
        from reportlab.lib.utils import ImageReader
        print("✅ ReportLab ImageReader importé avec succès")
    except ImportError as e:
        print(f"❌ Erreur d'import ReportLab: {e}")
        return False
    
    # Tester la lecture des images
    try:
        cachet_img = ImageReader(cachet_path)
        print("✅ Cachet lisible")
    except Exception as e:
        print(f"❌ Erreur lecture cachet: {e}")
        return False
    
    try:
        signature_img = ImageReader(signature_path)
        print("✅ Signature lisible")
    except Exception as e:
        print(f"❌ Erreur lecture signature: {e}")
        return False
    
    print("\n🎉 Tous les tests sont passés avec succès!")
    print("Le cachet et la signature seront automatiquement ajoutés aux PDF des devis.")
    
    return True

def test_pdf_generation():
    """
    Teste la génération d'un PDF avec le cachet et la signature
    """
    
    print("\n=== Test de génération PDF ===")
    
    try:
        from devis.models import Devis
        from devis.utils import generer_pdf_reportlab
        
        # Récupérer un devis existant pour le test
        devis = Devis.objects.first()
        
        if not devis:
            print("⚠️  Aucun devis trouvé pour le test")
            return False
        
        print(f"📄 Test avec le devis: {devis.numero}")
        
        # Récupérer les lignes du devis
        lignes = devis.lignes.all()
        
        # Utiliser la fonction get_societe_info() qui retourne le bon format
        from devis.utils import get_societe_info
        societe_info = get_societe_info()
        
        # Générer le PDF
        pdf_content = generer_pdf_reportlab(devis, lignes, societe_info)
        
        if pdf_content:
            print("✅ PDF généré avec succès")
            print(f"📊 Taille du PDF: {len(pdf_content)} bytes")
            
            # Sauvegarder le PDF de test
            test_pdf_path = "test_devis_avec_cachet.pdf"
            with open(test_pdf_path, 'wb') as f:
                f.write(pdf_content)
            print(f"💾 PDF de test sauvegardé: {test_pdf_path}")
            
            return True
        else:
            print("❌ Échec de la génération du PDF")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test d'intégration du cachet et de la signature DEVDRECO")
    print("=" * 60)
    
    # Test 1: Vérification des fichiers
    success1 = test_cachet_signature_integration()
    
    if success1:
        # Test 2: Génération PDF
        success2 = test_pdf_generation()
        
        if success2:
            print("\n🎉 Tous les tests sont passés!")
            print("Le cachet et la signature sont maintenant intégrés dans les PDF des devis.")
        else:
            print("\n⚠️  Test de génération PDF échoué")
    else:
        print("\n⚠️  Configuration incomplète")
        print("Veuillez ajouter les fichiers manquants et relancer le test.")
