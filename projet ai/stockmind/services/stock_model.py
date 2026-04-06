"""Chargement lazy du pipeline scikit-learn et inférence."""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

_model = None


def model_path_ready(path: Path) -> bool:
    return path.is_file()


def get_model(path: Path):
    global _model
    if _model is None and path.is_file():
        _model = joblib.load(path)
    return _model


def predict_quantity(
    path: Path,
    *,
    category: str,
    current_stock: int,
    avg_weekly_sales: float,
    lead_time_days: int,
    month: int,
) -> float:
    model = get_model(path)
    if model is None:
        raise RuntimeError("Modèle non disponible")
    row = pd.DataFrame(
        [
            {
                "category": category,
                "current_stock": current_stock,
                "avg_weekly_sales": avg_weekly_sales,
                "lead_time_days": lead_time_days,
                "month": month,
            }
        ]
    )
    return float(model.predict(row)[0])
