from django import template
from django.template.defaultfilters import floatformat
from ..utils import formater_montant, formater_montant_avec_decimaux, get_symbole_monetaire
from utilisateurs.utils import user_has_permission, user_has_module_permission

register = template.Library()

@register.filter
def format_montant(montant, decimales=2):
    """
    Filtre pour formater un montant avec le symbole monétaire
    
    Usage dans template:
    {{ montant|format_montant }}
    {{ montant|format_montant:0 }}  # Sans décimales
    """
    if montant is None:
        symbole = get_symbole_monetaire()
        return f"0 {symbole}"
    
    try:
        if decimales == 0:
            return formater_montant(montant)
        else:
            return formater_montant_avec_decimaux(montant, decimales=decimales)
    except:
        symbole = get_symbole_monetaire()
        return f"0 {symbole}"

@register.filter
def format_montant_simple(montant):
    """
    Filtre pour formater un montant sans décimales
    
    Usage dans template:
    {{ montant|format_montant_simple }}
    """
    return formater_montant(montant)

@register.filter
def format_montant_decimal(montant, decimales=2):
    """
    Filtre pour formater un montant avec décimales
    
    Usage dans template:
    {{ montant|format_montant_decimal }}
    {{ montant|format_montant_decimal:1 }}  # 1 décimale
    """
    return formater_montant_avec_decimaux(montant, decimales=decimales)

@register.simple_tag
def get_symbole():
    """
    Tag pour récupérer le symbole monétaire actuel
    
    Usage dans template:
    {% get_symbole as symbole %}
    Le symbole actuel est: {{ symbole }}
    """
    return get_symbole_monetaire()

@register.simple_tag
def get_symbole_monetaire_tag():
    """
    Tag pour récupérer le symbole monétaire actuel (alias)
    """
    return get_symbole_monetaire()

@register.filter
def format_prix(prix, unite=""):
    """
    Filtre pour formater un prix avec unité et symbole monétaire
    
    Usage dans template:
    {{ prix|format_prix:"par kg" }}
    """
    if prix is None:
        symbole = get_symbole_monetaire()
        return f"0 {symbole} {unite}".strip()
    
    try:
        montant_formate = formater_montant_avec_decimaux(prix, decimales=2)
        if unite:
            return f"{montant_formate} {unite}"
        return montant_formate
    except:
        symbole = get_symbole_monetaire()
        return f"0 {symbole} {unite}".strip()

@register.filter
def format_quantite(quantite, unite=""):
    """
    Filtre pour formater une quantité avec unité
    
    Usage dans template:
    {{ quantite|format_quantite:"kg" }}
    """
    if quantite is None:
        return f"0 {unite}".strip()
    
    try:
        if isinstance(quantite, str):
            quantite = float(quantite.replace(',', '.'))
        
        # Formater avec 2 décimales maximum
        if quantite == int(quantite):
            quantite_str = str(int(quantite))
        else:
            quantite_str = floatformat(quantite, 2)
        
        if unite:
            return f"{quantite_str} {unite}"
        return quantite_str
    except:
        return f"0 {unite}".strip()

@register.filter
def currency_symbol():
    """
    Filtre pour récupérer uniquement le symbole monétaire
    
    Usage dans template:
    {{ montant|currency_symbol }}
    """
    return get_symbole_monetaire()

@register.filter
def format_currency(montant, decimales=2):
    """
    Alias pour format_montant (compatibilité internationale)
    
    Usage dans template:
    {{ montant|format_currency }}
    """
    return format_montant(montant, decimales)

@register.filter
def format_montant_compact(montant):
    """
    Formate un montant de manière compacte (ex: 1K, 1M)
    
    Usage dans template:
    {{ montant|format_montant_compact }}
    """
    if montant is None:
        symbole = get_symbole_monetaire()
        return f"0 {symbole}"
    
    try:
        montant = float(montant)
        symbole = get_symbole_monetaire()
        
        if montant >= 1000000:
            return f"{montant/1000000:.1f}M {symbole}"
        elif montant >= 1000:
            return f"{montant/1000:.1f}K {symbole}"
        else:
            return f"{montant:,.0f} {symbole}"
    except:
        symbole = get_symbole_monetaire()
        return f"0 {symbole}"

@register.simple_tag
def get_parametres():
    """
    Tag pour récupérer tous les paramètres globaux
    
    Usage dans template:
    {% get_parametres as params %}
    Symbole: {{ params.symbole_monetaire }}
    """
    from ..utils import get_parametres_globaux
    return get_parametres_globaux()

# Filtres de permissions
@register.filter
def has_permission(user, permission_code):
    """
    Filtre pour vérifier si un utilisateur a une permission spécifique
    
    Usage dans template:
    {% if user|has_permission:"clients.view" %}
        <a href="{% url 'clients:client_list' %}">Clients</a>
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    return user_has_permission(user, permission_code)

@register.filter
def has_module_permission(user, module_action):
    """
    Filtre pour vérifier si un utilisateur a une permission pour un module et une action
    
    Usage dans template:
    {% if user|has_module_permission:"clients.view" %}
        <a href="{% url 'clients:client_list' %}">Clients</a>
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        module, action = module_action.split('.')
        return user_has_module_permission(user, module, action)
    except (ValueError, AttributeError):
        return False

@register.filter
def can_view_module(user, module):
    """
    Filtre pour vérifier si un utilisateur peut voir un module (permission view)
    
    Usage dans template:
    {% if user|can_view_module:"clients" %}
        <a href="{% url 'clients:client_list' %}">Clients</a>
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    return user_has_module_permission(user, module, 'view')

@register.filter
def can_add_module(user, module):
    """
    Filtre pour vérifier si un utilisateur peut ajouter dans un module
    
    Usage dans template:
    {% if user|can_add_module:"clients" %}
        <button>Ajouter un client</button>
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    return user_has_module_permission(user, module, 'add')

@register.filter
def can_change_module(user, module):
    """
    Filtre pour vérifier si un utilisateur peut modifier dans un module
    
    Usage dans template:
    {% if user|can_change_module:"clients" %}
        <button>Modifier</button>
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    return user_has_module_permission(user, module, 'change')

@register.filter
def can_delete_module(user, module):
    """
    Filtre pour vérifier si un utilisateur peut supprimer dans un module
    
    Usage dans template:
    {% if user|can_delete_module:"clients" %}
        <button>Supprimer</button>
    {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    return user_has_module_permission(user, module, 'delete')
