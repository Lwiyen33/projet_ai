"""Application Flask — backend IA (scikit-learn) + fichiers statiques HTML/CSS/JS."""
from __future__ import annotations

from pathlib import Path

from flask import Flask, send_from_directory


def create_app() -> Flask:
    root = Path(__file__).resolve().parent.parent
    frontend = root / "frontend"

    app = Flask(
        __name__,
        static_folder=str(frontend),
        static_url_path="",
    )
    app.config.from_object("stockmind.config.Config")

    from stockmind.routes import bp

    app.register_blueprint(bp)

    @app.errorhandler(404)
    def not_found(_e):
        p = frontend / "404.html"
        if p.is_file():
            return send_from_directory(frontend, "404.html"), 404
        return "Page introuvable", 404

    return app
