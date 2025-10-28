from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    # Liste des clients
    path('', views.client_list, name='client_list'),
    
    # Détails d'un client
    path('<int:pk>/', views.client_detail, name='client_detail'),
    
    # Création d'un client (AJAX)
    path('create/', views.client_create, name='client_create'),
    
    # Modification d'un client (AJAX)
    path('<int:pk>/update/', views.client_update, name='client_update'),
    
    # Suppression d'un client (AJAX)
    path('<int:pk>/delete/', views.client_delete, name='client_delete'),
    
    # Activation/Désactivation d'un client (AJAX)
    path('<int:pk>/toggle-status/', views.client_toggle_status, name='client_toggle_status'),
    
    # Export des clients
    path('export/', views.client_export, name='client_export'),
    
    # Statistiques des clients (AJAX)
    path('statistics/', views.client_statistics, name='client_statistics'),
    
    # Aperçu de la liste des clients
    path('liste-print/', views.client_liste_print, name='client_liste_print'),
]
