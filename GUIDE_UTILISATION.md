# Guide d'Utilisation - DEVDRECO SOFT

## 🚀 Démarrage rapide

### 1. Accès à l'application

**URL de l'application :** `http://localhost:8000/`

**Interface d'administration :** `http://localhost:8000/admin/`

### 2. Connexion

1. Cliquez sur le bouton **"Se connecter"** dans la barre de navigation
2. Une fenêtre popup **"Identifiez-vous !"** s'ouvre
3. Entrez vos identifiants :
   - **Nom d'utilisateur :** `admin`
   - **Mot de passe :** (celui que vous avez créé)
4. Cliquez sur **"Se connecter"**

### 3. Navigation

Une fois connecté, vous accédez au **tableau de bord** avec :
- **Menu latéral** : Navigation entre les modules
- **Statistiques** : Vue d'ensemble des données
- **Actions rapides** : Création rapide d'éléments

## 📋 Modules principaux

### 🏢 Gestion des Clients

**Accès :** Menu "Clients" ou bouton "Nouveau client"

#### Fonctionnalités :
- ✅ **Créer un client** : Informations complètes (nom, adresse, SIRET, TVA)
- ✅ **Rechercher** : Recherche par nom, email, téléphone, ville
- ✅ **Modifier** : Mise à jour des informations client
- ✅ **Supprimer** : Suppression logique (client inactif)
- ✅ **Tableau de bord client** : Vue d'ensemble des interactions

#### Types de clients :
- **Particulier** : Clients individuels
- **Entreprise** : Sociétés et organisations
- **Collectivité** : Organismes publics

### 📋 Gestion des Devis

**Accès :** Menu "Devis" ou bouton "Nouveau devis"

#### Fonctionnalités :
- ✅ **Créer un devis** : Avec lignes détaillées et calculs automatiques
- ✅ **Gérer les statuts** : Brouillon → Envoyé → Accepté/Refusé
- ✅ **Calculs automatiques** : HT, TVA, TTC
- ✅ **Dupliquer** : Créer un nouveau devis basé sur un existant
- ✅ **Envoyer** : Marquer comme envoyé avec date
- ✅ **Suivi** : Historique complet des actions

#### Statuts des devis :
- **Brouillon** : En cours de création
- **Envoyé** : Transmis au client
- **Accepté** : Validé par le client
- **Refusé** : Rejeté par le client
- **Expiré** : Date de validité dépassée

### 🧾 Gestion des Factures

**Accès :** Menu "Factures" ou bouton "Nouvelle facture"

#### Fonctionnalités :
- ✅ **Créer une facture** : À partir d'un devis accepté ou indépendamment
- ✅ **Suivi des paiements** : En attente → Partiellement payé → Payé
- ✅ **Calculs automatiques** : Montants restants à payer
- ✅ **Échéances** : Gestion des dates de paiement
- ✅ **Relances** : Factures en retard automatiquement identifiées

#### Statuts de paiement :
- **En attente** : Facture émise, paiement attendu
- **Partiellement payé** : Acompte reçu
- **Payé** : Montant total reçu
- **En retard** : Échéance dépassée
- **Annulé** : Facture annulée

### 📦 Gestion des Commandes

**Accès :** Menu "Commandes" ou bouton "Nouvelle commande"

#### Fonctionnalités :
- ✅ **Créer une commande** : Avec adresse de livraison
- ✅ **Suivi des statuts** : Brouillon → Envoyé → Confirmé → En cours → Livré
- ✅ **Liaison** : Avec devis et factures associés
- ✅ **Livraison** : Gestion des adresses et dates
- ✅ **Traçabilité** : Historique complet du processus

#### Statuts des commandes :
- **Brouillon** : En cours de création
- **Envoyé** : Transmis au fournisseur
- **Confirmé** : Validé par le fournisseur
- **En cours** : En cours de préparation/livraison
- **Livré** : Réception confirmée
- **Annulé** : Commande annulée

## 🔐 Sécurité et Permissions

### Rôles utilisateur

#### Administrateur (Superuser)
- ✅ **Accès complet** : Tous les modules et fonctionnalités
- ✅ **Gestion des utilisateurs** : Créer, modifier, supprimer des comptes
- ✅ **Configuration** : Paramètres système
- ✅ **Administration** : Interface d'administration Django

#### Utilisateur standard
- ✅ **Accès limité** : Modules clients, devis, factures, commandes
- ✅ **Modification** : Peut modifier son propre profil uniquement
- ❌ **Création d'utilisateurs** : Non autorisé
- ❌ **Administration** : Accès limité

### Authentification

- **Connexion requise** : Toutes les opérations nécessitent une authentification
- **Session sécurisée** : Protection CSRF activée
- **Validation** : Données validées côté serveur
- **Logs** : Historique des connexions et actions

## 📊 Tableau de bord

### Statistiques en temps réel
- **Nombre de clients** : Total des clients actifs
- **Nombre de devis** : Tous les devis créés
- **Nombre de factures** : Toutes les factures émises
- **Nombre de commandes** : Toutes les commandes créées

### Actions rapides
- **Nouveau client** : Création rapide d'un client
- **Nouveau devis** : Création rapide d'un devis
- **Nouvelle facture** : Création rapide d'une facture
- **Nouvelle commande** : Création rapide d'une commande

### Activité récente
- **Dernières actions** : Historique des opérations récentes
- **Statistiques** : Graphiques de performance
- **Alertes** : Notifications importantes

## 🎨 Interface utilisateur

### Design moderne
- **Couleur principale** : #ff6000 (Orange DEVDRECO)
- **Responsive** : Compatible mobile et tablette
- **Animations** : Transitions fluides
- **Icônes** : Font Awesome pour une meilleure UX

### Navigation intuitive
- **Menu latéral** : Accès rapide aux modules
- **Breadcrumbs** : Navigation hiérarchique
- **Recherche** : Recherche globale
- **Filtres** : Filtrage avancé des données

## 🔧 Fonctionnalités avancées

### Calculs automatiques
- **Devis** : HT, TVA, TTC calculés automatiquement
- **Factures** : Montants restants mis à jour
- **Commandes** : Totaux mis à jour en temps réel

### Workflow automatisé
- **Devis → Facture** : Génération automatique
- **Facture → Commande** : Liaison automatique
- **Statuts** : Transitions automatiques selon les actions

### Recherche et filtrage
- **Recherche globale** : Par nom, numéro, description
- **Filtres avancés** : Par statut, date, client
- **Tri** : Par colonnes personnalisables
- **Pagination** : Navigation dans les listes

## 📱 Compatibilité

### Navigateurs supportés
- ✅ **Chrome** : Version 90+
- ✅ **Firefox** : Version 88+
- ✅ **Safari** : Version 14+
- ✅ **Edge** : Version 90+

### Appareils
- ✅ **Desktop** : Écrans 1024px+
- ✅ **Tablette** : Écrans 768px-1023px
- ✅ **Mobile** : Écrans <768px

## 🆘 Support et aide

### En cas de problème
1. **Vérifiez votre connexion** : Assurez-vous d'être connecté
2. **Actualisez la page** : F5 ou Ctrl+R
3. **Videz le cache** : Ctrl+Shift+R
4. **Contactez l'administrateur** : Pour les problèmes persistants

### Contact technique
- **Email** : michevox.contact@gmail.com
- **Développeur** : Michel Mahomy
- **Support** : Disponible 24/7

## 📈 Bonnes pratiques

### Gestion des clients
- ✅ **Informations complètes** : Remplissez tous les champs
- ✅ **Validation** : Vérifiez les numéros SIRET et TVA
- ✅ **Historique** : Consultez régulièrement le tableau de bord client

### Gestion des devis
- ✅ **Numérotation** : Utilisez une numérotation cohérente
- ✅ **Validité** : Définissez des dates de validité réalistes
- ✅ **Lignes détaillées** : Décrivez précisément les prestations

### Gestion des factures
- ✅ **Échéances** : Définissez des échéances claires
- ✅ **Suivi** : Surveillez les paiements en retard
- ✅ **Relances** : Effectuez des relances régulières

### Gestion des commandes
- ✅ **Adresses** : Vérifiez les adresses de livraison
- ✅ **Suivi** : Suivez régulièrement l'état des commandes
- ✅ **Communication** : Maintenez le contact avec les fournisseurs

---

**DEVDRECO SOFT** - Solution complète de gestion pour entreprises d'architecture et BTP

*Développé avec ❤️ par Michel Mahomy* 