"""Fábrica do app: extensões, logging, blueprints, páginas de erro e comandos."""
import logging
import os
from datetime import date
from logging.handlers import RotatingFileHandler

import click
from flask import Flask, render_template, request
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from config import Config

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Entre na sua conta para continuar."
login_manager.login_message_category = "warning"

MONTHS = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    configure_logging(app)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    from app import models  # noqa: F401  (registra os models e o user_loader)

    from app.auth.routes import bp as auth_bp
    from app.comentarios.routes import bp as comentarios_bp
    from app.main.routes import bp as main_bp
    from app.receitas.routes import bp as receitas_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(receitas_bp)
    app.register_blueprint(comentarios_bp)

    register_error_handlers(app)
    register_commands(app)

    @app.context_processor
    def inject_globals():
        today = date.today()
        return {"current_edition": f"Edição de {MONTHS[today.month - 1]}"}

    app.logger.info("App iniciado (ambiente: %s)", app.config["APP_ENV"])
    return app


def configure_logging(app):
    """Log em logs/gula.log (com rotação) e no console, no formato
    data · nível · módulo · mensagem."""
    os.makedirs(app.config["LOG_DIR"], exist_ok=True)
    formatter = logging.Formatter(
        "%(asctime)s · %(levelname)s · %(module)s · %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        os.path.join(app.config["LOG_DIR"], "gula.log"),
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Remove handlers antigos (inclusive o padrão do Flask) para não duplicar linhas.
    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(app.config["LOG_LEVEL"])
    app.logger.propagate = False


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(error):
        app.logger.warning("403 em %s %s", request.method, request.path)
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning("404 em %s %s", request.method, request.path)
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        original = getattr(error, "original_exception", None)
        app.logger.error(
            "500 em %s %s: %s", request.method, request.path, original or error,
            exc_info=original,
        )
        return render_template("500.html"), 500


def register_commands(app):
    @app.cli.command("init-db")
    @click.option("--drop", is_flag=True, help="Apaga todas as tabelas antes de criar.")
    def init_db(drop):
        """Cria as tabelas do banco."""
        if drop:
            db.drop_all()
            app.logger.warning("init-db: tabelas apagadas")
        db.create_all()
        app.logger.info("init-db: tabelas criadas em %s", db.engine.url)
        click.echo("Banco criado: " + ", ".join(sorted(db.metadata.tables)))
