# -*- coding: utf-8 -*-
"""
Nettoyage et Préparation des Données Baniola
Pour entraînement de modèle de prédiction de prix
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
import unicodedata

# ============================================================================
# 1. CHARGEMENT DES DONNÉES
# ============================================================================
print("="*80)
print("CHARGEMENT DES DONNÉES")
print("="*80)

# Charger votre dataset (remplacez par le nom de votre fichier)
# df = pd.read_csv("baniola_peugeot_208_20231128_123456.csv", encoding='utf-8-sig')
# Ou si vous avez déjà le DataFrame en mémoire, utilisez directement df_voitures

# Pour cet exemple, je suppose que vous avez déjà df_voitures
# df = df_voitures.copy()

# Si vous chargez depuis un fichier:
import glob
fichiers = glob.glob("baniola_*.csv")
if fichiers:
    dernier_fichier = max(fichiers)
    print(f"Chargement de: {dernier_fichier}")
    df = pd.read_csv(dernier_fichier, encoding='utf-8-sig')
else:
    # Essayer de charger depuis un fichier Excel
    fichiers_excel = glob.glob("voitures_scrape_*.xlsx")
    if fichiers_excel:
        dernier_fichier_excel = max(fichiers_excel)
        print(f"Chargement de: {dernier_fichier_excel}")
        df = pd.read_excel(dernier_fichier_excel, engine='openpyxl')
    else:
        print("Aucun fichier CSV ou Excel trouvé. Veuillez vérifier les fichiers de données.")
        exit(1)

print(f"Nombre de lignes: {len(df)}")
print(f"Nombre de colonnes: {len(df.columns)}")
print(f"\nColonnes disponibles:")
print(df.columns.tolist())

# ============================================================================
# 2. ANALYSE INITIALE
# ============================================================================
print("\n" + "="*80)
print("ANALYSE INITIALE")
print("="*80)

print("\nPremières lignes:")
print(df.head())

print("\nInformations générales:")
print(df.info())

print("\nValeurs manquantes:")
print(df.isnull().sum())

print("\nValeurs manquantes (%):")
print((df.isnull().sum() / len(df) * 100).round(2))

# ============================================================================
# 3. FONCTIONS DE NETTOYAGE
# ============================================================================

def clean_prix(prix_str):
    """Nettoie et convertit le prix en numérique"""
    if pd.isna(prix_str):
        return np.nan
    
    prix_str = str(prix_str)
    # Enlever les espaces, virgules, et texte
    prix_str = prix_str.replace(' ', '').replace(',', '')
    prix_str = re.sub(r'DT|TND|dt|tnd|Négociable|négociable', '', prix_str, flags=re.IGNORECASE)
    prix_str = prix_str.strip()
    
    # Extraire le nombre
    match = re.search(r'\d+', prix_str)
    if match:
        try:
            return float(match.group())
        except:
            return np.nan
    return np.nan

def clean_kilometrage(km_str):
    """Nettoie et convertit le kilométrage en numérique"""
    if pd.isna(km_str):
        return np.nan
    
    km_str = str(km_str)
    # Enlever les espaces, points, virgules, et texte
    km_str = km_str.replace(' ', '').replace('.', '').replace(',', '')
    km_str = re.sub(r'Km|km|KM|kilomètres|kilometres', '', km_str, flags=re.IGNORECASE)
    km_str = km_str.strip()
    
    # Extraire le nombre
    match = re.search(r'\d+', km_str)
    if match:
        try:
            return float(match.group())
        except:
            return np.nan
    return np.nan

def clean_annee(annee_str):
    """Nettoie et convertit l'année en numérique"""
    if pd.isna(annee_str):
        return np.nan
    
    annee_str = str(annee_str)
    # Extraire les 4 chiffres de l'année
    match = re.search(r'\b(19\d{2}|20\d{2})\b', annee_str)
    if match:
        try:
            annee = int(match.group())
            # Vérifier que l'année est raisonnable
            if 1980 <= annee <= datetime.now().year + 1:
                return annee
        except:
            pass
    return np.nan

def clean_puissance_fiscale(pf_str):
    """Extrait la puissance fiscale"""
    if pd.isna(pf_str):
        return np.nan
    
    pf_str = str(pf_str)
    # Chercher le nombre suivi de CV
    match = re.search(r'(\d+)\s*(?:CV|cv|Ch)', pf_str, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except:
            return np.nan
    return np.nan

def clean_cylindree(cyl_str):
    """Extrait la cylindrée"""
    if pd.isna(cyl_str):
        return np.nan
    
    cyl_str = str(cyl_str)
    # Chercher le nombre (généralement en cm³)
    match = re.search(r'(\d+)', cyl_str)
    if match:
        try:
            return int(match.group(1))
        except:
            return np.nan
    return np.nan

def standardize_carburant(carb_str):
    """Standardise le type de carburant"""
    if pd.isna(carb_str):
        return 'Inconnu'
    
    carb_str = str(carb_str).lower().strip()
    
    if 'essence' in carb_str or 'gasoline' in carb_str:
        return 'Essence'
    elif 'diesel' in carb_str or 'gasoil' in carb_str or 'gazole' in carb_str:
        return 'Diesel'
    elif 'hybrid' in carb_str or 'hybride' in carb_str:
        return 'Hybride'
    elif 'electr' in carb_str or 'électr' in carb_str:
        return 'Electrique'
    elif 'gpl' in carb_str or 'lpg' in carb_str:
        return 'GPL'
    else:
        return 'Autre'

def standardize_boite(boite_str):
    """Standardise le type de boîte de vitesses - Garde NaN pour les valeurs manquantes"""
    if pd.isna(boite_str):
        return np.nan  # On garde NaN au lieu de 'Inconnu'
    
    boite_str = str(boite_str).lower().strip()
    
    if 'manuel' in boite_str or 'manual' in boite_str:
        return 'Manuelle'
    elif 'auto' in boite_str or 'automatique' in boite_str:
        return 'Automatique'
    elif 'semi' in boite_str or 'séquentiel' in boite_str:
        return 'Semi-automatique'
    else:
        return np.nan  # On retourne NaN pour les valeurs inconnues

def clean_marque(marque_str):
    """Nettoie et standardise la marque"""
    if pd.isna(marque_str):
        return 'Inconnu'
    
    marque_str = str(marque_str).strip().title()
    
    # Corrections spécifiques
    corrections = {
        'Bmw': 'BMW',
        'Mg': 'MG',
        'Gwm': 'GWM',
        'Byd': 'BYD',
        'Ds': 'DS',
        'Volkswagen': 'VW',
        'Mercedes': 'Mercedes-Benz'
    }
    
    return corrections.get(marque_str, marque_str)

def calculate_age(annee):
    """Calcule l'âge du véhicule"""
    if pd.isna(annee):
        return np.nan
    return datetime.now().year - annee

# ============================================================================
# 4. NETTOYAGE DES COLONNES PRINCIPALES
# ============================================================================
print("\n" + "="*80)
print("NETTOYAGE DES COLONNES")
print("="*80)

# Créer une copie pour le nettoyage
df_clean = df.copy()

# --- PRIX ---
print("\n[1/10] Nettoyage du Prix...")
if 'Prix' in df_clean.columns:
    df_clean['Prix_Clean'] = df_clean['Prix'].apply(clean_prix)
    print(f"  - Prix nettoyés: {df_clean['Prix_Clean'].notna().sum()}/{len(df_clean)}")
    print(f"  - Prix min: {df_clean['Prix_Clean'].min():.0f} DT")
    print(f"  - Prix max: {df_clean['Prix_Clean'].max():.0f} DT")
    print(f"  - Prix moyen: {df_clean['Prix_Clean'].mean():.0f} DT")
else:
    print("  - Colonne 'Prix' non trouvée")

# --- KILOMÉTRAGE ---
print("\n[2/10] Nettoyage du Kilométrage...")
if 'Kilométrage' in df_clean.columns or 'Kilometrage' in df_clean.columns:
    km_col = 'Kilométrage' if 'Kilométrage' in df_clean.columns else 'Kilometrage'
    df_clean['Kilometrage_Clean'] = df_clean[km_col].apply(clean_kilometrage)
    print(f"  - Kilométrages nettoyés: {df_clean['Kilometrage_Clean'].notna().sum()}/{len(df_clean)}")
    print(f"  - KM min: {df_clean['Kilometrage_Clean'].min():.0f} km")
    print(f"  - KM max: {df_clean['Kilometrage_Clean'].max():.0f} km")
    print(f"  - KM moyen: {df_clean['Kilometrage_Clean'].mean():.0f} km")
else:
    print("  - Colonne 'Kilométrage' non trouvée")

# --- ANNÉE ---
print("\n[3/10] Nettoyage de l'Année...")
if 'Année' in df_clean.columns or 'Annee' in df_clean.columns:
    annee_col = 'Année' if 'Année' in df_clean.columns else 'Annee'
    df_clean['Annee_Clean'] = df_clean[annee_col].apply(clean_annee)
    df_clean['Age_Vehicule'] = df_clean['Annee_Clean'].apply(calculate_age)
    print(f"  - Années nettoyées: {df_clean['Annee_Clean'].notna().sum()}/{len(df_clean)}")
    print(f"  - Année min: {df_clean['Annee_Clean'].min():.0f}")
    print(f"  - Année max: {df_clean['Annee_Clean'].max():.0f}")
    print(f"  - Âge moyen: {df_clean['Age_Vehicule'].mean():.1f} ans")
else:
    print("  - Colonne 'Année' non trouvée")

# --- MARQUE ---
print("\n[4/10] Nettoyage de la Marque...")
if 'Marque' in df_clean.columns:
    df_clean['Marque_Clean'] = df_clean['Marque'].apply(clean_marque)
    print(f"  - Marques nettoyées: {df_clean['Marque_Clean'].notna().sum()}/{len(df_clean)}")
    print(f"  - Nombre de marques uniques: {df_clean['Marque_Clean'].nunique()}")
    print(f"  - Top 5 marques:")
    print(df_clean['Marque_Clean'].value_counts().head())
else:
    print("  - Colonne 'Marque' non trouvée")

# --- MODÈLE ---
print("\n[5/10] Nettoyage du Modèle...")
if 'Modèle' in df_clean.columns or 'Model' in df_clean.columns:
    model_col = 'Modèle' if 'Modèle' in df_clean.columns else 'Model'
    df_clean['Modele_Clean'] = df_clean[model_col].astype(str).str.strip().str.title()
    print(f"  - Modèles nettoyés: {df_clean['Modele_Clean'].notna().sum()}/{len(df_clean)}")
    print(f"  - Nombre de modèles uniques: {df_clean['Modele_Clean'].nunique()}")
else:
    print("  - Colonne 'Modèle' non trouvée")

# --- CARBURANT ---
print("\n[6/10] Standardisation du Carburant...")
if 'Carburant' in df_clean.columns:
    df_clean['Carburant_Clean'] = df_clean['Carburant'].apply(standardize_carburant)
    print(f"  - Carburants standardisés: {df_clean['Carburant_Clean'].notna().sum()}/{len(df_clean)}")
    print(f"  - Distribution:")
    print(df_clean['Carburant_Clean'].value_counts())
else:
    print("  - Colonne 'Carburant' non trouvée")

# --- BOÎTE DE VITESSES ---
print("\n[7/10] Standardisation de la Boîte de vitesses...")
if 'Boîte de vitesses' in df_clean.columns or 'Boite de vitesses' in df_clean.columns or 'Boîte vitesse' in df_clean.columns:
    if 'Boîte de vitesses' in df_clean.columns:
        boite_col = 'Boîte de vitesses'
    elif 'Boite de vitesses' in df_clean.columns:
        boite_col = 'Boite de vitesses'
    else:
        boite_col = 'Boîte vitesse'
    df_clean['Boite_Clean'] = df_clean[boite_col].apply(standardize_boite)
    print(f"  - Boîtes standardisées: {df_clean['Boite_Clean'].notna().sum()}/{len(df_clean)}")
    print(f"  - Valeurs manquantes conservées: {df_clean['Boite_Clean'].isna().sum()}")
    print(f"  - Distribution:")
    print(df_clean['Boite_Clean'].value_counts(dropna=False))
else:
    print("  - Colonne 'Boîte de vitesses' non trouvée")

# --- PUISSANCE FISCALE ---
print("\n[8/10] Extraction de la Puissance fiscale...")
if 'Puissance fiscale' in df_clean.columns:
    df_clean['Puissance_Fiscale_Clean'] = df_clean['Puissance fiscale'].apply(clean_puissance_fiscale)
    print(f"  - Puissances extraites: {df_clean['Puissance_Fiscale_Clean'].notna().sum()}/{len(df_clean)}")
    if df_clean['Puissance_Fiscale_Clean'].notna().sum() > 0:
        print(f"  - Puissance min: {df_clean['Puissance_Fiscale_Clean'].min():.0f} CV")
        print(f"  - Puissance max: {df_clean['Puissance_Fiscale_Clean'].max():.0f} CV")
        print(f"  - Puissance moyenne: {df_clean['Puissance_Fiscale_Clean'].mean():.1f} CV")
else:
    print("  - Colonne 'Puissance fiscale' non trouvée")

# --- CYLINDRÉE ---
print("\n[9/10] Extraction de la Cylindrée...")
if 'Cylindrée' in df_clean.columns or 'Cylindree' in df_clean.columns:
    cyl_col = 'Cylindrée' if 'Cylindrée' in df_clean.columns else 'Cylindree'
    df_clean['Cylindree_Clean'] = df_clean[cyl_col].apply(clean_cylindree)
    print(f"  - Cylindrées extraites: {df_clean['Cylindree_Clean'].notna().sum()}/{len(df_clean)}")
    if df_clean['Cylindree_Clean'].notna().sum() > 0:
        print(f"  - Cylindrée min: {df_clean['Cylindree_Clean'].min():.0f} cm³")
        print(f"  - Cylindrée max: {df_clean['Cylindree_Clean'].max():.0f} cm³")
        print(f"  - Cylindrée moyenne: {df_clean['Cylindree_Clean'].mean():.0f} cm³")
else:
    print("  - Colonne 'Cylindrée' non trouvée")

# --- LOCALISATION ---
print("\n[10/10] Nettoyage de la Localisation...")
if 'Localisation' in df_clean.columns:
    df_clean['Localisation_Clean'] = df_clean['Localisation'].astype(str).str.strip().str.title()
    print(f"  - Localisations nettoyées: {df_clean['Localisation_Clean'].notna().sum()}/{len(df_clean)}")
    print(f"  - Nombre de localisations uniques: {df_clean['Localisation_Clean'].nunique()}")
    print(f"  - Top 5 localisations:")
    print(df_clean['Localisation_Clean'].value_counts().head())
else:
    print("  - Colonne 'Localisation' non trouvée")

# ============================================================================
# 5. SUPPRESSION DES OUTLIERS
# ============================================================================
print("\n" + "="*80)
print("SUPPRESSION DES OUTLIERS")
print("="*80)
print("Note: Les valeurs manquantes de 'Boîte de vitesses' sont conservées")

df_filtered = df_clean.copy()

# Supprimer les lignes avec prix manquant ou aberrant
if 'Prix_Clean' in df_filtered.columns:
    avant = len(df_filtered)
    df_filtered = df_filtered[df_filtered['Prix_Clean'].notna()]
    df_filtered = df_filtered[df_filtered['Prix_Clean'] > 1000]  # Prix minimum 1000 DT
    df_filtered = df_filtered[df_filtered['Prix_Clean'] < 500000]  # Prix maximum 500 000 DT
    apres = len(df_filtered)
    print(f"Prix: {avant} -> {apres} ({avant - apres} lignes supprimées)")

# Supprimer les lignes avec kilométrage aberrant
if 'Kilometrage_Clean' in df_filtered.columns:
    avant = len(df_filtered)
    df_filtered = df_filtered[df_filtered['Kilometrage_Clean'].notna()]
    df_filtered = df_filtered[df_filtered['Kilometrage_Clean'] >= 0]
    df_filtered = df_filtered[df_filtered['Kilometrage_Clean'] < 500000]  # Max 500 000 km
    apres = len(df_filtered)
    print(f"Kilométrage: {avant} -> {apres} ({avant - apres} lignes supprimées)")

# Supprimer les lignes avec année aberrante
if 'Annee_Clean' in df_filtered.columns:
    avant = len(df_filtered)
    df_filtered = df_filtered[df_filtered['Annee_Clean'].notna()]
    df_filtered = df_filtered[df_filtered['Annee_Clean'] >= 1980]
    df_filtered = df_filtered[df_filtered['Annee_Clean'] <= datetime.now().year + 1]
    apres = len(df_filtered)
    print(f"Année: {avant} -> {apres} ({avant - apres} lignes supprimées)")

# NOTE: On ne supprime PAS les lignes avec Boîte de vitesses manquante
print(f"Boîte de vitesses: Les valeurs manquantes sont conservées (pas de suppression)")

print(f"\nDonnées finales: {len(df_filtered)} lignes")

# ============================================================================
# 6. CRÉATION DU DATASET FINAL
# ============================================================================
print("\n" + "="*80)
print("CRÉATION DU DATASET FINAL")
print("="*80)

# Sélectionner les colonnes nettoyées
colonnes_finales = []

# Colonnes obligatoires pour le modèle
colonnes_mapping = {
    'Prix_Clean': 'Prix',
    'Marque_Clean': 'Marque',
    'Modele_Clean': 'Modele',
    'Annee_Clean': 'Annee',
    'Age_Vehicule': 'Age',
    'Kilometrage_Clean': 'Kilometrage',
    'Carburant_Clean': 'Carburant',
    'Boite_Clean': 'Boite_Vitesses',
    'Puissance_Fiscale_Clean': 'Puissance_Fiscale',
    'Cylindree_Clean': 'Cylindree'
}

# Créer le dataset final avec renommage
df_final = pd.DataFrame()
for col_clean, col_final in colonnes_mapping.items():
    if col_clean in df_filtered.columns:
        df_final[col_final] = df_filtered[col_clean]

print(f"Colonnes dans le dataset final: {list(df_final.columns)}")
print(f"Nombre de lignes: {len(df_final)}")

# ============================================================================
# 7. ANALYSE FINALE
# ============================================================================
print("\n" + "="*80)
print("ANALYSE DU DATASET FINAL")
print("="*80)

print("\nPremières lignes:")
print(df_final.head(10))

print("\nInformations:")
print(df_final.info())

print("\nStatistiques descriptives:")
print(df_final.describe())

print("\nValeurs manquantes:")
print(df_final.isnull().sum())

print("\nTaux de complétude par colonne:")
print(((df_final.notna().sum() / len(df_final)) * 100).round(2))

# ============================================================================
# 8. SAUVEGARDE
# ============================================================================
print("\n" + "="*80)
print("SAUVEGARDE DU DATASET NETTOYÉ")
print("="*80)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# CSV
csv_filename = f"baniola_clean_{timestamp}.csv"
df_final.to_csv(csv_filename, index=False, encoding='utf-8-sig')
print(f"[OK] CSV sauvegardé: {csv_filename}")

# Excel
try:
    excel_filename = f"baniola_clean_{timestamp}.xlsx"
    df_final.to_excel(excel_filename, index=False, engine='openpyxl')
    print(f"[OK] Excel sauvegardé: {excel_filename}")
except:
    print("[!] Installation d'openpyxl nécessaire pour Excel")

print("\n" + "="*80)
print("NETTOYAGE TERMINÉ AVEC SUCCÈS")
print("="*80)
print(f"Dataset final: {len(df_final)} lignes × {len(df_final.columns)} colonnes")
print(f"Prêt pour l'entraînement du modèle ML!")
print("="*80)