"""EN02 — consumidor do contrato 1.0: validação independente, leitura e formatação pt-BR.

Rejeita versão major desconhecida, hash/caminho inválido, referência quebrada e estado incoerente.
`kind=fixture` só é aceito em QA; `kind=baseline` só em rascunho explícito.
"""
from __future__ import annotations

import csv
import io
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from .common import REPO, read_json, sha256_file

MIN_FILES = ["manifest.json", "metadata.json", "model_inputs.json", "relatorio_cobertura.md", "tables/entities.csv", "tables/instruments.csv",
             "tables/sources.csv", "tables/observations.csv", "tables/definitions.csv", "tables/assumptions.csv", "tables/adjustments.csv",
             "tables/regulatory_terms.csv", "tables/corporate_actions.csv", "tables/financial_reconciliation.csv", "tables/obligation_schedule.csv",
             "tables/claims.csv", "results/valuation.json", "results/scenarios.json", "results/esg_matrix.json", "results/esg_bridge.json",
             "results/presentation_facts.json", "results/narrative.json", "results/recommendation.json", "workbooks/base_dados_coletados.xlsx",
             "workbooks/base_modelo_auditavel.xlsx", "qa/analysis_validation.json", "LEIA_PRIMEIRO.md", "pendencias.csv"]
SLOTS = ["lead", "sector", "swot", "medium_term", "esg", "bridge", "valuation_method", "valuation_result", "risks", "conclusion"]
VALIDITY = {"conditional_value", "no_meaningful_target", "unresolved"}
REQUIRED_COLUMNS = {"tables/observations.csv": {"value_id", "entity_id", "metric_id", "value", "value_state", "unit", "scale", "source_refs"},
                    "tables/claims.csv": {"claim_id", "claim_type", "text_template", "value_refs", "source_refs", "status", "limitations"},
                    "tables/sources.csv": {"source_id", "title", "url", "published_at"}}
STATES = {"analysis_incomplete", "analysis_proposed", "group_adopted", "baseline_unreconciled"}
TOKEN = re.compile(r"\{\{(value|entity|ticker):([^}|]+)(?:\|([a-z_]+))?\}\}")
ENTITY_NAME = {"sabesp": "Sabesp", "copasa": "Copasa", "sanepar": "Sanepar"}


class IncompatibleState(ValueError):
    """Pacote válido, mas em estado que não habilita a peça pedida (ex.: sem decisão proposta)."""


class BundleRejected(ValueError):
    pass


def _strict(path: Path):
    return read_json(path)


def _csv(path: Path) -> list[dict]:
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8"))))


def _jl(cell: str) -> list:
    if not cell:
        return []
    v = json.loads(cell)
    if not isinstance(v, list):
        raise ValueError("lista esperada")
    return v


def resolve(arg: str | Path) -> Path:
    """'latest' → ponteiro atômico (com conferência do hash do manifesto); senão caminho do pacote."""
    if str(arg) == "latest":
        ptr = read_json(REPO / "outputs/draft/analysis_bundle/latest.json")
        path = REPO / ptr["path"]
        if sha256_file(path / "manifest.json") != ptr["manifest_sha256"]:
            raise BundleRejected("latest.json aponta para manifesto com hash diferente")
        return path
    p = Path(arg)
    return p if p.is_absolute() else REPO / p


def validate(path: Path, allow_kinds=("analysis",)) -> list[str]:
    errors: list[str] = []
    for f in MIN_FILES:
        if not (path / f).is_file():
            errors.append(f"arquivo ausente: {f}")
    if errors:
        return errors
    man = _strict(path / "manifest.json")
    major = str(man.get("schema_version", "")).split(".")[0]
    if major != "1":
        return [f"versão major incompatível: {man.get('schema_version')!r}"]
    if man.get("kind") not in allow_kinds:
        errors.append(f"kind '{man.get('kind')}' não aceito neste modo")
    if man.get("state") not in STATES:
        errors.append(f"state inválido: {man.get('state')}")
    root = path.resolve()
    listed = set()
    for f in man.get("files", []):
        rel = PurePosixPath(f.get("path", ""))
        if rel.is_absolute() or ".." in rel.parts:
            errors.append(f"caminho fora da raiz: {rel}")
            continue
        fp = (path / str(rel)).resolve()
        if root not in fp.parents:
            errors.append(f"caminho fora da raiz: {rel}")
            continue
        listed.add(str(rel))
        if not fp.is_file() or fp.stat().st_size != f.get("bytes") or sha256_file(fp) != f.get("sha256"):
            errors.append(f"hash/bytes divergentes: {rel}")
    missing = [f for f in MIN_FILES if f != "manifest.json" and f not in listed]
    if missing:
        errors.append(f"arquivos fora do manifesto: {missing}")
    if errors:
        return errors
    for rel, cols in REQUIRED_COLUMNS.items():
        with open(path / rel, encoding="utf-8", newline="") as f:
            header = set(next(csv.reader(f), []))
        if cols - header:
            errors.append(f"{rel}: colunas ausentes {sorted(cols - header)}")
    if errors:
        return errors
    obs = {}
    for r in _csv(path / "tables/observations.csv"):
        if r["value_state"] in {"missing", "not_applicable"}:
            if r["value"] != "":
                errors.append(f"{r['value_id']}: ausente com número")
        else:
            try:
                if not math.isfinite(float(r["value"])):
                    errors.append(f"{r['value_id']}: não finito")
            except ValueError:
                errors.append(f"{r['value_id']}: valor inválido")
        obs[r["value_id"]] = r
    sources = {r["source_id"] for r in _csv(path / "tables/sources.csv")}
    for vid, r in obs.items():
        errors += [f"{vid}: fonte {s} inexistente" for s in _jl(r["source_refs"]) if s not in sources]
    claims = {r["claim_id"]: r for r in _csv(path / "tables/claims.csv")}
    for cid, c in claims.items():
        errors += [f"{cid}: fonte {s} inexistente" for s in _jl(c["source_refs"]) if s not in sources]
        for kind, ref, _ in TOKEN.findall(c["text_template"]):
            if kind == "value" and ref not in obs:
                errors.append(f"{cid}: token sem valor {ref}")
    val = _strict(path / "results/valuation.json")
    case_ids = set()
    for c in val.get("cases", []):
        case_ids.add(c["case_id"])
        if c.get("target_validity") not in VALIDITY:
            errors.append(f"{c['case_id']}: validade inválida")
        if c.get("target_validity") != "conditional_value" and c.get("paper_value") is not None:
            errors.append(f"{c['case_id']}: valor exibível sem validade")
        if c.get("target_validity") == "conditional_value" and not (isinstance(c.get("paper_value"), (int, float)) and c["paper_value"] >= 0):
            errors.append(f"{c['case_id']}: valor condicional sem número")
        for ref in c.get("value_refs", {}).values():
            if ref not in obs:
                errors.append(f"{c['case_id']}: value_ref {ref} inexistente")
    bridge = _strict(path / "results/esg_bridge.json")
    case_ids |= {c["case_id"] for c in bridge.get("cases", [])}
    nar = _strict(path / "results/narrative.json")
    if list(nar.get("slots", {})) != SLOTS:
        errors.append("narrative: slots divergentes do contrato")
    for s, ids in nar.get("slots", {}).items():
        errors += [f"slot {s}: claim {i} inexistente" for i in ids if i not in claims]
    for v in _strict(path / "results/presentation_facts.json").get("views", []):
        for se in v.get("series", []):
            for p in se.get("points", []):
                if p.get("y_value_ref") not in obs:
                    errors.append(f"{v['view_id']}: ponto sem valor")
                if p.get("case_ref") and p["case_ref"] not in case_ids:
                    errors.append(f"{v['view_id']}: case_ref inexistente")
    dec = _strict(path / "results/recommendation.json").get("decision", {})
    if dec.get("status") == "adopted" and not dec.get("human_record_refs"):
        errors.append("decisão adotada sem registros humanos")
    if man.get("state") == "group_adopted" and dec.get("status") != "adopted":
        errors.append("group_adopted sem decisão adotada")
    return errors


# ---------------- formatação pt-BR ------------------------------------------------------------
def _num(x: float, dec: int) -> str:
    s = f"{abs(x):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if x < 0 else "") + s


def _trim(s: str) -> str:
    return re.sub(r",?0+$", "", s) if "," in s else s


def format_value(value: float | None, unit: str, scale: float = 1.0, style: str = "") -> str:
    if value is None:
        return "N/D"
    signed = style == "signed"
    sign = "+" if signed and value > 0 else ""
    if style == "plain":
        return _trim(_num(value, 2))
    if style == "signed1" and unit == "ratio":
        return ("+" if value > 0 else "") + _num(value * 100, 1) + "%"
    if unit == "BRL" and scale == 1e6:
        if style != "precise" and abs(value) >= 1000:
            return sign + "R$ " + _num(value / 1000, 1) + " bi"
        return sign + "R$ " + _num(value, 1) + " mi"
    if unit in ("BRL/unit", "BRL/share", "BRL_per_BRL"):
        return sign + "R$ " + _num(value, 2)
    if unit == "ratio":
        return sign + _trim(_num(value * 100, 2)) + "%"
    if unit == "percentage_points":
        return sign + _trim(_num(value, 1)) + " p.p."
    if unit == "year":
        return str(int(round(value)))
    if unit == "years":
        n = int(round(value))
        return f"{n} ano" + ("" if n == 1 else "s")
    if unit == "MWm":
        return _trim(_num(value, 1)) + " MWm"
    if unit == "L_per_connection_day":
        return _num(value, 1) + " L/ligação/dia"
    if unit == "shares":
        return _num(value * scale / 1e6, 1) + " mi de ações"
    return sign + _trim(_num(value, 2)) + (f" {unit}" if unit not in ("flag", "") else "")


@dataclass
class Bundle:
    path: Path
    manifest: dict
    obs: dict
    claims: dict
    sources: dict
    defs: dict
    assumptions: dict
    cases: dict
    bridge_cases: dict
    matrix: list
    views: list
    slots: dict
    decision: dict
    reconciliation: list
    adjustments: list
    schedule: list
    terms: list
    events: list
    metadata: dict
    qa: dict
    extras: dict = field(default_factory=dict)

    @property
    def bundle_id(self) -> str:
        return self.manifest["bundle_id"]

    @property
    def manifest_sha256(self) -> str:
        return sha256_file(self.path / "manifest.json")

    def num(self, vid: str) -> float | None:
        r = self.obs[vid]
        return None if r["value"] == "" else float(r["value"])

    def fmt(self, vid: str, style: str = "") -> str:
        r = self.obs[vid]
        return format_value(self.num(vid), r["unit"], float(r["scale"] or 1), style)

    def entity_name(self, e: str) -> str:
        return ENTITY_NAME.get(e, e)

    def render(self, template: str, used: set | None = None) -> str:
        def sub(m):
            kind, ref, style = m.group(1), m.group(2), m.group(3) or ""
            if kind == "value":
                if used is not None:
                    used.add(ref)
                return self.fmt(ref, style)
            ent = self.decision["entity_id"] if ref == "decision" else ref
            return self.entity_name(ent) if kind == "entity" else self.decision.get("instrument_id", "")
        return TOKEN.sub(sub, template)

    def claim_text(self, cid: str, used: set | None = None) -> str:
        return self.render(self.claims[cid]["text_template"], used)

    def claim_sources(self, cid: str) -> list[str]:
        return _jl(self.claims[cid]["source_refs"])

    def value_sources(self, vid: str) -> list[str]:
        return _jl(self.obs[vid]["source_refs"])

    def case(self, cid: str) -> dict:
        return self.cases[cid]


def load(path: Path, allow_kinds=("analysis",)) -> Bundle:
    errors = validate(path, allow_kinds)
    if errors:
        raise BundleRejected("; ".join(errors[:12]))
    R = lambda n: _strict(path / f"results/{n}.json")
    val = R("valuation")
    rec = R("recommendation")
    return Bundle(
        path=path, manifest=_strict(path / "manifest.json"),
        obs={r["value_id"]: r for r in _csv(path / "tables/observations.csv")},
        claims={r["claim_id"]: r for r in _csv(path / "tables/claims.csv")},
        sources={r["source_id"]: r for r in _csv(path / "tables/sources.csv")},
        defs={r["definition_id"]: r for r in _csv(path / "tables/definitions.csv")},
        assumptions={r["assumption_id"]: r for r in _csv(path / "tables/assumptions.csv")},
        cases={c["case_id"]: c for c in val["cases"]}, bridge_cases={c["case_id"]: c for c in R("esg_bridge")["cases"]},
        matrix=R("esg_matrix")["rows"], views=R("presentation_facts")["views"], slots=R("narrative")["slots"], decision=rec["decision"],
        reconciliation=_csv(path / "tables/financial_reconciliation.csv"), adjustments=_csv(path / "tables/adjustments.csv"),
        schedule=_csv(path / "tables/obligation_schedule.csv"), terms=_csv(path / "tables/regulatory_terms.csv"),
        events=_csv(path / "tables/corporate_actions.csv"), metadata=_strict(path / "metadata.json"),
        qa=_strict(path / "qa/analysis_validation.json"),
        extras={"calibration": val.get("calibration", {}), "implied_wacc": val.get("implied_wacc_refs", {}),
                "legacy": val.get("legacy_replication", [])})
