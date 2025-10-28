from django.urls import path
from . import views

app_name = 'factures'

urlpatterns = [
    # Liste des factures
    path('', views.FactureListView.as_view(), name='facture_list'),
    
    # Détail d'une facture
    path('<int:pk>/', views.FactureDetailView.as_view(), name='facture_detail'),
    
    # Création d'une facture
    path('ajouter/', views.FactureCreateView.as_view(), name='facture_create'),
    
    # Modification d'une facture
    path('<int:pk>/modifier/', views.FactureUpdateView.as_view(), name='facture_update'),
    
    # Suppression d'une facture
    path('<int:pk>/supprimer/', views.FactureDeleteView.as_view(), name='facture_delete'),
    
    # Suppression AJAX d'une facture
    path('<int:pk>/supprimer-ajax/', views.facture_delete_ajax, name='facture_delete_ajax'),
    
    # Changement de statut d'une facture
    path('<int:pk>/changer-statut/', views.facture_toggle_status, name='facture_toggle_status'),
    
    # Aperçu d'une facture
    path('<int:pk>/apercu/', views.facture_apercu_ecran, name='facture_apercu_ecran'),
    
    # Impression et téléchargement PDF
    path('<int:pk>/imprimer/', views.facture_imprimer, name='facture_imprimer'),
    path('<int:pk>/telecharger/', views.facture_telecharger, name='facture_telecharger'),
]
