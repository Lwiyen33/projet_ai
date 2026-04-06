# StockMind — Backend IA de gestion de stock

Backend Python intelligent pour la gestion de stock. Expose une API REST (Flask) couplée à un modèle de machine learning (Random Forest) pour prédire les quantités à commander, avec une interface web HTML/CSS/JS intégrée.

---

## Structure du projet

```
.
├── app.py                  # Point d'entrée Flask
├── wsgi.py                 # Point d'entrée production (Gunicorn)
├── requirements.txt
├── stockmind/
│   ├── __init__.py         # Factory create_app()
│   ├── config.py           # Configuration centralisée
│   ├── routes.py           # Routes API + fichiers statiques
│   └── services/
│       ├── products.py     # CRUD produits (persistance JSON)
│       └── stock_model.py  # Chargement modèle + inférence
├── data/
│   ├── products.json       # Base de données produits
│   └── stock_synthetic.csv # Dataset d'entraînement
├── models/
│   └── stock_model.joblib  # Modèle entraîné
├── scripts/
│   ├── generate_data.py    # Génération du dataset synthétique
│   └── train_model.py      # Entraînement et évaluation du modèle
├── frontend/               # Interface web statique
│   ├── index.html
│   ├── documentation.html
│   ├── css/
│   └── js/
├── reports/
│   └── feature_importance.png
└── notebooks/
    └── analyse.ipynb
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Démarrage rapide

### 1. Générer les données et entraîner le modèle

```bash
python scripts/generate_data.py
python scripts/train_model.py
```

### 2. Lancer le serveur de développement

```bash
python app.py
```

L'application est accessible sur `http://127.0.0.1:5000`.

### 3. Production (Gunicorn)

```bash
gunicorn wsgi:app
```

---

## API REST

### Santé

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/health` | État du modèle et catégories disponibles |

### Produits

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/products` | Liste tous les produits |
| POST | `/api/products` | Crée un produit |
| PATCH | `/api/products/<id>` | Met à jour un produit |
| DELETE | `/api/products/<id>` | Supprime un produit |
| POST | `/api/products/<id>/suggest` | Suggestion de commande pour un produit |

### Prédiction directe

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/api/predict` | Prédit la quantité à commander |

#### Exemple — `POST /api/predict`

```json
{
  "category": "Electronique",
  "current_stock": 20,
  "avg_weekly_sales": 14.0,
  "lead_time_days": 12,
  "month": 6
}
```

Réponse :

```json
{ "ok": true, "quantity": 42 }
```

#### Catégories disponibles

`Electronique`, `Alimentaire`, `Textile`, `Outillage`

---

## Modèle ML

- Algorithme : `RandomForestRegressor` (scikit-learn)
- Cible : `recommended_order_qty` (quantité recommandée à commander)
- Features : `category`, `current_stock`, `avg_weekly_sales`, `lead_time_days`, `month`
- Split : 80% entraînement / 20% test, `random_state=42`
- Persistance : `joblib`

Les métriques (MAE, RMSE, R²) sont affichées à l'issue de l'entraînement.

---

## Gestion des erreurs

Toutes les erreurs retournent un JSON `{ "ok": false, "error": "..." }` sans stack trace exposée.
