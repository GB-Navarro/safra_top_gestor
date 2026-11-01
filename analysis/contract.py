"""Validação do contrato comum 1.0 (produtor: análise). Usada antes de publicar e nos testes negativos.

Opera sobre um diretório de pacote; não importa código de produção.
"""
from __future__ import annotations

import csv
import io
import json
import math
import re
from pathlib import Path, PurePosixPath

from .common import sha256_file

SCHEMA_VERSION = "1.0"
MIN_FILES = ["manifest.json", "metadata.json", "model_inputs.json", "relatorio_cobertura.md", "tables/entities.csv", "tables/instruments.csv",
             "tables/sources.csv", "tables/observations.csv", "tables/definitions.csv", "tables/assumptions.csv", "tables/adjustments.csv",
             "tables/regulatory_terms.csv", "tables/corporate_actions.csv", "tables/financial_reconciliation.csv", "tables/obligation_schedule.csv",
             "tables/claims.csv", "results/valuation.json", "results/scenarios.json", "results/esg_matrix.json", "results/esg_bridge.json",
             "results/presentation_facts.json", "results/narrative.json", "results/recommendation.json", "workbooks/base_dados_coletados.xlsx",
             "workbooks/base_modelo_auditavel.xlsx", "qa/analysis_validation.json", "LEIA_PRIMEIRO.md", "pendencias.csv"]
MANIFEST_FIELDS = ["schema_version", "bundle_id", "kind", "state", "market_asof", "valuation_date", "information_cutoff", "built_at", "files",
                   "external_evidence", "requirement_dispositions", "human_records", "limitations"]
STATES = {"analysis_incomplete", "analysis_proposed", "group_adopted"}
KINDS = {"analysis", "baseline", "fixture"}
OBS_FIELDS = ["value_id", "entity_id", "instrument_id", "metric_id", "value", "value_state", "unit", "scale", "period_start", "period_end",
              "observed_at", "scope", "definition_id", "fact_type", "source_refs", "assumption_refs", "calculation_ref"]
VALUE_STATES = {"observed", "derived", "assumed", "missing", "not_applicable"}
FACT_TYPES = {"fact", "assumption", "inference", "derived"}
CASE_FIELDS = ["case_id", "entity_id", "instrument_id", "scenario_id", "dimensions", "value_refs", "wacc", "g", "terminal_method",
               "equity_residual_before_floor", "equity_floor_applied", "paper_value", "target_validity", "assumption_refs", "limitations"]
VALIDITY = {"conditional_value", "no_meaningful_target", "unresolved"}
CLAIM_FIELDS = ["claim_id", "claim_type", "text_template", "value_refs", "source_refs", "assumption_refs", "calculation_refs", "status", "limitations"]
SLOTS = ["lead", "sector", "swot", "medium_term", "esg", "bridge", "valuation_method", "valuation_result", "risks", "conclusion"]
VIEW_TYPES = {"table", "bar", "line", "matrix", "scatter", "heatmap", "bridge"}
POINT_ROLES = {"ordinary", "start", "delta", "end"}
TABLE_HEADERS = {
    "tables/entities.csv": ["entity_id", "legal_name", "cvm_code", "cnpj", "currency", "identity_status"],
    "tables/instruments.csv": ["instrument_id", "entity_id", "ticker", "security_class", "currency", "bloomberg_security", "unit_components", "identity_status"],
    "tables/sources.csv": ["source_id", "issuer", "title", "url", "local_path", "published_at", "retrieved_at", "sha256", "access_method",
                           "reference_date", "version", "access_status"],
    "tables/definitions.csv": ["definition_id", "entity_id", "metric_id", "numerator", "denominator", "unit", "scope", "methodology",
                               "methodology_valid_from", "source_ids", "comparability_status"],
    "tables/assumptions.csv": ["assumption_id", "entity_id", "driver", "year", "base", "adverse", "favorable", "unit", "rationale",
                               "supporting_obs_ids", "owner", "reviewer", "approval_status", "source_id", "source_location", "value_refs"],
    "tables/observations.csv": OBS_FIELDS,
    "tables/claims.csv": CLAIM_FIELDS,
}
TOKEN = re.compile(r"\{\{value:([^}]+)\}\}")


def _strict_json(path: Path):
    text = path.read_text(encoding="utf-8")
    return json.loads(text, parse_constant=lambda c: (_ for _ in ()).throw(ValueError(f"constante inválida {c}")))


def _csv(path: Path) -> tuple[list[str], list[dict]]:
    text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    return list(reader.fieldnames or []), list(reader)


def _list(cell: str, where: str, errors: list) -> list:
    if cell == "":
        return []
    try:
        v = json.loads(cell)
    except json.JSONDecodeError:
        errors.append(f"{where}: lista não está em JSON")
        return []
    if not isinstance(v, list):
        errors.append(f"{where}: esperado lista JSON")
        return []
    return v


def validate(bundle: Path, *, allow_kinds=("analysis",), require_files=True) -> dict:
    bundle = Path(bundle)
    errors: list[str] = []
    warnings: list[str] = []
    if require_files:
        for f in MIN_FILES:
            if not (bundle / f).is_file():
                errors.append(f"Arquivo mínimo ausente: {f}")
    if errors:
        return {"status": "failed", "errors": errors, "warnings": warnings}
    man = _strict_json(bundle / "manifest.json")
    for k in MANIFEST_FIELDS:
        if k not in man:
            errors.append(f"manifest sem campo {k}")
    if man.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version incompatível: {man.get('schema_version')!r}")
    if man.get("kind") not in KINDS:
        errors.append(f"kind inválido: {man.get('kind')}")
    elif man.get("kind") not in allow_kinds:
        errors.append(f"kind '{man.get('kind')}' recusado neste carregador")
    if man.get("state") not in STATES:
        errors.append(f"state inválido: {man.get('state')}")
    if man.get("bundle_id") != bundle.name and not bundle.name.startswith(".tmp_"):
        errors.append("bundle_id diverge do diretório")
    if (man.get("market_asof"), man.get("valuation_date")) != ("2026-10-30", "2026-10-30"):
        errors.append("recortes de mercado/avaliação divergem de 30/10/2026")
    seen = set()
    listed = set()
    for f in man.get("files", []):
        p = PurePosixPath(f.get("path", ""))
        if p.is_absolute() or ".." in p.parts or str(p) == "manifest.json":
            errors.append(f"caminho inválido no manifesto: {p}")
            continue
        if str(p) in seen:
            errors.append(f"arquivo duplicado no manifesto: {p}")
        seen.add(str(p))
        listed.add(str(p))
        fp = bundle / str(p)
        if not fp.is_file():
            errors.append(f"arquivo do manifesto ausente: {p}")
            continue
        if fp.stat().st_size != f.get("bytes") or sha256_file(fp) != f.get("sha256"):
            errors.append(f"hash/bytes divergentes: {p}")
    for f in MIN_FILES:
        if f != "manifest.json" and f not in listed:
            errors.append(f"arquivo mínimo fora do manifesto: {f}")
    for ev in man.get("external_evidence", []):
        if not ev.get("sha256") or not ev.get("path"):
            errors.append(f"evidência externa sem caminho/hash: {ev.get('id')}")
    for d in man.get("requirement_dispositions", []):
        if not {"requirement_id", "slice", "status", "evidence_refs", "limitations"} <= set(d):
            errors.append(f"disposição incompleta: {d.get('requirement_id')}")
    # Tabelas
    obs = {}
    for rel, header in TABLE_HEADERS.items():
        got, rows = _csv(bundle / rel)
        missing = [h for h in header if h not in got]
        if missing:
            errors.append(f"{rel}: campos ausentes {missing}")
        if rel == "tables/observations.csv":
            for r in rows:
                vid = r["value_id"]
                if vid in obs:
                    errors.append(f"value_id duplicado: {vid}")
                obs[vid] = r
                if r["value_state"] not in VALUE_STATES:
                    errors.append(f"{vid}: value_state inválido")
                if r["fact_type"] not in FACT_TYPES:
                    errors.append(f"{vid}: fact_type inválido")
                val = r["value"]
                if r["value_state"] in {"missing", "not_applicable"}:
                    if val != "":
                        errors.append(f"{vid}: {r['value_state']} exige valor vazio")
                else:
                    try:
                        x = float(val)
                        if not math.isfinite(x):
                            errors.append(f"{vid}: valor não finito")
                    except ValueError:
                        errors.append(f"{vid}: valor não numérico {val!r}")
                try:
                    float(r["scale"])
                except ValueError:
                    errors.append(f"{vid}: scale não numérica")
                _list(r["source_refs"], vid, errors)
                _list(r["assumption_refs"], vid, errors)
                if r["value_state"] == "observed" and not _list(r["source_refs"], vid, []):
                    errors.append(f"{vid}: observação sem fonte")
    _, srcs = _csv(bundle / "tables/sources.csv")
    source_ids = {r["source_id"] for r in srcs}
    _, defs = _csv(bundle / "tables/definitions.csv")
    def_ids = {r["definition_id"] for r in defs}
    for vid, r in obs.items():
        for s in _list(r["source_refs"], vid, []):
            if s not in source_ids:
                errors.append(f"{vid}: fonte não resolvida {s}")
        if r["definition_id"] not in def_ids:
            errors.append(f"{vid}: definição não resolvida {r['definition_id']}")
    _, ass = _csv(bundle / "tables/assumptions.csv")
    ass_ids = {r["assumption_id"] for r in ass}
    _, claims = _csv(bundle / "tables/claims.csv")
    claim_ids = set()
    for cl in claims:
        cid = cl["claim_id"]
        claim_ids.add(cid)
        for t in TOKEN.findall(cl["text_template"]):
            if t not in obs:
                errors.append(f"{cid}: token sem valor {t}")
        for t in _list(cl["value_refs"], cid, errors):
            if t not in obs:
                errors.append(f"{cid}: value_ref não resolvido {t}")
        for a in _list(cl["assumption_refs"], cid, errors):
            if a not in ass_ids:
                errors.append(f"{cid}: premissa não resolvida {a}")
        for s in _list(cl["source_refs"], cid, errors):
            if s not in source_ids:
                errors.append(f"{cid}: fonte não resolvida {s}")
        if re.search(r"\d+[.,]\d{2,}", TOKEN.sub("", cl["text_template"])):
            warnings.append(f"{cid}: número literal no texto (verificar se é rótulo e não valor)")
    # Resultados
    results = {}
    for name in ("valuation", "scenarios", "esg_matrix", "esg_bridge", "presentation_facts", "narrative", "recommendation"):
        d = _strict_json(bundle / f"results/{name}.json")
        results[name] = d
        if d.get("schema_version") != SCHEMA_VERSION or d.get("bundle_id") != man.get("bundle_id"):
            errors.append(f"results/{name}.json: schema/bundle_id divergentes")
    case_ids = set()
    for name in ("valuation", "scenarios"):
        for cs in results[name].get("cases", []):
            cid = cs.get("case_id")
            for k in CASE_FIELDS:
                if k not in cs:
                    errors.append(f"{name}:{cid} sem campo {k}")
            if cs.get("target_validity") not in VALIDITY:
                errors.append(f"{name}:{cid} validade inválida")
            pv = cs.get("paper_value")
            if cs.get("target_validity") == "conditional_value":
                if not isinstance(pv, (int, float)) or pv < 0 or not (cs.get("equity_residual_before_floor") or 0) > 0:
                    errors.append(f"{name}:{cid} valor condicional exige paper_value ≥0 e resíduo positivo")
            elif pv is not None:
                errors.append(f"{name}:{cid} paper_value deve ser null quando {cs.get('target_validity')}")
            if not isinstance(cs.get("equity_floor_applied"), bool):
                errors.append(f"{name}:{cid} equity_floor_applied não booleano")
            for field, ref in cs.get("value_refs", {}).items():
                if ref not in obs:
                    errors.append(f"{name}:{cid} value_ref não resolvido {ref}")
                    continue
                if field in cs and isinstance(cs[field], (int, float)) and not isinstance(cs[field], bool):
                    x = float(obs[ref]["value"])
                    if abs(x - cs[field]) > 1e-9 * max(1.0, abs(x)):
                        errors.append(f"{name}:{cid} {field} não coincide com {ref}")
            for axis, opt in cs.get("dimensions", {}).items():
                if not {"option_id", "label", "value_ref"} <= set(opt):
                    errors.append(f"{name}:{cid} dimensão {axis} incompleta")
                elif opt["value_ref"] is not None and opt["value_ref"] not in obs:
                    errors.append(f"{name}:{cid} dimensão {axis} com value_ref inexistente")
            for a in cs.get("assumption_refs", []):
                if a not in ass_ids:
                    errors.append(f"{name}:{cid} premissa não resolvida {a}")
            if name == "valuation":
                if cid in case_ids:
                    errors.append(f"case_id duplicado {cid}")
                case_ids.add(cid)
    bridge_ids = set()
    for cs in results["esg_bridge"].get("cases", []):
        bridge_ids.add(cs["case_id"])
        for ref in cs.get("value_refs", {}).values():
            if ref not in obs:
                errors.append(f"esg_bridge:{cs['case_id']} value_ref não resolvido {ref}")
    for row in results["esg_matrix"].get("rows", []):
        for e, cell in row.get("cells", {}).items():
            for ref in cell.get("value_refs", []):
                if ref not in obs:
                    errors.append(f"esg_matrix:{row.get('row_id')}:{e} value_ref não resolvido {ref}")
    slots = results["narrative"].get("slots", {})
    if list(slots) != SLOTS:
        errors.append(f"narrative: slots devem ser exatamente {SLOTS}")
    for s, ids in slots.items():
        if not ids:
            errors.append(f"narrative: slot vazio {s}")
        for i in ids:
            if i not in claim_ids:
                errors.append(f"narrative:{s} claim inexistente {i}")
    all_cases = case_ids | bridge_ids
    for view in results["presentation_facts"].get("views", []):
        vid = view.get("view_id")
        if view.get("view_type") not in VIEW_TYPES:
            errors.append(f"view {vid}: tipo inválido")
        if view.get("slot") not in SLOTS:
            errors.append(f"view {vid}: slot inválido")
        for c in view.get("claim_refs", []):
            if c not in claim_ids:
                errors.append(f"view {vid}: claim inexistente {c}")
        for se in view.get("series", []):
            for p in se.get("points", []):
                if p.get("point_role") not in POINT_ROLES:
                    errors.append(f"view {vid}: point_role inválido")
                if p.get("y_value_ref") not in obs:
                    errors.append(f"view {vid}: y_value_ref inexistente {p.get('y_value_ref')}")
                if p.get("x_value_ref") and p["x_value_ref"] not in obs:
                    errors.append(f"view {vid}: x_value_ref inexistente")
                if p.get("case_ref") and p["case_ref"] not in all_cases:
                    errors.append(f"view {vid}: case_ref inexistente {p['case_ref']}")
                for c in p.get("claim_refs", []):
                    if c not in claim_ids:
                        errors.append(f"view {vid}: claim de ponto inexistente {c}")
        if view.get("view_type") == "bridge":
            roles = [p["point_role"] for se in view["series"] for p in se["points"]]
            if roles[:1] != ["start"] or roles[-1:] != ["end"]:
                errors.append(f"view {vid}: ponte exige start e end declarados")
    dec = results["recommendation"].get("decision", {})
    if dec.get("status") not in {"proposed", "adopted", "unresolved"}:
        errors.append("decision.status inválido")
    if dec.get("status") == "adopted" and not dec.get("human_record_refs"):
        errors.append("decisão adotada exige registros reais H08/H09")
    if man.get("state") == "group_adopted" and dec.get("status") != "adopted":
        errors.append("state group_adopted exige decision.status=adopted")
    for k in ("rationale_claim_refs", "alternative_claim_refs", "trigger_claim_refs"):
        for c in dec.get(k, []):
            if c not in claim_ids:
                errors.append(f"decision.{k}: claim inexistente {c}")
    mi = _strict_json(bundle / "model_inputs.json")
    for e, inputs in mi.get("entities", {}).items():
        for k, ref in inputs.get("value_refs", {}).items():
            if ref not in obs:
                errors.append(f"model_inputs:{e}:{k} value_ref inexistente {ref}")
    return {"status": "passed" if not errors else "failed", "errors": errors, "warnings": warnings,
            "counts": {"observations": len(obs), "claims": len(claim_ids), "cases": len(case_ids), "views": len(results["presentation_facts"].get("views", []))}}
