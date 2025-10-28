from .models import ParametresGeneraux, InformationsSociete

def parametres_globaux(request):
    """
    Contexte global pour rendre les paramètres disponibles dans tous les templates
    """
    try:
        # Récupérer les paramètres généraux
        parametres = ParametresGeneraux.objects.first()
        if not parametres:
            # Créer des paramètres par défaut si aucun n'existe
            parametres = ParametresGeneraux.objects.create(
                symbole_monetaire='GNF',
                nom_application='DEVDRECO SOFT',
                elements_par_page=20,
                format_date='d/m/Y',
                notifications_email=True,
                notifications_sms=False
            )
        
        # Récupérer les informations de la société
        infos_societe = InformationsSociete.objects.first()
        if not infos_societe:
            # Créer des informations par défaut si aucune n'existe
            infos_societe = InformationsSociete.objects.create(
                nom_raison_sociale='DEVDRECO SOFT',
                pays='Guinée',
                ville='Conakry'
            )
        
        return {
            'PARAMETRES_GLOBAUX': {
                'symbole_monetaire': parametres.symbole_monetaire,
                'nom_application': parametres.nom_application,
                'elements_par_page': parametres.elements_par_page,
                'format_date': parametres.format_date,
                'notifications_email': parametres.notifications_email,
                'notifications_sms': parametres.notifications_sms,
            },
            'INFOS_SOCIETE': {
                'nom_raison_sociale': infos_societe.nom_raison_sociale,
                'telephone_fixe': infos_societe.telephone_fixe,
                'telephone_portable': infos_societe.telephone_portable,
                'email': infos_societe.email,
                'adresse': infos_societe.adresse,
                'ville': infos_societe.ville,
                'pays': infos_societe.pays,
                'url_site': infos_societe.url_site,
                'logo': infos_societe.logo,
                'en_tete_document': infos_societe.en_tete_document,
                'pied_page_document': infos_societe.pied_page_document,
                'numero_registre_commerce': infos_societe.numero_registre_commerce,
                'numero_contribuable': infos_societe.numero_contribuable,
            }
        }
        
    except Exception as e:
        # En cas d'erreur, retourner des valeurs par défaut
        return {
            'PARAMETRES_GLOBAUX': {
                'symbole_monetaire': 'GNF',
                'nom_application': 'DEVDRECO SOFT',
                'elements_par_page': 20,
                'format_date': 'd/m/Y',
                'notifications_email': True,
                'notifications_sms': False,
            },
            'INFOS_SOCIETE': {
                'nom_raison_sociale': 'DEVDRECO SOFT',
                'pays': 'Guinée',
                'ville': 'Conakry',
            }
        }
