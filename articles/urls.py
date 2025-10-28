from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # URLs pour les catégories
    path('categories/', views.categorie_list, name='categorie_list'),
    path('categories/nouvelle/', views.categorie_create_popup, name='categorie_create_popup'),
    path('categories/<int:pk>/modifier/', views.categorie_update_popup, name='categorie_update_popup'),
    path('categories/<int:pk>/supprimer/', views.categorie_delete_popup, name='categorie_delete_popup'),
    
    # URLs pour les articles
    path('', views.article_list, name='article_list'),
    path('nouveau/', views.article_create_popup, name='article_create_popup'),
    path('<int:pk>/modifier/', views.article_update_popup, name='article_update_popup'),
    path('<int:pk>/supprimer/', views.article_delete_popup, name='article_delete_popup'),
    path('api/designations/', views.article_designations_api, name='article_designations_api'),
    
    # URLs pour l'import/export
    path('categories/export/', views.export_categories_excel, name='export_categories_excel'),
    path('categories/import/', views.import_categories_excel, name='import_categories_excel'),
    path('categories/modele/', views.download_template_categories, name='download_template_categories'),
    path('export/', views.export_articles_excel, name='export_articles_excel'),
    path('import/', views.import_articles_excel, name='import_articles_excel'),
    path('modele/', views.download_template_articles, name='download_template_articles'),
    
    # Aperçu de la liste des articles
    path('liste-print/', views.article_liste_print, name='article_liste_print'),
]

