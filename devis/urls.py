from django.urls import path
from . import views

app_name = 'devis'

urlpatterns = [
    # Vues de base
    path('', views.DevisListView.as_view(), name='devis_list'),
    path('nouveau/', views.DevisCreateView.as_view(), name='devis_create'),
    path('<int:pk>/', views.DevisDetailView.as_view(), name='devis_detail'),
    path('<int:pk>/modifier/', views.DevisUpdateView.as_view(), name='devis_update'),
    path('<int:pk>/supprimer/', views.DevisDeleteView.as_view(), name='devis_delete'),
    path('<int:pk>/supprimer-ajax/', views.devis_delete_ajax, name='devis_delete_ajax'),
    
    # Actions spéciales
    path('<int:pk>/envoyer/', views.devis_envoyer, name='devis_envoyer'),
    path('<int:pk>/accepter/', views.devis_accepter, name='devis_accepter'),
    path('<int:pk>/refuser/', views.devis_refuser, name='devis_refuser'),
    path('<int:pk>/dupliquer/', views.devis_dupliquer, name='devis_dupliquer'),
    
    # Impression et PDF
    path('<int:pk>/imprimer/', views.devis_imprimer, name='devis_imprimer'),
    path('<int:pk>/telecharger/', views.devis_telecharger, name='devis_telecharger'),
    path('<int:pk>/apercu/', views.devis_apercu_ecran, name='devis_apercu_ecran'),
    
    # Tableau de bord
    path('tableau-de-bord/', views.devis_dashboard, name='devis_dashboard'),
] 