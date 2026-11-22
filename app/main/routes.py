"""Capa e categorias. Dono: P3.

Stub da P1: as rotas já existem com os nomes do contrato para que o base.html
e os outros templates possam usar url_for desde o início. Substitua o corpo.
"""
from flask import Blueprint, abort, current_app, render_template

from app.models import CATEGORY_SLUGS

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("under_construction.html", part="P3", endpoint="main.index")


@bp.route("/categoria/<slug>")
def categoria(slug):
    if slug not in CATEGORY_SLUGS:
        current_app.logger.warning("Categoria inexistente: %s", slug)
        abort(404)
    return render_template(
        "under_construction.html", part="P3", endpoint="main.categoria",
        section=f"seção de {slug}",
    )
