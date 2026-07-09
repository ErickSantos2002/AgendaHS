from datetime import datetime
from flask import Blueprint, render_template, request, abort
from .db import get_db

bp = Blueprint("publico", __name__)


def _buscar_evento(slug):
    db = get_db()
    evento = db.execute("SELECT * FROM evento WHERE id=?", (slug,)).fetchone()
    if evento is None:
        abort(404)
    datas = db.execute(
        "SELECT * FROM evento_data WHERE evento_id=? ORDER BY data, horario", (slug,)
    ).fetchall()
    return evento, datas


@bp.route("/e/<slug>")
def responder_form(slug):
    evento, datas = _buscar_evento(slug)
    return render_template("publico.html", evento=evento, datas=datas)


@bp.route("/e/<slug>/responder", methods=["POST"])
def responder(slug):
    evento, datas = _buscar_evento(slug)
    nome = (request.form.get("nome") or "").strip()
    sem_disp = bool(request.form.get("sem_disponibilidade"))
    ids_validos = {str(d["id"]) for d in datas}
    marcadas = [x for x in request.form.getlist("datas") if x in ids_validos]

    erro = None
    if not nome:
        erro = "Informe seu nome."
    elif not sem_disp and not marcadas:
        erro = "Marque pelo menos uma data, ou 'Não tenho disponibilidade'."
    if erro:
        return render_template(
            "publico.html", evento=evento, datas=datas, erro=erro,
            nome=nome, marcadas=marcadas, sem_disp=sem_disp,
        ), 400

    # "Não tenho disponibilidade" tem prioridade: registra sem nenhuma data.
    escolhidas = [] if sem_disp else [int(x) for x in marcadas]

    db = get_db()
    existente = db.execute(
        "SELECT id FROM participante WHERE evento_id=? AND LOWER(nome)=LOWER(?)",
        (slug, nome),
    ).fetchone()
    if existente:
        pid = existente["id"]
        db.execute("DELETE FROM participante_data WHERE participante_id=?", (pid,))
    else:
        cur = db.execute(
            "INSERT INTO participante (evento_id, nome, criado_em) VALUES (?,?,?)",
            (slug, nome, datetime.now().isoformat(timespec="seconds")),
        )
        pid = cur.lastrowid
    for did in escolhidas:
        db.execute(
            "INSERT INTO participante_data (participante_id, evento_data_id) VALUES (?,?)",
            (pid, did),
        )
    db.commit()
    return render_template("publico_ok.html", evento=evento)
