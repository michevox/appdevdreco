# 🐘 Migration vers PostgreSQL - DEVDRECO SOFT

## 📋 Vue d'ensemble

Ce guide explique comment migrer DEVDRECO SOFT de SQLite vers PostgreSQL pour une meilleure performance et une préparation à la production.

## ✅ Prérequis

- Python 3.8+
- Django 4.2+
- PostgreSQL 12+ (recommandé)

## 🚀 Installation PostgreSQL

### Windows

1. **Téléchargement** :
   - Visitez : https://www.postgresql.org/download/windows/
   - Téléchargez l'installateur officiel

2. **Installation** :
   - Exécutez l'installateur
   - Choisissez un mot de passe pour l'utilisateur `postgres`
   - Notez le port (par défaut : 5432)

3. **Alternative avec gestionnaires de paquets** :
   ```bash
   # Avec Chocolatey
   choco install postgresql
   
   # Avec Scoop
   scoop install postgresql
   ```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### macOS

```bash
# Avec Homebrew
brew install postgresql
brew services start postgresql
```

## 🔧 Configuration

### 1. Créer la base de données

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer la base de données
CREATE DATABASE devdreco_soft;

# Vérifier la création
\l

# Quitter
\q
```

### 2. Configurer les variables d'environnement (optionnel)

Créez un fichier `.env` :
```env
DB_NAME=devdreco_soft
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
```

### 3. Modifier settings.py (déjà fait)

La configuration PostgreSQL est déjà appliquée dans `settings.py` :
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'devdreco_soft'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

## 📦 Migration des données

### 1. Sauvegarder les données SQLite (si nécessaire)

```bash
# Exporter les données SQLite
python manage.py dumpdata --natural-foreign --natural-primary > data_backup.json
```

### 2. Appliquer les migrations PostgreSQL

```bash
# Créer les tables dans PostgreSQL
python manage.py migrate

# Charger les données sauvegardées (si nécessaire)
python manage.py loaddata data_backup.json
```

### 3. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

## 🧪 Tests

### 1. Test de connexion

```bash
python test_postgresql_connection.py
```

### 2. Test de l'application

```bash
python manage.py runserver
```

Visitez : http://127.0.0.1:8000

## 🔍 Vérification

### Commandes utiles

```bash
# Vérifier la connexion
python manage.py dbshell

# Lister les tables
python manage.py showmigrations

# Vérifier les données
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.count()
```

## 🚨 Dépannage

### Erreur de connexion

1. **PostgreSQL non démarré** :
   ```bash
   # Windows (Services)
   services.msc
   
   # Linux
   sudo systemctl start postgresql
   ```

2. **Mot de passe incorrect** :
   - Vérifiez le mot de passe dans `settings.py`
   - Ou modifiez le mot de passe PostgreSQL

3. **Base de données n'existe pas** :
   ```bash
   createdb -U postgres devdreco_soft
   ```

### Erreurs de permissions

```bash
# Accorder les permissions
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE devdreco_soft TO postgres;"
```

## 📊 Avantages de PostgreSQL

- ✅ **Performance** : Meilleure gestion des requêtes complexes
- ✅ **Scalabilité** : Support de gros volumes de données
- ✅ **Sécurité** : Authentification et autorisation avancées
- ✅ **Production** : Standard pour les déploiements professionnels
- ✅ **Extensions** : Support des extensions PostgreSQL

## 🎯 Prochaines étapes

1. ✅ Migration vers PostgreSQL
2. 🔄 Configuration de la production
3. 🚀 Déploiement sur serveur
4. 📊 Monitoring et maintenance

---

**Note** : Cette migration prépare DEVDRECO SOFT pour un déploiement en production avec une base de données robuste et performante.
