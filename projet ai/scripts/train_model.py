"""
Entraîne un modèle de régression (quantité recommandée à commander) et sauvegarde le pipeline.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "stock_synthetic.csv"
DEFAULT_MODEL = ROOT / "models" / "stock_model.joblib"
DEFAULT_FIG = ROOT / "reports" / "feature_importance.png"


def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    required = {
        "category",
        "current_stock",
        "avg_weekly_sales",
        "lead_time_days",
        "month",
        "recommended_order_qty",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes: {missing}")
    return df


def build_pipeline() -> Pipeline:
    numeric = ["current_stock", "avg_weekly_sales", "lead_time_days", "month"]
    categorical = ["category"]
    preprocessor = ColumnTransformer(
        [
            ("num", "passthrough", numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ]
    )
    return Pipeline(
        [
            ("prep", preprocessor),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=120,
                    max_depth=12,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def plot_importances(pipeline: Pipeline, out_path: Path) -> None:
    prep: ColumnTransformer = pipeline.named_steps["prep"]
    model: RandomForestRegressor = pipeline.named_steps["model"]
    num_feats = prep.transformers_[0][2]
    cat_encoder: OneHotEncoder = prep.named_transformers_["cat"]
    cat_names = list(cat_encoder.get_feature_names_out(["category"]))
    names = list(num_feats) + cat_names
    importances = model.feature_importances_
    order = importances.argsort()[::-1][:15]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9, 5))
    plt.barh([names[i] for i in order[::-1]], importances[order[::-1]], color="#2c7fb8")
    plt.xlabel("Importance")
    plt.title("Importance des variables (Random Forest)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--model-out", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--fig-out", type=Path, default=DEFAULT_FIG)
    args = parser.parse_args()

    df = load_data(args.data)
    X = df.drop(columns=["recommended_order_qty"])
    y = df["recommended_order_qty"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipe = build_pipeline()
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)

    mae = mean_absolute_error(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    r2 = r2_score(y_test, pred)

    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R²:   {r2:.3f}")

    args.model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, args.model_out)
    print(f"Modèle sauvegardé: {args.model_out}")

    plot_importances(pipe, args.fig_out)
    print(f"Figure: {args.fig_out}")


if __name__ == "__main__":
    main()
