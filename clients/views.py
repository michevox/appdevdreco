from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta
import json
import re

from .models import Client
from .forms import ClientForm, ClientSearchForm
from utilisateurs.decorators import permission_required


def _normalize_digits(value: str) -> str:
	if not value:
		return ''
	return re.sub(r'[^\d]', '', value)


@login_required
@permission_required('clients.view')
def client_list(request):
	"""Vue pour afficher la liste des clients avec recherche et pagination"""
	
	# Récupération des paramètres de recherche
	search_form = ClientSearchForm(request.GET)
	clients = Client.objects.all()
	
	# Application des filtres
	if search_form.is_valid():
		search_term = search_form.cleaned_data.get('search_term')
		search_by = search_form.cleaned_data.get('search_by')
		type_client = search_form.cleaned_data.get('type_client')
		statut = search_form.cleaned_data.get('statut')
		date_debut = search_form.cleaned_data.get('date_debut')
		date_fin = search_form.cleaned_data.get('date_fin')
		
		# Recherche par terme
		if search_term:
			if search_by == 'nom':
				clients = clients.filter(nom_complet__icontains=search_term)
			elif search_by == 'telephone':
				# Recherche tolérante: on normalise en chiffres
				n = _normalize_digits(search_term)
				if n:
					# Match sur telephone normalisé qui contient n
					clients = clients.filter(telephone_normalise__icontains=n)
				else:
					clients = clients
			elif search_by == 'email':
				clients = clients.filter(email__icontains=search_term)
			else:
				# Recherche globale
				n = _normalize_digits(search_term)
				q = Q(nom_complet__icontains=search_term) | Q(email__icontains=search_term)
				if n:
					q |= Q(telephone_normalise__icontains=n)
				clients = clients.filter(q)
		
		# Filtre par type de client
		if type_client:
			clients = clients.filter(type_client=type_client)
		
		# Filtre par statut
		if statut:
			if statut == 'actif':
				clients = clients.filter(actif=True)
			elif statut == 'inactif':
				clients = clients.filter(actif=False)
		
		# Filtre par date
		if date_debut:
			clients = clients.filter(date_creation__date__gte=date_debut)
		if date_fin:
			clients = clients.filter(date_creation__date__lte=date_fin)
	
	# Tri par défaut
	clients = clients.order_by('-date_creation')
	
	# Pagination
	page = request.GET.get('page', 1)
	paginator = Paginator(clients, 10)  # 10 clients par page
	
	try:
		clients_page = paginator.page(page)
	except PageNotAnInteger:
		clients_page = paginator.page(1)
	except EmptyPage:
		clients_page = paginator.page(paginator.num_pages)
	
	# Statistiques
	total_clients = clients.count()
	clients_actifs = clients.filter(actif=True).count()
	clients_inactifs = clients.filter(actif=False).count()
	particuliers = clients.filter(type_client='particulier').count()
	entreprises = clients.filter(type_client='entreprise').count()
	
	# Clients récents (7 derniers jours)
	date_limite = timezone.now() - timedelta(days=7)
	clients_recents = clients.filter(date_creation__gte=date_limite).count()
	
	context = {
		'clients': clients_page,
		'search_form': search_form,
		'total_clients': total_clients,
		'clients_actifs': clients_actifs,
		'clients_inactifs': clients_inactifs,
		'particuliers': particuliers,
		'entreprises': entreprises,
		'clients_recents': clients_recents,
	}
	
	return render(request, 'clients/client_list.html', context)


@login_required
@permission_required('clients.view')
def client_liste_print(request):
	"""Vue pour l'aperçu PDF de la liste des clients"""
	from datetime import datetime, timedelta
	from django.utils import timezone
	
	# Récupération des paramètres de recherche
	search_form = ClientSearchForm(request.GET)
	clients = Client.objects.all()
	
	# Application des filtres (même logique que client_list)
	if search_form.is_valid():
		search_term = search_form.cleaned_data.get('search_term')
		search_by = search_form.cleaned_data.get('search_by')
		type_client = search_form.cleaned_data.get('type_client')
		statut = search_form.cleaned_data.get('statut')
		date_debut = search_form.cleaned_data.get('date_debut')
		date_fin = search_form.cleaned_data.get('date_fin')
		
		# Recherche par terme
		if search_term:
			if search_by == 'nom':
				clients = clients.filter(nom_complet__icontains=search_term)
			elif search_by == 'telephone':
				n = _normalize_digits(search_term)
				if n:
					clients = clients.filter(telephone_normalise__icontains=n)
			elif search_by == 'email':
				clients = clients.filter(email__icontains=search_term)
			else:
				n = _normalize_digits(search_term)
				q = Q(nom_complet__icontains=search_term) | Q(email__icontains=search_term)
				if n:
					q |= Q(telephone_normalise__icontains=n)
				clients = clients.filter(q)
		
		# Filtres
		if type_client:
			clients = clients.filter(type_client=type_client)
		if statut:
			if statut == 'actif':
				clients = clients.filter(actif=True)
			elif statut == 'inactif':
				clients = clients.filter(actif=False)
		if date_debut:
			clients = clients.filter(date_creation__date__gte=date_debut)
		if date_fin:
			clients = clients.filter(date_creation__date__lte=date_fin)
	
	# Tri par défaut
	clients = clients.order_by('type_client', 'nom_complet')
	
	# Statistiques
	stats = {
		'particuliers': clients.filter(type_client='particulier').count(),
		'entreprises': clients.filter(type_client='entreprise').count(),
		'actifs': clients.filter(actif=True).count(),
	}
	
	# Contexte pour le template
	context = {
		'clients': clients,
		'societe': get_societe_info(),
		'document_type': 'Liste des clients',
		'date_debut': date_debut or clients.first().date_creation.date() if clients.exists() else datetime.now().date(),
		'date_fin': date_fin or datetime.now().date(),
		'filtre_type': type_client or 'Tous',
		'stats': stats,
	}
	
	return render(request, 'clients/liste_clients_print.html', context)

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
@permission_required('clients.view')
def client_detail(request, pk):
	"""Vue pour afficher les détails d'un client"""
	client = get_object_or_404(Client, pk=pk)
	
	# Récupération des statistiques du client
	nombre_devis = client.get_nombre_devis()
	nombre_factures = client.get_nombre_factures()
	total_factures = client.get_total_factures()
	derniere_activite = client.get_derniere_activite()
	
	context = {
		'client': client,
		'nombre_devis': nombre_devis,
		'nombre_factures': nombre_factures,
		'total_factures': total_factures,
		'derniere_activite': derniere_activite,
	}
	
	return render(request, 'clients/client_detail.html', context)


@login_required
@permission_required('clients.add')
def client_create(request):
	"""Vue pour créer un nouveau client via popup AJAX"""
	if request.method == 'POST':
		form = ClientForm(request.POST)
		if form.is_valid():
			client = form.save()
			messages.success(request, f'Client "{client.nom_complet}" créé avec succès.')
			return JsonResponse({
				'success': True,
				'message': f'Client "{client.nom_complet}" créé avec succès.',
				'client_id': client.id,
				'client_nom': client.nom_complet
			})
		else:
			return JsonResponse({
				'success': False,
				'errors': form.errors
			})
	
	form = ClientForm()
	return render(request, 'clients/client_form_modal.html', {'form': form})


@login_required
@permission_required('clients.change')
def client_update(request, pk):
	"""Vue pour modifier un client via popup AJAX"""
	client = get_object_or_404(Client, pk=pk)
	
	if request.method == 'POST':
		form = ClientForm(request.POST, instance=client)
		if form.is_valid():
			client = form.save()
			messages.success(request, f'Client "{client.nom_complet}" modifié avec succès.')
			return JsonResponse({
				'success': True,
				'message': f'Client "{client.nom_complet}" modifié avec succès.',
				'client_id': client.id,
				'client_nom': client.nom_complet
			})
		else:
			return JsonResponse({
				'success': False,
				'errors': form.errors
			})
	
	form = ClientForm(instance=client)
	return render(request, 'clients/client_form_modal.html', {'form': form, 'client': client})


@login_required
@permission_required('clients.delete')
@require_POST
def client_delete(request, pk):
	"""Vue pour supprimer un client"""
	client = get_object_or_404(Client, pk=pk)
	nom_client = client.nom_complet
	
	try:
		client.delete()
		messages.success(request, f'Client "{nom_client}" supprimé avec succès.')
		return JsonResponse({
			'success': True,
			'message': f'Client "{nom_client}" supprimé avec succès.'
		})
	except Exception as e:
		return JsonResponse({
			'success': False,
			'message': f'Erreur lors de la suppression: {str(e)}'
		})


@login_required
@permission_required('clients.change')
@require_POST
def client_toggle_status(request, pk):
	"""Vue pour activer/désactiver un client"""
	client = get_object_or_404(Client, pk=pk)
	
	try:
		client.actif = not client.actif
		client.save()
		
		status = "activé" if client.actif else "désactivé"
		messages.success(request, f'Client "{client.nom_complet}" {status} avec succès.')
		
		return JsonResponse({
			'success': True,
			'message': f'Client "{client.nom_complet}" {status} avec succès.',
			'actif': client.actif
		})
	except Exception as e:
		return JsonResponse({
			'success': False,
			'message': f'Erreur lors du changement de statut: {str(e)}'
		})


@login_required
@permission_required('clients.export')
def client_export(request):
	"""Vue pour exporter la liste des clients"""
	from django.http import HttpResponse
	import csv
	
	# Récupération des clients avec les mêmes filtres que la liste
	search_form = ClientSearchForm(request.GET)
	clients = Client.objects.all()
	
	if search_form.is_valid():
		# Application des mêmes filtres que dans client_list
		search_term = search_form.cleaned_data.get('search_term')
		search_by = search_form.cleaned_data.get('search_by')
		type_client = search_form.cleaned_data.get('type_client')
		statut = search_form.cleaned_data.get('statut')
		date_debut = search_form.cleaned_data.get('date_debut')
		date_fin = search_form.cleaned_data.get('date_fin')
		
		if search_term:
			if search_by == 'nom':
				clients = clients.filter(nom_complet__icontains=search_term)
			elif search_by == 'telephone':
				n = _normalize_digits(search_term)
				if n:
					clients = clients.filter(telephone_normalise__icontains=n)
			elif search_by == 'email':
				clients = clients.filter(email__icontains=search_term)
			else:
				n = _normalize_digits(search_term)
				q = Q(nom_complet__icontains=search_term) | Q(email__icontains=search_term)
				if n:
					q |= Q(telephone_normalise__icontains=n)
				clients = clients.filter(q)
		
		if type_client:
			clients = clients.filter(type_client=type_client)
		
		if statut:
			if statut == 'actif':
				clients = clients.filter(actif=True)
			elif statut == 'inactif':
				clients = clients.filter(actif=False)
		
		if date_debut:
			clients = clients.filter(date_creation__date__gte=date_debut)
		if date_fin:
			clients = clients.filter(date_creation__date__lte=date_fin)
	
	# Création du fichier CSV
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = f'attachment; filename="clients_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
	
	writer = csv.writer(response)
	writer.writerow([
		'Nom complet/Raison sociale',
		'Type',
		'Téléphone',
		'Email',
		'Adresse',
		'Statut',
		'Date de création',
		'Dernière modification'
	])
	
	for client in clients:
		writer.writerow([
			client.nom_complet,
			client.get_type_display_short(),
			client.telephone,
			client.email or '',
			client.adresse or '',
			'Actif' if client.actif else 'Inactif',
			client.date_creation.strftime('%d/%m/%Y %H:%M'),
			client.date_modification.strftime('%d/%m/%Y %H:%M')
		])
	
	return response


@login_required
@permission_required('clients.view')
def client_statistics(request):
	"""Vue pour les statistiques des clients (AJAX)"""
	# Statistiques générales
	total_clients = Client.objects.count()
	clients_actifs = Client.objects.filter(actif=True).count()
	clients_inactifs = Client.objects.filter(actif=False).count()
	particuliers = Client.objects.filter(type_client='particulier').count()
	entreprises = Client.objects.filter(type_client='entreprise').count()
	
	# Évolution mensuelle (6 derniers mois)
	evolution_mensuelle = []
	for i in range(6):
		date = timezone.now() - timedelta(days=30*i)
		debut_mois = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		fin_mois = (debut_mois + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
		
		count = Client.objects.filter(
			date_creation__gte=debut_mois,
			date_creation__lte=fin_mois
		).count()
		
		evolution_mensuelle.append({
			'mois': debut_mois.strftime('%B %Y'),
			'count': count
		})
	
	return JsonResponse({
		'total_clients': total_clients,
		'clients_actifs': clients_actifs,
		'clients_inactifs': clients_inactifs,
		'particuliers': particuliers,
		'entreprises': entreprises,
		'evolution_mensuelle': evolution_mensuelle
	})
