# DEVDRECO SOFT

## Description

DEVDRECO SOFT est une application web professionnelle développée en Django pour la gestion complète des activités d'une entreprise d'architecture et BTP. L'application permet de gérer les clients, créer des devis, émettre des factures et gérer les bons de commande.

## Fonctionnalités principales

### 🏢 Gestion des clients
- Création et gestion des profils clients (particuliers, entreprises, collectivités)
- Informations complètes : coordonnées, SIRET, TVA intracommunautaire
- Historique des interactions avec chaque client
- Recherche et filtrage avancés

### 📋 Gestion des devis
- Création de devis détaillés avec lignes multiples
- Calcul automatique des montants HT, TVA et TTC
- Gestion des statuts (brouillon, envoyé, accepté, refusé)
- Duplication de devis existants
- Envoi automatique aux clients

### 🧾 Gestion des factures
- Génération de factures à partir des devis acceptés
- Suivi des paiements (en attente, partiellement payé, payé)
- Calcul automatique des montants restants
- Gestion des échéances et relances

### 📦 Gestion des commandes
- Création de bons de commande
- Suivi des statuts (brouillon, envoyé, confirmé, en cours, livré)
- Gestion des adresses de livraison
- Liaison avec devis et factures

## Technologies utilisées

- **Backend** : Django 5.2.4
- **Base de données** : SQLite (développement) / PostgreSQL (production)
- **Frontend** : HTML5, CSS3, JavaScript, Bootstrap
- **Langage** : Python 3.13.5
- **Système d'authentification** : Django Auth

## Installation et configuration

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation

1. **Cloner le projet**
```bash
git clone [URL_DU_REPO]
cd DEVDRECO-SOFT
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv
```

3. **Activer l'environnement virtuel**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Installer les dépendances**
```bash
pip install django
```

5. **Configurer la base de données**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

7. **Démarrer le serveur de développement**
```bash
python manage.py runserver
```

### Accès à l'application

- **Interface d'administration** : http://localhost:8000/admin/
- **Application principale** : http://localhost:8000/

## Structure du projet

```
DEVDRECO-SOFT/
├── devdreco_soft/          # Configuration principale du projet
├── clients/                # Gestion des clients
├── devis/                  # Gestion des devis
├── factures/               # Gestion des factures
├── commandes/              # Gestion des commandes
├── core/                   # Fonctionnalités communes
├── static/                 # Fichiers statiques (CSS, JS, images)
├── media/                  # Fichiers uploadés
├── templates/              # Templates HTML
├── manage.py              # Script de gestion Django
└── README.md              # Documentation
```

## Modèles de données

### Client
- Informations de base (nom, type, coordonnées)
- Informations professionnelles (SIRET, TVA)
- Historique des interactions

### Devis
- Informations commerciales
- Lignes de devis détaillées
- Calculs automatiques
- Gestion des statuts

### Facture
- Liaison avec devis
- Suivi des paiements
- Calculs automatiques
- Gestion des échéances

### Bon de commande
- Liaison avec devis et factures
- Gestion des livraisons
- Suivi des statuts

## Fonctionnalités avancées

### 🔐 Sécurité
- Authentification requise pour toutes les opérations
- Gestion des permissions utilisateur
- Validation des données côté serveur
- Protection CSRF

### 📊 Tableaux de bord
- Statistiques en temps réel
- Graphiques de performance
- Alertes automatiques
- Rapports personnalisables

### 📧 Envoi automatique
- Génération de PDF pour devis/factures
- Envoi par email automatique
- Templates personnalisables
- Suivi des envois

### 🔄 Workflow automatisé
- Transition automatique devis → facture → commande
- Calculs automatiques des montants
- Mise à jour des statuts
- Notifications automatiques

## Configuration pour la production

### Variables d'environnement
```bash
DEBUG=False
SECRET_KEY=votre_cle_secrete
DATABASE_URL=postgresql://user:password@host:port/db
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre_email@gmail.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe
```

### Base de données PostgreSQL
```bash
pip install psycopg2-binary
```

### Fichiers statiques
```bash
python manage.py collectstatic
```

## Développement

### Ajout de nouvelles fonctionnalités
1. Créer les modèles dans l'application appropriée
2. Générer et appliquer les migrations
3. Créer les vues et formulaires
4. Configurer les URLs
5. Créer les templates
6. Tester les fonctionnalités

### Tests
```bash
python manage.py test
```

### Linting
```bash
pip install flake8
flake8 .
```

## Support et maintenance

### Logs
- Les logs sont stockés dans `logs/`
- Rotation automatique des logs
- Niveaux de log configurables

### Sauvegarde
- Sauvegarde automatique de la base de données
- Sauvegarde des fichiers uploadés
- Rétention configurable

### Monitoring
- Surveillance des performances
- Alertes automatiques
- Rapports de santé système

## Licence

Ce projet est développé pour DEVDRECO. Tous droits réservés.

## Contact

Pour toute question ou support technique :
- Email : michevox.contact@gmail.com
- Développeur : Michel Mahomy

---

**DEVDRECO SOFT** - Solution complète de gestion pour entreprises d'architecture et BTP 