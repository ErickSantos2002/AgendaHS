from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect, url_for
)
from .db import get_db
from .slug import gerar_slug
from .auth import login_required

bp = Blueprint("eventos", __name__)


def criar_evento(titulo, descricao, datas):
    db = get_db()
    slug = gerar_slug()
    db.execute(
        "INSERT INTO evento (id, titulo, descricao, criado_em) VALUES (?,?,?,?)",
        (slug, titulo, descricao or None,
         datetime.now().isoformat(timespec="seconds")),
    )
    for d in datas:
        db.execute(
            "INSERT INTO evento_data (evento_id, data, horario) VALUES (?,?,?)",
            (slug, d["data"], d["horario"] or None),
        )
    db.commit()
    return slug


def resumo_evento(slug):
    db = get_db()
    evento = db.execute("SELECT * FROM evento WHERE id=?", (slug,)).fetchone()
    if evento is None:
        return None
    datas = db.execute(
        "SELECT * FROM evento_data WHERE evento_id=? ORDER BY data, horario", (slug,)
    ).fetchall()
    parts = db.execute(
        "SELECT * FROM participante WHERE evento_id=? ORDER BY criado_em", (slug,)
    ).fetchall()
    participantes = []
    contagem = {d["id"]: 0 for d in datas}
    for p in parts:
        ids = {
            r["evento_data_id"]
            for r in db.execute(
                "SELECT evento_data_id FROM participante_data WHERE participante_id=?",
                (p["id"],),
            )
        }
        for did in ids:
            if did in contagem:
                contagem[did] += 1
        participantes.append({"nome": p["nome"], "disponibilidades": ids})
    melhor_data_id = None
    if contagem:
        melhor = max(contagem.values())
        if melhor > 0:
            melhor_data_id = max(contagem, key=contagem.get)
    return {
        "evento": evento, "datas": datas, "participantes": participantes,
        "contagem": contagem, "melhor_data_id": melhor_data_id,
    }


@bp.route("/painel")
@login_required
def painel():
    db = get_db()
    eventos = db.execute("""
        SELECT e.id, e.titulo, e.criado_em,
               (SELECT COUNT(*) FROM evento_data d WHERE d.evento_id=e.id) n_datas,
               (SELECT COUNT(*) FROM participante p WHERE p.evento_id=e.id) n_respostas
        FROM evento e ORDER BY e.criado_em DESC
    """).fetchall()
    return render_template("painel.html", eventos=eventos)


@bp.route("/eventos/novo")
@login_required
def novo():
    return render_template("evento_novo.html")


@bp.route("/eventos", methods=["POST"])
@login_required
def criar():
    titulo = (request.form.get("titulo") or "").strip()
    descricao = (request.form.get("descricao") or "").strip()
    datas_raw = request.form.getlist("data")
    horarios_raw = request.form.getlist("horario")
    datas = [
        {"data": d.strip(),
         "horario": (horarios_raw[i] if i < len(horarios_raw) else "").strip()}
        for i, d in enumerate(datas_raw) if d.strip()
    ]
    if not titulo:
        return render_template("evento_novo.html", erro="Informe o título."), 400
    if not datas:
        return render_template("evento_novo.html", erro="Adicione ao menos uma data."), 400
    slug = criar_evento(titulo, descricao, datas)
    return redirect(url_for("eventos.detalhe", slug=slug))


@bp.route("/eventos/<slug>")
@login_required
def detalhe(slug):
    dados = resumo_evento(slug)
    if dados is None:
        return render_template("404.html"), 404
    link_publico = url_for("publico.responder_form", slug=slug, _external=True)
    return render_template("evento_detalhe.html", link_publico=link_publico, **dados)
