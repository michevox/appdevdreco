#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devdreco_soft.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from devis.views import DevisListView

def quick_test():
    print("=== Test rapide de la vue ===")
    
    try:
        # Créer une requête de test
        factory = RequestFactory()
        request = factory.get('/devis/')
        
        # Créer un utilisateur
        user = User.objects.first()
        if user:
            request.user = user
            print(f"Utilisateur: {user.username}")
        
        # Tester la vue
        view = DevisListView()
        view.request = request
        
        # Obtenir le queryset
        queryset = view.get_queryset()
        print(f"✅ Queryset obtenu: {queryset.count()} devis")
        
        # Obtenir le contexte
        context = view.get_context_data()
        print(f"✅ Contexte obtenu avec les clés: {list(context.keys())}")
        
        if 'devis_list' in context:
            print(f"✅ devis_list dans le contexte: {len(context['devis_list'])} éléments")
            
            # Vérifier le premier devis
            if context['devis_list']:
                devis = context['devis_list'][0]
                print(f"✅ Premier devis: {devis.numero} - HT: {devis.montant_ht}")
        
        print("\n🎉 La vue fonctionne parfaitement !")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    quick_test()
