# 🎛️ Système de Paramètres - DEVDRECO SOFT

## 📋 Vue d'ensemble

Le système de paramètres permet aux administrateurs de configurer l'application et de gérer les utilisateurs. Il comprend trois modules principaux :

1. **Paramètres généraux** - Configuration de base de l'application
2. **Informations de la société** - Données de l'entreprise
3. **Gestion des utilisateurs** - Création et gestion des comptes

## 🔐 Accès et permissions

- **Seuls les administrateurs** peuvent accéder aux paramètres
- **Utilisateurs standard** n'ont pas accès à cette section
- L'accès se fait via le menu **Paramètres** dans la sidebar

## 🎯 Fonctionnalités principales

### 1. Paramètres généraux (`/parametres/generaux/`)

#### Paramètres monétaires
- **Symbole monétaire** : FCFA, EUR, USD, GBP, JPY, CHF, CAD, AUD
- Ce symbole sera utilisé dans tous les documents (devis, factures)

#### Paramètres de l'application
- **Nom de l'application** : Personnalisation du titre
- **Éléments par page** : Pagination des listes
- **Format de date** : Affichage des dates (ex: d/m/Y, Y-m-d)

#### Notifications
- **Notifications par email** : Activer/désactiver
- **Notifications par SMS** : Activer/désactiver

### 2. Informations de la société (`/parametres/societe/`)

#### Informations de base
- Nom ou raison sociale
- Téléphones (fixe et portable)
- Adresse email
- Adresse complète, ville, code postal, pays

#### Web et documents
- URL du site web
- **Logo de la société** (jpg, jpeg, png, gif)
- **En-tête pour documents** (devis, factures)
- **Pied de page pour documents**

#### Informations légales
- Numéro de registre de commerce
- Numéro de contribuable

### 3. Gestion des utilisateurs (`/parametres/utilisateurs/`)

#### Création d'utilisateurs
- Nom d'utilisateur unique
- Prénom et nom
- Adresse email
- Mot de passe sécurisé
- Rôle (Administrateur ou Standard)

#### Profil utilisateur
- **Rôle** : Détermine les permissions
- **Téléphone** : Contact
- **Poste** : Fonction dans l'entreprise
- **Département** : Service
- **Date d'embauche**
- **Statut actif/inactif**

#### Actions disponibles
- ✅ **Modifier** le profil
- 🔑 **Changer le mot de passe**
- ⚡ **Activer/Désactiver** le compte
- 🗑️ **Supprimer** l'utilisateur

## 🚀 Utilisation

### Accéder aux paramètres
1. Connectez-vous en tant qu'administrateur
2. Cliquez sur **Paramètres** dans le menu de gauche
3. Ou cliquez sur l'icône ⚙️ dans le header

### Configurer l'application
1. **Paramètres généraux** : Configurez la monnaie et l'affichage
2. **Informations société** : Renseignez les données de votre entreprise
3. **Gestion utilisateurs** : Créez et gérez les comptes

### Créer un nouvel utilisateur
1. Allez dans **Gestion des utilisateurs**
2. Cliquez sur **Nouvel utilisateur**
3. Remplissez le formulaire
4. Choisissez le rôle approprié
5. Enregistrez

## 🔒 Sécurité

- **Authentification requise** pour tous les accès
- **Vérification des rôles** avant autorisation
- **Validation des données** sur tous les formulaires
- **Protection CSRF** sur tous les formulaires

## 📱 Interface utilisateur

### Design responsive
- **Desktop** : Layout en colonnes avec sidebar
- **Tablet** : Adaptation automatique
- **Mobile** : Interface optimisée

### Navigation intuitive
- **Onglets** pour naviguer entre les sections
- **Breadcrumbs** pour le contexte
- **Actions rapides** pour les tâches fréquentes

### Feedback utilisateur
- **Messages de succès** après chaque action
- **Validation en temps réel** des formulaires
- **Aperçu** des informations avant sauvegarde

## 🛠️ Configuration technique

### Modèles Django
- `ParametresGeneraux` : Paramètres de base
- `InformationsSociete` : Données de l'entreprise
- `UtilisateurCustom` : Profils utilisateurs étendus

### Vues sécurisées
- **Décorateurs** de sécurité sur toutes les vues
- **Vérification des permissions** avant accès
- **Gestion des erreurs** avec messages appropriés

### Formulaires robustes
- **Validation** côté serveur et client
- **Gestion des erreurs** avec affichage contextuel
- **Sauvegarde sécurisée** des données

## 📊 Statistiques et monitoring

### Tableau de bord
- **Nombre total d'utilisateurs**
- **Utilisateurs actifs/inactifs**
- **Répartition par rôle**
- **Derniers utilisateurs créés**

### État de la configuration
- **Paramètres configurés** ✓
- **Informations société renseignées** ✓
- **Statut de la base de données**

## 🔧 Maintenance

### Sauvegarde
- **Base de données** : Sauvegardez régulièrement
- **Fichiers médias** : Sauvegardez le dossier `media/`
- **Logs** : Surveillez les erreurs

### Mise à jour
- **Django** : Maintenez à jour
- **Dépendances** : Vérifiez régulièrement
- **Sécurité** : Appliquez les patches

## 🆘 Support et dépannage

### Problèmes courants
1. **Accès refusé** : Vérifiez que vous êtes administrateur
2. **Formulaire invalide** : Vérifiez tous les champs requis
3. **Erreur de sauvegarde** : Vérifiez les permissions de la base

### Logs et debugging
- **Console Django** : Messages d'erreur détaillés
- **Base de données** : Vérifiez l'intégrité des données
- **Permissions** : Vérifiez les droits utilisateur

## 📈 Évolutions futures

### Fonctionnalités prévues
- **Audit trail** des modifications
- **Sauvegarde automatique** des paramètres
- **API REST** pour l'intégration
- **Notifications push** en temps réel

### Personnalisation avancée
- **Thèmes visuels** personnalisables
- **Workflows** configurables
- **Intégrations** avec d'autres systèmes

---

## 🎉 Conclusion

Le système de paramètres offre une interface complète et sécurisée pour configurer DEVDRECO SOFT. Il respecte les bonnes pratiques de sécurité et d'ergonomie, tout en offrant une flexibilité maximale pour l'adaptation aux besoins de votre entreprise.

Pour toute question ou suggestion d'amélioration, n'hésitez pas à contacter l'équipe de développement.
