"""
URL configuration for devdreco_soft project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Application principale
    path('', include('core.urls')),
    
    # Applications DEVDRECO SOFT
    path('clients/', include('clients.urls')),
    path('devis/', include('devis.urls')),
    path('factures/', include('factures.urls')),
    path('commandes/', include('commandes.urls')),
    path('parametres/', include('parametres.urls')),
    path('articles/', include('articles.urls')),
    path('rapports/', include('rapports.urls')),
    path('fournisseurs/', include('fournisseurs.urls')),
    path('utilisateurs/', include('utilisateurs.urls')),
    path('aide/', include('aide.urls')),
]

# URLs pour les fichiers statiques et médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
