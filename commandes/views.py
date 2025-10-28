from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from .models import BonCommande, LigneCommande
from .forms import BonCommandeForm, LigneCommandeFormSet, BonCommandeSearchForm
from clients.models import Client
from devis.models import Devis
from fournisseurs.models import Fournisseur
from utilisateurs.decorators import class_permission_required

@class_permission_required('commandes.view')
class BonCommandeListView(LoginRequiredMixin, ListView):
    """Vue pour lister tous les bons de commande"""
    model = BonCommande
    template_name = 'commandes/commande_list.html'
    context_object_name = 'commande_list'
    paginate_by = 20
    
    def get_queryset(self):
        """Filtre les commandes selon les paramètres de recherche"""
        queryset = BonCommande.objects.select_related('client', 'fournisseur', 'devis')
        
        # Filtre par type de commande
        type_commande = self.request.GET.get('type_commande')
        if type_commande:
            queryset = queryset.filter(type_commande=type_commande)
        
        # Filtre par statut
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        # Filtre par fournisseur
        fournisseur_id = self.request.GET.get('fournisseur')
        if fournisseur_id:
            queryset = queryset.filter(fournisseur_id=fournisseur_id)
        
        # Filtre par client
        client_id = self.request.GET.get('client')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        # Filtre par date de début
        date_debut = self.request.GET.get('date_debut')
        if date_debut:
            queryset = queryset.filter(date_creation__gte=date_debut)
        
        # Filtre par date de fin
        date_fin = self.request.GET.get('date_fin')
        if date_fin:
            queryset = queryset.filter(date_creation__lte=date_fin)
        
        # Recherche textuelle
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(numero__icontains=q) |
                Q(client__nom_complet__icontains=q) |
                Q(fournisseur__nom__icontains=q) |
                Q(objet__icontains=q)
            )
        
        return queryset.order_by('-date_creation')
    
    def get_context_data(self, **kwargs):
        """Ajoute les statistiques et données supplémentaires au contexte"""
        context = super().get_context_data(**kwargs)
        
        # Statistiques
        context['total_commandes'] = BonCommande.objects.count()
        context['commandes_brouillon'] = BonCommande.objects.filter(statut='brouillon').count()
        context['commandes_envoyees'] = BonCommande.objects.filter(statut='envoye').count()
        context['commandes_confirmees'] = BonCommande.objects.filter(statut='confirme').count()
        context['commandes_en_cours'] = BonCommande.objects.filter(statut='en_cours').count()
        context['commandes_livrees'] = BonCommande.objects.filter(statut='livre').count()
        context['commandes_annulees'] = BonCommande.objects.filter(statut='annule').count()
        
        # Commandes du mois en cours
        current_month = datetime.now().month
        current_year = datetime.now().year
        context['commandes_ce_mois'] = BonCommande.objects.filter(
            date_creation__month=current_month,
            date_creation__year=current_year
        ).count()
        
        # Total des montants HT
        total_ht = BonCommande.objects.aggregate(total=Sum('montant_ht'))['total'] or 0
        context['total_montant_ht'] = total_ht
        
        # Liste des fournisseurs et clients pour les filtres
        context['fournisseurs'] = Fournisseur.objects.filter(actif=True)
        context['clients'] = Client.objects.filter(actif=True)
        
        # Formulaire de recherche
        context['search_form'] = BonCommandeSearchForm(self.request.GET)
        
        return context

@class_permission_required('commandes.view')
class BonCommandeDetailView(LoginRequiredMixin, DetailView):
    """Vue pour afficher les détails d'une commande"""
    model = BonCommande
    template_name = 'commandes/commande_detail.html'
    context_object_name = 'commande'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lignes'] = self.object.lignes.all()
        return context

@class_permission_required('commandes.add')
class BonCommandeCreateView(LoginRequiredMixin, CreateView):
    """Vue pour créer une nouvelle commande"""
    model = BonCommande
    form_class = BonCommandeForm
    template_name = 'commandes/commande_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['lignes_formset'] = LigneCommandeFormSet(self.request.POST, instance=self.object)
        else:
            context['lignes_formset'] = LigneCommandeFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        lignes_formset = context['lignes_formset']
        
        if form.is_valid() and lignes_formset.is_valid():
            self.object = form.save()
            lignes_formset.instance = self.object
            lignes_formset.save()
            
            # Forcer le recalcul des montants en rafraîchissant l'objet
            self.object.refresh_from_db()
            self.object.calculer_montants()
            
            messages.success(self.request, 'Bon de commande créé avec succès.')
            return redirect('commandes:commande_detail', pk=self.object.pk)
        
        return self.render_to_response(self.get_context_data(form=form))

@class_permission_required('commandes.change')
class BonCommandeUpdateView(LoginRequiredMixin, UpdateView):
    """Vue pour modifier une commande existante"""
    model = BonCommande
    form_class = BonCommandeForm
    template_name = 'commandes/commande_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['lignes_formset'] = LigneCommandeFormSet(self.request.POST, instance=self.object)
        else:
            context['lignes_formset'] = LigneCommandeFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        lignes_formset = context['lignes_formset']
        
        if lignes_formset.is_valid():
            try:
                self.object = form.save()
                lignes_formset.save()
                
                # Forcer le recalcul des montants en rafraîchissant l'objet
                self.object.refresh_from_db()
                self.object.calculer_montants()
                
                messages.success(self.request, 'Bon de commande modifié avec succès.')
                return redirect('commandes:commande_detail', pk=self.object.pk)
            except Exception as e:
                messages.error(self.request, f'Erreur lors de la sauvegarde: {str(e)}')
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)

@class_permission_required('commandes.delete')
class BonCommandeDeleteView(LoginRequiredMixin, DeleteView):
    """Vue pour supprimer une commande"""
    model = BonCommande
    template_name = 'commandes/commande_confirm_delete.html'
    success_url = reverse_lazy('commandes:commande_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Bon de commande supprimé avec succès.')
        return super().delete(request, *args, **kwargs)

@login_required
def commande_confirmer(request, pk):
    """Marque une commande comme confirmée"""
    commande = get_object_or_404(BonCommande, pk=pk)
    commande.confirmer()
    messages.success(request, f'Commande {commande.numero} confirmée avec succès.')
    return redirect('commandes:commande_detail', pk=pk)

@login_required
def commande_livrer(request, pk):
    """Marque une commande comme livrée"""
    commande = get_object_or_404(BonCommande, pk=pk)
    commande.livrer()
    messages.success(request, f'Commande {commande.numero} marquée comme livrée.')
    return redirect('commandes:commande_detail', pk=pk)

@login_required
def commande_annuler(request, pk):
    """Marque une commande comme annulée"""
    commande = get_object_or_404(BonCommande, pk=pk)
    commande.annuler()
    messages.success(request, f'Commande {commande.numero} annulée.')
    return redirect('commandes:commande_detail', pk=pk)

@login_required
def commande_envoyer(request, pk):
    """Marque une commande comme envoyée"""
    commande = get_object_or_404(BonCommande, pk=pk)
    commande.statut = 'envoye'
    commande.save()
    messages.success(request, f'Commande {commande.numero} marquée comme envoyée.')
    return redirect('commandes:commande_detail', pk=pk)

@login_required
def commande_en_cours(request, pk):
    """Marque une commande comme en cours"""
    commande = get_object_or_404(BonCommande, pk=pk)
    commande.statut = 'en_cours'
    commande.save()
    messages.success(request, f'Commande {commande.numero} marquée comme en cours.')
    return redirect('commandes:commande_detail', pk=pk)

@login_required
def generer_numero_commande(request):
    """Génère automatiquement un numéro de commande"""
    from datetime import datetime
    
    # Format: CMD-YYYYMMDD-XXX
    today = datetime.now()
    prefix = f"CMD-{today.strftime('%Y%m%d')}"
    
    # Trouver le dernier numéro du jour
    derniere_commande = BonCommande.objects.filter(
        numero__startswith=prefix
    ).order_by('numero').last()
    
    if derniere_commande:
        # Extraire le numéro séquentiel
        try:
            dernier_numero = int(derniere_commande.numero.split('-')[-1])
            nouveau_numero = dernier_numero + 1
        except (ValueError, IndexError):
            nouveau_numero = 1
    else:
        nouveau_numero = 1
    
    # Formater avec 3 chiffres
    numero_commande = f"{prefix}-{nouveau_numero:03d}"
    
    return JsonResponse({'numero': numero_commande})

@login_required
def ajouter_ligne_commande(request, pk):
    """Ajoute une ligne à une commande via AJAX"""
    if request.method == 'POST':
        commande = get_object_or_404(BonCommande, pk=pk)
        
        description = request.POST.get('description')
        quantite = request.POST.get('quantite')
        unite = request.POST.get('unite')
        prix_unitaire = request.POST.get('prix_unitaire')
        
        if all([description, quantite, unite, prix_unitaire]):
            try:
                ligne = LigneCommande.objects.create(
                    commande=commande,
                    description=description,
                    quantite=quantite,
                    unite=unite,
                    prix_unitaire_ht=prix_unitaire
                )
                
                # Recalculer les montants
                commande.calculer_montants()
                
                return JsonResponse({
                    'success': True,
                    'ligne_id': ligne.id,
                    'montant_ht': float(ligne.montant_ht),
                    'message': 'Ligne ajoutée avec succès'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur: {str(e)}'
                })
        
        return JsonResponse({
            'success': False,
            'message': 'Tous les champs sont requis'
        })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@login_required
def imprimer_commande(request, pk):
    """Vue pour imprimer un bon de commande en PDF"""
    commande = get_object_or_404(BonCommande, pk=pk)
    
    # Récupérer les lignes de la commande
    lignes = commande.lignes.all()
    
    # Contexte pour le template
    context = {
        'bon_commande': commande,
        'lignes': lignes,
        'societe': get_societe_info(),
        'document_type': 'Bon de commande'
    }
    
    try:
        # Générer le PDF avec ReportLab
        from .utils import generer_pdf_commande
        
        # Générer le PDF
        pdf_content = generer_pdf_commande(commande, lignes, get_societe_info(), mode='inline')
        
        # Réponse HTTP avec le PDF
        from django.http import HttpResponse
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="bon_commande_{commande.numero}.pdf"'
        
        return response
        
    except Exception as e:
        # En cas d'erreur, afficher un message d'erreur
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, f'Erreur lors de la génération du PDF: {str(e)}')
        return redirect('commandes:commande_detail', pk=commande.pk)

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
