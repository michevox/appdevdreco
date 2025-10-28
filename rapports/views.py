from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta, date
import json
import csv
import io
from decimal import Decimal

from .models import RapportVentes, RapportClients, RapportArticles, RapportFinancier, ConfigurationRapport
from clients.models import Client
from devis.models import Devis, LigneDevis
# from factures.models import Facture  # Temporairement commenté
from commandes.models import BonCommande
from articles.models import Article, Categorie
from parametres.models import InformationsSociete


@login_required
def dashboard_rapports(request):
    """Tableau de bord des rapports"""
    # Statistiques rapides
    stats = {
        'total_devis': Devis.objects.count(),
        'devis_ce_mois': Devis.objects.filter(
            date_creation__month=timezone.now().month,
            date_creation__year=timezone.now().year
        ).count(),
        # 'total_factures': Facture.objects.count(),  # Temporairement commenté
        'total_factures': 0,
        # 'factures_ce_mois': Facture.objects.filter(
        #     date_emission__month=timezone.now().month,
        #     date_emission__year=timezone.now().year
        # ).count(),  # Temporairement commenté
        'factures_ce_mois': 0,
        'total_clients': Client.objects.count(),
        'clients_actifs': Client.objects.filter(actif=True).count(),
        'total_articles': Article.objects.count(),
        'articles_actifs': Article.objects.filter(actif=True).count(),
    }
    
    # Chiffre d'affaires du mois
    ca_mois = Devis.objects.filter(
        date_creation__month=timezone.now().month,
        date_creation__year=timezone.now().year
    ).aggregate(total=Sum('montant_ttc'))['total'] or 0
    
    stats['ca_mois'] = ca_mois
    
    # Rapports récents
    rapports_ventes = RapportVentes.objects.filter(creer_par=request.user)[:5]
    rapports_clients = RapportClients.objects.filter(creer_par=request.user)[:5]
    rapports_articles = RapportArticles.objects.filter(creer_par=request.user)[:5]
    rapports_financiers = RapportFinancier.objects.filter(creer_par=request.user)[:5]
    
    context = {
        'stats': stats,
        'rapports_ventes': rapports_ventes,
        'rapports_clients': rapports_clients,
        'rapports_articles': rapports_articles,
        'rapports_financiers': rapports_financiers,
    }
    
    return render(request, 'rapports/dashboard.html', context)


@login_required
def rapports_ventes(request):
    """Liste des rapports de ventes"""
    rapports = RapportVentes.objects.filter(creer_par=request.user)
    
    # Filtres
    type_rapport = request.GET.get('type', '')
    if type_rapport:
        rapports = rapports.filter(type_rapport=type_rapport)
    
    context = {
        'rapports': rapports,
        'type_rapport': type_rapport,
    }
    
    return render(request, 'rapports/rapports_ventes.html', context)


@login_required
def creer_rapport_ventes(request):
    """Créer un nouveau rapport de ventes"""
    if request.method == 'POST':
        # Logique de création du rapport
        nom = request.POST.get('nom')
        type_rapport = request.POST.get('type_rapport')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        format_sortie = request.POST.get('format_sortie')
        
        # Créer le rapport
        rapport = RapportVentes.objects.create(
            nom=nom,
            type_rapport=type_rapport,
            date_debut=date_debut,
            date_fin=date_fin,
            format_sortie=format_sortie,
            creer_par=request.user
        )
        
        messages.success(request, f"Rapport '{nom}' créé avec succès!")
        return redirect('rapports:rapports_ventes')
    
    return render(request, 'rapports/creer_rapport_ventes.html')


@login_required
def rapports_clients(request):
    """Liste des rapports clients"""
    rapports = RapportClients.objects.filter(creer_par=request.user)
    
    context = {
        'rapports': rapports,
    }
    
    return render(request, 'rapports/rapports_clients.html', context)


@login_required
def rapports_articles(request):
    """Liste des rapports articles"""
    rapports = RapportArticles.objects.filter(creer_par=request.user)
    
    context = {
        'rapports': rapports,
    }
    
    return render(request, 'rapports/rapports_articles.html', context)


@login_required
def rapports_financiers(request):
    """Liste des rapports financiers"""
    rapports = RapportFinancier.objects.filter(creer_par=request.user)
    
    context = {
        'rapports': rapports,
    }
    
    return render(request, 'rapports/rapports_financiers.html', context)


@login_required
def telecharger_rapport(request, rapport_type, rapport_id):
    """Télécharger un rapport généré"""
    if rapport_type == 'ventes':
        rapport = get_object_or_404(RapportVentes, id=rapport_id, creer_par=request.user)
    elif rapport_type == 'clients':
        rapport = get_object_or_404(RapportClients, id=rapport_id, creer_par=request.user)
    elif rapport_type == 'articles':
        rapport = get_object_or_404(RapportArticles, id=rapport_id, creer_par=request.user)
    elif rapport_type == 'financiers':
        rapport = get_object_or_404(RapportFinancier, id=rapport_id, creer_par=request.user)
    else:
        return HttpResponse("Type de rapport invalide", status=400)
    
    if not rapport.fichier_genere:
        messages.error(request, "Le fichier du rapport n'a pas été généré.")
        return redirect('rapports:dashboard')
    
    # Déterminer le type MIME
    if rapport.fichier_genere.name.endswith('.pdf'):
        content_type = 'application/pdf'
    elif rapport.fichier_genere.name.endswith('.xlsx'):
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif rapport.fichier_genere.name.endswith('.csv'):
        content_type = 'text/csv'
    else:
        content_type = 'application/octet-stream'
    
    response = HttpResponse(rapport.fichier_genere.read(), content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{rapport.fichier_genere.name}"'
    return response