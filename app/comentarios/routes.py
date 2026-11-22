"""Página da receita e comentários. Dono: P5.

Stub da P1: as rotas já existem com os nomes do contrato. Substitua o corpo.
"""
from flask import Blueprint, redirect, render_template, url_for

bp = Blueprint("comentarios", __name__)


@bp.route("/receitas/<int:id>", methods=["GET", "POST"])
def detalhe(id):
    return render_template("under_construction.html", part="P5", endpoint="comentarios.detalhe")


@bp.route("/comentarios/<int:id>/excluir", methods=["POST"])
def excluir(id):
    return redirect(url_for("main.index"))
