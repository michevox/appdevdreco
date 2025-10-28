from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import Fournisseur, ProduitFournisseur
from .forms import FournisseurForm, ProduitFournisseurForm, FournisseurSearchForm
from articles.models import Article


@login_required
def fournisseur_list(request):
    """Liste des fournisseurs avec recherche et filtres"""
    form = FournisseurSearchForm(request.GET)
    
    # Base queryset
    fournisseurs = Fournisseur.objects.all()
    
    # Appliquer les filtres
    if form.is_valid():
        search = form.cleaned_data.get('search', '').strip()
        type_fournisseur = form.cleaned_data.get('type_fournisseur')
        actif = form.cleaned_data.get('actif')
        tri = form.cleaned_data.get('tri', 'nom_complet')
        
        # Recherche textuelle
        if search:
            fournisseurs = fournisseurs.filter(
                Q(nom_complet__icontains=search) |
                Q(email__icontains=search) |
                Q(telephone__icontains=search) |
                Q(contact_principal__icontains=search) |
                Q(ville__icontains=search)
            )
        
        # Filtre par type
        if type_fournisseur:
            fournisseurs = fournisseurs.filter(type_fournisseur=type_fournisseur)
        
        # Filtre par statut
        if actif == 'true':
            fournisseurs = fournisseurs.filter(actif=True)
        elif actif == 'false':
            fournisseurs = fournisseurs.filter(actif=False)
        
        # Tri
        if tri:
            fournisseurs = fournisseurs.order_by(tri)
        else:
            fournisseurs = fournisseurs.order_by('nom_complet')
    
    # Pagination
    paginator = Paginator(fournisseurs, 20)
    page_number = request.GET.get('page')
    fournisseurs_page = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total': Fournisseur.objects.count(),
        'actifs': Fournisseur.objects.filter(actif=True).count(),
        'inactifs': Fournisseur.objects.filter(actif=False).count(),
    }
    
    # Répartition par type
    types_stats = Fournisseur.objects.values('type_fournisseur').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'fournisseurs': fournisseurs_page,
        'form': form,
        'stats': stats,
        'types_stats': types_stats,
    }
    
    return render(request, 'fournisseurs/fournisseur_list.html', context)


@login_required
def fournisseur_liste_print(request):
    """Vue pour l'aperçu PDF de la liste des fournisseurs"""
    from datetime import datetime
    
    form = FournisseurSearchForm(request.GET)
    
    # Base queryset
    fournisseurs = Fournisseur.objects.all()
    
    # Appliquer les filtres (même logique que fournisseur_list)
    if form.is_valid():
        search = form.cleaned_data.get('search', '').strip()
        type_fournisseur = form.cleaned_data.get('type_fournisseur')
        actif = form.cleaned_data.get('actif')
        
        # Recherche textuelle
        if search:
            fournisseurs = fournisseurs.filter(
                Q(nom_complet__icontains=search) |
                Q(email__icontains=search) |
                Q(telephone__icontains=search) |
                Q(contact_principal__icontains=search) |
                Q(ville__icontains=search)
            )
        
        # Filtres
        if type_fournisseur:
            fournisseurs = fournisseurs.filter(type_fournisseur=type_fournisseur)
        if actif == 'true':
            fournisseurs = fournisseurs.filter(actif=True)
        elif actif == 'false':
            fournisseurs = fournisseurs.filter(actif=False)
    
    # Tri par défaut
    fournisseurs = fournisseurs.order_by('type_fournisseur', 'nom_complet')
    
    # Statistiques
    stats = {
        'materiaux': fournisseurs.filter(type_fournisseur='materiaux').count(),
        'services': fournisseurs.filter(type_fournisseur='services').count(),
        'equipements': fournisseurs.filter(type_fournisseur='equipements').count(),
        'actifs': fournisseurs.filter(actif=True).count(),
    }
    
    # Contexte pour le template
    context = {
        'fournisseurs': fournisseurs,
        'societe': get_societe_info(),
        'document_type': 'Liste des fournisseurs',
        'date_debut': datetime.now().date(),
        'date_fin': datetime.now().date(),
        'filtre_type': type_fournisseur or 'Tous',
        'stats': stats,
    }
    
    return render(request, 'fournisseurs/liste_fournisseurs_print.html', context)

def get_societe_info():
    """Retourne les informations de l'entreprise"""
    return {
        'nom': 'DEVDRECO SOFT',
        'adresse': '123 Avenue des Affaires',
        'ville': 'Lomé, Togo',
        'telephone': '+228 90 12 34 56',
        'email': 'contact@devdreco-soft.com',
        'site_web': 'www.devdreco-soft.com',
        'logo': None,
    }


@login_required
def fournisseur_detail(request, pk):
    """Détail d'un fournisseur"""
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    
    # Produits associés
    produits = ProduitFournisseur.objects.filter(
        fournisseur=fournisseur
    ).select_related('article').order_by('article__designation')
    
    # Statistiques des produits
    produits_stats = {
        'total': produits.count(),
        'actifs': produits.filter(actif=True).count(),
        'prix_moyen': produits.aggregate(
            avg_price=Avg('prix_achat_ht')
        )['avg_price'] or 0,
    }
    
    context = {
        'fournisseur': fournisseur,
        'produits': produits,
        'produits_stats': produits_stats,
    }
    
    return render(request, 'fournisseurs/fournisseur_detail.html', context)


@login_required
def fournisseur_create(request):
    """Création d'un nouveau fournisseur"""
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            fournisseur = form.save()
            messages.success(request, f'Fournisseur "{fournisseur.nom_complet}" créé avec succès.')
            return redirect('fournisseurs:fournisseur_detail', pk=fournisseur.pk)
    else:
        form = FournisseurForm()
    
    context = {
        'form': form,
        'title': 'Nouveau fournisseur',
        'submit_text': 'Créer le fournisseur',
    }
    
    return render(request, 'fournisseurs/fournisseur_form.html', context)


@login_required
def fournisseur_update(request, pk):
    """Modification d'un fournisseur"""
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            fournisseur = form.save()
            messages.success(request, f'Fournisseur "{fournisseur.nom_complet}" modifié avec succès.')
            return redirect('fournisseurs:fournisseur_detail', pk=fournisseur.pk)
    else:
        form = FournisseurForm(instance=fournisseur)
    
    context = {
        'form': form,
        'fournisseur': fournisseur,
        'title': f'Modifier {fournisseur.nom_complet}',
        'submit_text': 'Modifier le fournisseur',
    }
    
    return render(request, 'fournisseurs/fournisseur_form.html', context)


@login_required
@require_http_methods(["POST"])
def fournisseur_delete(request, pk):
    """Suppression d'un fournisseur"""
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    
    # Vérifier s'il y a des produits associés
    produits_count = ProduitFournisseur.objects.filter(fournisseur=fournisseur).count()
    
    if produits_count > 0:
        messages.error(
            request, 
            f'Impossible de supprimer le fournisseur "{fournisseur.nom_complet}" car il a {produits_count} produit(s) associé(s).'
        )
        return redirect('fournisseurs:fournisseur_detail', pk=fournisseur.pk)
    
    nom_fournisseur = fournisseur.nom_complet
    fournisseur.delete()
    
    messages.success(request, f'Fournisseur "{nom_fournisseur}" supprimé avec succès.')
    return redirect('fournisseurs:fournisseur_list')


@login_required
def fournisseur_toggle_status(request, pk):
    """Activer/Désactiver un fournisseur"""
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    
    fournisseur.actif = not fournisseur.actif
    fournisseur.save()
    
    status = "activé" if fournisseur.actif else "désactivé"
    messages.success(request, f'Fournisseur "{fournisseur.nom_complet}" {status} avec succès.')
    
    return redirect('fournisseurs:fournisseur_detail', pk=fournisseur.pk)


# Vues pour les produits fournisseurs

@login_required
def produit_fournisseur_list(request):
    """Liste des produits fournisseurs"""
    produits = ProduitFournisseur.objects.select_related(
        'fournisseur', 'article'
    ).order_by('fournisseur__nom_complet', 'article__designation')
    
    # Filtres
    fournisseur_id = request.GET.get('fournisseur')
    article_id = request.GET.get('article')
    actif = request.GET.get('actif')
    
    if fournisseur_id:
        produits = produits.filter(fournisseur_id=fournisseur_id)
    if article_id:
        produits = produits.filter(article_id=article_id)
    if actif == 'true':
        produits = produits.filter(actif=True)
    elif actif == 'false':
        produits = produits.filter(actif=False)
    
    # Pagination
    paginator = Paginator(produits, 20)
    page_number = request.GET.get('page')
    produits_page = paginator.get_page(page_number)
    
    # Données pour les filtres
    fournisseurs = Fournisseur.objects.filter(actif=True).order_by('nom_complet')
    articles = Article.objects.filter(actif=True).order_by('designation')
    
    context = {
        'produits': produits_page,
        'fournisseurs': fournisseurs,
        'articles': articles,
    }
    
    return render(request, 'fournisseurs/produit_fournisseur_list.html', context)


@login_required
def produit_fournisseur_create(request):
    """Création d'un nouveau produit fournisseur"""
    if request.method == 'POST':
        form = ProduitFournisseurForm(request.POST)
        if form.is_valid():
            produit = form.save()
            messages.success(
                request, 
                f'Produit "{produit.article.designation}" ajouté au fournisseur "{produit.fournisseur.nom_complet}" avec succès.'
            )
            return redirect('fournisseurs:produit_fournisseur_list')
    else:
        form = ProduitFournisseurForm()
    
    context = {
        'form': form,
        'title': 'Nouveau produit fournisseur',
        'submit_text': 'Ajouter le produit',
    }
    
    return render(request, 'fournisseurs/produit_fournisseur_form.html', context)


@login_required
def produit_fournisseur_update(request, pk):
    """Modification d'un produit fournisseur"""
    produit = get_object_or_404(ProduitFournisseur, pk=pk)
    
    if request.method == 'POST':
        form = ProduitFournisseurForm(request.POST, instance=produit)
        if form.is_valid():
            produit = form.save()
            messages.success(request, 'Produit fournisseur modifié avec succès.')
            return redirect('fournisseurs:produit_fournisseur_list')
    else:
        form = ProduitFournisseurForm(instance=produit)
    
    context = {
        'form': form,
        'produit': produit,
        'title': f'Modifier {produit.article.designation}',
        'submit_text': 'Modifier le produit',
    }
    
    return render(request, 'fournisseurs/produit_fournisseur_form.html', context)


@login_required
@require_http_methods(["POST"])
def produit_fournisseur_delete(request, pk):
    """Suppression d'un produit fournisseur"""
    produit = get_object_or_404(ProduitFournisseur, pk=pk)
    
    nom_produit = produit.article.designation
    nom_fournisseur = produit.fournisseur.nom_complet
    produit.delete()
    
    messages.success(
        request, 
        f'Produit "{nom_produit}" retiré du fournisseur "{nom_fournisseur}" avec succès.'
    )
    
    return redirect('fournisseurs:produit_fournisseur_list')


# Vues AJAX

@login_required
def fournisseur_create_popup(request):
    """Création de fournisseur en popup (AJAX)"""
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            fournisseur = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Fournisseur "{fournisseur.nom_complet}" créé avec succès.',
                'fournisseur': {
                    'id': fournisseur.id,
                    'nom_complet': fournisseur.nom_complet,
                    'type_fournisseur': fournisseur.get_type_fournisseur_display(),
                    'telephone': fournisseur.get_telephone_formate(),
                    'email': fournisseur.email or '',
                    'actif': fournisseur.actif,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    form = FournisseurForm()
    return render(request, 'fournisseurs/fournisseur_form_popup.html', {'form': form})


@login_required
def fournisseur_api(request):
    """API pour récupérer la liste des fournisseurs (AJAX)"""
    fournisseurs = Fournisseur.objects.filter(actif=True).order_by('nom_complet')
    
    data = []
    for fournisseur in fournisseurs:
        data.append({
            'id': fournisseur.id,
            'nom_complet': fournisseur.nom_complet,
            'type_fournisseur': fournisseur.get_type_fournisseur_display(),
            'telephone': fournisseur.get_telephone_formate(),
            'email': fournisseur.email or '',
        })
    
    return JsonResponse({'fournisseurs': data})