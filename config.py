"""Configuração do app. Tudo que muda entre máquinas vem do arquivo .env."""
import os

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Carrega o .env da raiz do projeto (necessário também no WSGI do PythonAnywhere,
# que não passa pelo comando "flask").
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _abs_path(path):
    """Caminhos relativos no .env são relativos à raiz do projeto."""
    if os.path.isabs(path):
        return path
    return os.path.join(BASE_DIR, path)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-inseguro-troque-no-env"

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///gula.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = _abs_path(
        os.environ.get("UPLOAD_FOLDER") or os.path.join("app", "static", "uploads")
    )
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # limite de 5 MB por upload

    APP_ENV = os.environ.get("APP_ENV", "production")
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    LOG_LEVEL = "DEBUG" if APP_ENV == "development" else "INFO"
