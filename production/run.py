"""CLI da Parte 2: consome um pacote 1.0 publicado e gera a apresentação final de 12 slides (HTML, PDF e PPTX),
o script, o apoio técnico de 7 páginas, figuras, QA e portões.

Exemplos (raiz do repositório):
  .venv/Scripts/python.exe -m production.run --input-bundle latest                  (perfil deck12)
  .venv/Scripts/python.exe -m production.run --input-bundle latest --check          (só validar o pacote)
  .venv/Scripts/python.exe -m production.run --record-visual-review outputs/draft/production/<build_id> --notes "..."
  .venv/Scripts/python.exe -m production.run --publish outputs/draft/production/<build_id>
  .venv/Scripts/python.exe -m production.run --release-report
  .venv/Scripts/python.exe -m production.run --promote-final group_material        (recusa com motivos se o portão bloquear)
  .venv/Scripts/python.exe -m production.run --baseline default                     (rascunho provisório da fotografia legada)
Não recalcula finanças, não importa analysis/, não envia nada a terceiros.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from .common import REPO, SAO_PAULO, now_iso, read_json, sha256_file, write_csv, write_json

PROFILES = ("deck12",)


def build(bundle_arg: str, out_root: Path, qa_root: Path, run_qa: bool = True, profile: str = "deck12") -> dict:
    from . import brand, consumer, deck_model, docs, figures, html_deck, narrative, pptx_deck, qa, snapshot, video
    snapshot.ensure()  # EN01: fotografia própria dos insumos legados antes de qualquer publicação
    path = consumer.resolve(bundle_arg)
    b = consumer.load(path)
    build_id = f"pr_{datetime.now(SAO_PAULO).strftime('%Y%m%dT%H%M%S')}_{b.bundle_id.split('_')[-1]}"
    out, qa_dir = out_root / build_id, qa_root / build_id
    want = (profile,)
    model = deck_model.build(b)
    write_json(out / "deck_model.json", model)
    html_deck.build(model, out / "html/apresentacao_esg.html")
    figures.build(model, out / "figuras")
    text = narrative.build(b, model, out)
    video.write_profiles()
    pptx_deck.build_support(model, b, out / "figuras", out / "apoio_tecnico.pptx")
    docs.build(b, model, out)
    place = deck_model.placements(model, "html/apresentacao_esg.html", profile, b)
    write_csv(out / "claim_placements.csv", place, ["artifact", "profile", "page", "block", "claim_id", "value_ids", "source_ids", "input_bundle", "input_manifest_sha256"])
    summary = qa.run(b, model, out, qa_dir, place, text, profile) if run_qa else {"status": "skipped"}
    files = [{"path": p.relative_to(out).as_posix(), "bytes": p.stat().st_size, "sha256": sha256_file(p)}
             for p in sorted(out.rglob("*")) if p.is_file() and p.name != "manifest.json"]
    write_json(out / "manifest.json", {"build_id": build_id, "built_at": now_iso(), "input_bundle": b.bundle_id, "input_manifest_sha256": b.manifest_sha256,
                                       "input_state": b.manifest["state"], "decision_status": b.decision["status"], "profiles": list(want),
                                       "qa_status": summary.get("status"), "qa_report": f"outputs/qa/production/{build_id}/production_qa.json", "files": files,
                                       "design_system": brand.reference(),
                                       "note": "Rascunho de peças; publicação canônica só pelo integrador (--publish) sob trava."})
    return {"build_id": build_id, "path": out, "qa": summary}


def record_visual_review(build: Path, notes: str, reviewer: str) -> dict:
    """Registra a revisão visual das capturas deste build, vinculada aos hashes das peças (portão group_material)."""
    from .release import VISUAL_OK
    qa_dir = REPO / "outputs/qa/production" / build.name
    q = read_json(qa_dir / "production_qa.json")
    if q.get("status") != "passed":
        raise SystemExit(f"QA do build não aprovada ({q.get('status')}); corrigir antes de registrar revisão visual")
    caps = [REPO / c for c in q["captures"]]
    missing = [str(c) for c in caps if not c.is_file()]
    if missing:
        raise SystemExit(f"Capturas ausentes: {missing[:3]}")
    rec = {"build_id": build.name, "reviewed_at": now_iso(), "reviewer": reviewer, "status": VISUAL_OK, "artifacts": q["artifacts"],
           "captures": {c.relative_to(REPO).as_posix(): sha256_file(c) for c in caps},
           "contact_sheets": sorted(p.name for p in qa_dir.glob("*_contact_sheet.png")), "notes": notes,
           "scope": "Layout, legibilidade, sobreposição, contraste e modos (gravação, escuro, 1366×768); não aprova economia nem substitui a revisão do grupo.",
           "human_review": False}
    write_json(qa_dir / "visual_review.json", rec)
    return rec


def baseline_draft(snapshot_arg: str) -> dict:
    """Adapta a fotografia legada (kind=baseline) e informa quais peças o estado habilita; nada é publicado."""
    from . import adapter, consumer, deck_model, snapshot
    snap = snapshot.ensure() if snapshot_arg in ("default", "latest") else Path(snapshot_arg)
    if not (snap / "snapshot.json").is_file():
        raise SystemExit(f"Fotografia inexistente: {snap} (use 'default' ou data/interim/production/baseline/<legacy_id>)")
    p = adapter.adapt(snap)
    errs = consumer.validate(p, allow_kinds=("baseline",))
    report = {"created_at": now_iso(), "snapshot": snap.name, "adapted": p.relative_to(REPO).as_posix(), "valid_as_baseline": not errs, "errors": errs[:10]}
    pieces = {}
    if not errs:
        b = consumer.load(p, allow_kinds=("baseline",))
        try:
            deck_model.build(b)
            pieces["deck12"] = "habilitado"
        except consumer.IncompatibleState as exc:
            pieces["deck12"] = f"indisponível: {exc}"
        valid = sum(c["target_validity"] == "conditional_value" for c in b.cases.values())
        pieces["valores_por_caso"] = f"{valid} de {len(b.cases)} casos com alvo exibível (validade desconhecida vira unresolved)"
        pieces["conferencia_de_fontes"] = f"{len(b.sources)} fontes e {len(b.obs)} observações legíveis pelo consumidor"
    report["pieces"] = pieces
    write_json(REPO / "outputs/qa/production" / f"baseline_{snap.name}" / "compatibility.json", report)
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m production.run", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input-bundle", default=None, help="'latest' ou caminho de outputs/draft/analysis_bundle/<id>")
    ap.add_argument("--profile", choices=PROFILES, default="deck12", help="Perfil da apresentação (12 slides em HTML, PDF e PPTX)")
    ap.add_argument("--output", default="outputs/draft/production", help="Raiz dos builds (só raízes próprias da Parte 2)")
    ap.add_argument("--check", action="store_true", help="Só validar o pacote de entrada (consumidor 1.0)")
    ap.add_argument("--no-qa", action="store_true")
    ap.add_argument("--record-visual-review", metavar="BUILD_DIR", help="Registrar revisão visual das capturas do build (hashes atuais)")
    ap.add_argument("--notes", default="", help="Observações da revisão visual")
    ap.add_argument("--reviewer", default="agente (revisão das capturas)", help="Quem revisou")
    ap.add_argument("--publish", metavar="BUILD_DIR", help="Integrador: publicar build aprovado nos destinos canônicos (sob trava)")
    ap.add_argument("--release-report", action="store_true", help="Avaliar portões de liberação com a evidência atual")
    ap.add_argument("--promote-final", choices=("group_material", "video_submission"),
                    help="Copiar o rascunho publicado para outputs/final só se o portão do estágio passar (nunca envia)")
    ap.add_argument("--baseline", metavar="SNAPSHOT", help="'default' ou data/interim/production/baseline/<legacy_id>: rascunho provisório (kind=baseline)")
    ap.add_argument("--baseline-adapt", action="store_true", help="Atalho de --baseline default")
    a = ap.parse_args(argv)
    from . import consumer, release
    if a.release_report:
        rep = release.report(release.collect())
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        return 0
    if a.promote_final:
        from . import publish
        res = publish.promote_final(a.promote_final)
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0 if res["promoted"] else 2
    if a.baseline or a.baseline_adapt:
        rep = baseline_draft(a.baseline or "default")
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        return 0 if rep["valid_as_baseline"] else 1
    if a.record_visual_review:
        rec = record_visual_review(REPO / a.record_visual_review, a.notes, a.reviewer)
        print(f"Revisão visual registrada: {rec['build_id']} ({len(rec['captures'])} capturas)")
        return 0
    if a.publish:
        from . import publish
        res = publish.publish(REPO / a.publish)
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    if not a.input_bundle:
        ap.error("--input-bundle é obrigatório (use 'latest')")
    out_root = (REPO / a.output).resolve()
    if not out_root.is_relative_to((REPO / "outputs/draft/production").resolve()):
        ap.error("--output deve ficar em outputs/draft/production/ (raiz própria); destinos canônicos só via --publish")
    path = consumer.resolve(a.input_bundle)
    if a.check:
        errs = consumer.validate(path)
        print("Pacote 1.0", "válido" if not errs else "REJEITADO", path.name)
        for e in errs[:20]:
            print("  ", e)
        return 0 if not errs else 1
    try:
        res = build(a.input_bundle, out_root, REPO / "outputs/qa/production", not a.no_qa, a.profile)
    except consumer.IncompatibleState as exc:
        print(f"Peças indisponíveis para este pacote: {exc}")
        return 2
    q = res["qa"]
    print(f"Build {res['build_id']} ({a.profile}): QA {q.get('status')}")
    for k, v in (q.get("checks") or {}).items():
        print(f"  {k}: {v.get('status')}")
    for g in q.get("release_gates", []):
        print(f"  portão {g['stage']}: {'liberado' if g['passed'] else 'bloqueado — ' + '; '.join(g['reasons'][:3])}")
    return 0 if q.get("status") in ("passed", "skipped") else 1


if __name__ == "__main__":
    sys.exit(main())
