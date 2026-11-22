"""Cadastro, login, logout e perfil. Dono: P2.

Stub da P1: as rotas já existem com os nomes do contrato. Substitua o corpo.
O user_loader e o login_view = "auth.login" já estão configurados (models.py e
app/__init__.py).
"""
from flask import Blueprint, redirect, render_template, url_for

bp = Blueprint("auth", __name__)


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    return render_template("under_construction.html", part="P2", endpoint="auth.cadastro")


@bp.route("/login", methods=["GET", "POST"])
def login():
    return render_template("under_construction.html", part="P2", endpoint="auth.login")


@bp.route("/logout")
def logout():
    return redirect(url_for("main.index"))


@bp.route("/perfil")
def perfil():
    return render_template("under_construction.html", part="P2", endpoint="auth.perfil")
