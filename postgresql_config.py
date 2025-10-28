"""
Configuration PostgreSQL pour DEVDRECO SOFT
"""

# Configuration de base de données PostgreSQL
POSTGRESQL_CONFIG = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'devdreco_soft',
    'USER': 'postgres',
    'PASSWORD': 'password',  # Changez ce mot de passe
    'HOST': 'localhost',
    'PORT': '5432',
    'OPTIONS': {
        'charset': 'utf8',
    },
}

# Instructions d'installation
INSTALLATION_INSTRUCTIONS = """
🐘 Installation PostgreSQL pour DEVDRECO SOFT

1. INSTALLATION POSTGRESQL :
   - Windows : https://www.postgresql.org/download/windows/
   - Ou avec Chocolatey : choco install postgresql
   - Ou avec Scoop : scoop install postgresql

2. CRÉATION DE LA BASE DE DONNÉES :
   - Ouvrez psql : psql -U postgres
   - Créez la base : CREATE DATABASE devdreco_soft;
   - Vérifiez : \\l

3. CONFIGURATION DJANGO :
   - Les paramètres sont déjà configurés dans settings.py
   - Modifiez le mot de passe dans settings.py si nécessaire

4. MIGRATION :
   - python manage.py migrate
   - python manage.py createsuperuser

5. TEST :
   - python manage.py runserver
   - Vérifiez que l'application fonctionne
"""

print(INSTALLATION_INSTRUCTIONS)
