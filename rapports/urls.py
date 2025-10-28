from django.urls import path
from . import views

app_name = 'rapports'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_rapports, name='dashboard'),
    
    # Rapports de ventes
    path('ventes/', views.rapports_ventes, name='rapports_ventes'),
    path('ventes/creer/', views.creer_rapport_ventes, name='creer_rapport_ventes'),
    
    # Rapports clients
    path('clients/', views.rapports_clients, name='rapports_clients'),
    
    # Rapports articles
    path('articles/', views.rapports_articles, name='rapports_articles'),
    
    # Rapports financiers
    path('financiers/', views.rapports_financiers, name='rapports_financiers'),
    
    # Téléchargement
    path('telecharger/<str:rapport_type>/<int:rapport_id>/', views.telecharger_rapport, name='telecharger_rapport'),
]
