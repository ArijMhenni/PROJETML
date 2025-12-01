# 🚗 Prédiction du Prix des Véhicules - Marché Tunisien

Ce projet utilise un modèle de Machine Learning (Extra Trees Regressor) pour prédire le prix des véhicules d'occasion sur le marché tunisien.

## 📁 Structure du Projet

```
PROJET/
├── Data/
│   ├── cleaned/          # Datasets nettoyés
│   └── row/              # Datasets bruts
├── models/
│   ├── extra_trees_tuned.pkl    # Modèle entraîné
│   └── encoders.pkl             # Encodeurs (label, one-hot)
├── training/
│   └── training.ipynb           # Notebook d'entraînement complet
├── cleaning/
│   └── *.ipynb                  # Notebooks de nettoyage des données
├── car_price_predictor.py       # Classe Python du pipeline
├── pipeline.ipynb               # Notebook de démonstration
└── README.md                    # Ce fichier
```

## 🎯 Fonctionnalités

- **Prédiction du prix** d'un véhicule basée sur ses caractéristiques
- **Prédiction en batch** pour plusieurs véhicules
- **Validation des données** entrées
- **API simple** et réutilisable via la classe `CarPricePredictor`

## 📊 Performance du Modèle

- **R² Score**: 0.8749
- **RMSE**: 21,721 DT
- **MAE**: 14,412 DT
- **Features utilisées**: 23 colonnes

## 🚀 Utilisation Rapide

### 1. Installation

```python
import pandas as pd
import numpy as np
from car_price_predictor import CarPricePredictor
```

### 2. Initialisation

```python
# Créer une instance du prédicteur
predictor = CarPricePredictor(
    model_path='models/extra_trees_tuned.pkl',
    encoders_path='models/encoders.pkl'
)
```

### 3. Prédiction Simple

```python
# Prédire le prix d'un véhicule
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

print(f"Prix estimé: {result['prix_predit']:,.0f} DT")
```

### 4. Prédiction en Batch

```python
# Liste de véhicules
vehicles = [
    {
        'marque': 'BMW', 'modele': 'Série 1', 'annee': 2020,
        'kilometrage': 130000, 'energie': 'Essence',
        'boite_vitesses': 'Automatique', 'puissance_fiscale': 10
    },
    {
        'marque': 'PEUGEOT', 'modele': '208', 'annee': 2021,
        'kilometrage': 119000, 'energie': 'Diesel',
        'boite_vitesses': 'Manuelle', 'puissance_fiscale': 5
    }
]

# Prédire pour tous
results = predictor.predict_batch(vehicles)
```

## 📋 Paramètres d'Entrée

| Paramètre           | Type  | Valeurs Acceptées                         | Description          |
| ------------------- | ----- | ----------------------------------------- | -------------------- |
| `marque`            | str   | 30 marques (voir liste)                   | Marque du véhicule   |
| `modele`            | str   | Tout                                      | Modèle (informatif)  |
| `annee`             | int   | 1900-2025                                 | Année de fabrication |
| `kilometrage`       | float | > 0                                       | Kilométrage en km    |
| `energie`           | str   | Diesel, Essence, Hybride, Electrique, GPL | Type de carburant    |
| `boite_vitesses`    | str   | Manuelle, Automatique                     | Type de transmission |
| `puissance_fiscale` | int   | > 0                                       | Puissance en CV      |

## 🏷️ Marques Acceptées

**Premium European**: BMW, MERCEDES, Audi, VW, Porsche, Land Rover, Mini

**Economic European**: PEUGEOT, CITROEN, RENAULT, Fiat, SEAT, Dacia, Opel, SKODA, Ford

**Asian**: Toyota, HYUNDAI, KIA, SUZUKI, NISSAN

**Chinese**: MG, GWM, CHERY

**Others**: OTHER_BRAND, AMERICAN, UTILITY, JAPANESE, CHINESE, LUXURY_BRAND

## 📈 Features du Modèle

### Features Numériques (6)

- Age (calculé automatiquement)
- Kilometrage
- Puissance_Fiscale
- Km_par_Age
- Log_Km
- Puissance_Age_Ratio

### Features Binaires (2)

- Is_Luxury
- Boite_Auto

### Features Encodées (15)

- Marque_encoded (Label Encoding)
- Energie (5 colonnes One-Hot)
- Brand_Category (5 colonnes One-Hot)
- Age_Category (4 colonnes One-Hot)

## 🛠️ Technologies Utilisées

- **Python 3.11+**
- **pandas** - Manipulation des données
- **numpy** - Calculs numériques
- **scikit-learn** - Machine Learning
- **pickle** - Sérialisation du modèle

## 📝 Exemples de Résultats

### Exemple 1: BMW Série 1 (2020)

- **Kilométrage**: 130,000 km
- **Énergie**: Essence
- **Prix estimé**: ~85,000 DT

### Exemple 2: Peugeot 208 (2021)

- **Kilométrage**: 119,000 km
- **Énergie**: Diesel
- **Prix estimé**: ~45,000 DT

### Exemple 3: Toyota Corolla Neuve (2024)

- **Kilométrage**: 5,000 km
- **Énergie**: Hybride
- **Prix estimé**: ~115,000 DT

## ⚠️ Notes Importantes

1. **Fourchette de prix**: Le modèle retourne une fourchette de ±10% pour tenir compte de l'incertitude
2. **Validation**: Toutes les entrées sont validées avant la prédiction
3. **Gestion d'erreurs**: Les erreurs sont capturées et retournées dans le résultat
4. **Age automatique**: L'âge du véhicule est calculé automatiquement à partir de l'année

## 🔮 Prochaines Étapes

- [ ] Déployer en API REST (FastAPI/Flask)
- [ ] Créer une interface web
- [ ] Ajouter des logs de prédiction
- [ ] Implémenter un système de feedback
- [ ] Améliorer le modèle avec plus de données

## 👥 Auteurs

ML Project Team - 2025

## 📄 Licence

Ce projet est destiné à des fins éducatives et de recherche.
