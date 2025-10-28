#!/usr/bin/env python3
"""
Script d'installation automatique PostgreSQL pour DEVDRECO SOFT
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Succès")
            return True
        else:
            print(f"❌ {description} - Erreur: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def check_postgresql():
    """Vérifie si PostgreSQL est installé"""
    print("🔍 Vérification de PostgreSQL...")
    
    # Vérifier psql
    result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ PostgreSQL trouvé: {result.stdout.strip()}")
        return True
    else:
        print("❌ PostgreSQL non trouvé")
        return False

def install_postgresql_windows():
    """Instructions d'installation pour Windows"""
    print("""
    🐘 Installation PostgreSQL sur Windows
    
    OPTION 1 - Installateur officiel :
    1. Téléchargez depuis : https://www.postgresql.org/download/windows/
    2. Exécutez l'installateur
    3. Choisissez un mot de passe pour 'postgres'
    4. Notez le port (par défaut 5432)
    
    OPTION 2 - Chocolatey :
    choco install postgresql
    
    OPTION 3 - Scoop :
    scoop install postgresql
    
    Après installation, redémarrez ce script.
    """)

def create_database():
    """Crée la base de données"""
    print("🗄️ Création de la base de données...")
    
    # Commandes pour créer la base de données
    commands = [
        'createdb -U postgres devdreco_soft',
        'psql -U postgres -c "\\l"'
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Exécution: {cmd}"):
            print(f"⚠️ Commande échouée: {cmd}")
            print("💡 Essayez manuellement:")
            print("   psql -U postgres")
            print("   CREATE DATABASE devdreco_soft;")
            return False
    
    return True

def run_django_migrations():
    """Exécute les migrations Django"""
    print("🔄 Migration Django...")
    
    commands = [
        'python manage.py migrate',
        'python manage.py collectstatic --noinput'
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Exécution: {cmd}"):
            print(f"⚠️ Commande échouée: {cmd}")
            return False
    
    return True

def test_connection():
    """Teste la connexion"""
    print("🧪 Test de connexion...")
    
    try:
        import django
        from django.conf import settings
        from django.db import connection
        
        # Configuration Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devdreco_soft.settings')
        django.setup()
        
        # Test de connexion
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Connexion réussie !")
            print(f"📊 Version: {version[0]}")
            return True
            
    except Exception as e:
        print(f"❌ Erreur de test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🐘 Installation PostgreSQL pour DEVDRECO SOFT")
    print("="*60)
    
    # Vérifier PostgreSQL
    if not check_postgresql():
        install_postgresql_windows()
        print("\n⚠️ Installez PostgreSQL d'abord, puis relancez ce script")
        return
    
    # Créer la base de données
    if not create_database():
        print("\n❌ Impossible de créer la base de données")
        return
    
    # Exécuter les migrations
    if not run_django_migrations():
        print("\n❌ Erreur lors des migrations")
        return
    
    # Tester la connexion
    if not test_connection():
        print("\n❌ Test de connexion échoué")
        return
    
    print("\n🎉 Installation PostgreSQL terminée !")
    print("\nProchaines étapes :")
    print("1. Créez un superutilisateur : python manage.py createsuperuser")
    print("2. Lancez l'application : python manage.py runserver")
    print("3. Visitez : http://127.0.0.1:8000")

if __name__ == "__main__":
    main()
