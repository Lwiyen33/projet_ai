"""
Génère un jeu de données synthétique pour la gestion de stock (démonstration pédagogique).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
CATEGORIES = ["Electronique", "Alimentaire", "Textile", "Outillage"]


def build_dataset(n_rows: int = 2500) -> pd.DataFrame:
    n = n_rows
    category = RNG.choice(CATEGORIES, size=n)
    current_stock = RNG.integers(0, 400, size=n)
    avg_weekly_sales = RNG.uniform(2.0, 90.0, size=n)
    lead_time_days = RNG.integers(4, 25, size=n)
    month = RNG.integers(1, 13, size=n)

    # Quantité "idéale" couvrant le délai + marge — bruit réaliste
    weeks_cover = lead_time_days / 7.0
    base_need = avg_weekly_sales * weeks_cover
    seasonal = 1.0 + 0.08 * np.sin(2 * np.pi * month / 12.0)
    noise = RNG.normal(0, 18.0, size=n)

    cat_factor = np.where(category == "Alimentaire", 1.12, 1.0)
    cat_factor = np.where(category == "Electronique", 0.95, cat_factor)

    recommended = base_need * seasonal * cat_factor - 0.35 * current_stock + noise
    recommended = np.clip(np.round(recommended), 0, 800).astype(int)

    return pd.DataFrame(
        {
            "category": category,
            "current_stock": current_stock,
            "avg_weekly_sales": np.round(avg_weekly_sales, 2),
            "lead_time_days": lead_time_days,
            "month": month,
            "recommended_order_qty": recommended,
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=2500)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "stock_synthetic.csv",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df = build_dataset(args.rows)
    df.to_csv(args.output, index=False)
    print(f"Écrit {len(df)} lignes -> {args.output}")


if __name__ == "__main__":
    main()
