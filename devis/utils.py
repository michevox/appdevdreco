"""
Utilitaires pour la gestion des devis
"""

def get_societe_info():
    """
    Retourne les informations de l'entreprise depuis les paramètres
    """
    try:
        from parametres.models import InformationsSociete
        societe = InformationsSociete.objects.first()
        if societe:
            return {
                'nom': societe.nom_raison_sociale,
                'adresse': societe.adresse,
                'ville': societe.ville,
                'telephone': societe.telephone_fixe or societe.telephone_portable,
                'email': societe.email,
                'site_web': societe.url_site,
                'logo': societe.logo.url if societe.logo else None,
                'en_tete_document': societe.en_tete_document,
                'pied_page_document': societe.pied_page_document,
            }
    except Exception:
        pass
    
    # Valeurs par défaut si pas de paramètres
    return {
        'nom': 'DEVDRECO SOFT',
        'adresse': '123 Avenue des Affaires',
        'ville': 'Conakry, Guinée',
        'telephone': '+224 123 45 67 89',
        'email': 'contact@devdreco-soft.com',
        'site_web': 'www.devdreco-soft.com',
        'logo': None,
        'en_tete_document': None,
        'pied_page_document': None,
    }

def format_montant(montant, devise=None):
    """
    Formate un montant avec la devise dynamique
    """
    if devise is None:
        from parametres.utils import get_symbole_monetaire
        devise = get_symbole_monetaire()
    
    if montant is None:
        return f"0,00 {devise}"
    
    try:
        montant_float = float(montant)
        return f"{montant_float:,.2f} {devise}".replace(',', ' ').replace('.', ',').replace(' ', '.')
    except (ValueError, TypeError):
        return f"0,00 {devise}"

def calculer_tva(montant_ht, taux_tva):
    """
    Calcule la TVA à partir du montant HT et du taux
    """
    try:
        montant_ht = float(montant_ht)
        taux_tva = float(taux_tva)
        return montant_ht * (taux_tva / 100)
    except (ValueError, TypeError):
        return 0.0

def calculer_ttc(montant_ht, taux_tva):
    """
    Calcule le montant TTC à partir du montant HT et du taux de TVA
    """
    try:
        montant_ht = float(montant_ht)
        tva = calculer_tva(montant_ht, taux_tva)
        return montant_ht + tva
    except (ValueError, TypeError):
        return 0.0

def generer_numero_devis(prefixe='DEV', date=None):
    """
    Génère un numéro de devis unique au format DEV-YYYYMMDD-XXX
    """
    from datetime import datetime
    from .models import Devis
    
    if date is None:
        date = datetime.now()
    
    # Format: DEV-YYYYMMDD-XXX
    prefix = f"{prefixe}-{date.strftime('%Y%m%d')}"
    
    # Trouver le dernier numéro du jour
    dernier_devis = Devis.objects.filter(
        numero__startswith=prefix
    ).order_by('numero').last()
    
    if dernier_devis:
        try:
            # Extraire le numéro séquentiel et l'incrémenter
            dernier_numero = int(dernier_devis.numero.split('-')[-1])
            nouveau_numero = dernier_numero + 1
        except (ValueError, IndexError):
            nouveau_numero = 1
    else:
        nouveau_numero = 1
    
    # Formater avec 3 chiffres
    return f"{prefix}-{nouveau_numero:03d}"

def valider_devis(devis):
    """
    Valide un devis et retourne les erreurs éventuelles
    """
    erreurs = []
    
    # Vérifications de base
    if not devis.client:
        erreurs.append("Le client est obligatoire")
    
    if not devis.objet:
        erreurs.append("L'objet du devis est obligatoire")
    
    if not devis.date_validite:
        erreurs.append("La date de validité est obligatoire")
    
    if devis.date_validite and devis.date_validite < devis.date_creation:
        erreurs.append("La date de validité ne peut pas être antérieure à la date de création")
    
    # Vérifications des lignes
    if not devis.lignes.exists():
        erreurs.append("Le devis doit contenir au moins une ligne")
    
    # Vérifications financières
    if devis.montant_ht < 0:
        erreurs.append("Le montant HT ne peut pas être négatif")
    
    if devis.taux_tva < 0 or devis.taux_tva > 100:
        erreurs.append("Le taux de TVA doit être compris entre 0 et 100%")
    
    return erreurs

def envoyer_devis_email(devis, destinataire=None):
    """
    Envoie le devis par email (à implémenter selon vos besoins)
    """
    if destinataire is None:
        destinataire = devis.client.email
    
    if not destinataire:
        return False, "Aucune adresse email disponible"
    
    # Ici, vous pouvez implémenter l'envoi d'email
    # avec Django ou une autre bibliothèque
    # Par exemple avec django.core.mail
    
    return True, "Email envoyé avec succès"

def exporter_devis_excel(devis):
    """
    Exporte le devis en format Excel (à implémenter selon vos besoins)
    """
    # Ici, vous pouvez implémenter l'export Excel
    # avec openpyxl ou xlsxwriter
    
    return None, "Export Excel non encore implémenté"

def generer_pdf_reportlab(devis, lignes, societe, mode='inline'):
    """
    Génère un PDF avec ReportLab basé sur l'image de référence devis.png
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from io import BytesIO
    from datetime import datetime
    
    # Créer un buffer pour le PDF
    buffer = BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Styles basés sur l'image de référence
    styles = getSampleStyleSheet()
    
    # Couleurs de l'image de référence
    orange_primary = colors.HexColor('#ff6b35')
    orange_light = colors.HexColor('#ffb366')
    gray_dark = colors.HexColor('#2c3e50')
    gray_accent = colors.HexColor('#34495e')
    gray_light = colors.HexColor('#f8f9fa')
    
    # Style pour le titre principal
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=5,
        alignment=TA_CENTER,
        textColor=colors.black
    )
    
    # Style pour les informations
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6
    )
    
    # Style pour le texte normal
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Style pour les totaux
    total_style = ParagraphStyle(
        'TotalStyle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_RIGHT
    )
    
    # Style pour le total TTC
    total_ttc_style = ParagraphStyle(
        'TotalTTCStyle',
        parent=styles['Normal'],
        fontSize=16,
        spaceAfter=6,
        alignment=TA_RIGHT,
        textColor=colors.white,
        backColor=colors.black,
        borderPadding=10
    )
    
    # Fonction pour dessiner l'en-tête avec image
    def draw_header(canvas, doc):
        canvas.saveState()
        try:
            from parametres.models import InformationsSociete
            soc = InformationsSociete.objects.first()
            if soc and hasattr(soc, 'bandeau_entete') and soc.bandeau_entete:
                try:
                    from reportlab.lib.utils import ImageReader
                    img = ImageReader(soc.bandeau_entete.path)
                    # Dessiner l'image en haut de la page (pleine largeur, hauteur 100px)
                    canvas.drawImage(img, 0, A4[1] - 100, width=A4[0], height=100, preserveAspectRatio=False, mask='auto')
                except Exception:
                    pass
        except Exception:
            pass
        canvas.restoreState()
    
    # Fonction pour dessiner le pied de page avec image
    def draw_footer(canvas, doc):
        canvas.saveState()
        try:
            from parametres.models import InformationsSociete
            from reportlab.lib.utils import ImageReader
            import os
            
            soc = InformationsSociete.objects.first()
            
            # Dessiner le bandeau de pied de page s'il existe
            if soc and hasattr(soc, 'bandeau_pied') and soc.bandeau_pied:
                try:
                    img = ImageReader(soc.bandeau_pied.path)
                    # Dessiner l'image en bas de la page (pleine largeur, hauteur 80px)
                    canvas.drawImage(img, 0, 0, width=A4[0], height=80, preserveAspectRatio=False, mask='auto')
                except Exception:
                    pass
            
            # Ajouter le cachet DEVDRECO
            try:
                # Chemin absolu vers l'image du cachet
                from django.conf import settings
                media_root = getattr(settings, 'MEDIA_ROOT', 'media')
                cachet_path = os.path.join(media_root, 'cachets_signatures', 'cachet_devdreco.png')
                
                # Dimensions du cachet (encore plus grande)
                cachet_width = 6*cm
                cachet_height = 6*cm
                
                # Position du cachet (en bas à droite, un peu plus haut et plus à gauche)
                cachet_x = A4[0] - cachet_width - 2.5*cm  # 2.5cm de marge droite (plus à gauche)
                cachet_y = 2.5*cm  # 2.5cm du bas (plus haut)
                
                # Dessiner le cachet s'il existe
                if os.path.exists(cachet_path):
                    try:
                        cachet_img = ImageReader(cachet_path)
                        canvas.drawImage(
                            cachet_img, 
                            cachet_x, 
                            cachet_y, 
                            width=cachet_width, 
                            height=cachet_height, 
                            preserveAspectRatio=True, 
                            mask='auto'
                        )
                    except Exception:
                        # En cas d'erreur avec l'image, dessiner un rectangle de test
                        canvas.setFillColorRGB(0.8, 0.8, 0.8)
                        canvas.rect(cachet_x, cachet_y, cachet_width, cachet_height, fill=1)
                        canvas.setFillColorRGB(0, 0, 0)
                        canvas.drawString(cachet_x + 0.5*cm, cachet_y + 1*cm, "CACHET")
                
                # Ajouter les textes superposés sur le cachet
                try:
                    # Configuration du texte
                    canvas.setFont("Helvetica-Bold", 10)
                    canvas.setFillColorRGB(1, 1, 1)  # Blanc pour contraster avec le cachet
                    
                    # Position des textes (superposés sur le cachet)
                    text_x = cachet_x + (cachet_width / 2)  # Centre du cachet
                    text_y_haut = cachet_y + (cachet_height * 0.8)  # Dans la partie haute du cachet
                    text_y_bas = cachet_y + (cachet_height * 0.2)  # Dans la partie basse du cachet
                    
                    # Texte "Directeur général" (dans la partie haute du cachet)
                    canvas.drawCentredText(text_x, text_y_haut, "Directeur général")
                    
                    # Texte "M. Mensah Kodjo Amélio" (dans la partie basse du cachet)
                    canvas.setFont("Helvetica", 8)  # Police plus petite
                    canvas.drawCentredText(text_x, text_y_bas, "M. Mensah Kodjo Amélio")
                    
                except Exception:
                    # En cas d'erreur avec le texte, continuer sans
                    pass
                    
            except Exception:
                # En cas d'erreur générale, continuer sans le cachet/signature
                pass
                
        except Exception:
            pass
        canvas.restoreState()
    
    # Contenu du PDF basé sur l'image de référence
    story = []
    
    # Espace pour l'en-tête (sera rempli par l'image)
    story.append(Spacer(1, 2*cm))
    
    # Les informations de l'entreprise sont supprimées du PDF
    
    # Informations du devis et client (structure de l'image)
    left_card = [
        [Paragraph('<b>N° Devis</b> : ' + devis.numero, info_style)],
        [Paragraph('<b>Date</b> : ' + devis.date_creation.strftime('%d/%m/%Y'), info_style)],
        [Paragraph('<b>Validité</b> : ' + devis.date_validite.strftime('%d/%m/%Y'), info_style)],
        [Paragraph('<b>Statut</b> : ' + devis.get_statut_display(), info_style)],
    ]
    right_card = [
        [Paragraph('<b>Client</b> : ' + (devis.client.nom_complet or ''), info_style)],
        [Paragraph('<b>Téléphone</b> : ' + (devis.client.telephone or ''), info_style)],
        [Paragraph('<b>Adresse</b> : ' + (devis.client.adresse or ''), info_style)],
        [Paragraph('<b>Type de client</b> : ' + (devis.client.get_type_client_display() if hasattr(devis.client, 'get_type_client_display') else ''), info_style)],
    ]

    left_table = Table(left_card, colWidths=[8*cm])
    left_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))

    right_table = Table(right_card, colWidths=[8*cm])
    right_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))

    cards = Table([[left_table, right_table]], colWidths=[8*cm, 8*cm])
    cards.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))

    story.append(cards)
    story.append(Spacer(1, 16))
    
    # Objet du devis
    if devis.objet:
        story.append(Paragraph(f"<b>Objet :</b> {devis.objet}", info_style))
        story.append(Spacer(1, 10))
    
    # Titre principal
    story.append(Paragraph("DEVIS QUANTITATIF ET ESTIMATIF", title_style))
    story.append(Spacer(1, 20))
    
    # Tableau des articles (sans lignes de catégories)
    if lignes:
        # En-têtes du tableau avec retours à la ligne
        # Créer un style spécial pour les en-têtes
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=normal_style,
            fontSize=9,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        table_data = [[
            Paragraph('Désignation', header_style),
            Paragraph('Quantité', header_style),
            Paragraph('Unité', header_style),
            Paragraph('Prix unitaire HT<br/>(GNF)', header_style),
            Paragraph('Montant total HT<br/>(GNF)', header_style)
        ]]
        
        # Styles pour centrer les quantités et unités
        center_style = ParagraphStyle(
            'CenterStyle',
            parent=normal_style,
            alignment=TA_CENTER
        )
        
        # Style pour aligner à droite les prix et montants
        right_style = ParagraphStyle(
            'RightStyle',
            parent=normal_style,
            alignment=TA_RIGHT
        )
        
        # Ajouter toutes les lignes d'articles avec retours automatiques à la ligne
        for ligne in lignes:
            # Formater les montants sans décimales ni symbole monétaire
            prix_unitaire = f"{ligne.prix_unitaire_ht:,.0f}".replace(',', '.')
            montant_total = f"{ligne.montant_ht:,.0f}".replace(',', '.')
            
            # Formater la quantité sans décimales
            quantite = f"{ligne.quantite:,.0f}".replace(',', '.')
            
            # Utiliser Paragraph pour permettre les retours automatiques à la ligne
            table_data.append([
                Paragraph(ligne.description, normal_style),
                Paragraph(quantite, center_style),
                Paragraph(ligne.unite, center_style),
                Paragraph(prix_unitaire, right_style),
                Paragraph(montant_total, right_style)
            ])
        
        # Ligne TOTAL générale avec cellule fusionnée
        total_general = sum(ligne.montant_ht for ligne in lignes)
        total_formate = f"{total_general:,.0f}".replace(',', '.')
        
        # Style pour le montant total en gras et centré
        total_style = ParagraphStyle(
            'TotalStyle',
            parent=normal_style,
            fontSize=11,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        # Style pour le mot "TOTAL" en gras et orange
        total_word_style = ParagraphStyle(
            'TotalWordStyle',
            parent=normal_style,
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=orange_primary,
            alignment=TA_CENTER
        )
        
        table_data.append([
            Paragraph('TOTAL', total_word_style),
            Paragraph(total_formate, total_style),
            '', '', ''
        ])
        
        # Créer le tableau avec des largeurs de colonnes appropriées
        article_table = Table(table_data, colWidths=[6*cm, 2*cm, 2*cm, 3.5*cm, 3.5*cm])
        
        # Style du tableau avec retours automatiques à la ligne
        table_style = [
            # En-tête principal (fond noir, texte blanc)
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Articles (fond blanc, texte noir)
            ('BACKGROUND', (0, 1), (-2, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-2, -1), colors.black),
            ('ALIGN', (0, 1), (0, -2), 'LEFT'),  # Désignation
            ('ALIGN', (1, 1), (1, -2), 'CENTER'),  # Quantité (centrée en largeur)
            ('ALIGN', (2, 1), (2, -2), 'CENTER'),  # Unité (centrée en largeur)
            ('ALIGN', (3, 1), (3, -2), 'RIGHT'),  # Prix
            ('ALIGN', (4, 1), (4, -2), 'RIGHT'),  # Total
            
            # Ligne TOTAL (fond blanc, "TOTAL" en orange, montant en noir)
            ('BACKGROUND', (0, -1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, -1), (0, -1), orange_primary),  # "TOTAL" en orange
            ('TEXTCOLOR', (1, -1), (4, -1), colors.black),  # Autres cellules en noir
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, -1), (0, -1), 'LEFT'),  # "TOTAL"
            ('ALIGN', (1, -1), (4, -1), 'CENTER'),  # Montant centré dans les 4 dernières colonnes
            ('SPAN', (1, -1), (4, -1)),  # Fusionner les 4 dernières cellules
            
            # Bordures pour tout le tableau
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding pour éviter le débordement et permettre les retours à la ligne
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            
            # Hauteur minimale des cellules pour permettre les retours à la ligne
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white]),
        ]
        
        # Appliquer tous les styles
        article_table.setStyle(TableStyle(table_style))
        
        story.append(article_table)
        story.append(Spacer(1, 20))
    
    # Section totaux (style de l'image de référence)
    story.append(Spacer(1, 20))
    
    # Créer les données pour les totaux
    sous_total = f"{devis.montant_ht:,.0f}".replace(',', '.') + 'GNF'
    tva_montant = f"{devis.montant_tva:,.0f}".replace(',', '.') + 'GNF'
    total_ttc = f"{devis.montant_ttc:,.0f}".replace(',', '.') + 'GNF'
    
    totaux_data = [
        ['Sous-total HT :', sous_total],
        [f'TVA ({devis.taux_tva}%) :', tva_montant],
        ['Total TTC :', total_ttc],
    ]
    
    # Créer le tableau des totaux
    totaux_table = Table(totaux_data, colWidths=[8*cm, 4*cm])
    totaux_table.setStyle(TableStyle([
        # Style général
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Labels à gauche
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Valeurs à droite
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Padding pour l'espacement
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        
        # Style pour les deux premières lignes (fond blanc, texte noir)
        ('BACKGROUND', (0, 0), (-1, 1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
        
        # Style pour la ligne Total TTC (fond noir, texte blanc)
        ('BACKGROUND', (0, 2), (-1, 2), colors.black),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.white),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (-1, 2), 11),
    ]))
    
    story.append(totaux_table)
    story.append(Spacer(1, 30))
    
    # Pied de page (si pas d'image)
    if not societe.get('pied_page_document'):
        footer_text = f"Devis généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} - {societe['nom']}"
        story.append(Paragraph(footer_text, normal_style))
    
    # Construire le PDF avec en-têtes et pieds de page
    def on_page(canvas, doc):
        draw_header(canvas, doc)
        draw_footer(canvas, doc)
    
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    
    # Récupérer le contenu du PDF
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content