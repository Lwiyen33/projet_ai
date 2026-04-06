"""Persistance simple des produits (JSON) — CRUD pour la gestion de stock."""
from __future__ import annotations

import json
from pathlib import Path

from stockmind.config import Config

_DEFAULT_PRODUCTS = [
    {
        "id": 1,
        "name": "Casque sans fil",
        "category": "Electronique",
        "stock": 48,
        "avg_weekly_sales": 14.0,
        "lead_time_days": 12,
    },
    {
        "id": 2,
        "name": "Cafe grain 1kg",
        "category": "Alimentaire",
        "stock": 120,
        "avg_weekly_sales": 55.0,
        "lead_time_days": 7,
    },
    {
        "id": 3,
        "name": "T-shirt uni",
        "category": "Textile",
        "stock": 200,
        "avg_weekly_sales": 40.0,
        "lead_time_days": 21,
    },
    {
        "id": 4,
        "name": "Marteau pro",
        "category": "Outillage",
        "stock": 15,
        "avg_weekly_sales": 6.0,
        "lead_time_days": 18,
    },
]


def _path() -> Path:
    return Config.PRODUCTS_PATH


def _ensure_file() -> None:
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.is_file():
        p.write_text(
            json.dumps(_DEFAULT_PRODUCTS, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def load_all() -> list[dict]:
    _ensure_file()
    raw = _path().read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, list):
        return list(_DEFAULT_PRODUCTS)
    return sorted(data, key=lambda x: int(x.get("id", 0)))


def _save_all(products: list[dict]) -> None:
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(products, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp.replace(p)


def _next_id(products: list[dict]) -> int:
    return max((int(p["id"]) for p in products), default=0) + 1


def get_by_id(pid: int) -> dict | None:
    for p in load_all():
        if int(p["id"]) == pid:
            return p
    return None


def create(
    *,
    name: str,
    category: str,
    stock: int,
    avg_weekly_sales: float,
    lead_time_days: int,
) -> dict:
    products = load_all()
    row = {
        "id": _next_id(products),
        "name": name.strip(),
        "category": category,
        "stock": int(stock),
        "avg_weekly_sales": float(avg_weekly_sales),
        "lead_time_days": int(lead_time_days),
    }
    products.append(row)
    _save_all(products)
    return row


def update(
    pid: int,
    *,
    name: str | None = None,
    category: str | None = None,
    stock: int | None = None,
    avg_weekly_sales: float | None = None,
    lead_time_days: int | None = None,
) -> dict | None:
    products = load_all()
    for i, p in enumerate(products):
        if int(p["id"]) != pid:
            continue
        if name is not None:
            p["name"] = name.strip()
        if category is not None:
            p["category"] = category
        if stock is not None:
            p["stock"] = int(stock)
        if avg_weekly_sales is not None:
            p["avg_weekly_sales"] = float(avg_weekly_sales)
        if lead_time_days is not None:
            p["lead_time_days"] = int(lead_time_days)
        products[i] = p
        _save_all(products)
        return p
    return None


def delete(pid: int) -> bool:
    products = load_all()
    new_list = [p for p in products if int(p["id"]) != pid]
    if len(new_list) == len(products):
        return False
    _save_all(new_list)
    return True
