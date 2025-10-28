from django.urls import path
from . import views

app_name = 'commandes'

urlpatterns = [
    # Vues principales
    path('', views.BonCommandeListView.as_view(), name='commande_list'),
    path('nouveau/', views.BonCommandeCreateView.as_view(), name='commande_create'),
    path('<int:pk>/', views.BonCommandeDetailView.as_view(), name='commande_detail'),
    path('<int:pk>/modifier/', views.BonCommandeUpdateView.as_view(), name='commande_update'),
    path('<int:pk>/supprimer/', views.BonCommandeDeleteView.as_view(), name='commande_delete'),
    
    # Actions sur les commandes
    path('<int:pk>/confirmer/', views.commande_confirmer, name='commande_confirmer'),
    path('<int:pk>/envoyer/', views.commande_envoyer, name='commande_envoyer'),
    path('<int:pk>/en-cours/', views.commande_en_cours, name='commande_en_cours'),
    path('<int:pk>/livrer/', views.commande_livrer, name='commande_livrer'),
    path('<int:pk>/annuler/', views.commande_annuler, name='commande_annuler'),
    
    # Utilitaires
    path('generer-numero/', views.generer_numero_commande, name='generer_numero_commande'),
    path('<int:pk>/ajouter-ligne/', views.ajouter_ligne_commande, name='ajouter_ligne_commande'),
    path('<int:pk>/imprimer/', views.imprimer_commande, name='commande_print'),
] 