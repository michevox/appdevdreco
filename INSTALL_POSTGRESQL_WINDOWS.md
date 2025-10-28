# 🐘 Installation PostgreSQL sur Windows - DEVDRECO SOFT

## 🚨 Problème Actuel

L'erreur `Connection refused` indique que PostgreSQL n'est pas installé ou démarré sur votre système.

## ✅ Solution Immédiate

L'application fonctionne maintenant avec **SQLite** (base de données de développement).

## 🚀 Installation PostgreSQL (Optionnel)

### Méthode 1 : Installateur Officiel (Recommandé)

1. **Télécharger PostgreSQL** :
   - Visitez : https://www.postgresql.org/download/windows/
   - Téléchargez la version 15+ (64-bit)

2. **Installer PostgreSQL** :
   - Exécutez l'installateur téléchargé
   - Choisissez un mot de passe pour l'utilisateur `postgres`
   - Notez le port (par défaut : 5432)
   - Laissez les options par défaut

3. **Vérifier l'installation** :
   ```cmd
   psql --version
   ```

### Méthode 2 : Chocolatey (Si installé)

```cmd
choco install postgresql
```

### Méthode 3 : Scoop (Si installé)

```cmd
scoop install postgresql
```

## 🔧 Configuration après Installation

### 1. Démarrer PostgreSQL

```cmd
# Via les Services Windows
services.msc
# Cherchez "postgresql" et démarrez le service

# Ou via la ligne de commande
net start postgresql-x64-15
```

### 2. Créer la base de données

```cmd
# Se connecter à PostgreSQL
psql -U postgres

# Créer la base de données
CREATE DATABASE devdreco_soft;

# Vérifier
\l

# Quitter
\q
```

### 3. Activer PostgreSQL dans Django

Dans `devdreco_soft/settings.py`, décommentez la section PostgreSQL :

```python
# Décommentez cette section
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'devdreco_soft',
        'USER': 'postgres',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Commentez la section SQLite
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
```

### 4. Migrer vers PostgreSQL

```cmd
python manage.py migrate
python manage.py createsuperuser
```

## 🧪 Test de l'Installation

```cmd
python test_postgresql_connection.py
```

## 📊 Avantages de PostgreSQL

- ✅ **Performance** : Meilleure gestion des requêtes
- ✅ **Sécurité** : Authentification avancée
- ✅ **Production** : Standard pour les déploiements
- ✅ **Scalabilité** : Support de gros volumes

## 🎯 Recommandation

**Pour le développement** : SQLite est suffisant
**Pour la production** : PostgreSQL est recommandé

L'application fonctionne parfaitement avec SQLite pour le développement et les tests !
