"""EN11 — integrador: publica um build aprovado nos destinos canônicos, sob trava, com reversão e manifesto.

Só publica build com QA e revisão visual atuais e pacote analítico válido; executa as suítes de teste no estado
publicado e registra os relatórios de integração. Nunca toca registros humanos (data/interim/decisoes_equipe.md etc.).
`promote_final` só copia para outputs/final quando o portão do estágio passa com evidência real.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from . import consumer, release
from .common import LOCK_PATH, REPO, SAO_PAULO, copy, documentation_lock, now_iso, read_csv, read_json, sha256_file, write_json, write_text

PROCESSED = ["entities.csv", "instruments.csv", "sources.csv", "observations.csv", "definitions.csv", "assumptions.csv", "adjustments.csv",
             "regulatory_terms.csv", "corporate_actions.csv", "claims.csv"]
RESULTS = ["valuation.json", "scenarios.json", "esg_matrix.json", "esg_bridge.json", "presentation_facts.json"]
DRAFT = ["apoio_tecnico.pptx", "apoio_tecnico.pdf", "roteiro_narrativo.md", "script_apresentacao.md", "perguntas_banca.md", "guia_gravacao.md",
         "decisao_proposta.md", "PROXIMOS_PASSOS.md", "pendencias.md", "conciliacao_financeira.md", "auditoria_modelos.md", "LEIA_PRIMEIRO.md",
         "checklist_envio.md"]
# Peças de perfis aposentados (pptx9/html10): saem dos destinos canônicos, com cópia na reversão.
OBSOLETE = ["outputs/draft/script_apresentacao_html10.md", "config/video_segments_html10.json"]
DIRECT = ["outputs/qa/workbook_recalculation.json", "outputs/qa/rendering.json", "outputs/qa/script_word_counts.json", "outputs/qa/html/html_validation.json",
          "outputs/qa/package_validation.json", "data/processed/CANONICAL_SOURCE.json", "outputs/draft/html/manifest.json",
          "outputs/qa/release_validation.json", "outputs/qa/execution_validation.json", "outputs/qa/relatorio_validacao.md"]
SUITES = [("analysis", ["-m", "unittest", "discover", "-s", "tests/analysis", "-p", "test_*.py"]),
          ("production", ["-m", "unittest", "discover", "-s", "tests/production", "-p", "test_*.py"]),
          ("legacy_core", ["-m", "unittest", "tests/test_core.py"])]


def _plan(build: Path, b: consumer.Bundle) -> list[tuple[Path, Path]]:
    D, Q, B = REPO / "outputs/draft", REPO / "outputs/qa", b.path
    pairs = [(build / n, D / n) for n in DRAFT]
    pairs += [(p, D / "figuras" / p.name) for p in sorted((build / "figuras").iterdir())]
    pairs += [(p, D / "teleprompter" / p.name) for p in sorted((build / "teleprompter").iterdir())]
    for ext in ("html", "pdf", "pptx"):
        pairs.append((build / f"html/apresentacao_esg.{ext}", D / f"html/apresentacao_esg.{ext}"))
    # A mesma apresentação final nos nomes de sempre (substitui o deck antigo de nove slides).
    pairs += [(build / "html/apresentacao_esg.pdf", D / "apresentacao_esg.pdf"), (build / "html/apresentacao_esg.pptx", D / "apresentacao_esg.pptx")]
    qa = REPO / "outputs/qa/production" / build.name
    pairs += [(p, Q / "html" / p.name) for p in sorted((qa / "html").glob("*.png"))]
    pairs += [(qa / "visual_review.json", Q / "visual_review.json")]
    pairs += [(B / "workbooks/base_modelo_auditavel.xlsx", D / "base_modelo_auditavel.xlsx")]
    for name in ("base_dados_coletados.xlsx",):
        pairs.append((B / "workbooks" / name, D / "coleta" / name))
    for name in ("model_inputs.json", "relatorio_cobertura.md", "pendencias.csv", "LEIA_PRIMEIRO.md"):
        pairs.append((B / name, D / "coleta" / name))
    pairs += [(B / "tables" / n, REPO / "data/processed" / n) for n in PROCESSED]
    pairs += [(B / "results" / n, REPO / "data/processed" / n) for n in RESULTS]
    pairs += [(B / "tables/financial_reconciliation.csv", REPO / "data/interim/financial_reconciliation.csv"),
              (B / "tables/obligation_schedule.csv", REPO / "data/interim/obligation_schedule.csv")]
    return pairs


def _check_build(build: Path) -> dict:
    man = read_json(build / "manifest.json")
    if man.get("qa_status") != "passed":
        raise PermissionError(f"Build sem QA aprovado: {man.get('qa_status')}")
    if man.get("profiles") != ["deck12"]:
        raise PermissionError(f"Publicação canônica exige o perfil deck12; build tem {man.get('profiles')}")
    for f in man["files"]:
        if sha256_file(build / f["path"]) != f["sha256"]:
            raise PermissionError(f"Build alterado após o QA: {f['path']}")
    qa_dir = REPO / "outputs/qa/production" / build.name
    q = read_json(qa_dir / "production_qa.json")
    vr = qa_dir / "visual_review.json"
    if not vr.is_file() or read_json(vr).get("artifacts") != q["artifacts"] or read_json(vr).get("status") != release.VISUAL_OK:
        raise PermissionError("Revisão visual ausente ou desatualizada para os hashes deste build (--record-visual-review)")
    return man


def _originals() -> dict:
    base = read_json(REPO / "data/catalog/original_files_manifest.json")["files"]
    keep = [f for f in base if f["content_policy"] == "preserve_bytes"]
    bad = [f["current_path"] for f in keep if not (REPO / f["current_path"]).is_file() or sha256_file(REPO / f["current_path"]) != f["sha256"]]
    return {"checked": len(keep), "preserved": len(keep) - len(bad), "changed_or_missing": bad}


def _suites() -> dict:
    out = {}
    for name, args in SUITES:
        p = subprocess.run([sys.executable, *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env={**os.environ, "PYTHONIOENCODING": "utf-8", "OPENBLAS_NUM_THREADS": "1"})
        m = re.search(r"Ran (\d+) tests?", p.stderr)
        skipped = re.search(r"skipped=(\d+)", p.stderr)
        out[name] = {"exit_code": p.returncode, "tests": int(m.group(1)) if m else 0, "skipped": int(skipped.group(1)) if skipped else 0,
                     "tail": p.stderr.strip().splitlines()[-1] if p.stderr.strip() else ""}
    return out


def _report(b, build, qa, suites, originals, gates, pid) -> tuple[dict, str]:
    ok_tests = all(s["exit_code"] == 0 for s in suites.values())
    status = "passed_technical_checks_with_economic_review_pending" if ok_tests and qa["status"] == "passed" and not originals["changed_or_missing"] else "failed"
    sinisa = REPO / "data/processed/sinisa_municipal.csv"
    report = {"created_at": now_iso(), "status": status, "publish_id": pid, "build_id": build.name, "input_bundle": b.bundle_id,
              "input_state": b.manifest["state"], "decision_status": b.decision["status"],
              "errors": [f"suite {k}: código {v['exit_code']}" for k, v in suites.items() if v["exit_code"]] + [f"original alterado: {x}" for x in originals["changed_or_missing"]],
              "source_files_verified": len(b.sources), "canonical_observations": len(b.obs),
              "cvm_accounts": len(read_csv(REPO / "data/processed/cvm_accounts.csv")) if (REPO / "data/processed/cvm_accounts.csv").is_file() else 0,
              "sinisa_municipal_observations": len(read_csv(sinisa)) if sinisa.is_file() else 0,
              "original_assets_preserved": originals["preserved"], "originals": originals,  # contagem, como no registro legado
              "core_tests_exit_code": max(s["exit_code"] for s in suites.values()), "core_test_count": sum(s["tests"] for s in suites.values()),
              "test_suites": suites, "bundle_qa": b.qa.get("status"), "production_qa": qa["status"], "production_checks": len(qa["checks"]),
              "release_gates": gates, "economic_certification": False,
              "verified_scope": ["contrato 1.0 do pacote (hashes, referências, estados)", "QA analítica do pacote (registrada pela Parte 1)",
                                 "peças: autoteste do HTML de 12 slides em 1920/1366 (geometria, navegação, sem controles), offline, PDF e PPTX de 12 páginas, apoio7, números entre formatos, claims, falas e estilo",
                                 "revisão visual do build vinculada aos hashes", "suítes de teste no estado publicado", "preservação dos originais"],
              "note": "Testes verificam contas, formatos e rastreabilidade; não certificam premissas econômicas nem substituem H07–H13."}
    gl = "\n".join(f"| {g['stage']} | {'liberado' if g['passed'] else 'bloqueado'} | {'; '.join(g['reasons']) or '—'} |" for g in gates)
    tl = "\n".join(f"| {k} | {v['tests']} | {v['skipped']} | {v['exit_code']} |" for k, v in suites.items())
    md = f"""# Relatório de validação

Gerado pelo integrador da Parte 2 em {report['created_at']} (publicação `{pid}`).

- Pacote analítico: `{b.bundle_id}` — estado `{b.manifest['state']}`, decisão `{b.decision['status']}`; QA analítica `{b.qa.get('status')}`.
- Build das peças: `{build.name}` — QA `{qa['status']}` ({len(qa['checks'])} verificações); revisão visual vinculada aos hashes.
- Originais preservados: {originals['preserved']} de {originals['checked']}.
- Status: **{status}**.

## Suítes de teste (executadas nesta publicação)

| Suíte | Testes | Pulados | Código |
|---|---:|---:|---:|
{tl}

## Portões de liberação

| Estágio | Situação | Motivos |
|---|---|---|
{gl}

## Escopo e limites

{'; '.join(report['verified_scope'])}.

{report['note']} O agente não envia nada ao Safra.
"""
    return report, md


def publish(build: Path) -> dict:
    man = _check_build(build)
    b = consumer.load(consumer.resolve("latest"))
    if b.bundle_id != man["input_bundle"] or b.manifest_sha256 != man["input_manifest_sha256"]:
        raise PermissionError("Pacote analítico mudou desde o build; regenerar as peças antes de publicar")
    pid = f"pub_{datetime.now(SAO_PAULO).strftime('%Y%m%dT%H%M%S')}"
    rollback = REPO / "data/interim/production/rollback" / pid
    pairs = _plan(build, b)
    copied = []
    with documentation_lock(f"Parte 2: publicação canônica {build.name}"):
        new_caps = {d for _, d in pairs if d.parent == REPO / "outputs/qa/html"}
        stale = [REPO / p for p in OBSOLETE] + [p for p in (REPO / "outputs/qa/html").glob("*.png") if p not in new_caps]
        for dst in [d for _, d in pairs] + [REPO / p for p in DIRECT] + stale:
            if dst.is_file():  # reversão: guarda a versão anterior antes de substituir ou remover (cópias e escritas diretas)
                copy(dst, rollback / dst.relative_to(REPO))
        removed = []
        for old in stale:
            if old.is_file():
                old.unlink()
                removed.append(old.relative_to(REPO).as_posix())
        for src, dst in pairs:
            copy(src, dst, publishing=True)
            copied.append({"path": dst.relative_to(REPO).as_posix(), "sha256": sha256_file(dst), "from": src.relative_to(REPO).as_posix()})
        qa_dir = REPO / "outputs/qa/production" / build.name
        qa = read_json(qa_dir / "production_qa.json")
        bq = b.qa["checks"]["workbook_recalculation"]
        write_json(REPO / "outputs/qa/workbook_recalculation.json", {"created_at": now_iso(), "status": bq.get("status"), "checks": bq.get("checks"),
                   "max_relative_error": bq.get("max_relative_error"), "engine": bq.get("engine"),
                   "delivery_workbook_sha256": sha256_file(REPO / "outputs/draft/base_modelo_auditavel.xlsx"), "source": f"pacote {b.bundle_id} (QA analítica)",
                   "scope": "Fórmulas do caso-base recalculadas no LibreOffice vs Python; não certifica premissas."}, publishing=True)
        pages = qa["checks"]["html_pdf_pages"]["pages"]
        write_json(REPO / "outputs/qa/rendering.json", [{"name": "apresentacao_esg", "pages": pages}, {"name": "html/apresentacao_esg", "pages": pages},
                                                        {"name": "apoio_tecnico", "pages": qa["checks"]["support7_pages"]["pages"]}], publishing=True)
        wc = read_json(build / "script_word_counts.json")
        prof = wc["profiles"]["deck12"]
        # `blocks` (bloco/voz/tempo/palavras) é lido pelos verificadores documentais
        blocks = [{"block": k, "slide": v["slide"], "speaker": v["speaker"], "time": f"{v['seconds']} s", "words": v["words"]} for k, v in wc["blocks"].items()]
        write_json(REPO / "outputs/qa/script_word_counts.json", {"profile": "deck12", "total_words": prof["total_words"], "planned_seconds": prof["planned_seconds"],
                                                                 "blocks": blocks, "profiles": wc["profiles"], "source": build.name,
                                                                 "note": "Contagem planejada; nenhum ensaio ou gravação real inferido."}, publishing=True)
        write_json(REPO / "outputs/qa/html/html_validation.json", {"build_id": build.name, "selftest_1920": qa["checks"]["html_selftest_1920"],
                   "selftest_1366": qa["checks"]["html_selftest_1366"], "offline": qa["checks"]["html_offline"],
                   "flat_no_controls": qa["checks"]["html_flat_no_controls"], "pdf_pages": qa["checks"]["html_pdf_pages"],
                   "pptx_pages": qa["checks"]["pptx_pages"], "browser": qa["checks"]["html_selftest_1920"].get("browser")}, publishing=True)
        write_json(REPO / "outputs/qa/package_validation.json", {"created_at": now_iso(), "status": qa["status"], "checks": len(qa["checks"]),
                   "source": f"outputs/qa/production/{build.name}/production_qa.json", "scope": qa["scope"]}, publishing=True)
        write_json(REPO / "data/processed/CANONICAL_SOURCE.json", {"bundle_id": b.bundle_id, "manifest_sha256": b.manifest_sha256, "published_by": "production",
                   "publish_id": pid, "schema": "contrato 1.0 (value_id/claims); o pipeline legado (--legacy) usa outro esquema"}, publishing=True)
        manifest = {"publish_id": pid, "published_at": now_iso(), "build_id": build.name, "input_bundle": b.bundle_id,
                    "input_manifest_sha256": b.manifest_sha256, "files": copied, "removed_obsolete": removed, "rollback": rollback.relative_to(REPO).as_posix(),
                    "final_promoted": False, "note": "Rascunhos canônicos; outputs/final permanece reservado até os portões de grupo/vídeo."}
        write_json(REPO / "outputs/draft/html/manifest.json", {k: manifest[k] for k in ("publish_id", "build_id", "input_bundle")} |
                   {"files": [c for c in copied if c["path"].startswith("outputs/draft/html/")]}, publishing=True)
        write_json(REPO / "outputs/draft/production/published.json", manifest)
        # Verificação no estado publicado: suítes, originais e portões (evidência real, sem injeção)
        suites, originals = _suites(), _originals()
        gates = release.report(release.collect(b.path, qa_dir / "production_qa.json"))
        write_json(REPO / "outputs/qa/release_validation.json", {"created_at": now_iso(), "publish_id": pid, "build_id": build.name, "gates": gates,
                   "note": "Portões avaliados com evidência real do workspace; nenhum registro humano presumido."}, publishing=True)
        report, md = _report(b, build, qa, suites, originals, gates, pid)
        write_json(REPO / "outputs/qa/execution_validation.json", report, publishing=True)
        write_text(REPO / "outputs/qa/relatorio_validacao.md", md, publishing=True)
        manifest.update(validation_status=report["status"], test_suites={k: (v["tests"], v["exit_code"]) for k, v in suites.items()})
        write_json(REPO / "outputs/draft/production/published.json", manifest)
    return {"publish_id": pid, "build_id": build.name, "copied": len(copied), "rollback": manifest["rollback"], "validation": report["status"],
            "tests": {k: f"{v['tests']} testes, código {v['exit_code']}" for k, v in suites.items()},
            "gates": {g["stage"]: g["passed"] for g in gates}}


BANNER = re.compile(r"<!-- PROJECT_STATUS:START -->.*?<!-- PROJECT_STATUS:END -->\n*", re.S)


def _same_without_banner(published: Path, source: Path) -> bool:
    """Markdown publicado pode receber só o banner do sincronizador documental; o resto deve ser o arquivo do build."""
    if published.suffix != ".md" or not source.is_file():
        return False
    strip = lambda p: BANNER.sub("", p.read_text(encoding="utf-8")).strip()
    return strip(published) == strip(source)


def promote_final(stage: str = "group_material", ev: dict | None = None, target: Path | None = None, lock_path: Path = LOCK_PATH) -> dict:
    """Copia o rascunho canônico publicado para outputs/final só se o portão do estágio passar.

    `ev`/`target` existem para a sandbox de testes (evidência injetada e raiz temporária); no uso real a evidência
    vem de release.collect() e o destino é outputs/final/. Nunca envia nada.
    """
    ev = ev if ev is not None else release.collect()
    gate = release.evaluate(stage, ev)
    if not gate["passed"]:
        return {"promoted": False, "stage": stage, "reasons": gate["reasons"]}
    if not (REPO / "outputs/draft/production/published.json").is_file():
        return {"promoted": False, "stage": stage, "reasons": ["nenhuma publicação canônica do integrador (--publish)"]}
    pub = read_json(REPO / "outputs/draft/production/published.json")
    root = target or REPO / "outputs/final"
    files = [f for f in pub["files"] if f["path"].startswith("outputs/draft/") and not f["path"].startswith("outputs/draft/coleta/")]
    copied = []
    with documentation_lock(f"Parte 2: promoção final ({stage})", lock_path):
        for f in files:
            src = REPO / f["path"]
            if sha256_file(src) != f["sha256"] and not _same_without_banner(src, REPO / f["from"]):
                raise PermissionError(f"Rascunho publicado alterado depois da publicação: {f['path']}")
            dst = root / Path(f["path"]).relative_to("outputs/draft")
            copy(src, dst, publishing=True)
            copied.append({"path": dst.as_posix(), "sha256": f["sha256"]})
        write_json(root / "manifest.json", {"promoted_at": now_iso(), "stage": stage, "publish_id": pub["publish_id"], "build_id": pub["build_id"],
                                            "input_bundle": pub["input_bundle"], "files": copied, "submitted": False}, publishing=True)
    return {"promoted": True, "stage": stage, "files": len(copied), "submitted": False}
