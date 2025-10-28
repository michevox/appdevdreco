#!/usr/bin/env python3
"""
Script pour créer des images de test du cachet et de la signature
"""

import os
from PIL import Image, ImageDraw, ImageFont
import sys

def create_test_cachet():
    """Crée une image de test pour le cachet"""
    
    # Créer le dossier s'il n'existe pas
    os.makedirs("media/cachets_signatures", exist_ok=True)
    
    # Dimensions du cachet (3cm x 3cm à 300 DPI)
    width, height = 354, 354  # 3cm à 300 DPI
    
    # Créer une image avec fond transparent
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Dessiner un cercle bleu pour le cachet
    margin = 20
    draw.ellipse([margin, margin, width-margin, height-margin], 
                 fill=(0, 100, 200, 200), outline=(0, 50, 150, 255), width=3)
    
    # Ajouter du texte
    try:
        # Essayer d'utiliser une police système
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        # Police par défaut si arial n'est pas disponible
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Texte du cachet
    text = "DEVDRECO\nSARLU\nTél: 655 43 33 33"
    
    # Calculer la position du texte (centré)
    bbox = draw.textbbox((0, 0), text, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Dessiner le texte
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font_large, align="center")
    
    # Sauvegarder
    cachet_path = "media/cachets_signatures/cachet_devdreco.png"
    img.save(cachet_path, "PNG")
    print(f"✅ Cachet de test créé: {cachet_path}")
    
    return cachet_path

def create_test_signature():
    """Crée une image de test pour la signature"""
    
    # Dimensions de la signature (2.5cm x 1.5cm à 300 DPI)
    width, height = 295, 177  # 2.5cm x 1.5cm à 300 DPI
    
    # Créer une image avec fond transparent
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Dessiner une signature stylisée
    # Ligne de signature ondulée
    points = []
    for i in range(0, width, 5):
        y = height // 2 + 20 * (i / width) * (1 if i % 10 < 5 else -1)
        points.append((i, y))
    
    if len(points) > 1:
        draw.line(points, fill=(0, 0, 0, 255), width=3)
    
    # Ajouter quelques traits supplémentaires pour simuler une signature
    for i in range(3):
        start_x = i * width // 3
        start_y = height // 2 + 10
        end_x = start_x + 30
        end_y = start_y + 20
        draw.line([(start_x, start_y), (end_x, end_y)], fill=(0, 0, 0, 200), width=2)
    
    # Sauvegarder
    signature_path = "media/cachets_signatures/signature_devdreco.png"
    img.save(signature_path, "PNG")
    print(f"✅ Signature de test créée: {signature_path}")
    
    return signature_path

def main():
    """Fonction principale"""
    
    print("=== Création d'images de test pour le cachet et la signature ===")
    
    try:
        # Créer les images de test
        cachet_path = create_test_cachet()
        signature_path = create_test_signature()
        
        print(f"\n🎉 Images de test créées avec succès!")
        print(f"📁 Cachet: {cachet_path}")
        print(f"✍️  Signature: {signature_path}")
        print("\n💡 Ces images de test permettront de vérifier que le système fonctionne.")
        print("   Vous pouvez les remplacer par vos vraies images plus tard.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des images: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Vous pouvez maintenant tester la génération de PDF avec cachet et signature!")
    else:
        print("\n❌ Échec de la création des images de test.")
