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
from .models import Devis, LigneDevis
from .forms import DevisForm, LigneDevisFormSet
from .utils import get_societe_info
from clients.models import Client
from utilisateurs.decorators import permission_required, class_permission_required
from utilisateurs.utils import filter_queryset_by_permissions
import os
import tempfile

@class_permission_required('devis.view')
class DevisListView(LoginRequiredMixin, ListView):
    """Vue pour lister tous les devis"""
    model = Devis
    template_name = 'devis/devis_list.html'
    context_object_name = 'devis_list'
    paginate_by = 20
    
    def get_queryset(self):
        """Filtre les devis selon les paramètres de recherche"""
        # Utiliser select_related pour optimiser les requêtes client
        # Éviter prefetch_related('lignes') qui peut causer des problèmes avec les champs décimaux
        queryset = Devis.objects.select_related('client')
        
        # Filtrer selon les permissions utilisateur
        queryset = filter_queryset_by_permissions(self.request.user, queryset, 'devis')
        
        # Filtre par statut
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
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
                Q(objet__icontains=q)
            )
        
        return queryset.order_by('-date_creation')
    
    def get_context_data(self, **kwargs):
        """Ajoute les statistiques et données supplémentaires au contexte"""
        # S'assurer que tous les attributs nécessaires sont définis
        if not hasattr(self, 'object_list'):
            self.object_list = self.get_queryset()
        if not hasattr(self, 'kwargs'):
            self.kwargs = {}
            
        context = super().get_context_data(**kwargs)
        
        # Gestion robuste des erreurs de base de données
        try:
            # Statistiques avec gestion d'erreur robuste
            try:
                context['total_devis'] = Devis.objects.count()
            except Exception as e:
                print(f"Erreur lors du comptage total des devis: {e}")
                context['total_devis'] = 0
                
            try:
                context['devis_brouillon'] = Devis.objects.filter(statut='brouillon').count()
            except Exception as e:
                print(f"Erreur lors du comptage des devis brouillon: {e}")
                context['devis_brouillon'] = 0
                
            try:
                context['devis_en_attente'] = Devis.objects.filter(statut='en_attente').count()
            except Exception as e:
                print(f"Erreur lors du comptage des devis en attente: {e}")
                context['devis_en_attente'] = 0
                
            try:
                context['devis_acceptes'] = Devis.objects.filter(statut='accepte').count()
            except Exception as e:
                print(f"Erreur lors du comptage des devis acceptés: {e}")
                context['devis_acceptes'] = 0
                
            try:
                context['devis_refuses'] = Devis.objects.filter(statut='refuse').count()
            except Exception as e:
                print(f"Erreur lors du comptage des devis refusés: {e}")
                context['devis_refuses'] = 0
            
            # Devis du mois en cours avec gestion d'erreur robuste
            from datetime import datetime, date
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Utiliser des filtres de date plus robustes
            try:
                # Calculer le premier et le dernier jour du mois
                first_day = date(current_year, current_month, 1)
                if current_month == 12:
                    last_day = date(current_year + 1, 1, 1) - timedelta(days=1)
                else:
                    last_day = date(current_year, current_month + 1, 1) - timedelta(days=1)
                
                context['devis_ce_mois'] = Devis.objects.filter(
                    date_creation__gte=first_day,
                    date_creation__lte=last_day
                ).count()
            except Exception as e:
                print(f"Erreur lors du calcul des devis du mois: {e}")
                context['devis_ce_mois'] = 0
            
            # Total des montants HT avec gestion d'erreur
            from django.db.models import Sum
            try:
                total_ht = Devis.objects.aggregate(total=Sum('montant_ht'))['total'] or 0
                context['total_montant_ht'] = total_ht
            except Exception as e:
                print(f"Erreur lors du calcul du total HT: {e}")
                context['total_montant_ht'] = 0
            
            # Liste des clients pour le filtre avec gestion d'erreur
            from clients.models import Client
            try:
                context['clients'] = Client.objects.filter(actif=True)
            except Exception as e:
                print(f"Erreur lors de la récupération des clients: {e}")
                context['clients'] = []
                
        except Exception as e:
            print(f"Erreur générale dans get_context_data: {e}")
            # Valeurs par défaut en cas d'erreur
            context['total_devis'] = 0
            context['devis_brouillon'] = 0
            context['devis_en_attente'] = 0
            context['devis_acceptes'] = 0
            context['devis_refuses'] = 0
            context['devis_ce_mois'] = 0
            context['total_montant_ht'] = 0
            context['clients'] = []
        
        return context

class DevisDetailView(LoginRequiredMixin, DetailView):
    """Vue pour afficher les détails d'un devis"""
    model = Devis
    template_name = 'devis/devis_detail.html'
    context_object_name = 'devis'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            devis = self.get_object()
            # Récupérer les lignes avec gestion d'erreur robuste
            try:
                lignes = devis.lignes.all()
                context['lignes'] = lignes
            except Exception as e:
                print(f"Erreur lors de la récupération des lignes: {e}")
                context['lignes'] = []
        except Exception as e:
            print(f"Erreur dans DevisDetailView.get_context_data: {e}")
            context['lignes'] = []
        return context
    
    def get_object(self, queryset=None):
        """Récupère l'objet avec gestion d'erreur robuste"""
        try:
            return super().get_object(queryset)
        except Exception as e:
            print(f"Erreur lors de la récupération du devis: {e}")
            # Retourner un objet vide en cas d'erreur
            from django.http import Http404
            raise Http404("Devis non trouvé ou inaccessible")

class DevisCreateView(LoginRequiredMixin, CreateView):
    """Vue pour créer un nouveau devis"""
    model = Devis
    form_class = DevisForm
    template_name = 'devis/devis_form.html'
    success_url = reverse_lazy('devis:devis_list')
    
    def get_initial(self):
        """Génère automatiquement le numéro de devis"""
        initial = super().get_initial()
        
        # Générer le prochain numéro de devis
        from datetime import datetime
        
        # Format: DEV-YYYYMMDD-XXX
        today = datetime.now()
        prefix = f"DEV-{today.strftime('%Y%m%d')}"
        
        # Trouver le dernier numéro du jour
        last_devis = Devis.objects.filter(
            numero__startswith=prefix
        ).order_by('numero').last()
        
        if last_devis:
            # Extraire le numéro séquentiel
            try:
                last_number = int(last_devis.numero.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        # Formater avec 3 chiffres
        initial['numero'] = f"{prefix}-{next_number:03d}"
        
        return initial
    
    def form_valid(self, form):
        """Gère la création du devis avec ses articles"""
        try:
            print("=== DÉBUT CRÉATION DEVIS ===")
            print(f"Données du formulaire: {form.cleaned_data}")
            print(f"POST data: {self.request.POST}")
            
            # Sauvegarder le devis
            self.object = form.save()
            print(f"Devis créé avec ID: {self.object.id}")
            
            # Récupérer les données des articles depuis le formulaire
            articles_data = self.request.POST.get('articles_data')
            print(f"Articles data: {articles_data}")
            
            if articles_data:
                try:
                    import json
                    articles = json.loads(articles_data)
                    print(f"Articles parsés: {articles}")
                    
                    # Créer les lignes de devis avec gestion d'erreur robuste
                    for i, article in enumerate(articles):
                        try:
                            # Nettoyer et valider les données de manière robuste
                            quantite_str = str(article.get('quantite', '1')).strip()
                            prix_str = str(article.get('prix_unitaire_ht', '0')).strip()
                            
                            # Remplacer les virgules par des points et nettoyer
                            quantite_str = quantite_str.replace(',', '.').replace(' ', '')
                            prix_str = prix_str.replace(',', '.').replace(' ', '')
                            
                            # Validation et conversion sécurisée
                            try:
                                quantite = Decimal(quantite_str)
                                if quantite <= 0:
                                    quantite = Decimal('1.00')
                            except (ValueError, InvalidOperation):
                                quantite = Decimal('1.00')
                            
                            try:
                                prix_unitaire_ht = Decimal(prix_str)
                                if prix_unitaire_ht < 0:
                                    prix_unitaire_ht = Decimal('0.00')
                            except (ValueError, InvalidOperation):
                                prix_unitaire_ht = Decimal('0.00')
                            
                            # Créer la ligne avec des valeurs validées en utilisant save()
                            ligne = LigneDevis(
                                devis=self.object,
                                description=article.get('description', 'Article sans description'),
                                quantite=quantite,
                                unite=article.get('unite', 'unité'),
                                prix_unitaire_ht=prix_unitaire_ht
                            )
                            ligne.save()  # Utiliser save() pour déclencher la logique personnalisée
                            print(f"Ligne {i+1} créée: {ligne.id}")
                            
                        except Exception as e:
                            print(f"Erreur création ligne {i+1}: {e}")
                            # Créer une ligne avec des valeurs par défaut sécurisées
                            try:
                                ligne = LigneDevis(
                                    devis=self.object,
                                    description=article.get('description', 'Article sans description'),
                                    quantite=Decimal('1.00'),
                                    unite=article.get('unite', 'unité'),
                                    prix_unitaire_ht=Decimal('0.00')
                                )
                                ligne.save()  # Utiliser save() pour déclencher la logique personnalisée
                                print(f"Ligne {i+1} créée avec valeurs par défaut: {ligne.id}")
                            except Exception as e2:
                                print(f"Erreur critique création ligne {i+1}: {e2}")
                                # Supprimer le devis si on ne peut pas créer les lignes
                                self.object.delete()
                                messages.error(self.request, f'Erreur critique lors de la création des lignes de devis: {str(e2)}')
                                return self.form_invalid(form)
                    
                    # Forcer le recalcul des montants du devis
                    try:
                        # Rafraîchir l'objet depuis la base de données
                        self.object.refresh_from_db()
                        self.object.calculer_montants()
                        print(f"Montants recalculés: HT={self.object.montant_ht}, TVA={self.object.montant_tva}, TTC={self.object.montant_ttc}")
                    except Exception as e:
                        print(f"Erreur lors du calcul des montants: {e}")
                        # Continuer même si le calcul échoue
                        pass
                    
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Erreur JSON: {e}")
                    messages.error(self.request, f'Erreur lors du traitement des articles: {str(e)}')
                    return self.form_invalid(form)
                except Exception as e:
                    print(f"Erreur création lignes: {e}")
                    messages.error(self.request, f'Erreur lors de la création des lignes: {str(e)}')
                    return self.form_invalid(form)
            
            print("=== DEVIS CRÉÉ AVEC SUCCÈS ===")
            messages.success(self.request, 'Devis créé avec succès.')
            # Redirection FORCÉE vers la liste des devis
            return redirect('devis:devis_list')
            
        except Exception as e:
            print(f"Erreur générale: {e}")
            import traceback
            traceback.print_exc()
            messages.error(self.request, f'Erreur lors de la création du devis: {str(e)}')
            return self.form_invalid(form)

class DevisUpdateView(LoginRequiredMixin, UpdateView):
    """Vue pour modifier un devis"""
    model = Devis
    form_class = DevisForm
    template_name = 'devis/devis_form.html'
    success_url = reverse_lazy('devis:devis_list')
    
    def get_context_data(self, **kwargs):
        """Ajoute les articles existants au contexte"""
        context = super().get_context_data(**kwargs)
        if self.object:
            # Récupérer les articles existants pour les afficher dans le formulaire
            articles = []
            for ligne in self.object.lignes.all():
                articles.append({
                    'description': ligne.description,
                    'quantite': ligne.quantite,
                    'unite': ligne.unite,
                    'prix_unitaire_ht': ligne.prix_unitaire_ht,
                    'montant_ht': ligne.montant_ht
                })
            context['existing_articles'] = articles
        return context
    
    def form_valid(self, form):
        """Gère la mise à jour du devis avec ses articles"""
        # Récupérer l'objet existant avant la sauvegarde
        existing_devis = self.get_object()
        
        # Préserver les champs automatiques
        form.instance.date_creation = existing_devis.date_creation
        
        # Sauvegarder le devis en utilisant update_fields pour éviter de toucher aux champs automatiques
        # Récupérer seulement les champs du formulaire
        update_fields = []
        for field_name in form.fields.keys():
            if field_name != 'date_creation':  # Exclure les champs automatiques
                update_fields.append(field_name)
        
        # Sauvegarder avec update_fields
        self.object = form.save(commit=False)
        self.object.save(update_fields=update_fields)
        
        # Récupérer les données des articles depuis le formulaire
        articles_data = self.request.POST.get('articles_data')
        
        if articles_data:
            try:
                import json
                articles = json.loads(articles_data)
                
                # Supprimer les anciennes lignes
                self.object.lignes.all().delete()
                
                # Créer les nouvelles lignes de devis
                for article in articles:
                    # Convertir les valeurs numériques en Decimal avec validation
                    from decimal import Decimal, InvalidOperation
                    try:
                        # Nettoyer et valider les données
                        quantite_str = str(article.get('quantite', '1')).strip()
                        prix_str = str(article.get('prix_unitaire_ht', '0')).strip()
                        
                        # Remplacer les virgules par des points et nettoyer
                        quantite_str = quantite_str.replace(',', '.').replace(' ', '')
                        prix_str = prix_str.replace(',', '.').replace(' ', '')
                        
                        # Conversion en Decimal
                        quantite = Decimal(quantite_str)
                        prix_unitaire_ht = Decimal(prix_str)
                        
                        # Validation des valeurs
                        if quantite <= 0:
                            quantite = Decimal('1.00')
                        if prix_unitaire_ht < 0:
                            prix_unitaire_ht = Decimal('0.00')
                        
                        LigneDevis.objects.create(
                            devis=self.object,
                            description=article.get('description', 'Article sans description'),
                            quantite=quantite,
                            unite=article.get('unite', 'unité'),
                            prix_unitaire_ht=prix_unitaire_ht
                        )
                        
                    except (InvalidOperation, ValueError) as e:
                        print(f"Erreur conversion ligne: {e}")
                        print(f"Données problématiques: quantite='{article.get('quantite')}', prix='{article.get('prix_unitaire_ht')}'")
                        # Utiliser des valeurs par défaut sécurisées
                        LigneDevis.objects.create(
                            devis=self.object,
                            description=article.get('description', 'Article sans description'),
                            quantite=Decimal('1.00'),
                            unite=article.get('unite', 'unité'),
                            prix_unitaire_ht=Decimal('0.00')
                        )
                
                # Recalculer les montants du devis
                self.object.calculer_montants()
                
            except (json.JSONDecodeError, KeyError) as e:
                messages.error(self.request, f'Erreur lors du traitement des articles: {str(e)}')
                return self.form_invalid(form)
        
        messages.success(self.request, 'Devis modifié avec succès.')
        # Redirection FORCÉE vers la liste des devis
        return redirect('devis:devis_list')

class DevisDeleteView(LoginRequiredMixin, DeleteView):
    """Vue pour supprimer un devis"""
    model = Devis
    template_name = 'devis/devis_confirm_delete.html'
    success_url = reverse_lazy('devis:devis_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Devis supprimé avec succès.')
        return super().delete(request, *args, **kwargs)

@login_required
def devis_envoyer(request, pk):
    """Vue pour envoyer un devis"""
    devis = get_object_or_404(Devis, pk=pk)
    devis.envoyer()
    messages.success(request, f'Devis {devis.numero} envoyé avec succès.')
    return redirect('devis:devis_detail', pk=pk)

@login_required
def devis_accepter(request, pk):
    """Vue pour accepter un devis"""
    devis = get_object_or_404(Devis, pk=pk)
    devis.accepter()
    messages.success(request, f'Devis {devis.numero} accepté.')
    return redirect('devis:devis_detail', pk=pk)

@login_required
def devis_refuser(request, pk):
    """Vue pour refuser un devis"""
    devis = get_object_or_404(Devis, pk=pk)
    devis.refuser()
    messages.success(request, f'Devis {devis.numero} refusé.')
    return redirect('devis:devis_detail', pk=pk)

@login_required
def devis_dupliquer(request, pk):
    """Vue pour dupliquer un devis"""
    devis_original = get_object_or_404(Devis, pk=pk)
    
    # Créer un nouveau devis basé sur l'original
    nouveau_devis = Devis.objects.create(
        client=devis_original.client,
        objet=f"Copie - {devis_original.objet}",
        description=devis_original.description,
        taux_tva=devis_original.taux_tva,
        conditions_paiement=devis_original.conditions_paiement,
        date_validite=timezone.now().date() + timedelta(days=30)
    )
    
    # Copier les lignes
    for ligne in devis_original.lignes.all():
        LigneDevis.objects.create(
            devis=nouveau_devis,
            description=ligne.description,
            quantite=ligne.quantite,
            unite=ligne.unite,
            prix_unitaire_ht=ligne.prix_unitaire_ht
        )
    
    nouveau_devis.calculer_montants()
    messages.success(request, f'Devis dupliqué avec succès (nouveau numéro: {nouveau_devis.numero}).')
    return redirect('devis:devis_detail', pk=nouveau_devis.pk)

@login_required
def devis_dashboard(request):
    """Vue pour le tableau de bord des devis"""
    context = {
        'devis_total': Devis.objects.count(),
        'devis_envoyes': Devis.objects.filter(statut='envoye').count(),
        'devis_acceptes': Devis.objects.filter(statut='accepte').count(),
        'devis_refuses': Devis.objects.filter(statut='refuse').count(),
        'devis_recent': Devis.objects.all()[:10],
        'devis_en_retard': Devis.objects.filter(
            date_validite__lt=timezone.now().date(),
            statut__in=['brouillon', 'envoye']
        ),
    }
    return render(request, 'devis/devis_dashboard.html', context)

@login_required
def devis_imprimer(request, pk):
    """Vue pour imprimer un devis en PDF"""
    devis = get_object_or_404(Devis, pk=pk)
    
    # Récupérer les lignes du devis
    lignes = devis.lignes.all()
    
    # Contexte pour le template
    context = {
        'devis': devis,
        'lignes': lignes,
        'societe': get_societe_info()
    }
    
    try:
        # Générer le PDF avec ReportLab
        from .utils import generer_pdf_reportlab
        
        # Générer le PDF
        pdf_content = generer_pdf_reportlab(devis, lignes, get_societe_info(), mode='inline')
        
        # Réponse HTTP avec le PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="devis_{devis.numero}.pdf"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la génération du PDF: {str(e)}')
        return redirect('devis:devis_detail', pk=pk)

@login_required
def devis_telecharger(request, pk):
    """Vue pour télécharger un devis en PDF"""
    devis = get_object_or_404(Devis, pk=pk)
    
    # Récupérer les lignes du devis
    lignes = devis.lignes.all()
    
    # Contexte pour le template
    context = {
        'devis': devis,
        'lignes': lignes,
        'societe': get_societe_info()
    }
    
    try:
        # Générer le PDF avec ReportLab
        from .utils import generer_pdf_reportlab
        
        # Générer le PDF
        pdf_content = generer_pdf_reportlab(devis, lignes, get_societe_info(), mode='attachment')
        
        # Réponse HTTP avec le PDF en téléchargement
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="devis_{devis.numero}.pdf"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la génération du PDF: {str(e)}')
        return redirect('devis:devis_detail', pk=pk)

@login_required
def devis_apercu_ecran(request, pk):
    """Vue pour l'aperçu PDF d'un devis dans l'éditeur PDF du navigateur"""
    devis = get_object_or_404(Devis, pk=pk)
    
    # Récupérer les lignes du devis
    lignes = devis.lignes.all()
    
    # Contexte pour le template
    context = {
        'devis': devis,
        'lignes': lignes,
        'societe': get_societe_info(),
        'document_type': 'Devis'
    }
    
    # Rendre le template HTML
    html_content = render_to_string('devis/devis_print.html', context)
    
    # Créer une réponse avec le contenu HTML
    response = HttpResponse(html_content, content_type='text/html')
    response['Content-Disposition'] = f'inline; filename="devis_{devis.numero}.html"'
    
    return response

@login_required
def devis_delete_ajax(request, pk):
    """Vue AJAX pour supprimer un devis et retourner une réponse JSON"""
    if request.method == 'POST':
        try:
            devis = get_object_or_404(Devis, pk=pk)
            numero = devis.numero
            devis.delete()
            return JsonResponse({
                'success': True,
                'message': f'Devis {numero} supprimé avec succès.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de la suppression: {str(e)}'
            })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Méthode non autorisée.'
        })
