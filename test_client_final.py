#!/usr/bin/env python
"""
Script final pour tester la correction du formulaire de client
"""

import os
import sys
import django
from pathlib import Path

def test_client_final():
    """Teste la correction finale du formulaire de client"""
    print("=== TEST FINAL DU FORMULAIRE DE CLIENT ===")
    
    try:
        # Configuration Django
        BASE_DIR = Path(__file__).resolve().parent
        sys.path.append(str(BASE_DIR))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devdreco_soft.settings')
        django.setup()
        
        from clients.forms import ClientForm
        
        # Test 1: Formulaire avec données valides
        print("1. Test avec données valides...")
        data_valid = {
            'nom_complet': 'Client Test Final',
            'type_client': 'particulier',
            'phone_country_code': '+225',
            'phone_number': '626402000',
            'email': 'testfinal@example.com',
            'adresse': 'Adresse Test Final',
            'actif': True
        }
        
        form_valid = ClientForm(data=data_valid)
        
        if form_valid.is_valid():
            print(f"   ✅ Formulaire valide")
            telephone = form_valid.cleaned_data.get('telephone')
            print(f"   Téléphone généré: '{telephone}'")
            
            if telephone and telephone.startswith('+225'):
                print(f"   ✅ Champ telephone correctement rempli")
            else:
                print(f"   ❌ Champ telephone mal rempli: '{telephone}'")
                return False
        else:
            print(f"   ❌ Formulaire invalide")
            print(f"   Erreurs: {form_valid.errors}")
            return False
        
        # Test 2: Formulaire avec numéro de téléphone manquant
        print("\n2. Test avec numéro de téléphone manquant...")
        data_invalid = {
            'nom_complet': 'Client Test Final 2',
            'type_client': 'particulier',
            'phone_country_code': '+225',
            'phone_number': '',  # Numéro vide
            'email': 'testfinal2@example.com',
            'adresse': 'Adresse Test Final 2',
            'actif': True
        }
        
        form_invalid = ClientForm(data=data_invalid)
        
        if not form_invalid.is_valid():
            print(f"   ✅ Formulaire correctement rejeté (comme attendu)")
            if 'phone_number' in form_invalid.errors:
                print(f"   ✅ Erreur sur phone_number: {form_invalid.errors['phone_number']}")
            else:
                print(f"   ❌ Erreur manquante sur phone_number")
                return False
        else:
            print(f"   ❌ Formulaire accepté alors qu'il devrait être rejeté")
            return False
        
        print("\n🎉 Tous les tests ont réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_client_final()
    
    if success:
        print("\n✅ La correction du formulaire de client fonctionne parfaitement !")
        print("✅ Le champ téléphone est maintenant correctement rempli.")
        print("✅ La validation des erreurs fonctionne correctement.")
        print("✅ Vous pouvez créer des clients sans erreurs.")
    else:
        print("\n❌ Le problème persiste dans le formulaire de client.")

