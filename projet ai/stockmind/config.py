"""Configuration centralisée de l'application."""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-local-stockmind-only")
    MODEL_PATH = PROJECT_ROOT / "models" / "stock_model.joblib"
    PRODUCTS_PATH = PROJECT_ROOT / "data" / "products.json"
    CATEGORIES = ["Electronique", "Alimentaire", "Textile", "Outillage"]
