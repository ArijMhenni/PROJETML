import pandas as pd
import os
import glob
from prettytable import PrettyTable

def afficher_tableau_lisible(csv_pattern="baniola_*.csv"):
    """
    Affiche un tableau lisible des données de voitures depuis des CSV
    Charge tous les fichiers CSV correspondant au pattern
    """
    # Trouver tous les fichiers CSV baniola
    fichiers_csv = glob.glob(csv_pattern)
    if not fichiers_csv:
        print(f"Aucun fichier CSV trouvé avec le pattern '{csv_pattern}'.")
        return

    # Trier par date de modification (plus récent en premier)
    fichiers_csv.sort(key=os.path.getmtime, reverse=True)

    print(f"[+] {len(fichiers_csv)} fichier(s) CSV trouvé(s):")
    for f in fichiers_csv:
        print(f"    * {f}")

    # Charger et combiner tous les CSV
    all_data = []
    for csv_file in fichiers_csv:
        try:
            df = pd.read_csv(csv_file, encoding="utf-8-sig")
            print(f"    [+] {len(df)} lignes depuis {csv_file}")
            all_data.append(df)
        except Exception as e:
            print(f"    [!] Erreur lors du chargement de {csv_file}: {e}")
            continue

    if not all_data:
        print("Aucune donnée chargée.")
        return

    # Combiner tous les DataFrames
    df_voitures = pd.concat(all_data, ignore_index=True)
    print(f"\n[OK] Total: {len(df_voitures)} voitures depuis {len(all_data)} fichiers")

    # Colonnes importantes à afficher (sans URL si présente)
    cols_afficher = ["Marque", "Prix", "Année", "Kilométrage", "Carburant", "Boîte vitesse", "Modèle", "Puissance fiscale", "Nombre de portes"]

    # Vérifier quelles colonnes existent
    cols_existantes = [col for col in cols_afficher if col in df_voitures.columns]

    if not cols_existantes:
        print("Aucune colonne pertinente trouvée dans le CSV.")
        return

    # Créer le tableau PrettyTable
    table = PrettyTable()

    # Définir les noms des colonnes
    table.field_names = cols_existantes

    # Ajouter les données ligne par ligne
    for _, row in df_voitures.iterrows():
        row_data = []
        for col in cols_existantes:
            value = str(row[col]) if pd.notna(row[col]) else "N/A"
            # Tronquer les valeurs trop longues pour la lisibilité
            if len(value) > 30:
                value = value[:27] + "..."
            row_data.append(value)
        table.add_row(row_data)

    # Configuration du tableau
    table.align = "l"  # Alignement à gauche
    table.border = True
    table.header = True
    table.padding_width = 1

    # Afficher le tableau
    print("\n" + "="*100)
    print(f"RÉSULTATS DU SCRAPING - {len(fichiers_csv)} fichiers CSV")
    print("="*100)
    print(table)

    print("\n" + "="*100)
    print("INFORMATIONS SUR LE DATASET")
    print("="*100)
    print(f"Nombre de voitures: {len(df_voitures)}")
    print(f"Nombre de colonnes: {len(df_voitures.columns)}")
    print(f"\nColonnes affichées :")
    for col in cols_existantes:
        print(f"  • {col}")

# Exécution
if __name__ == "__main__":
    afficher_tableau_lisible()
