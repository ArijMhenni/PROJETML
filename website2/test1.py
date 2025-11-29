# -*- coding: utf-8 -*-
"""
Notebook de scraping Baniola.tn - Peugeot 208 à Ariana
Adapté depuis SparkAuto scraper
"""

# ============================================================================
# 1. IMPORTS
# ============================================================================
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from datetime import datetime
import re
import unicodedata

def clean_text(text):
    """Nettoie le texte : enlève les accents et les emojis"""
    if not isinstance(text, str):
        return text
    # Enlever les accents
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('ascii')
    # Enlever les emojis (caractères non-ASCII)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text

# ============================================================================
# 2. CONFIGURATION DU DRIVER
# ============================================================================
def setup_driver():
    """Configure et initialise le driver Selenium"""
    chrome_options = Options()
    # Décommenter pour mode headless
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-gpu')
    
    # Options pour éviter la détection
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Masquer l'indicateur webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.set_page_load_timeout(30)
    
    return driver

# ============================================================================
# 3. FONCTIONS D'EXTRACTION
# ============================================================================
def wait_for_element(driver, by, value, timeout=10):
    """Attend qu'un élément soit présent sur la page"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except:
        return None

def extract_text_safe(driver, selector, by=By.CSS_SELECTOR):
    """Extrait le texte d'un élément de manière sécurisée"""
    try:
        element = driver.find_element(by, selector)
        return element.text.strip() if element else 'N/A'
    except:
        return 'N/A'

def extract_car_details_baniola(driver, url):
    """
    Extrait tous les détails d'une voiture depuis Baniola
    Adapté pour la structure HTML de Baniola
    """
    try:
        print(f"  [*] Chargement de la page...")
        driver.get(url)
        
        # Attendre le chargement
        time.sleep(3)
        
        # Attendre l'élément principal (titre)
        wait_for_element(driver, By.CSS_SELECTOR, "h1.fw-bold", timeout=15)
        
        car_data = {}
        
        # ==================== TITRE ====================
        print("  [+] Extraction du titre...")
        try:
            titre_elem = driver.find_element(By.CSS_SELECTOR, 'h1.fw-bold')
            car_data['Titre'] = titre_elem.text.strip()
            # Extraire la marque du titre (premier mot)
            car_data['Marque'] = car_data['Titre'].split()[0] if car_data['Titre'] != 'N/A' else 'N/A'
            print(f"      Titre: {car_data['Titre']}")
            print(f"      Marque extraite: {car_data['Marque']}")
        except Exception as e:
            print(f"      [!] Erreur titre: {e}")
            car_data['Titre'] = 'N/A'
            car_data['Marque'] = 'N/A'
        
        # ==================== PRIX ====================
        print("  [+] Extraction du prix...")
        try:
            prix_elem = driver.find_element(By.CLASS_NAME, 'announcement-pricing-container')
            prix = prix_elem.text.strip().replace('\n', ' ').replace('Négociable', '').strip()
            car_data['Prix'] = prix
            print(f"      Prix: {car_data['Prix']}")
        except Exception as e:
            print(f"      [!] Erreur prix: {e}")
            car_data['Prix'] = 'N/A'
        
        # ==================== LOCALISATION ====================
        print("  [+] Extraction de la localisation...")
        try:
            # Chercher dans le footer ou les éléments de localisation
            localisation_elements = driver.find_elements(By.XPATH, "//i[contains(@class, 'fa-map-marker-alt')]/parent::*")
            if localisation_elements:
                car_data['Localisation'] = localisation_elements[0].text.strip()
            else:
                car_data['Localisation'] = 'Ariana'
            print(f"      Localisation: {car_data['Localisation']}")
        except:
            car_data['Localisation'] = 'Ariana'
        
        # ==================== DATE PUBLICATION ====================
        try:
            date_elements = driver.find_elements(By.XPATH, "//i[contains(@class, 'fa-calendar-alt')]/parent::*")
            if date_elements:
                car_data['Date_publication'] = date_elements[0].text.strip()
            else:
                car_data['Date_publication'] = 'N/A'
        except:
            car_data['Date_publication'] = 'N/A'
        
        # ==================== SPÉCIFICATIONS TECHNIQUES ====================
        print("  [+] Extraction des specifications...")
        try:
            spec_lines = driver.find_elements(By.CLASS_NAME, "spec-line")
            
            print(f"      Nombre de specs trouvees: {len(spec_lines)}")
            
            spec_count = 0
            for spec_line in spec_lines:
                try:
                    spec_name = spec_line.find_element(By.CLASS_NAME, "spec-name").text.strip()
                    spec_data = spec_line.find_element(By.CLASS_NAME, "spec-data").text.strip()
                    
                    if spec_name and spec_data:
                        car_data[spec_name] = spec_data
                        spec_count += 1
                        print(f"      - {spec_name}: {spec_data}")
                        
                except Exception as e:
                    continue
            
            print(f"      Total specs extraites: {spec_count}")
            
        except Exception as e:
            print(f"      [!] Erreur specifications: {e}")
        
        # ==================== DESCRIPTION ====================
        print("  [+] Extraction de la description...")
        try:
            # Essayer de trouver un element plus specifique pour la description
            description_element = driver.find_element(By.CSS_SELECTOR, ".announcement-description, .description, [class*='description']")
            description = description_element.text.strip()
            # Nettoyer le texte : supprimer les numeros de telephone et "Voir plus"
            description = re.sub(r'\d{8,}', '', description)  # Supprimer les numeros de 8 chiffres ou plus
            description = re.sub(r'Voir plus.*', '', description, flags=re.IGNORECASE).strip()
            if len(description) > 500:
                description = description[:500] + "..."
            car_data['Description'] = description
        except:
            # Fallback vers la methode precedente si le selecteur specifique echoue
            sections = driver.find_elements(By.TAG_NAME, "section")
            description = "Non disponible"
            for section in sections:
                section_text = section.text
                if "Description" in section_text or "description" in section_text:
                    description = section_text.split("Description")[-1].strip()
                    # Nettoyer le texte
                    description = re.sub(r'\d{8,}', '', description)
                    description = re.sub(r'Voir plus.*', '', description, flags=re.IGNORECASE).strip()
                    if len(description) > 500:
                        description = description[:500] + "..."
                    break
            car_data['Description'] = description
        
        # ==================
        #== URL ====================
        car_data['URL'] = url
        
        # ==================== RÉSUMÉ ====================
        print(f"\n  [OK] EXTRACTION TERMINEE")
        print(f"      - Titre: {car_data.get('Titre', 'N/A')}")
        print(f"      - Prix: {car_data.get('Prix', 'N/A')}")
        print(f"      - Localisation: {car_data.get('Localisation', 'N/A')}")
        print(f"      - Marque: {car_data.get('Marque', 'N/A')}")
        print(f"      - Modele: {car_data.get('Modèle', 'N/A')}")
        print(f"      - Annee: {car_data.get('Année', 'N/A')}")
        print(f"      - Caracteristiques: {len([k for k in car_data.keys() if k not in ['Titre', 'Description', 'Prix', 'Localisation', 'Date_publication', 'URL']])}")
        
        return car_data
        
    except Exception as e:
        print(f"  [!] Erreur generale: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================================================
# 4. RÉCUPÉRATION DES LIENS
# ============================================================================
def get_car_links_from_baniola(driver, base_url, max_cars=None, max_pages=1):
    """
    Récupère les liens des voitures depuis Baniola
    max_cars: nombre maximum de voitures à récupérer (None = toutes)
    max_pages: nombre maximum de pages à scraper (défaut = 1)
    """
    all_car_links = []

    try:
        print(f"\n[*] Recuperation des liens depuis {base_url}...")
        if max_cars:
            print(f"    Limite: {max_cars} voitures maximum")
        print(f"    Pages: {max_pages} page(s) maximum")

        for page in range(1, max_pages + 1):
            if max_cars and len(all_car_links) >= max_cars:
                break

            # Construire l'URL de la page
            if page == 1:
                page_url = base_url
            else:
                page_url = f"{base_url}?page={page}"

            print(f"\n[*] Chargement de la page {page}: {page_url}")
            driver.get(page_url)
            time.sleep(3)

            # Trouver toutes les cartes d'annonces
            try:
                annonces = driver.find_elements(By.CLASS_NAME, "annonce-card")

                print(f"[+] Page {page}: {len(annonces)} annonce(s) trouvee(s)")

                if len(annonces) == 0:
                    print(f"[!] Page {page} vide, arrêt de la pagination")
                    break

                for idx, annonce in enumerate(annonces):
                    # Vérifier si on a atteint la limite
                    if max_cars and len(all_car_links) >= max_cars:
                        break

                    try:
                        # Récupérer le lien
                        link_elem = annonce.find_element(By.CLASS_NAME, "ad-link")
                        href = link_elem.get_attribute('href')

                        if href and href not in all_car_links:
                            all_car_links.append(href)

                    except Exception as e:
                        print(f"    [!] Erreur extraction lien page {page}, annonce {idx+1}: {e}")
                        continue

            except Exception as e:
                print(f"[!] Erreur lors de l'extraction des annonces page {page}: {e}")
                continue

        print(f"\n[OK] Total: {len(all_car_links)} lien(s) unique(s) trouve(s) sur {page} page(s)")
        return all_car_links

    except Exception as e:
        print(f"[!] Erreur generale: {e}")
        import traceback
        traceback.print_exc()
        return all_car_links

# ============================================================================
# 5. FONCTION PRINCIPALE DE SCRAPING
# ============================================================================
def scrape_baniola(base_url, max_cars=10, max_pages=1):
    """
    Fonction principale pour scraper Baniola
    base_url: URL de la page de recherche
    max_cars: nombre maximum de voitures à scraper
    max_pages: nombre maximum de pages à scraper
    """
    print(f"\n{'='*80}")
    print(f"DEBUT DU SCRAPING BANIOLA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    print(f"URL: {base_url}")
    print(f"Limite: {max_cars} voitures, {max_pages} pages")
    print()

    driver = None
    cars_data = []

    try:
        # Initialiser le driver
        print("[*] Configuration du WebDriver...")
        driver = setup_driver()
        print("[OK] WebDriver configure\n")

        # Récupérer les liens de toutes les voitures
        car_urls = get_car_links_from_baniola(driver, base_url, max_cars, max_pages)
        
        if not car_urls:
            print("[!] Aucun lien de voiture trouve")
            return pd.DataFrame()
        
        # Extraire les détails de chaque voiture
        for i, url in enumerate(car_urls, 1):
            print(f"\n{'='*80}")
            print(f"[{i}/{len(car_urls)}] Traitement: {url}")
            print(f"{'='*80}")
            
            car_details = extract_car_details_baniola(driver, url)
            
            if car_details:
                cars_data.append(car_details)
                print(f"  [OK] Voiture ajoutee")
            else:
                print(f"  [!] Echec de l'extraction")
            
            # Pause entre les requêtes
            if i < len(car_urls):
                time.sleep(2)
        
    except Exception as e:
        print(f"\n[!] Erreur generale: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Fermer le driver
        if driver:
            driver.quit()
            print("\n[*] WebDriver ferme")
    
    # Créer le DataFrame
    if cars_data:
        df = pd.DataFrame(cars_data)
        print(f"\n[OK] Scraping termine! {len(cars_data)} voiture(s) extraite(s)")

        # Nettoyer les données : enlever accents, emojis, URLs et remplacer Titre par Marque
        if 'URL' in df.columns:
            df = df.drop(columns=['URL'])
        if 'Titre' in df.columns:
            df = df.drop(columns=['Titre'])

        # Appliquer le nettoyage à toutes les colonnes textuelles
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(clean_text)

        return df
    else:
        print("\n[!] Aucune donnee extraite")
        return pd.DataFrame()

# ============================================================================
# 6. NETTOYAGE ET TRANSFORMATION DES DONNÉES
# ============================================================================
def clean_dataframe(df):
    """Nettoie et transforme les données"""
    if df.empty:
        return df
    
    df_clean = df.copy()
    
    # Nettoyer le prix
    if 'Prix' in df_clean.columns:
        df_clean['Prix_Numeric'] = pd.to_numeric(
            df_clean['Prix'].astype(str).str.replace(' ', '').str.replace(',', '').str.replace('DT', '').str.replace('TND', ''),
            errors='coerce'
        )
    
    # Nettoyer le kilométrage
    if 'Kilométrage' in df_clean.columns:
        df_clean['Kilométrage_Numeric'] = pd.to_numeric(
            df_clean['Kilométrage'].astype(str).str.replace(' ', '').str.replace('Km', '').str.replace('km', ''),
            errors='coerce'
        )
    
    # Extraire l'année
    if 'Année' in df_clean.columns:
        df_clean['Année_Numeric'] = pd.to_numeric(df_clean['Année'], errors='coerce')
    
    return df_clean

# ============================================================================
# 7. SCRAPING D'URLs SPÉCIFIQUES
# ============================================================================
def scrape_specific_cars(driver, car_urls):
    """
    Scrape des voitures spécifiques depuis leurs URLs individuelles
    """
    cars_data = []

    for i, url in enumerate(car_urls, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(car_urls)}] SCRAPING URL SPÉCIFIQUE: {url}")
        print(f"{'='*80}")

        car_details = extract_car_details_baniola(driver, url)

        if car_details:
            cars_data.append(car_details)
            print(f"  [OK] Voiture ajoutée")
        else:
            print(f"  [!] Échec de l'extraction")

        # Pause entre les requêtes
        if i < len(car_urls):
            time.sleep(2)

    return cars_data

# ============================================================================
# 8. EXÉCUTION DU SCRAPING
# ============================================================================

# Liste des URLs de base pour différents modèles de voitures
base_urls = [
    "https://baniola.tn/voitures/marques/Peugeot",  # Peugeot 208 à Ariana
    "https://baniola.tn/voitures/marques/Suzuki/Spresso",     # Suzuki Spresso
    "https://baniola.tn/voitures/marques/Kia/Rio",             # Kia Rio
    "https://baniola.tn/voitures/marques/Dacia",               # Toutes les Dacia
    "https://baniola.tn/voitures/marques/Volkswagen",          # Toutes les Volkswagen
    "https://baniola.tn/voitures/marques/Land-Rover",          # Toutes les Land Rover
    "https://baniola.tn/voitures/marques/Citroen",             # Toutes les Citroën
    "https://baniola.tn/voitures/marques/Fiat",                # Toutes les Fiat
    "https://baniola.tn/voitures/marques/Sympol",              # Toutes les Sympol
    "https://baniola.tn/voitures/marques/MG",                  # Toutes les MG
    "https://baniola.tn/voitures/marques/Audi"                 # Toutes les Audi
]

# URLs spécifiques de voitures à scraper individuellement
specific_car_urls = []

# Scraper toutes les voitures pour chaque modèle
print("\n" + "="*80)
print("LANCEMENT DU SCRAPING MULTI-MODÈLES")
print("="*80)

all_cars_data = []

# Scraper depuis les pages de recherche
for base_url in base_urls:
    print(f"\n{'='*100}")
    print(f"SCRAPING POUR: {base_url}")
    print(f"{'='*100}")
    df_model = scrape_baniola(base_url, max_cars=None, max_pages=5)
    if not df_model.empty:
        all_cars_data.append(df_model)

# Scraper les voitures spécifiques
if specific_car_urls:
    print(f"\n{'='*100}")
    print(f"SCRAPING DE {len(specific_car_urls)} VOITURES SPÉCIFIQUES")
    print(f"{'='*100}")

    driver = setup_driver()
    try:
        specific_cars_data = scrape_specific_cars(driver, specific_car_urls)

        if specific_cars_data:
            df_specific = pd.DataFrame(specific_cars_data)

            # Nettoyer les données
            if 'URL' in df_specific.columns:
                df_specific = df_specific.drop(columns=['URL'])
            if 'Titre' in df_specific.columns:
                df_specific = df_specific.drop(columns=['Titre'])

            # Appliquer le nettoyage à toutes les colonnes textuelles
            for col in df_specific.columns:
                if df_specific[col].dtype == 'object':
                    df_specific[col] = df_specific[col].apply(clean_text)

            all_cars_data.append(df_specific)
            print(f"\n[OK] {len(specific_cars_data)} voitures spécifiques ajoutées")
    finally:
        driver.quit()

# Combiner tous les DataFrames
if all_cars_data:
    df_voitures = pd.concat(all_cars_data, ignore_index=True)
else:
    df_voitures = pd.DataFrame()

# ============================================================================
# 8. AFFICHAGE DES RÉSULTATS
# ============================================================================
if not df_voitures.empty:
    print("\n" + "="*80)
    print("RESULTATS DU SCRAPING")
    print("="*80)
    print(df_voitures)
    
    print("\n" + "="*80)
    print("INFORMATIONS SUR LE DATASET")
    print("="*80)
    print(f"Nombre de voitures: {len(df_voitures)}")
    print(f"Nombre de colonnes: {len(df_voitures.columns)}")
    print(f"\nColonnes extraites:")
    for col in df_voitures.columns:
        print(f"  * {col}")
    
    # Nettoyage des données
    print("\n" + "="*80)
    print("NETTOYAGE DES DONNEES")
    print("="*80)
    df_clean = clean_dataframe(df_voitures)
    print("[OK] Donnees nettoyees")
    
    # Statistiques
    print("\n" + "="*80)
    print("STATISTIQUES DESCRIPTIVES")
    print("="*80)
    
    if 'Prix_Numeric' in df_clean.columns:
        print("\n[*] STATISTIQUES SUR LES PRIX:")
        print(f"    Prix moyen    : {df_clean['Prix_Numeric'].mean():,.0f} DT")
        print(f"    Prix minimum  : {df_clean['Prix_Numeric'].min():,.0f} DT")
        print(f"    Prix maximum  : {df_clean['Prix_Numeric'].max():,.0f} DT")
        print(f"    Prix median   : {df_clean['Prix_Numeric'].median():,.0f} DT")
    
    if 'Kilométrage_Numeric' in df_clean.columns:
        print("\n[*] STATISTIQUES SUR LE KILOMETRAGE:")
        print(f"    KM moyen      : {df_clean['Kilométrage_Numeric'].mean():,.0f} Km")
        print(f"    KM minimum    : {df_clean['Kilométrage_Numeric'].min():,.0f} Km")
        print(f"    KM maximum    : {df_clean['Kilométrage_Numeric'].max():,.0f} Km")
    
    # Sauvegarde
    print("\n" + "="*80)
    print("SAUVEGARDE DES DONNEES")
    print("="*80)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # CSV
    csv_filename = f"baniola_multi_modeles_{timestamp}.csv"
    df_voitures.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    print(f"[OK] CSV sauvegarde: {csv_filename}")

    # Excel
    try:
        excel_filename = f"baniola_multi_modeles_{timestamp}.xlsx"
        df_voitures.to_excel(excel_filename, index=False, engine='openpyxl')
        print(f"[OK] Excel sauvegarde: {excel_filename}")
    except:
        print("[!] Installation d'openpyxl necessaire pour Excel")
    
    print("\n" + "="*80)
    print("SCRAPING TERMINE AVEC SUCCES")
    print("="*80)
else:
    print("\n[!] Aucune donnee extraite")