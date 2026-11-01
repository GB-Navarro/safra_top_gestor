"""EN10 — portões de liberação por estágio (substituem a recusa incondicional do modo final).

Cada portão exige evidência própria; nenhum aprova economia por navegação/teste de software,
nenhum presume H07–H13 e o agente nunca envia nada. Evidência pode ser injetada em testes.
"""
from __future__ import annotations

import re
from pathlib import Path

from .common import REPO, read_json

STAGES = ["data_factual", "analysis_proposal", "group_material", "video_submission", "sent"]
VISUAL_OK = "reviewed_no_material_layout_defect"


def collect(bundle_dir: Path | None = None, production_qa: Path | None = None) -> dict:
    """Evidência real do workspace (sem inferência por decurso de tempo ou existência de arquivo vazio)."""
    from . import consumer
    ev = {"bundle_valid": False, "bundle_state": None, "bundle_qa": None, "open_dispositions": None, "decision_status": None,
          "human_records": [], "production_qa": None, "visual_review": None, "h07_records": [], "rehearsals_logged": 0, "clips_ready": False,
          "video_reviewed_record": None, "submission_receipt": None}
    try:
        path = bundle_dir or consumer.resolve("latest")
        errs = consumer.validate(path)
        ev["bundle_valid"] = not errs
        man = read_json(path / "manifest.json")
        ev["bundle_state"] = man.get("state")
        ev["bundle_qa"] = read_json(path / "qa/analysis_validation.json").get("status")
        ev["open_dispositions"] = [d["requirement_id"] for d in man.get("requirement_dispositions", []) if d.get("status") == "open"]
        dec = read_json(path / "results/recommendation.json")["decision"]
        ev["decision_status"], ev["human_records"] = dec.get("status"), dec.get("human_record_refs", [])
    except Exception as exc:  # noqa: BLE001 — sem pacote válido o portão recusa com motivo
        ev["bundle_error"] = str(exc)
    if production_qa is None:  # sem build explícito: avaliar o build publicado como rascunho canônico
        pub = REPO / "outputs/draft/production/published.json"
        if pub.is_file():
            production_qa = REPO / "outputs/qa/production" / read_json(pub)["build_id"] / "production_qa.json"
    if production_qa and production_qa.is_file():
        q = read_json(production_qa)
        ev["production_qa"] = q.get("status")
        vr = production_qa.parent / "visual_review.json"
        if vr.is_file():
            v = read_json(vr)
            ev["visual_review"] = v.get("status") if v.get("artifacts") == q.get("artifacts") else "stale_for_current_artifacts"
    orient = REPO / "data/raw/orientacoes"
    # O JSON de regras verificadas via web é público; H07 exige instruções privadas reais recebidas.
    ev["h07_records"] = [p.name for p in orient.glob("*") if p.is_file() and p.name not in (".gitkeep", "regulamento_2026_verificado_via_web.json")]
    fb = REPO / "data/interim/feedback_ensaio.md"
    if fb.is_file():
        ev["rehearsals_logged"] = len(re.findall(r"^\| B\d[^|]*\|[^|]*\|[^|]*\| (?!pendente)[^|]+\|", fb.read_text(encoding="utf-8"), flags=re.M))
    c = REPO / "config/video_segments.json"
    if c.is_file() and all((REPO / s["path"]).is_file() for s in read_json(c)["segments"]):
        ev["clips_ready"] = True
    for name, key in (("video_review.json", "video_reviewed_record"), ("comprovante_envio.json", "submission_receipt")):
        p = REPO / "data/raw/orientacoes" / name
        ev[key] = str(p.relative_to(REPO)) if p.is_file() else None
    return ev


def evaluate(stage: str, ev: dict) -> dict:
    if stage not in STAGES:
        raise ValueError(stage)
    reasons = []
    def need(cond, why):
        if not cond:
            reasons.append(why)
    need(ev.get("bundle_valid"), "pacote analítico 1.0 inválido ou ausente")
    need(ev.get("bundle_qa") == "passed", "QA analítica do pacote não aprovada")
    if stage in STAGES[1:]:
        need(ev.get("bundle_state") in ("analysis_proposed", "group_adopted"), f"estado analítico insuficiente: {ev.get('bundle_state')}")
        need(not ev.get("open_dispositions"), f"requisitos abertos: {ev.get('open_dispositions')}")
    if stage in STAGES[2:]:
        need(ev.get("decision_status") == "adopted" and ev.get("human_records"), "H08/H09 sem registro real de adoção pelo grupo")
        need(ev.get("production_qa") == "passed", "QA das peças (Parte 2) não aprovada para a versão atual")
        need(ev.get("visual_review") == VISUAL_OK, "revisão visual não registrada para os hashes atuais das peças")
    if stage in STAGES[3:]:
        need(ev.get("h07_records"), "H07: instruções privadas (horário, canal, formato) não registradas")
        need(ev.get("rehearsals_logged", 0) >= 2, "H10: menos de dois ensaios registrados com tempos reais")
        need(ev.get("clips_ready"), "H11: clipes reais ausentes")
        need(ev.get("video_reviewed_record"), "revisão integral do vídeo pelo grupo não registrada")
    if stage == "sent":
        need(ev.get("submission_receipt"), "H13: comprovante de envio não registrado (o agente nunca envia)")
    return {"stage": stage, "passed": not reasons, "reasons": reasons}


def report(ev: dict) -> list[dict]:
    return [evaluate(s, ev) for s in STAGES]
