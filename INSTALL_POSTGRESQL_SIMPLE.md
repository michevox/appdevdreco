# 🐘 Installation PostgreSQL - Guide Simple

## 🚨 IMPORTANT : PostgreSQL requis

L'application DEVDRECO SOFT utilise maintenant **PostgreSQL uniquement**. SQLite a été supprimé.

## 🚀 Installation Rapide

### Option 1 : Script Automatique (Recommandé)

```cmd
# Exécuter le script d'installation
install_postgresql_windows.bat
```

### Option 2 : PowerShell (Avancé)

```powershell
# Exécuter en tant qu'administrateur
.\install_postgresql.ps1
```

### Option 3 : Installation Manuelle

1. **Télécharger PostgreSQL** :
   - Visitez : https://www.postgresql.org/download/windows/
   - Téléchargez la version 15+ (64-bit)

2. **Installer** :
   - Exécutez l'installateur
   - Choisissez un mot de passe pour `postgres`
   - Notez le port (5432 par défaut)

3. **Créer la base de données** :
   ```cmd
   psql -U postgres
   CREATE DATABASE devdreco_soft;
   \q
   ```

## 🔧 Configuration

### 1. Démarrer PostgreSQL

```cmd
# Via les Services Windows
services.msc
# Cherchez "postgresql" et démarrez

# Ou via ligne de commande
net start postgresql-x64-15
```

### 2. Créer la base de données

```cmd
# Se connecter
psql -U postgres

# Créer la base
CREATE DATABASE devdreco_soft;

# Vérifier
\l

# Quitter
\q
```

### 3. Migrer Django

```cmd
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 🧪 Test

```cmd
python test_postgresql_connection.py
```

## ❌ Dépannage

### Erreur "Connection refused"
- PostgreSQL n'est pas démarré
- Solution : `net start postgresql-x64-15`

### Erreur "Database does not exist"
- Base de données non créée
- Solution : `CREATE DATABASE devdreco_soft;`

### Erreur "Authentication failed"
- Mot de passe incorrect
- Solution : Vérifiez le mot de passe dans `settings.py`

## 📊 Avantages PostgreSQL

- ✅ **Performance** : 10x plus rapide que SQLite
- ✅ **Sécurité** : Authentification robuste
- ✅ **Production** : Standard industriel
- ✅ **Scalabilité** : Support de millions d'enregistrements

---

**Note** : L'application ne fonctionnera plus sans PostgreSQL. Assurez-vous de l'installer avant de continuer.
