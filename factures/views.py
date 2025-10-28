from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta, date, datetime
from decimal import Decimal, InvalidOperation
from .models import Facture, LigneFacture
from .forms import FactureForm, LigneFactureFormSet
from fournisseurs.models import Fournisseur
from utilisateurs.decorators import permission_required, class_permission_required
from utilisateurs.utils import filter_queryset_by_permissions
import os
import tempfile

@class_permission_required('factures.view')
class FactureListView(LoginRequiredMixin, ListView):
    """Vue pour lister toutes les factures"""
    model = Facture
    template_name = 'factures/facture_list.html'
    context_object_name = 'factures_list'
    paginate_by = 20
    
    def get_queryset(self):
        """Filtre les factures selon les paramètres de recherche"""
        # Utiliser select_related pour optimiser les requêtes fournisseur
        queryset = Facture.objects.select_related('fournisseur')
        
        # Filtrer selon les permissions utilisateur
        queryset = filter_queryset_by_permissions(self.request.user, queryset, 'factures')
        
        # Filtre par statut
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        # Filtre par fournisseur
        fournisseur_id = self.request.GET.get('fournisseur')
        if fournisseur_id:
            queryset = queryset.filter(fournisseur_id=fournisseur_id)
        
        # Filtre par date de début
        date_debut = self.request.GET.get('date_debut')
        if date_debut:
            queryset = queryset.filter(date_emission__gte=date_debut)
        
        # Filtre par date de fin
        date_fin = self.request.GET.get('date_fin')
        if date_fin:
            queryset = queryset.filter(date_emission__lte=date_fin)
        
        # Recherche textuelle
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(numero__icontains=q) |
                Q(fournisseur__nom__icontains=q) |
                Q(objet__icontains=q)
            )
        
        return queryset.order_by('-date_emission')
    
    def get_context_data(self, **kwargs):
        """Ajoute les statistiques et données supplémentaires au contexte"""
        context = super().get_context_data(**kwargs)
        
        # Gestion robuste des erreurs de base de données
        try:
            # Statistiques avec gestion d'erreur robuste
            try:
                context['total_factures'] = Facture.objects.count()
            except Exception as e:
                print(f"Erreur lors du comptage total des factures: {e}")
                context['total_factures'] = 0
                
            try:
                context['factures_brouillon'] = Facture.objects.filter(statut='brouillon').count()
            except Exception as e:
                print(f"Erreur lors du comptage des factures brouillon: {e}")
                context['factures_brouillon'] = 0
                
            try:
                context['factures_en_attente'] = Facture.objects.filter(statut='en_attente').count()
            except Exception as e:
                print(f"Erreur lors du comptage des factures en attente: {e}")
                context['factures_en_attente'] = 0
                
            try:
                context['factures_validees'] = Facture.objects.filter(statut='validee').count()
            except Exception as e:
                print(f"Erreur lors du comptage des factures validées: {e}")
                context['factures_validees'] = 0
                
            try:
                context['factures_payees'] = Facture.objects.filter(statut='payee').count()
            except Exception as e:
                print(f"Erreur lors du comptage des factures payées: {e}")
                context['factures_payees'] = 0
                
            try:
                context['factures_annulees'] = Facture.objects.filter(statut='annulee').count()
            except Exception as e:
                print(f"Erreur lors du comptage des factures annulées: {e}")
                context['factures_annulees'] = 0
                
            # Calcul du montant total HT avec gestion d'erreur
            try:
                from django.db.models import Sum
                total_montant_ht = Facture.objects.aggregate(
                    total=Sum('montant_ht')
                )['total'] or Decimal('0.00')
                context['total_montant_ht'] = total_montant_ht
            except Exception as e:
                print(f"Erreur lors du calcul du montant total HT: {e}")
                context['total_montant_ht'] = Decimal('0.00')
                
        except Exception as e:
            print(f"Erreur générale dans get_context_data: {e}")
            # Valeurs par défaut en cas d'erreur
            context.update({
                'total_factures': 0,
                'factures_brouillon': 0,
                'factures_en_attente': 0,
                'factures_validees': 0,
                'factures_payees': 0,
                'factures_annulees': 0,
                'total_montant_ht': Decimal('0.00')
            })
        
        # Ajouter la liste des fournisseurs pour le filtre
        try:
            context['fournisseurs'] = Fournisseur.objects.filter(actif=True).order_by('nom')
        except Exception as e:
            print(f"Erreur lors de la récupération des fournisseurs: {e}")
            context['fournisseurs'] = []
        
        return context

@class_permission_required('factures.view')
class FactureDetailView(LoginRequiredMixin, DetailView):
    """Vue pour afficher les détails d'une facture"""
    model = Facture
    template_name = 'factures/facture_detail.html'
    context_object_name = 'facture'
    
    def get_queryset(self):
        """Filtre selon les permissions utilisateur"""
        queryset = Facture.objects.select_related('fournisseur').prefetch_related('lignes')
        return filter_queryset_by_permissions(self.request.user, queryset, 'factures')

@class_permission_required('factures.add')
class FactureCreateView(LoginRequiredMixin, CreateView):
    """Vue pour créer une nouvelle facture"""
    model = Facture
    form_class = FactureForm
    template_name = 'factures/facture_form.html'
    
    def get_context_data(self, **kwargs):
        """Ajoute le formset des lignes au contexte"""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['lignes_formset'] = LigneFactureFormSet(self.request.POST)
        else:
            context['lignes_formset'] = LigneFactureFormSet()
        return context
    
    def form_valid(self, form):
        """Traite le formulaire et le formset des lignes"""
        context = self.get_context_data()
        lignes_formset = context['lignes_formset']
        
        if lignes_formset.is_valid():
            # Sauvegarder la facture
            self.object = form.save()
            
            # Sauvegarder les lignes
            lignes_formset.instance = self.object
            lignes_formset.save()
            
            # Forcer le recalcul des montants en rafraîchissant l'objet
            self.object.refresh_from_db()
            self.object.calculer_montants()
            
            messages.success(self.request, f'Facture "{self.object.numero}" créée avec succès.')
            return redirect('factures:facture_detail', pk=self.object.pk)
        else:
            return self.form_invalid(form)

@class_permission_required('factures.change')
class FactureUpdateView(LoginRequiredMixin, UpdateView):
    """Vue pour modifier une facture"""
    model = Facture
    form_class = FactureForm
    template_name = 'factures/facture_form.html'
    
    def get_queryset(self):
        """Filtre selon les permissions utilisateur"""
        queryset = Facture.objects.select_related('fournisseur').prefetch_related('lignes')
        return filter_queryset_by_permissions(self.request.user, queryset, 'factures')
    
    def get_context_data(self, **kwargs):
        """Ajoute le formset des lignes au contexte"""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['lignes_formset'] = LigneFactureFormSet(self.request.POST, instance=self.object)
        else:
            context['lignes_formset'] = LigneFactureFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        """Traite le formulaire et le formset des lignes"""
        context = self.get_context_data()
        lignes_formset = context['lignes_formset']
        
        if lignes_formset.is_valid():
            # Sauvegarder la facture
            self.object = form.save()
            
            # Sauvegarder les lignes
            lignes_formset.save()
            
            # Forcer le recalcul des montants en rafraîchissant l'objet
            self.object.refresh_from_db()
            self.object.calculer_montants()
            
            messages.success(self.request, f'Facture "{self.object.numero}" modifiée avec succès.')
            return redirect('factures:facture_detail', pk=self.object.pk)
        else:
            return self.form_invalid(form)

@class_permission_required('factures.delete')
class FactureDeleteView(LoginRequiredMixin, DeleteView):
    """Vue pour supprimer une facture"""
    model = Facture
    template_name = 'factures/facture_confirm_delete.html'
    success_url = reverse_lazy('factures:facture_list')
    
    def get_queryset(self):
        """Filtre selon les permissions utilisateur"""
        queryset = Facture.objects.select_related('fournisseur')
        return filter_queryset_by_permissions(self.request.user, queryset, 'factures')

@login_required
def facture_apercu_ecran(request, pk):
    """Vue pour l'aperçu HTML d'une facture dans le navigateur"""
    facture = get_object_or_404(Facture, pk=pk)
    
    # Récupérer les lignes de la facture
    lignes = facture.lignes.all()
    
    # Contexte pour le template
    context = {
        'facture': facture,
        'lignes': lignes,
        'societe': get_societe_info(),
        'document_type': 'Facture'
    }
    
    # Utiliser le nouveau template HTML pour l'aperçu
    return render(request, 'factures/facture_print.html', context)

@login_required
def facture_imprimer(request, pk):
    """Vue pour imprimer une facture en PDF"""
    facture = get_object_or_404(Facture, pk=pk)
    
    # Récupérer les lignes de la facture
    lignes = facture.lignes.all()
    
    # Contexte pour le template
    context = {
        'facture': facture,
        'lignes': lignes,
        'societe': get_societe_info()
    }
    
    try:
        # Générer le PDF avec ReportLab
        from .utils import generer_pdf_facture
        
        # Générer le PDF
        pdf_content = generer_pdf_facture(facture, lignes, get_societe_info(), mode='inline')
        
        # Réponse HTTP avec le PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="facture_{facture.numero}.pdf"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la génération du PDF: {str(e)}')
        return redirect('factures:facture_detail', pk=pk)

@login_required
def facture_telecharger(request, pk):
    """Vue pour télécharger une facture en PDF"""
    facture = get_object_or_404(Facture, pk=pk)
    
    # Récupérer les lignes de la facture
    lignes = facture.lignes.all()
    
    # Contexte pour le template
    context = {
        'facture': facture,
        'lignes': lignes,
        'societe': get_societe_info()
    }
    
    try:
        # Générer le PDF avec ReportLab
        from .utils import generer_pdf_facture
        
        # Générer le PDF
        pdf_content = generer_pdf_facture(facture, lignes, get_societe_info(), mode='attachment')
        
        # Réponse HTTP avec le PDF en téléchargement
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{facture.numero}.pdf"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la génération du PDF: {str(e)}')
        return redirect('factures:facture_detail', pk=pk)

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
@permission_required('factures.delete')
def facture_delete_ajax(request, pk):
    """Vue AJAX pour supprimer une facture"""
    if request.method == 'POST':
        try:
            facture = get_object_or_404(Facture, pk=pk)
            numero = facture.numero
            facture.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Facture "{numero}" supprimée avec succès.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de la suppression: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée.'
    })

@login_required
@permission_required('factures.change')
def facture_toggle_status(request, pk):
    """Vue pour changer le statut d'une facture"""
    if request.method == 'POST':
        try:
            facture = get_object_or_404(Facture, pk=pk)
            action = request.POST.get('action')
            
            if action == 'valider':
                facture.valider()
                message = f'Facture "{facture.numero}" validée avec succès.'
            elif action == 'payer':
                facture.payer()
                message = f'Facture "{facture.numero}" marquée comme payée.'
            elif action == 'annuler':
                facture.annuler()
                message = f'Facture "{facture.numero}" annulée.'
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Action non reconnue.'
                })
            
            return JsonResponse({
                'success': True,
                'message': message,
                'statut': facture.statut
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors du changement de statut: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée.'
    })