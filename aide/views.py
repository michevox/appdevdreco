from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class AideIndexView(LoginRequiredMixin, TemplateView):
    """Page d'accueil de l'aide"""
    template_name = 'aide/index.html'

class AideUtilisationView(LoginRequiredMixin, TemplateView):
    """Guide d'utilisation"""
    template_name = 'aide/utilisation.html'

class AideFaqView(LoginRequiredMixin, TemplateView):
    """FAQ - Questions fréquemment posées"""
    template_name = 'aide/faq.html'

class AideContactView(LoginRequiredMixin, TemplateView):
    """Contact et support"""
    template_name = 'aide/contact.html'

class AideAProposView(LoginRequiredMixin, TemplateView):
    """À propos de l'application"""
    template_name = 'aide/a_propos.html'

@login_required
def aide_recherche(request):
    """Recherche dans l'aide"""
    query = request.GET.get('q', '')
    context = {
        'query': query,
        'results': []
    }
    
    # Ici on pourrait implémenter une recherche dans la documentation
    # Pour l'instant, on retourne une page simple
    return render(request, 'aide/recherche.html', context)