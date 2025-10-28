from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta, date
import json

# Import des modèles
from clients.models import Client
from devis.models import Devis
# from factures.models import Facture  # Temporairement commenté
from commandes.models import BonCommande
from articles.models import Article, Categorie
from fournisseurs.models import Fournisseur

# Create your views here.

def home(request):
    """Page d'accueil principale"""
    return render(request, 'core/home.html')

def login_view(request):
    """Vue pour la connexion"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} !')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Identifiants incorrects.')
    
    return render(request, 'core/login.html')

def logout_view(request):
    """Vue pour la déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('core:home')

@login_required
def dashboard(request):
    """Tableau de bord principal enrichi avec statistiques et graphiques"""
    
    # Statistiques générales
    clients_count = Client.objects.count()
    devis_count = Devis.objects.count()
    # factures_count = Facture.objects.count()  # Temporairement commenté
    factures_count = 0
    commandes_count = BonCommande.objects.count()
    articles_count = Article.objects.count()
    fournisseurs_count = Fournisseur.objects.count()
    
    # Statistiques du mois en cours
    now = timezone.now()
    current_month = now.month
    current_year = now.year
    
    devis_ce_mois = Devis.objects.filter(
        date_creation__month=current_month,
        date_creation__year=current_year
    ).count()
    
    # factures_ce_mois = Facture.objects.filter(
    #     date_emission__month=current_month,
    #     date_emission__year=current_year
    # ).count()  # Temporairement commenté
    factures_ce_mois = 0
    
    commandes_ce_mois = BonCommande.objects.filter(
        date_creation__month=current_month,
        date_creation__year=current_year
    ).count()
    
    # Chiffre d'affaires
    ca_total = Devis.objects.aggregate(total=Sum('montant_ttc'))['total'] or 0
    ca_ce_mois = Devis.objects.filter(
        date_creation__month=current_month,
        date_creation__year=current_year
    ).aggregate(total=Sum('montant_ttc'))['total'] or 0
    
    # Statistiques des devis par statut
    devis_par_statut = Devis.objects.values('statut').annotate(count=Count('id')).order_by('statut')
    
    # Statistiques des factures par statut de paiement
    # factures_par_statut = Facture.objects.values('statut_paiement').annotate(count=Count('id')).order_by('statut_paiement')  # Temporairement commenté
    factures_par_statut = []
    
    # Évolution des ventes sur les 6 derniers mois
    evolution_ventes = []
    for i in range(6):
        mois_date = now - timedelta(days=30*i)
        mois_devis = Devis.objects.filter(
            date_creation__month=mois_date.month,
            date_creation__year=mois_date.year
        ).aggregate(total=Sum('montant_ttc'))['total'] or 0
        evolution_ventes.append({
            'mois': mois_date.strftime('%b %Y'),
            'montant': float(mois_devis)
        })
    evolution_ventes.reverse()
    
    # Top 5 des clients par chiffre d'affaires
    top_clients = Devis.objects.values(
        'client__nom_complet'
    ).annotate(
        total_ca=Sum('montant_ttc')
    ).order_by('-total_ca')[:5]
    
    # Articles les plus vendus (simulation - à adapter selon votre logique)
    articles_populaires = Article.objects.filter(actif=True)[:5]
    
    # Activité récente (derniers devis, factures, etc.)
    derniers_devis = Devis.objects.select_related('client').order_by('-date_creation')[:5]
    # dernieres_factures = Facture.objects.select_related('client').order_by('-date_emission')[:5]  # Temporairement commenté
    dernieres_factures = []
    derniers_clients = Client.objects.order_by('-date_creation')[:3]
    
    # Taux de conversion devis -> factures
    devis_acceptes = Devis.objects.filter(statut='accepte').count()
    taux_conversion = (factures_count / devis_count * 100) if devis_count > 0 else 0
    
    # Montant moyen par devis
    montant_moyen_devis = (ca_total / devis_count) if devis_count > 0 else 0
    
    # Factures en retard
    # factures_en_retard = Facture.objects.filter(
    #     statut_paiement__in=['en_attente', 'partiellement_paye'],
    #     date_echeance__lt=now.date()
    # ).count()  # Temporairement commenté
    factures_en_retard = 0
    
    context = {
        'user': request.user,
        
        # Statistiques générales
        'clients_count': clients_count,
        'devis_count': devis_count,
        'factures_count': factures_count,
        'commandes_count': commandes_count,
        'articles_count': articles_count,
        'fournisseurs_count': fournisseurs_count,
        
        # Statistiques du mois
        'devis_ce_mois': devis_ce_mois,
        'factures_ce_mois': factures_ce_mois,
        'commandes_ce_mois': commandes_ce_mois,
        
        # Chiffre d'affaires
        'ca_total': ca_total,
        'ca_ce_mois': ca_ce_mois,
        
        # Données pour graphiques
        'devis_par_statut': list(devis_par_statut),
        'factures_par_statut': list(factures_par_statut),
        'evolution_ventes': evolution_ventes,
        'top_clients': list(top_clients),
        'articles_populaires': articles_populaires,
        
        # Activité récente
        'derniers_devis': derniers_devis,
        'dernieres_factures': dernieres_factures,
        'derniers_clients': derniers_clients,
        
        # Métriques avancées
        'taux_conversion': round(taux_conversion, 1),
        'montant_moyen_devis': round(montant_moyen_devis, 2),
        'factures_en_retard': factures_en_retard,
    }
    
    return render(request, 'core/dashboard.html', context)

@csrf_exempt
def ajax_login(request):
    """Connexion AJAX pour la popup"""
    print(f"DEBUG: ajax_login appelée avec méthode {request.method}")
    
    if request.method == 'POST':
        try:
            print(f"DEBUG: Body reçu: {request.body}")
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            print(f"DEBUG: Username: {username}, Password: {'*' * len(password) if password else 'None'}")
            
            user = authenticate(request, username=username, password=password)
            print(f"DEBUG: User authentifié: {user}")
            
            if user is not None:
                login(request, user)
                print(f"DEBUG: Utilisateur connecté: {user.username}")
                return JsonResponse({
                    'success': True,
                    'message': f'Bienvenue {user.username} !',
                    'redirect_url': '/dashboard/'
                })
            else:
                print("DEBUG: Authentification échouée")
                return JsonResponse({
                    'success': False,
                    'message': 'Identifiants incorrects.'
                })
        except json.JSONDecodeError as e:
            print(f"DEBUG: Erreur JSON: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Données invalides.'
            })
        except Exception as e:
            print(f"DEBUG: Erreur générale: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Erreur serveur: {str(e)}'
            })
    
    print("DEBUG: Méthode non autorisée")
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée.'
    })
