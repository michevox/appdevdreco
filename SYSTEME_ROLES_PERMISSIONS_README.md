# 🔐 Système de Rôles et Permissions - DEVDRECO SOFT

## 📋 Vue d'ensemble

Le système de rôles et permissions de DEVDRECO SOFT offre un contrôle d'accès granulaire et professionnel pour votre application. Il permet de définir précisément quelles fonctionnalités chaque utilisateur peut utiliser selon son rôle et ses permissions personnalisées.

## 🏗️ Architecture du système

### Modèles principaux

1. **Role** - Définit les rôles utilisateur (Administrateur, Manager, Utilisateur Standard, Lecture Seule)
2. **Permission** - Définit les permissions spécifiques par module et action
3. **RolePermission** - Associe les permissions aux rôles
4. **UtilisateurProfile** - Extension du modèle User Django avec système de rôles
5. **UtilisateurPermission** - Permissions personnalisées par utilisateur
6. **ConnexionUtilisateur** - Historique des connexions

### Rôles par défaut

| Rôle | Description | Permissions |
|------|-------------|-------------|
| **Administrateur** | Accès complet à toutes les fonctionnalités | Toutes les permissions |
| **Manager** | Accès à la gestion et aux rapports | Toutes sauf gestion des utilisateurs |
| **Utilisateur Standard** | Accès de base aux fonctionnalités principales | Lecture et création pour clients, devis, articles |
| **Lecture Seule** | Accès en lecture seule | Lecture uniquement pour tous les modules |

## 🚀 Installation et Configuration

### 1. Application créée

L'application `utilisateurs` a été ajoutée à votre projet avec :
- Modèles de rôles et permissions
- Middlewares de vérification
- Décorateurs de protection
- Templates d'administration
- Utilitaires de gestion

### 2. Middlewares configurés

Les middlewares suivants ont été ajoutés dans `settings.py` :

```python
MIDDLEWARE = [
    # ... autres middlewares
    'utilisateurs.middleware.PermissionMiddleware',
    'utilisateurs.middleware.ConnexionMiddleware', 
    'utilisateurs.middleware.NavigationMiddleware',
]
```

### 3. URLs configurées

```python
# Dans devdreco_soft/urls.py
path('utilisateurs/', include('utilisateurs.urls')),
```

## 🎯 Utilisation du système

### 1. Vérification des permissions dans les vues

#### Avec des décorateurs

```python
from utilisateurs.decorators import permission_required, admin_required

@permission_required('devis.view')
def liste_devis(request):
    # Code de la vue
    pass

@admin_required()
def gestion_utilisateurs(request):
    # Code réservé aux administrateurs
    pass
```

#### Avec des vues basées sur les classes

```python
from utilisateurs.decorators import class_permission_required

@class_permission_required('clients.view')
class ClientListView(ListView):
    # Code de la vue
    pass
```

### 2. Filtrage des données selon les permissions

```python
from utilisateurs.utils import filter_queryset_by_permissions

def get_queryset(self):
    queryset = Client.objects.all()
    # Filtrer selon les permissions utilisateur
    queryset = filter_queryset_by_permissions(
        self.request.user, 
        queryset, 
        'clients'
    )
    return queryset
```

### 3. Vérification des permissions dans les templates

```html
{% if user.user_profile.a_permission 'devis.add' %}
    <a href="{% url 'devis:ajouter' %}" class="btn btn-primary">
        Ajouter un devis
    </a>
{% endif %}
```

### 4. Navigation conditionnelle

La navigation est automatiquement filtrée selon les permissions de l'utilisateur grâce au `NavigationMiddleware`.

## 🛠️ Gestion des utilisateurs et permissions

### 1. Interface d'administration Django

Accédez à `/admin/` pour gérer :
- Les rôles et leurs permissions
- Les utilisateurs et leurs profils
- L'historique des connexions

### 2. Interface personnalisée

Accédez à `/utilisateurs/` pour :
- Lister tous les utilisateurs
- Voir les détails d'un utilisateur
- Gérer les permissions personnalisées

### 3. Mon profil

Accédez à `/utilisateurs/profil/` pour :
- Voir vos permissions
- Consulter l'historique de vos connexions

## 📊 Permissions disponibles

### Modules et actions

| Module | Actions disponibles |
|--------|-------------------|
| **Clients** | Voir, Ajouter, Modifier, Supprimer, Exporter, Imprimer |
| **Devis** | Voir, Ajouter, Modifier, Supprimer, Exporter, Imprimer |
| **Factures** | Voir, Ajouter, Modifier, Supprimer, Exporter, Imprimer |
| **Commandes** | Voir, Ajouter, Modifier, Supprimer, Exporter, Imprimer |
| **Articles** | Voir, Ajouter, Modifier, Supprimer, Exporter, Importer |
| **Fournisseurs** | Voir, Ajouter, Modifier, Supprimer, Exporter, Imprimer |
| **Rapports** | Voir, Exporter, Imprimer |
| **Paramètres** | Voir, Modifier |
| **Utilisateurs** | Voir, Ajouter, Modifier, Supprimer |

## 🔧 Fonctions utilitaires

### Vérification des permissions

```python
from utilisateurs.utils import user_has_permission, is_admin, is_manager

# Vérifier une permission spécifique
if user_has_permission(user, 'devis.add'):
    # L'utilisateur peut ajouter des devis
    pass

# Vérifier le rôle
if is_admin(user):
    # L'utilisateur est administrateur
    pass
```

### Création d'utilisateurs avec rôles

```python
from utilisateurs.utils import create_user_with_role

user = create_user_with_role(
    username='nouveau_user',
    email='user@example.com',
    password='motdepasse',
    role_name='Utilisateur Standard',
    telephone='+224 123456789',
    poste='Commercial',
    departement='Ventes'
)
```

## 🎨 Personnalisation des permissions

### 1. Permissions personnalisées par utilisateur

Vous pouvez accorder ou refuser des permissions spécifiques à un utilisateur, même si son rôle ne les inclut pas :

```python
from utilisateurs.utils import update_user_permissions

# Accorder une permission spécifique
update_user_permissions(user, {
    'rapports.view': True,
    'devis.delete': False
})
```

### 2. Création de nouveaux rôles

```python
from utilisateurs.models import Role, RolePermission

# Créer un nouveau rôle
role = Role.objects.create(
    nom='Commercial Senior',
    description='Commercial avec accès aux rapports',
    type_role='standard'
)

# Assigner des permissions au rôle
permissions = Permission.objects.filter(
    module__in=['clients', 'devis', 'rapports'],
    action__in=['view', 'add', 'change']
)

for permission in permissions:
    RolePermission.objects.create(
        role=role,
        permission=permission,
        accordee=True
    )
```

## 🔍 Surveillance et audit

### Historique des connexions

Le système enregistre automatiquement :
- Date et heure de connexion
- Adresse IP
- User Agent
- Statut de la connexion (réussie/échouée)

### Traçabilité des actions

Toutes les actions sensibles sont tracées dans les logs Django.

## 🚨 Sécurité

### Bonnes pratiques

1. **Principe du moindre privilège** : Accordez seulement les permissions nécessaires
2. **Révision régulière** : Vérifiez périodiquement les permissions des utilisateurs
3. **Séparation des rôles** : Évitez qu'un utilisateur cumule trop de rôles
4. **Audit des connexions** : Surveillez les connexions suspectes

### Protection contre les attaques

- Vérification des permissions côté serveur
- Protection CSRF sur tous les formulaires
- Validation des données d'entrée
- Logs de sécurité

## 🧪 Tests

### Script de test

Un script de test complet est disponible : `test_permissions.py`

```bash
python test_permissions.py
```

Ce script vérifie :
- Création des rôles et permissions
- Fonctionnement des permissions
- Création d'utilisateurs avec rôles
- Fonctions utilitaires

## 📝 Exemples d'utilisation

### Exemple 1 : Vue protégée par permission

```python
@permission_required('factures.view')
def liste_factures(request):
    factures = Facture.objects.all()
    return render(request, 'factures/liste.html', {
        'factures': factures
    })
```

### Exemple 2 : Bouton conditionnel dans un template

```html
{% if user.user_profile.a_permission 'devis.add' %}
    <a href="{% url 'devis:ajouter' %}" class="btn btn-success">
        <i class="fas fa-plus"></i> Nouveau devis
    </a>
{% endif %}
```

### Exemple 3 : Filtrage des données

```python
def get_queryset(self):
    queryset = super().get_queryset()
    
    # Si l'utilisateur n'est pas admin, filtrer ses propres données
    if not is_admin(self.request.user):
        queryset = queryset.filter(
            createur=self.request.user
        )
    
    return queryset
```

## 🆘 Dépannage

### Problèmes courants

1. **Utilisateur sans permissions** : Vérifiez que l'utilisateur a un rôle assigné
2. **Permissions non appliquées** : Vérifiez que les middlewares sont activés
3. **Erreur 403** : L'utilisateur n'a pas les permissions nécessaires

### Logs de débogage

Activez les logs Django pour voir les vérifications de permissions :

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'utilisateurs': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 📞 Support

Pour toute question ou problème avec le système de rôles et permissions :

1. Consultez les logs Django
2. Vérifiez la configuration des middlewares
3. Testez avec le script `test_permissions.py`
4. Contactez l'équipe de développement

---

**🎉 Félicitations !** Votre système de rôles et permissions est maintenant opérationnel et prêt à sécuriser votre application DEVDRECO SOFT.
