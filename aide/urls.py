from django.urls import path
from . import views

app_name = 'aide'

urlpatterns = [
    # Page d'accueil de l'aide
    path('', views.AideIndexView.as_view(), name='index'),
    
    # Sections d'aide
    path('utilisation/', views.AideUtilisationView.as_view(), name='utilisation'),
    path('faq/', views.AideFaqView.as_view(), name='faq'),
    path('contact/', views.AideContactView.as_view(), name='contact'),
    path('a-propos/', views.AideAProposView.as_view(), name='a_propos'),
    
    # Recherche
    path('recherche/', views.aide_recherche, name='recherche'),
]
