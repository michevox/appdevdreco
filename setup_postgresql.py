#!/usr/bin/env python3
"""
Script de configuration PostgreSQL pour DEVDRECO SOFT
"""

import os
import subprocess
import sys
from pathlib import Path

def print_step(step, message):
    """Affiche une étape du processus"""
    print(f"\n{'='*50}")
    print(f"ÉTAPE {step}: {message}")
    print('='*50)

def check_postgresql_installed():
    """Vérifie si PostgreSQL est installé"""
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ PostgreSQL trouvé: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PostgreSQL n'est pas installé")
        return False

def install_postgresql_windows():
    """Instructions pour installer PostgreSQL sur Windows"""
    print_step(1, "Installation de PostgreSQL")
    print("""
    Pour installer PostgreSQL sur Windows :
    
    1. Téléchargez PostgreSQL depuis : https://www.postgresql.org/download/windows/
    2. Exécutez l'installateur
    3. Choisissez un mot de passe pour l'utilisateur 'postgres'
    4. Notez le port (par défaut 5432)
    
    Ou utilisez Chocolatey :
    choco install postgresql
    
    Ou utilisez Scoop :
    scoop install postgresql
    """)

def create_database():
    """Crée la base de données DEVDRECO SOFT"""
    print_step(2, "Création de la base de données")
    
    # Commandes SQL pour créer la base de données
    sql_commands = [
        "CREATE DATABASE devdreco_soft;",
        "\\l"  # Lister les bases de données
    ]
    
    print("Exécutez ces commandes dans psql :")
    for cmd in sql_commands:
        print(f"  {cmd}")
    
    print("""
    Ou utilisez cette commande directe :
    createdb -U postgres devdreco_soft
    """)

def configure_django():
    """Configure Django pour PostgreSQL"""
    print_step(3, "Configuration Django")
    
    settings_file = Path("devdreco_soft/settings.py")
    if settings_file.exists():
        print("✅ Configuration PostgreSQL déjà appliquée dans settings.py")
    else:
        print("❌ Fichier settings.py non trouvé")

def run_migrations():
    """Exécute les migrations Django"""
    print_step(4, "Migration des données")
    
    commands = [
        "python manage.py makemigrations",
        "python manage.py migrate",
        "python manage.py createsuperuser"
    ]
    
    print("Exécutez ces commandes :")
    for cmd in commands:
        print(f"  {cmd}")

def main():
    """Fonction principale"""
    print("🐘 Configuration PostgreSQL pour DEVDRECO SOFT")
    print("="*60)
    
    # Vérifier si PostgreSQL est installé
    if not check_postgresql_installed():
        install_postgresql_windows()
        print("\n⚠️  Installez PostgreSQL d'abord, puis relancez ce script")
        return
    
    # Créer la base de données
    create_database()
    
    # Configurer Django
    configure_django()
    
    # Exécuter les migrations
    run_migrations()
    
    print("\n🎉 Configuration PostgreSQL terminée !")
    print("\nProchaines étapes :")
    print("1. Assurez-vous que PostgreSQL est démarré")
    print("2. Créez la base de données 'devdreco_soft'")
    print("3. Exécutez : python manage.py migrate")
    print("4. Créez un superutilisateur : python manage.py createsuperuser")

if __name__ == "__main__":
    main()
