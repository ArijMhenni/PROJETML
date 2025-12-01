"""
Car Price Predictor - Classe de prédiction du prix des véhicules
==================================================================

Ce module contient la classe CarPricePredictor qui encapsule toute la logique
de prédiction du prix des véhicules en utilisant le modèle Extra Trees.

Auteur: ML Project Team
Date: 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class CarPricePredictor:
    """
    Classe pour prédire le prix des véhicules en utilisant le modèle Extra Trees.
    
    Cette classe encapsule toute la logique de transformation des données et de prédiction,
    rendant le pipeline facile à réutiliser et à déployer.
    
    Attributes:
    -----------
    model : ExtraTreesRegressor
        Le modèle de prédiction chargé depuis le fichier pickle
    encoders : dict
        Dictionnaire contenant tous les encodeurs nécessaires
    marques_acceptees : list
        Liste des marques de véhicules acceptées
    luxury_brands : list
        Liste des marques de luxe
    brand_categories : dict
        Dictionnaire de catégorisation des marques
    
    Methods:
    --------
    predict(marque, modele, annee, kilometrage, energie, boite_vitesses, puissance_fiscale)
        Prédit le prix d'un véhicule
    predict_batch(vehicles_list)
        Prédit les prix pour une liste de véhicules
    get_vehicle_info(marque)
        Retourne les informations sur une marque
    
    Example:
    --------
    >>> predictor = CarPricePredictor()
    >>> result = predictor.predict('BMW', 'Série 3', 2021, 45000, 'Diesel', 'Automatique', 9)
    >>> print(f"Prix estimé: {result['prix_predit']:,.0f} DT")
    """
    
    def __init__(self, model_path='models/extra_trees_tuned.pkl', encoders_path='models/encoders.pkl'):
        """
        Initialise le prédicteur en chargeant le modèle et les encodeurs.
        
        Parameters:
        -----------
        model_path : str
            Chemin vers le fichier pickle du modèle
        encoders_path : str
            Chemin vers le fichier pickle des encodeurs
        """
        # Charger le modèle
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        # Charger les encodeurs
        with open(encoders_path, 'rb') as f:
            self.encoders = pickle.load(f)
        
        # Configuration des marques
        self.marques_acceptees = [
            'MERCEDES', 'VW', 'PEUGEOT', 'KIA', 'CITROEN', 'BMW', 'Fiat', 'OTHER_BRAND',
            'Audi', 'CHINESE', 'HYUNDAI', 'Toyota', 'SUZUKI', 'RENAULT', 'Dacia',
            'JAPANESE', 'Ford', 'MG', 'GWM', 'SEAT', 'AMERICAN', 'NISSAN', 'CHERY',
            'SKODA', 'Porsche', 'LUXURY_BRAND', 'Opel', 'Mini', 'Land Rover', 'UTILITY'
        ]
        
        self.luxury_brands = ['BMW', 'MERCEDES', 'Audi', 'Porsche', 'Land Rover', 'LUXURY_BRAND', 'Mini']
        
        self.brand_categories = {
            'Economic_European': ['PEUGEOT', 'CITROEN', 'RENAULT', 'Fiat', 'SEAT', 'Dacia', 'Opel', 'SKODA', 'Ford'],
            'Premium_European': ['BMW', 'MERCEDES', 'Audi', 'VW', 'Porsche', 'Land Rover', 'Mini', 'LUXURY_BRAND'],
            'Asian': ['Toyota', 'HYUNDAI', 'KIA', 'SUZUKI', 'NISSAN', 'JAPANESE'],
            'Chinese': ['CHINESE', 'MG', 'GWM', 'CHERY'],
            'Other': ['OTHER_BRAND', 'AMERICAN', 'UTILITY']
        }
        
        print(f"✅ CarPricePredictor initialisé")
        print(f"   • Modèle: {type(self.model).__name__}")
        print(f"   • {len(self.marques_acceptees)} marques disponibles")
    
    def _age_category(self, age):
        """Catégorise un véhicule selon son âge"""
        if age == 0:
            return 'Neuf'
        elif age <= 3:
            return 'Récent'
        elif age <= 7:
            return 'Occasion_Standard'
        else:
            return 'Ancien'
    
    def _categorize_brand(self, marque):
        """Catégorise une marque selon son origine"""
        for category, brands in self.brand_categories.items():
            if marque in brands:
                return category
        return 'Other'
    
    def _prepare_features(self, marque, annee, kilometrage, energie, boite_vitesses, puissance_fiscale):
        """
        Prépare les features pour le modèle.
        
        Returns:
        --------
        pd.DataFrame
            DataFrame avec les 23 features nécessaires
        """
        # Validation
        if marque not in self.marques_acceptees:
            raise ValueError(f"Marque '{marque}' non reconnue. Marques acceptées: {self.marques_acceptees}")
        
        energies_acceptees = ['Diesel', 'Essence', 'Hybride', 'Electrique', 'GPL']
        if energie not in energies_acceptees:
            raise ValueError(f"Énergie '{energie}' non reconnue. Valeurs acceptées: {energies_acceptees}")
        
        boites_acceptees = ['Manuelle', 'Automatique']
        if boite_vitesses not in boites_acceptees:
            raise ValueError(f"Boîte '{boite_vitesses}' non reconnue. Valeurs acceptées: {boites_acceptees}")
        
        # Calcul de l'âge
        annee_actuelle = datetime.now().year
        age = annee_actuelle - annee
        
        if age < 0:
            raise ValueError(f"L'année {annee} est dans le futur!")
        
        # Feature engineering
        km_par_age = kilometrage / (age + 1)
        log_km = np.log1p(kilometrage)
        is_luxury = 1 if marque in self.luxury_brands else 0
        age_cat = self._age_category(age)
        puissance_age_ratio = puissance_fiscale / (age + 1)
        brand_cat = self._categorize_brand(marque)
        
        # Encodage de la marque
        le_marque = self.encoders['marque_encoder']
        try:
            marque_encoded = le_marque.transform([marque])[0]
        except ValueError:
            marque_encoded = le_marque.transform(['OTHER_BRAND'])[0]
        
        # Créer le dictionnaire de données dans l'ordre exact
        data = {
            'Age': age,
            'Kilometrage': kilometrage,
            'Puissance_Fiscale': puissance_fiscale,
            'Km_par_Age': km_par_age,
            'Log_Km': log_km,
            'Is_Luxury': is_luxury,
            'Puissance_Age_Ratio': puissance_age_ratio,
            'Boite_Auto': 1 if boite_vitesses == 'Automatique' else 0,
            'Marque_encoded': marque_encoded
        }
        
        # One-Hot Encoding
        for col in self.encoders['energie_columns']:
            energie_type = col.replace('Energie_', '')
            data[col] = 1 if energie_type == energie else 0
        
        for col in self.encoders['brand_category_columns']:
            brand_cat_type = col.replace('Brand_Cat_', '')
            data[col] = 1 if brand_cat_type == brand_cat else 0
        
        for col in self.encoders['age_category_columns']:
            age_cat_type = col.replace('Age_Cat_', '')
            data[col] = 1 if age_cat_type == age_cat else 0
        
        return pd.DataFrame([data])
    
    def predict(self, marque, modele, annee, kilometrage, energie, boite_vitesses, puissance_fiscale, verbose=False):
        """
        Prédit le prix d'un véhicule.
        
        Parameters:
        -----------
        marque : str
            La marque du véhicule
        modele : str
            Le modèle du véhicule (informatif)
        annee : int
            L'année de fabrication
        kilometrage : float
            Le kilométrage du véhicule
        energie : str
            Type d'énergie ('Diesel', 'Essence', 'Hybride', 'Electrique', 'GPL')
        boite_vitesses : str
            Type de boîte ('Manuelle' ou 'Automatique')
        puissance_fiscale : int
            Puissance fiscale en CV
        verbose : bool, optional
            Afficher les détails de la prédiction
        
        Returns:
        --------
        dict
            Résultat de la prédiction avec le prix et les informations
        """
        try:
            # Préparer les features
            df_input = self._prepare_features(marque, annee, kilometrage, energie, boite_vitesses, puissance_fiscale)
            
            # Prédiction
            prix_predit = self.model.predict(df_input)[0]
            prix_min = prix_predit * 0.90
            prix_max = prix_predit * 1.10
            
            if verbose:
                print("="*70)
                print("🚗 PRÉDICTION DU PRIX")
                print("="*70)
                print(f"   • Véhicule: {marque} {modele} ({annee})")
                print(f"   • Kilométrage: {kilometrage:,.0f} km")
                print(f"   • Énergie: {energie} | Boîte: {boite_vitesses}")
                print(f"   • Puissance: {puissance_fiscale} CV")
                print(f"\n🎯 Prix estimé: {prix_predit:,.0f} DT")
                print(f"📊 Fourchette: {prix_min:,.0f} - {prix_max:,.0f} DT")
                print("="*70)
            
            return {
                'success': True,
                'prix_predit': prix_predit,
                'prix_min': prix_min,
                'prix_max': prix_max,
                'marque': marque,
                'modele': modele,
                'annee': annee,
                'age': datetime.now().year - annee,
                'kilometrage': kilometrage,
                'energie': energie,
                'boite_vitesses': boite_vitesses,
                'puissance_fiscale': puissance_fiscale
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def predict_batch(self, vehicles_list, verbose=False):
        """
        Prédit les prix pour une liste de véhicules.
        
        Parameters:
        -----------
        vehicles_list : list of dict
            Liste de dictionnaires contenant les informations des véhicules
            Chaque dict doit avoir: marque, modele, annee, kilometrage, energie, boite_vitesses, puissance_fiscale
        verbose : bool, optional
            Afficher les détails
        
        Returns:
        --------
        list of dict
            Liste des résultats de prédiction
        """
        results = []
        for vehicle in vehicles_list:
            result = self.predict(
                marque=vehicle['marque'],
                modele=vehicle['modele'],
                annee=vehicle['annee'],
                kilometrage=vehicle['kilometrage'],
                energie=vehicle['energie'],
                boite_vitesses=vehicle['boite_vitesses'],
                puissance_fiscale=vehicle['puissance_fiscale'],
                verbose=verbose
            )
            results.append(result)
        
        return results
    
    def get_vehicle_info(self, marque):
        """
        Retourne les informations sur une marque.
        
        Parameters:
        -----------
        marque : str
            La marque du véhicule
        
        Returns:
        --------
        dict
            Informations sur la marque
        """
        if marque not in self.marques_acceptees:
            return {
                'exists': False,
                'message': f"Marque '{marque}' non reconnue"
            }
        
        return {
            'exists': True,
            'marque': marque,
            'is_luxury': marque in self.luxury_brands,
            'category': self._categorize_brand(marque)
        }


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le prédicteur
    predictor = CarPricePredictor()
    
    # Test simple
    result = predictor.predict(
        marque='BMW',
        modele='Série 3',
        annee=2021,
        kilometrage=45000,
        energie='Diesel',
        boite_vitesses='Automatique',
        puissance_fiscale=9,
        verbose=True
    )
    
    if result['success']:
        print(f"\n✅ Prédiction réussie: {result['prix_predit']:,.0f} DT")
    else:
        print(f"\n❌ Erreur: {result['error']}")
