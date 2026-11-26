"""Página da receita e comentários. Dono: P5."""
import re

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.comentarios.forms import ComentarioForm
from app.models import Comentario, Receita

bp = Blueprint("comentarios", __name__)

TAG_LABELS = {
    "oven": "Forno",
    "stove": "Fogão",
    "fried": "Frito",
    "raw": "Cru",
    "vegan": "Vegano",
    "cold": "Gelados",
    "citrico": "Cítricos",
    "classico": "Clássicos",
    "sem-alcool": "Sem álcool",
}

_STEP_PREFIX_RE = re.compile(r"^\d+[\.\)\-]\s+")


def _parse_ingredients(raw_text):
    return [line.strip() for line in (raw_text or "").splitlines() if line.strip()]


def _parse_steps(raw_text):
    steps = []
    for line in (raw_text or "").splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        cleaned = _STEP_PREFIX_RE.sub("", cleaned, count=1)
        steps.append(cleaned)
    return steps


def _parse_tags(raw_tags):
    parsed = []
    for item in (raw_tags or "").split(","):
        slug = item.strip()
        if not slug:
            continue
        label = TAG_LABELS.get(slug.casefold(), slug)
        parsed.append((slug, label))
    return parsed


@bp.route("/receitas/<int:id>", methods=["GET", "POST"])
def detalhe(id):
    receita = db.session.get(Receita, id)
    if receita is None:
        current_app.logger.warning("Receita %s não encontrada", id)
        abort(404)

    form = ComentarioForm()

    if request.method == "POST":
        if not current_user.is_authenticated:
            current_app.logger.warning(
                "Tentativa de comentar na receita %s sem autenticação", receita.id
            )
            flash("Entre na sua conta para comentar nesta receita.", "warning")
            return redirect(
                url_for(
                    "auth.login",
                    next=url_for("comentarios.detalhe", id=receita.id, _anchor="comentarios"),
                )
            )

        if form.validate_on_submit():
            comentario = Comentario(
                texto=form.texto.data,
                nota=form.nota.data,
                receita_id=receita.id,
                autor_id=current_user.id,
            )
            db.session.add(comentario)
            db.session.commit()
            current_app.logger.info(
                "Comentário %s criado na receita %s pelo usuário %s (nota=%s)",
                comentario.id,
                receita.id,
                current_user.id,
                comentario.nota,
            )
            flash("Comentário publicado com sucesso!", "success")
            return redirect(
                url_for("comentarios.detalhe", id=receita.id, _anchor="comentarios")
            )

        current_app.logger.debug(
            "Formulário de comentário inválido na receita %s (usuário=%s): %s",
            receita.id,
            current_user.id,
            form.errors,
        )

    comentarios = (
        Comentario.query.filter_by(receita_id=receita.id)
        .order_by(Comentario.criado_em.desc(), Comentario.id.desc())
        .all()
    )
    total_comentarios = len(comentarios)
    media_notas = (
        round(sum(c.nota for c in comentarios) / total_comentarios, 1)
        if total_comentarios
        else None
    )

    if request.method == "GET":
        current_app.logger.debug(
            "Receita %s visualizada (%s, comentarios=%s)",
            receita.id,
            receita.titulo,
            total_comentarios,
        )

    return render_template(
        "comentarios/detalhe.html",
        receita=receita,
        form=form,
        comentarios=comentarios,
        total_comentarios=total_comentarios,
        media_notas=media_notas,
        ingredientes=_parse_ingredients(receita.ingredientes),
        passos=_parse_steps(receita.modo_preparo),
        tags=_parse_tags(receita.tags),
        section=receita.categoria.nome,
    )


@bp.route("/comentarios/<int:id>/excluir", methods=["POST"])
@login_required
def excluir(id):
    comentario = db.session.get(Comentario, id)
    if comentario is None:
        current_app.logger.warning(
            "Tentativa de excluir comentário inexistente %s pelo usuário %s",
            id,
            current_user.id,
        )
        abort(404)

    if comentario.autor_id != current_user.id:
        current_app.logger.warning(
            "Usuário %s tentou excluir o comentário %s sem permissão",
            current_user.id,
            comentario.id,
        )
        abort(403)

    receita_id = comentario.receita_id
    db.session.delete(comentario)
    db.session.commit()
    current_app.logger.info(
        "Comentário %s excluído pelo usuário %s (receita %s)",
        id,
        current_user.id,
        receita_id,
    )
    flash("Comentário excluído.", "info")
    return redirect(url_for("comentarios.detalhe", id=receita_id, _anchor="comentarios"))
