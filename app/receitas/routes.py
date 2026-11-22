"""Criar, editar e excluir receitas. Dono: P4.

Stub da P1: as rotas já existem com os nomes do contrato. Substitua o corpo.
"""
from flask import Blueprint, redirect, render_template, url_for

bp = Blueprint("receitas", __name__)


@bp.route("/receitas/nova", methods=["GET", "POST"])
def nova():
    return render_template("under_construction.html", part="P4", endpoint="receitas.nova")


@bp.route("/receitas/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    return render_template("under_construction.html", part="P4", endpoint="receitas.editar")


@bp.route("/receitas/<int:id>/excluir", methods=["POST"])
def excluir(id):
    return redirect(url_for("main.index"))
