"""Routes : fichiers statiques (HTML/CSS/JS) + API JSON (produits + modèle ML)."""
from __future__ import annotations

from datetime import datetime

from flask import Blueprint, current_app, jsonify, request, send_from_directory

from stockmind.config import Config
from stockmind.services import products as prod
from stockmind.services import stock_model as sm

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return send_from_directory(current_app.static_folder, "index.html")


@bp.route("/documentation.html")
def documentation():
    return send_from_directory(current_app.static_folder, "documentation.html")


@bp.route("/api/health", methods=["GET"])
def api_health():
    return jsonify(
        {
            "model_ok": sm.model_path_ready(Config.MODEL_PATH),
            "categories": Config.CATEGORIES,
        }
    )


@bp.route("/api/products", methods=["GET"])
def api_products_list():
    return jsonify({"ok": True, "products": prod.load_all()})


@bp.route("/api/products", methods=["POST"])
def api_products_create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"ok": False, "error": "JSON attendu."}), 400
    try:
        name = str(data.get("name", "")).strip()
        category = data.get("category", "")
        stock = int(data["stock"])
        avg_weekly_sales = float(data["avg_weekly_sales"])
        lead_time_days = int(data["lead_time_days"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"ok": False, "error": "Champs : name, category, stock, avg_weekly_sales, lead_time_days."}), 400

    if not name:
        return jsonify({"ok": False, "error": "Nom requis."}), 400
    if category not in Config.CATEGORIES:
        return jsonify(
            {"ok": False, "error": f"Catégorie invalide : {', '.join(Config.CATEGORIES)}"},
        ), 400
    if stock < 0 or lead_time_days < 1:
        return jsonify({"ok": False, "error": "stock ≥ 0, délai ≥ 1."}), 400

    row = prod.create(
        name=name,
        category=category,
        stock=stock,
        avg_weekly_sales=avg_weekly_sales,
        lead_time_days=lead_time_days,
    )
    return jsonify({"ok": True, "product": row}), 201


@bp.route("/api/products/<int:pid>", methods=["PATCH"])
def api_products_patch(pid):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"ok": False, "error": "JSON attendu."}), 400

    kwargs = {}
    if "name" in data:
        kwargs["name"] = str(data["name"])
    if "category" in data:
        kwargs["category"] = str(data["category"])
    if "stock" in data:
        kwargs["stock"] = int(data["stock"])
    if "avg_weekly_sales" in data:
        kwargs["avg_weekly_sales"] = float(data["avg_weekly_sales"])
    if "lead_time_days" in data:
        kwargs["lead_time_days"] = int(data["lead_time_days"])

    if not kwargs:
        return jsonify({"ok": False, "error": "Aucun champ à modifier."}), 400

    if kwargs.get("category") and kwargs["category"] not in Config.CATEGORIES:
        return jsonify({"ok": False, "error": "Catégorie invalide."}), 400

    updated = prod.update(pid, **kwargs)
    if updated is None:
        return jsonify({"ok": False, "error": "Produit introuvable."}), 404
    return jsonify({"ok": True, "product": updated})


@bp.route("/api/products/<int:pid>", methods=["DELETE"])
def api_products_delete(pid):
    if not prod.delete(pid):
        return jsonify({"ok": False, "error": "Produit introuvable."}), 404
    return jsonify({"ok": True})


@bp.route("/api/products/<int:pid>/suggest", methods=["POST"])
def api_products_suggest(pid):
    p = prod.get_by_id(pid)
    if p is None:
        return jsonify({"ok": False, "error": "Produit introuvable."}), 404

    data = request.get_json(silent=True) or {}
    month = data.get("month")
    if month is None:
        month = datetime.now().month
    else:
        month = int(month)

    model_path = Config.MODEL_PATH
    if not sm.model_path_ready(model_path):
        return jsonify(
            {
                "ok": False,
                "error": "Modèle introuvable. Lancez python scripts/train_model.py",
            }
        ), 503

    if month < 1 or month > 12:
        return jsonify({"ok": False, "error": "Mois entre 1 et 12."}), 400

    try:
        pred = sm.predict_quantity(
            model_path,
            category=p["category"],
            current_stock=int(p["stock"]),
            avg_weekly_sales=float(p["avg_weekly_sales"]),
            lead_time_days=int(p["lead_time_days"]),
            month=month,
        )
        qty = int(max(0, round(pred)))
        return jsonify({"ok": True, "quantity": qty, "month_used": month})
    except Exception as e:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(e)}), 500


@bp.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"ok": False, "error": "Corps JSON attendu."}), 400

    model_path = Config.MODEL_PATH
    if not sm.model_path_ready(model_path):
        return jsonify(
            {
                "ok": False,
                "error": "Modèle introuvable. Exécutez : python scripts/generate_data.py puis python scripts/train_model.py",
            }
        ), 503

    try:
        category = data.get("category", "")
        if category not in Config.CATEGORIES:
            return jsonify(
                {
                    "ok": False,
                    "error": f"Catégorie invalide. Valeurs : {', '.join(Config.CATEGORIES)}",
                }
            ), 400

        current_stock = int(data["current_stock"])
        avg_weekly_sales = float(data["avg_weekly_sales"])
        lead_time_days = int(data["lead_time_days"])
        month = int(data["month"])
    except (KeyError, TypeError, ValueError):
        return jsonify(
            {
                "ok": False,
                "error": "Champs requis : category, current_stock, avg_weekly_sales, lead_time_days, month (types valides).",
            }
        ), 400

    if month < 1 or month > 12 or current_stock < 0 or lead_time_days < 1:
        return jsonify({"ok": False, "error": "Valeurs hors bornes (mois 1–12, stock ≥ 0, délai ≥ 1)."}), 400

    try:
        pred = sm.predict_quantity(
            model_path,
            category=category,
            current_stock=current_stock,
            avg_weekly_sales=avg_weekly_sales,
            lead_time_days=lead_time_days,
            month=month,
        )
        qty = int(max(0, round(pred)))
        return jsonify({"ok": True, "quantity": qty})
    except Exception as e:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(e)}), 500
