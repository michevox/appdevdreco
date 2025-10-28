"""
Utilitaires pour la gestion des bons de commande
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

def generer_pdf_commande(commande, lignes, societe, mode='inline'):
    """
    Génère un PDF avec ReportLab pour un bon de commande
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
    
    # Informations du bon de commande et client (structure de l'image)
    left_card = [
        [Paragraph('<b>N° Bon de Commande</b> : ' + commande.numero, info_style)],
        [Paragraph('<b>Date</b> : ' + commande.date_creation.strftime('%d/%m/%Y'), info_style)],
        [Paragraph('<b>Type</b> : ' + commande.get_type_commande_display(), info_style)],
        [Paragraph('<b>Objet</b> : ' + commande.objet, info_style)],
    ]
    right_card = [
        [Paragraph('<b>Client/Fournisseur</b> : ' + (commande.client.nom_complet if commande.client else commande.fournisseur.nom_complet if commande.fournisseur else ''), info_style)],
        [Paragraph('<b>Téléphone</b> : ' + (commande.client.telephone if commande.client else commande.fournisseur.telephone if commande.fournisseur else ''), info_style)],
        [Paragraph('<b>Adresse</b> : ' + (commande.client.adresse if commande.client else commande.fournisseur.adresse if commande.fournisseur else ''), info_style)],
        [Paragraph('<b>Date livraison</b> : ' + commande.date_livraison_souhaitee.strftime('%d/%m/%Y'), info_style)],
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

    # Tableau des deux cartes côte à côte
    info_table = Table([[left_table, right_table]], colWidths=[8*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Titre de la section articles
    story.append(Paragraph('<b>Articles commandés</b>', title_style))
    story.append(Spacer(1, 10))
    
    # Tableau des lignes de commande
    if lignes:
        # En-têtes du tableau
        table_data = [['Description', 'Quantité', 'Unité', 'Prix unitaire HT', 'Montant HT']]
        
        # Lignes de données
        for ligne in lignes:
            table_data.append([
                ligne.description,
                str(ligne.quantite),
                ligne.unite,
                f"{ligne.prix_unitaire_ht:.2f}",
                f"{ligne.montant_ht:.2f}"
            ])
        
        # Créer le tableau
        table = Table(table_data, colWidths=[6*cm, 2*cm, 2*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            # Style général
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
    else:
        story.append(Paragraph('<i>Aucune ligne de commande</i>', normal_style))
    
    story.append(Spacer(1, 20))
    
    # Tableau des totaux
    totaux_data = [
        ['Montant HT', f"{commande.montant_ht:.2f}"],
        [f'TVA ({commande.taux_tva}%)', f"{commande.montant_tva:.2f}"],
        ['Total TTC', f"{commande.montant_ttc:.2f}"],
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
        footer_text = f"Bon de commande généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} - {societe['nom']}"
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
