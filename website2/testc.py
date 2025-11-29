# -*- coding: utf-8 -*-
"""
Notebook de scraping Baniola.tn - Export XLSX
"""

import pandas as pd
import os
import glob
from prettytable import PrettyTable
from datetime import datetime

def afficher_tableau_lisible(csv_pattern="**/baniola_multi_modeles_*.csv"):
    """
    Affiche un tableau lisible et génère un fichier XLSX depuis les CSV trouvés.
    """

    # Trouver les fichiers CSV
    fichiers_csv = glob.glob(csv_pattern, recursive=True)
    if not fichiers_csv:
        print(f"Aucun fichier CSV trouvé avec le pattern '{csv_pattern}'.")
        return

    # Trier par date de modification (plus récent en premier)
    fichiers_csv.sort(key=os.path.getmtime, reverse=True)

    print(f"[+] {len(fichiers_csv)} fichier(s) CSV trouvé(s):")
    for f in fichiers_csv:
        print(f"    • {f}")

    # Charger tous les CSV
    all_data = []
    for csv_file in fichiers_csv:
        try:
            df = pd.read_csv(csv_file, encoding="utf-8-sig")
            print(f"    [+] {len(df)} lignes depuis {csv_file}")
            all_data.append(df)
        except Exception as e:
            print(f"    [!] Erreur lors du chargement de {csv_file}: {e}")

    if not all_data:
        print("Aucune donnée chargée.")
        return

    # Fusionner les DataFrames
    df_voitures = pd.concat(all_data, ignore_index=True)
    print(f"\n[OK] Total : {len(df_voitures)} voitures chargées.")

    # ──────────────────────────────────────────────
    # SUPPRIMER colonnes inutiles (tous formats possibles)
    colonnes_a_supprimer = [
        "Date de publication",
        "Date_publication",
        "date_publication",
        "datePublication",
        "Localisation"
    ]

    for col in colonnes_a_supprimer:
        if col in df_voitures.columns:
            print(f"[INFO] Suppression colonne : {col}")
            df_voitures.drop(columns=[col], inplace=True)

    # Garder explicitement la colonne Boîte de vitesses
    print("[INFO] Conservation explicite de la colonne Boîte de vitesses")

    # RENOMMER colonnes sans accents
    nouveaux_noms = {
        "Marque": "Marque",
        "Prix": "Prix",
        "Année": "Annee",
        "Kilométrage": "Kilometrage",
        "Carburant": "Carburant",
        "Boîte vitesse": "Boite vitesse",
        "Modèle": "Modele",
        "Puissance fiscale": "Puissance fiscale",
        "Nombre de portes": "Nombre de portes"
    }
    df_voitures.rename(columns=nouveaux_noms, inplace=True)
    # ──────────────────────────────────────────────

    # Colonnes à afficher
    cols_afficher = [
        "Marque", "Prix", "Annee", "Kilometrage",
        "Carburant", "Boite vitesse", "Modele",
        "Puissance fiscale", "Nombre de portes"
    ]

    cols_existantes = [col for col in cols_afficher if col in df_voitures.columns]

    # --- EXPORT EXCEL ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_excel = f"voitures_scrape_{timestamp}.xlsx"

    df_voitures.to_excel(nom_excel, index=False)
    print(f"[OK] Fichier Excel généré : {nom_excel}")

    # --- Affichage du tableau dans le terminal ---
    table = PrettyTable()
    table.field_names = cols_existantes

    for _, row in df_voitures.iterrows():
        row_data = []
        for col in cols_existantes:
            value = str(row[col]) if pd.notna(row[col]) else "N/A"
            if len(value) > 30:
                value = value[:27] + "..."
            row_data.append(value)
        table.add_row(row_data)

    table.align = "l"

    print("\n" + "="*100)
    print("RÉSULTATS DU SCRAPING (APERÇU)")
    print("="*100)
    print(table)

    print("\n" + "="*100)
    print("INFORMATIONS SUR LE DATASET")
    print("="*100)
    print(f"Nombre total de voitures : {len(df_voitures)}")
    print(f"Nombre de colonnes : {len(df_voitures.columns)}")
    print("Colonnes affichées :")
    for col in cols_existantes:
        print(f"  • {col}")

if __name__ == "__main__":
    afficher_tableau_lisible()
