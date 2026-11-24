"""Capa, catálogo e busca. Dono: P3."""
import unicodedata

from flask import Blueprint, abort, current_app, render_template, request
from sqlalchemy import false, func, or_

from app import db
from app.models import Categoria, Receita

bp = Blueprint("main", __name__)

CATEGORY_PRESENTATION = {
    "salgados": {
        "title": "Salgadas",
        "eyebrow": "Da cozinha para a mesa",
        "description": "Receitas salgadas para compartilhar, do petisco ao prato principal.",
        "filters": [("quick", "Rápida"), ("oven", "Forno"), ("vegan", "Vegano")],
    },
    "doces": {
        "title": "Doces",
        "eyebrow": "Um carinho a cada colherada",
        "description": "Um bolo para o café, um doce de colher e uma sobremesa para dividir.",
        "filters": [("quick", "Rápida"), ("oven", "Forno"), ("cold", "Gelados")],
    },
    "bar": {
        "title": "Bar",
        "eyebrow": "Receitas para brindar",
        "description": "Drinks para abrir a noite, acompanhar a conversa e servir bem gelados.",
        "filters": [
            ("citrico", "Cítricos"),
            ("classico", "Clássicos"),
            ("sem-alcool", "Sem álcool"),
        ],
    },
}

RELATED_CATEGORIES = {
    "salgados": ("doces", "Ir para os doces"),
    "doces": ("salgados", "Ir para os salgados"),
    "bar": ("doces", "Ir para os doces"),
}


def _normalize_text(value):
    normalized = unicodedata.normalize("NFD", value)
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn").casefold()


def _filter_tag(query, tag):
    if tag == "quick":
        return query.filter(Receita.tempo_min <= 30)

    if "," in tag:
        return query.filter(false())

    tags_column = func.replace(func.lower(func.coalesce(Receita.tags, "")), " ", "")
    normalized_tag = tag.replace(" ", "")
    escaped_tag = normalized_tag.replace("/", "//").replace("%", "/%").replace("_", "/_")
    return query.filter(
        or_(
            tags_column == normalized_tag,
            tags_column.like(f"{escaped_tag},%", escape="/"),
            tags_column.like(f"%,{escaped_tag},%", escape="/"),
            tags_column.like(f"%,{escaped_tag}", escape="/"),
        )
    )


@bp.route("/")
def index():
    featured = (
        Receita.query.join(Categoria)
        .filter(Categoria.slug == "salgados", Receita.titulo == "Moqueca de banana-da-terra")
        .first()
    )
    if featured is None:
        featured = Receita.query.join(Categoria).filter(Categoria.slug == "salgados").first()

    recent_recipes = (
        Receita.query.order_by(Receita.criado_em.desc(), Receita.id.desc()).limit(3).all()
    )
    return render_template(
        "main/index.html",
        featured=featured,
        recent_recipes=recent_recipes,
    )


@bp.route("/categoria/<slug>")
def categoria(slug):
    categoria = Categoria.query.filter_by(slug=slug).first()
    if categoria is None or slug not in CATEGORY_PRESENTATION:
        current_app.logger.warning("Categoria inexistente: %s", slug)
        abort(404)

    search_term = request.args.get("q", "").strip()
    tag = request.args.get("tag", "").strip().casefold()
    if search_term or tag:
        current_app.logger.debug(
            "Busca no catálogo: categoria=%s q=%r tag=%r",
            slug,
            search_term,
            tag,
        )

    query = Receita.query.filter_by(categoria_id=categoria.id)
    if tag:
        query = _filter_tag(query, tag)
    recipes = query.order_by(Receita.criado_em.desc(), Receita.id.desc()).all()
    if search_term:
        normalized_term = _normalize_text(search_term)
        recipes = [
            recipe
            for recipe in recipes
            if normalized_term in _normalize_text(recipe.titulo)
        ]

    related_slug, related_label = RELATED_CATEGORIES[slug]
    return render_template(
        "main/categoria.html",
        categoria=categoria,
        presentation=CATEGORY_PRESENTATION[slug],
        recipes=recipes,
        search_term=search_term,
        tag=tag,
        related_slug=related_slug,
        related_label=related_label,
    )
