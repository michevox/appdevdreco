#!/usr/bin/env python3
"""
Script de test de connexion PostgreSQL pour DEVDRECO SOFT
"""

import os
import sys
import django
from pathlib import Path

# Ajouter le répertoire du projet au path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devdreco_soft.settings')
django.setup()

def test_postgresql_connection():
    """Teste la connexion à PostgreSQL"""
    try:
        from django.db import connection
        from django.core.management import execute_from_command_line
        
        print("🐘 Test de connexion PostgreSQL...")
        print("="*50)
        
        # Test de connexion
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Connexion réussie !")
            print(f"📊 Version PostgreSQL : {version[0]}")
            
        # Test des tables Django
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()
        print(f"📋 Tables trouvées : {len(tables)}")
        
        for table in tables[:5]:  # Afficher les 5 premières tables
            print(f"  - {table[0]}")
        
        if len(tables) > 5:
            print(f"  ... et {len(tables) - 5} autres tables")
            
        print("\n🎉 PostgreSQL est correctement configuré !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        print("\n🔧 Solutions possibles :")
        print("1. Vérifiez que PostgreSQL est installé et démarré")
        print("2. Vérifiez les paramètres dans settings.py")
        print("3. Créez la base de données : createdb -U postgres devdreco_soft")
        print("4. Exécutez les migrations : python manage.py migrate")
        return False

def test_django_models():
    """Teste les modèles Django"""
    try:
        print("\n🔍 Test des modèles Django...")
        
        from django.apps import apps
        from django.db import models
        
        # Lister les applications
        app_configs = apps.get_app_configs()
        print(f"📱 Applications trouvées : {len(app_configs)}")
        
        for app_config in app_configs:
            if not app_config.name.startswith('django.'):
                models_count = len(app_config.get_models())
                print(f"  - {app_config.name}: {models_count} modèles")
        
        print("✅ Modèles Django fonctionnels !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur avec les modèles : {e}")
        return False

def main():
    """Fonction principale"""
    print("🧪 Test de configuration PostgreSQL pour DEVDRECO SOFT")
    print("="*60)
    
    # Test de connexion
    connection_ok = test_postgresql_connection()
    
    if connection_ok:
        # Test des modèles
        models_ok = test_django_models()
        
        if models_ok:
            print("\n🎉 Tous les tests sont passés !")
            print("✅ PostgreSQL est prêt pour DEVDRECO SOFT")
        else:
            print("\n⚠️  Problème avec les modèles Django")
    else:
        print("\n❌ Problème de connexion PostgreSQL")
        print("\n📖 Consultez le fichier postgresql_config.py pour les instructions")

if __name__ == "__main__":
    main()
