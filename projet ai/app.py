"""
Backend Flask : API JSON + fichiers statiques HTML/CSS/JS (frontend/).
Lancer : python app.py → http://127.0.0.1:5000
Production : wsgi.py
"""
from stockmind import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
