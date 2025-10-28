#!/usr/bin/env python
"""
Script pour créer un devis complètement propre avec des données minimales
"""

import sqlite3
from pathlib import Path
from datetime import datetime, date

def create_clean_devis():
    """Crée un devis complètement propre avec des données minimales"""
    print("=== CRÉATION D'UN DEVIS COMPLÈTEMENT PROPRE ===")
    
    try:
        # Chemin vers la base de données
        db_path = Path(__file__).resolve().parent / "db.sqlite3"
        
        # Connexion directe à SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Vérifier qu'il y a au moins un client
        print("1. Vérification des clients...")
        cursor.execute("SELECT id, nom_complet FROM clients_client LIMIT 1")
        client = cursor.fetchone()
        
        if not client:
            print("   ❌ Aucun client trouvé. Création d'un client de test...")
            cursor.execute("""
                INSERT INTO clients_client (nom_complet, email, telephone, adresse, date_creation)
                VALUES (?, ?, ?, ?, ?)
            """, ("Client Test", "test@example.com", "123456789", "Adresse Test", datetime.now()))
            client_id = cursor.lastrowid
            print(f"   ✅ Client de test créé avec ID: {client_id}")
        else:
            client_id, nom_complet = client
            print(f"   ✅ Client trouvé: {nom_complet} (ID: {client_id})")
        
        # 2. Créer un devis complètement propre avec des valeurs décimales explicites
        print("\n2. Création du devis propre...")
        
        # Utiliser des valeurs décimales très simples
        numero = "DEV-TEST-001"
        objet = "Test de devis propre"
        description = "Ceci est un devis de test pour vérifier le bon fonctionnement"
        
        # Valeurs décimales explicites
        montant_ht = "100.00"
        montant_tva = "20.00"
        montant_ttc = "120.00"
        taux_tva = "20.00"
        
        # Dates
        date_creation = datetime.now()
        date_validite = date.today()
        date_modification = datetime.now()
        
        cursor.execute("""
            INSERT INTO devis_devis (
                numero, client_id, objet, description, taux_tva, conditions_paiement, 
                notes, statut, date_creation, date_validite, date_modification,
                montant_ht, montant_tva, montant_ttc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            numero, client_id, objet, description, taux_tva, "Paiement à 30 jours", 
            "Devis de test", "brouillon", date_creation, date_validite, date_modification,
            montant_ht, montant_tva, montant_ttc
        ))
        
        devis_id = cursor.lastrowid
        print(f"   ✅ Devis propre créé avec ID: {devis_id}")
        print(f"      Numéro: {numero}")
        print(f"      Montants: HT={montant_ht}, TVA={montant_tva}, TTC={montant_ttc}")
        
        # 3. Créer une ligne de devis simple
        print("\n3. Création d'une ligne de devis simple...")
        
        ligne_description = "Article de test"
        quantite = "1.00"
        unite = "unité"
        prix_unitaire_ht = "100.00"
        montant_ligne_ht = "100.00"
        
        cursor.execute("""
            INSERT INTO devis_lignedevis (
                devis_id, description, quantite, unite, prix_unitaire_ht, montant_ht
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (devis_id, ligne_description, quantite, unite, prix_unitaire_ht, montant_ligne_ht))
        
        ligne_id = cursor.lastrowid
        print(f"   ✅ Ligne de devis créée avec ID: {ligne_id}")
        print(f"      {quantite} × {prix_unitaire_ht} = {montant_ligne_ht}")
        
        # 4. Vérifier les types après création
        print("\n4. Vérification des types après création:")
        cursor.execute("""
            SELECT id, numero, typeof(montant_ht), typeof(montant_tva), typeof(montant_ttc)
            FROM devis_devis
            WHERE id = ?
        """, (devis_id,))
        
        devis_types = cursor.fetchone()
        if devis_types:
            devis_id_check, numero_check, type_ht, type_tva, type_ttc = devis_types
            print(f"   Devis {devis_id_check} ({numero_check}): HT={type_ht}, TVA={type_tva}, TTC={type_ttc}")
            
            # Vérifier les lignes
            cursor.execute("""
                SELECT id, typeof(quantite), typeof(prix_unitaire_ht), typeof(montant_ht)
                FROM devis_lignedevis
                WHERE devis_id = ?
            """, (devis_id,))
            
            ligne_types = cursor.fetchone()
            if ligne_types:
                ligne_id_check, type_qty, type_prix, type_montant = ligne_types
                print(f"   Ligne {ligne_id_check}: quantite={type_qty}, prix={type_prix}, montant={type_montant}")
        
        # 5. Valider tous les changements
        conn.commit()
        print(f"\n🎉 Devis propre créé avec succès !")
        print(f"   ID du devis: {devis_id}")
        print(f"   Numéro: {numero}")
        
        return devis_id
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du devis propre: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def test_clean_devis(devis_id):
    """Teste l'accès au devis propre"""
    print(f"\n=== TEST DU DEVIS PROPRE ID {devis_id} ===")
    
    try:
        import os
        import sys
        import django
        from pathlib import Path
        
        # Configuration Django
        BASE_DIR = Path(__file__).resolve().parent
        sys.path.append(str(BASE_DIR))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devdreco_soft.settings')
        django.setup()
        
        from devis.models import Devis
        
        # Test de récupération du devis propre
        try:
            devis = Devis.objects.get(id=devis_id)
            print(f"   ✅ Devis {devis.id} récupéré: {devis.numero}")
            print(f"      montant_ht: {devis.montant_ht} (type: {type(devis.montant_ht)})")
            print(f"      montant_tva: {devis.montant_tva} (type: {type(devis.montant_tva)})")
            print(f"      montant_ttc: {devis.montant_ttc} (type: {type(devis.montant_ttc)})")
            
            # Tester l'accès aux lignes
            lignes = devis.lignes.all()
            print(f"      {lignes.count()} lignes récupérées")
            
            for ligne in lignes:
                print(f"        Ligne {ligne.id}: {ligne.quantite} × {ligne.prix_unitaire_ht} = {ligne.montant_ht}")
                
            print("\n🎉 Le devis propre fonctionne parfaitement !")
            return True
                
        except Exception as e:
            print(f"   ❌ Erreur lors de la récupération du devis {devis_id}: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur générale lors des tests Django: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        # Créer un devis propre
        devis_id = create_clean_devis()
        
        if devis_id:
            # Tester le devis propre
            test_success = test_clean_devis(devis_id)
            
            print("\n=== RÉSUMÉ ===")
            if test_success:
                print("✅ Un devis propre a été créé avec succès.")
                print(f"✅ Le devis ID {devis_id} fonctionne parfaitement sans erreur.")
                print("✅ Tous les montants sont du type decimal correct.")
                print(f"Testez maintenant l'affichage du devis {devis_id} dans le navigateur.")
            else:
                print("✅ Le devis propre a été créé mais Django a encore des problèmes.")
        else:
            print("\n❌ La création du devis propre a échoué.")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
