from django.urls import path
from . import views

app_name = 'parametres'

urlpatterns = [
    # Tableau de bord des paramètres
    path('', views.tableau_bord_parametres, name='tableau_bord'),
    
    # Paramètres généraux
    path('generaux/', views.parametres_generaux, name='parametres_generaux'),
    
    # Informations de la société
    path('societe/', views.informations_societe, name='informations_societe'),
    
    # Gestion des utilisateurs
    path('utilisateurs/', views.UtilisateurListView.as_view(), name='utilisateur_list'),
    path('utilisateurs/nouveau/', views.UtilisateurCreateView.as_view(), name='utilisateur_create'),
    path('utilisateurs/<int:pk>/modifier/', views.UtilisateurUpdateView.as_view(), name='utilisateur_update'),
    path('utilisateurs/<int:pk>/supprimer/', views.UtilisateurDeleteView.as_view(), name='utilisateur_delete'),
    path('utilisateurs/<int:pk>/activer-desactiver/', views.utilisateur_activer_desactiver, name='utilisateur_activer_desactiver'),
    path('utilisateurs/<int:pk>/changer-mot-de-passe/', views.utilisateur_changer_mot_de_passe, name='utilisateur_changer_mot_de_passe'),
    
    # Gestion des permissions
    path('permissions/', views.gestion_permissions, name='gestion_permissions'),
    path('permissions/utilisateur/<int:user_id>/modifier/', views.modifier_permissions_utilisateur, name='modifier_permissions_utilisateur'),
    path('permissions/utilisateur/<int:user_id>/role/', views.modifier_role_utilisateur, name='modifier_role_utilisateur'),
    path('permissions/utilisateur/<int:user_id>/activer-desactiver/', views.activer_desactiver_utilisateur, name='activer_desactiver_utilisateur'),
    path('permissions/ajouter/', views.ajouter_permission_utilisateur, name='ajouter_permission_utilisateur'),
    path('permissions/supprimer/', views.supprimer_permission_utilisateur, name='supprimer_permission_utilisateur'),
]
