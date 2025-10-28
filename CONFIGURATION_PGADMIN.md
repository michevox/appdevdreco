# 🐘 Configuration PostgreSQL avec pgAdmin - DEVDRECO SOFT

## 🎯 Configuration Rapide

### 1. **Ouvrir pgAdmin**
- Lancez pgAdmin depuis le menu Démarrer
- Connectez-vous avec le mot de passe PostgreSQL

### 2. **Créer la Base de Données**
1. **Clic droit** sur "Databases" → **Create** → **Database...**
2. **Nom** : `devdreco_soft`
3. **Owner** : `postgres`
4. **Cliquez** sur "Save"

### 3. **Vérifier la Connexion**
- La base `devdreco_soft` doit apparaître dans la liste
- **Statut** : Active

## 🔧 Configuration Django

### 1. **Modifier settings.py** (déjà fait)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'devdreco_soft',
        'USER': 'postgres',
        'PASSWORD': 'votre_mot_de_passe_postgresql',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 2. **Mettre à jour le mot de passe**
Dans `devdreco_soft/settings.py`, ligne 101 :
```python
'PASSWORD': 'votre_mot_de_passe_postgresql',  # Remplacez par votre mot de passe
```

## 🚀 Migration

### 1. **Exécuter les migrations**
```cmd
python manage.py migrate
```

### 2. **Créer un superutilisateur**
```cmd
python manage.py createsuperuser
```

### 3. **Lancer l'application**
```cmd
python manage.py runserver
```

## 🧪 Test de Connexion

### Via pgAdmin
1. **Ouvrir** pgAdmin
2. **Se connecter** au serveur PostgreSQL
3. **Vérifier** que `devdreco_soft` existe

### Via Django
```cmd
python test_postgresql_connection.py
```

## ❌ Dépannage

### Erreur "Authentication failed"
- **Cause** : Mot de passe incorrect
- **Solution** : Vérifiez le mot de passe dans `settings.py`

### Erreur "Database does not exist"
- **Cause** : Base de données non créée
- **Solution** : Créez `devdreco_soft` dans pgAdmin

### Erreur "Connection refused"
- **Cause** : PostgreSQL non démarré
- **Solution** : Démarrez le service PostgreSQL

## 📊 Avantages pgAdmin

- ✅ **Interface graphique** : Facile à utiliser
- ✅ **Gestion des bases** : Création/modification visuelle
- ✅ **Monitoring** : Surveillance des performances
- ✅ **Requêtes SQL** : Éditeur intégré

---

**Note** : Une fois configuré, l'application DEVDRECO SOFT utilisera PostgreSQL pour toutes les opérations de base de données.
