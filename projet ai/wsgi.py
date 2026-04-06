"""WSGI pour déploiement : gunicorn wsgi:app"""
from stockmind import create_app

app = create_app()
