from decimal import Decimal
from .models import ParametresGeneraux

def get_symbole_monetaire():
    """
    Récupère le symbole monétaire actuel depuis les paramètres
    """
    try:
        parametres = ParametresGeneraux.objects.first()
        if parametres:
            return parametres.symbole_monetaire
        return 'GNF'  # Valeur par défaut
    except:
        return 'GNF'

def formater_montant(montant, symbole=None):
    """
    Formate un montant avec le symbole monétaire
    
    Args:
        montant: Montant à formater (Decimal, float, ou string)
        symbole: Symbole monétaire à utiliser (optionnel, utilise le symbole par défaut si non spécifié)
    
    Returns:
        String formaté (ex: "25 000 GNF")
    """
    if montant is None:
        return "0 GNF"
    
    try:
        # Récupérer le symbole monétaire
        if symbole is None:
            symbole = get_symbole_monetaire()
        
        # Convertir en Decimal avec validation robuste
        if isinstance(montant, str):
            # Nettoyer la chaîne
            montant_clean = montant.replace(',', '.').replace(' ', '').strip()
            if not montant_clean or montant_clean in ['', '.', '-', '+', 'nan', 'inf', '-inf', '+inf']:
                return f"0 {symbole}"
            try:
                montant = Decimal(montant_clean)
            except:
                return f"0 {symbole}"
        elif isinstance(montant, float):
            if not montant or montant != montant:  # Vérifier NaN
                return f"0 {symbole}"
            try:
                montant = Decimal(str(montant))
            except:
                return f"0 {symbole}"
        elif isinstance(montant, int):
            try:
                montant = Decimal(montant)
            except:
                return f"0 {symbole}"
        elif isinstance(montant, Decimal):
            # Vérifier si le Decimal est valide
            try:
                if montant.is_nan() or montant.is_infinite():
                    return f"0 {symbole}"
            except:
                return f"0 {symbole}"
        else:
            return f"0 {symbole}"
        
        # Formater le montant avec séparateurs de milliers
        try:
            montant_str = "{:,.0f}".format(montant).replace(',', ' ')
            return f"{montant_str} {symbole}"
        except:
            return f"0 {symbole}"
        
    except Exception as e:
        print(f"Erreur formatage montant '{montant}': {e}")
        return f"0 {symbole or 'GNF'}"

def formater_montant_avec_decimaux(montant, symbole=None, decimales=2):
    """
    Formate un montant avec décimales et le symbole monétaire
    
    Args:
        montant: Montant à formater
        symbole: Symbole monétaire à utiliser
        decimales: Nombre de décimales à afficher
    
    Returns:
        String formaté (ex: "25 000,50 GNF")
    """
    if montant is None:
        return "0,00 GNF"
    
    try:
        # Récupérer le symbole monétaire
        if symbole is None:
            symbole = get_symbole_monetaire()
        
        # Convertir en Decimal avec validation robuste
        if isinstance(montant, str):
            # Nettoyer la chaîne
            montant_clean = montant.replace(',', '.').replace(' ', '').strip()
            if not montant_clean or montant_clean in ['', '.', '-', '+', 'nan', 'inf', '-inf', '+inf']:
                return f"0,00 {symbole}"
            try:
                montant = Decimal(montant_clean)
            except:
                return f"0,00 {symbole}"
        elif isinstance(montant, float):
            if not montant or montant != montant:  # Vérifier NaN
                return f"0,00 {symbole}"
            try:
                montant = Decimal(str(montant))
            except:
                return f"0,00 {symbole}"
        elif isinstance(montant, int):
            try:
                montant = Decimal(montant)
            except:
                return f"0,00 {symbole}"
        elif isinstance(montant, Decimal):
            # Vérifier si le Decimal est valide
            try:
                if montant.is_nan() or montant.is_infinite():
                    return f"0,00 {symbole}"
            except:
                return f"0,00 {symbole}"
        else:
            return f"0,00 {symbole}"
        
        # Formater avec décimales
        try:
            format_pattern = f"{{:,.{decimales}f}}"
            montant_str = format_pattern.format(montant)
            
            # Remplacer la virgule par un espace pour les milliers et le point par une virgule pour les décimales
            if decimales > 0:
                # Séparer la partie entière et décimale
                parties = montant_str.split('.')
                partie_entiere = parties[0].replace(',', ' ')
                if len(parties) > 1:
                    montant_str = f"{partie_entiere},{parties[1]}"
                else:
                    montant_str = f"{partie_entiere},00"
            else:
                montant_str = montant_str.replace(',', ' ')
            
            return f"{montant_str} {symbole}"
        except:
            return f"0,00 {symbole}"
        
    except Exception as e:
        return f"0,00 {symbole or 'GNF'}"

def get_parametres_globaux():
    """
    Récupère tous les paramètres globaux
    """
    try:
        parametres = ParametresGeneraux.objects.first()
        if parametres:
            return {
                'symbole_monetaire': parametres.symbole_monetaire,
                'nom_application': parametres.nom_application,
                'elements_par_page': parametres.elements_par_page,
                'format_date': parametres.format_date,
                'notifications_email': parametres.notifications_email,
                'notifications_sms': parametres.notifications_sms,
            }
        return {
            'symbole_monetaire': 'GNF',
            'nom_application': 'DEVDRECO SOFT',
            'elements_par_page': 20,
            'format_date': 'd/m/Y',
            'notifications_email': True,
            'notifications_sms': False,
        }
    except:
        return {
            'symbole_monetaire': 'GNF',
            'nom_application': 'DEVDRECO SOFT',
            'elements_par_page': 20,
            'format_date': 'd/m/Y',
            'notifications_email': True,
            'notifications_sms': False,
        }
