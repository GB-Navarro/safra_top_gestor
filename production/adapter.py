"""EN02 — adaptador do baseline legado para a forma do contrato 1.0 (kind=baseline, state=baseline_unreconciled).

Uso só em rascunho/QA explícito. Validade de alvo desconhecida vira `unresolved`; nada é preenchido com zero.
Peças que exigem claims/slots ausentes ficam indisponíveis (o deck só aceita kind=analysis).
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from .common import REPO, now_iso, read_csv, read_json, sha256_file, write_csv, write_json
from .consumer import MIN_FILES, SLOTS
from .snapshot import ensure

OUT = REPO / "data/interim/production/baseline_adapted"
HEADERS = {
    "tables/entities.csv": ["entity_id", "legal_name", "cvm_code", "cnpj", "currency", "identity_status"],
    "tables/instruments.csv": ["instrument_id", "entity_id", "ticker", "security_class", "currency", "bloomberg_security", "unit_components", "identity_status"],
    "tables/sources.csv": ["source_id", "issuer", "title", "url", "local_path", "published_at", "retrieved_at", "sha256", "access_method", "reference_date",
                           "version", "access_status"],
    "tables/definitions.csv": ["definition_id", "entity_id", "metric_id", "numerator", "denominator", "unit", "scope", "methodology",
                               "methodology_valid_from", "source_ids", "comparability_status"],
}
OBS = ["value_id", "entity_id", "instrument_id", "metric_id", "value", "value_state", "unit", "scale", "period_start", "period_end", "observed_at", "scope",
       "definition_id", "fact_type", "source_refs", "assumption_refs", "calculation_ref"]


def adapt(snap: Path | None = None) -> Path:
    snap = snap or ensure()
    F = snap / "files"
    bid = f"baseline_{snap.name}"
    out = OUT / bid
    if out.exists():
        shutil.rmtree(out)
    P = lambda rel: F / rel
    for rel, header in HEADERS.items():
        src = P("data/processed/" + rel.split("/")[1])
        write_csv(out / rel, read_csv(src) if src.is_file() else [], header)
    obs = []
    for r in read_csv(P("data/processed/observations.csv")):
        obs.append({"value_id": r["obs_id"], "entity_id": r["entity_id"], "instrument_id": r["instrument_id"], "metric_id": r["metric_id"], "value": r["value"],
                    "value_state": "observed", "unit": r["unit"], "scale": r["scale"], "period_start": r["period_start"], "period_end": r["period_end"],
                    "observed_at": r["observed_at"], "scope": r["scope"], "definition_id": r["definition_id"], "fact_type": "fact",
                    "source_refs": [r["source_id"]] if r["source_id"] else [], "assumption_refs": [], "calculation_ref": ""})
    write_csv(out / "tables/observations.csv", obs, OBS)
    # Claims legados (text/source_ids/obs_ids separados por ';') para as colunas do contrato; texto sem tokens.
    split = lambda cell: [x for x in (cell or "").split(";") if x]
    legacy_claims = read_csv(P("data/processed/claims.csv")) if P("data/processed/claims.csv").is_file() else []
    write_csv(out / "tables/claims.csv", [{"claim_id": r["claim_id"], "claim_type": r["claim_type"], "text_template": r["text"],
                                           "value_refs": split(r.get("obs_ids")), "source_refs": split(r.get("source_ids")), "assumption_refs": [],
                                           "calculation_refs": split(r.get("calculation_id")), "status": "baseline_unreconciled",
                                           "limitations": [x for x in (r.get("caveat"), "claim legado sem conciliação") if x]} for r in legacy_claims],
              ["claim_id", "claim_type", "text_template", "value_refs", "source_refs", "assumption_refs", "calculation_refs", "status", "limitations"])
    for rel in ("assumptions", "adjustments", "regulatory_terms", "corporate_actions"):
        src = P(f"data/processed/{rel}.csv")
        rows = read_csv(src) if src.is_file() else []
        write_csv(out / f"tables/{rel}.csv", rows, list(rows[0].keys()) if rows else ["id"])
    for rel in ("financial_reconciliation", "obligation_schedule"):
        write_csv(out / f"tables/{rel}.csv", [], ["status"])
    legacy = read_json(P("data/processed/valuation.json"))
    cases = []
    for e, r in legacy.items():
        # Legado não guarda resíduo/validade por ponto de grade: estado desconhecido, nunca alvo exibível.
        for s in r.get("scenarios", []) + [{"label": f"grid {x['wacc']}/{x['g']}", **x} for x in r.get("sensitivity", [])]:
            cases.append({"case_id": f"baseline.{e}.{len(cases)}", "entity_id": e, "instrument_id": r["ticker"], "scenario_id": s["label"], "dimensions": {},
                          "value_refs": {}, "wacc": s.get("wacc"), "g": s.get("g"), "terminal_method": "legacy", "equity_residual_before_floor": None,
                          "equity_floor_applied": False, "paper_value": None, "target_validity": "unresolved", "assumption_refs": [],
                          "limitations": ["baseline_unreconciled: resíduo e validade por ponto ausentes no legado"]})
    head = {"schema_version": "1.0", "bundle_id": bid}
    write_json(out / "results/valuation.json", {**head, "cases": cases})
    write_json(out / "results/scenarios.json", {**head, "cases": []})
    write_json(out / "results/esg_matrix.json", {**head, "rows": []})
    write_json(out / "results/esg_bridge.json", {**head, "cases": []})
    write_json(out / "results/presentation_facts.json", {**head, "views": []})
    write_json(out / "results/narrative.json", {**head, "slots": {s: [] for s in SLOTS}})
    write_json(out / "results/recommendation.json", {**head, "decision": {"status": "unresolved", "rationale_claim_refs": [], "alternative_claim_refs": [],
                                                                          "trigger_claim_refs": [], "human_record_refs": []}})
    write_json(out / "model_inputs.json", {**head, "entities": {}, "note": "baseline: entradas do ramo revisado inexistentes"})
    write_json(out / "metadata.json", {**head, "kind": "baseline", "source_snapshot": snap.name, "limitations": ["adaptação provisória; não é análise"]})
    write_json(out / "qa/analysis_validation.json", {**head, "status": "not_applicable_baseline"})
    (out / "relatorio_cobertura.md").write_text("# Baseline adaptado\n\nFotografia legada sem conciliação; uso só em rascunho.\n", encoding="utf-8")
    (out / "LEIA_PRIMEIRO.md").write_text("# Baseline provisório\n\nNão é pacote analítico. Validade dos alvos desconhecida.\n", encoding="utf-8")
    write_csv(out / "pendencias.csv", [{"requirement_id": "C21", "disposition": "baseline_unreconciled"}], ["requirement_id", "disposition"])
    (out / "workbooks").mkdir(parents=True, exist_ok=True)
    for name, src in (("base_dados_coletados.xlsx", "outputs/draft/coleta/base_dados_coletados.xlsx"), ("base_modelo_auditavel.xlsx", "outputs/draft/base_modelo_auditavel.xlsx")):
        shutil.copy2(F / src, out / "workbooks" / name)
    files = [{"path": p.relative_to(out).as_posix(), "bytes": p.stat().st_size, "sha256": sha256_file(p)}
             for p in sorted(out.rglob("*")) if p.is_file() and p.name != "manifest.json"]
    write_json(out / "manifest.json", {**head, "kind": "baseline", "state": "baseline_unreconciled", "market_asof": "2026-10-30", "valuation_date": "2026-10-30",
                                       "information_cutoff": "2026-10-31T18:25:27-03:00", "built_at": now_iso(), "files": files, "external_evidence": [],
                                       "requirement_dispositions": [], "human_records": [], "limitations": ["baseline_unreconciled"]})
    missing = [f for f in MIN_FILES if not (out / f).is_file()]
    if missing:
        raise RuntimeError(f"Adaptador incompleto: {missing}")
    return out
