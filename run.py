"""Ponto de entrada.

Local:            flask run          (o .flaskenv aponta FLASK_APP para este arquivo)
PythonAnywhere:   o arquivo WSGI faz  from run import app as application
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
