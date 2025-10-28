from django.urls import path
from . import views

app_name = 'utilisateurs'

urlpatterns = [
    # Gestion des utilisateurs
    path('', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('detail/<int:user_id>/', views.detail_utilisateur, name='detail_utilisateur'),
    
    # Profil utilisateur
    path('profil/', views.mon_profil, name='mon_profil'),
]
