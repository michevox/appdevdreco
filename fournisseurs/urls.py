from django.urls import path
from . import views

app_name = 'fournisseurs'

urlpatterns = [
    # URLs pour les fournisseurs
    path('', views.fournisseur_list, name='fournisseur_list'),
    path('nouveau/', views.fournisseur_create, name='fournisseur_create'),
    path('popup/nouveau/', views.fournisseur_create_popup, name='fournisseur_create_popup'),
    path('<int:pk>/', views.fournisseur_detail, name='fournisseur_detail'),
    path('<int:pk>/modifier/', views.fournisseur_update, name='fournisseur_update'),
    path('<int:pk>/supprimer/', views.fournisseur_delete, name='fournisseur_delete'),
    path('<int:pk>/toggle-status/', views.fournisseur_toggle_status, name='fournisseur_toggle_status'),
    
    # URLs pour les produits fournisseurs
    path('produits/', views.produit_fournisseur_list, name='produit_fournisseur_list'),
    path('produits/nouveau/', views.produit_fournisseur_create, name='produit_fournisseur_create'),
    path('produits/<int:pk>/modifier/', views.produit_fournisseur_update, name='produit_fournisseur_update'),
    path('produits/<int:pk>/supprimer/', views.produit_fournisseur_delete, name='produit_fournisseur_delete'),
    
    # APIs
    path('api/', views.fournisseur_api, name='fournisseur_api'),
    
    # Aperçu de la liste des fournisseurs
    path('liste-print/', views.fournisseur_liste_print, name='fournisseur_liste_print'),
]



