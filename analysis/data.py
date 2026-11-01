"""Leitura da fotografia congelada e registro de valores/definições/fontes/claims.

Todo número usado em resultados recebe um value_id estável com estado, tipo de fato,
unidade, escala, período, escopo, definição e referências (contrato 1.0).
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from .common import read_csv, read_json, sha256_file

VALUE_STATES = {"observed", "derived", "assumed", "missing", "not_applicable"}
FACT_TYPES = {"fact", "assumption", "inference", "derived"}
ID_RE = re.compile(r"^[A-Za-z0-9_.:\-]+$")


class Baseline:
    """Acesso somente leitura aos arquivos copiados em <snapshot>/files."""

    def __init__(self, snapshot_dir: Path):
        self.dir = Path(snapshot_dir)
        self.files = self.dir / "files"
        self.meta = read_json(self.dir / "snapshot.json")
        self.snapshot_id = self.meta["snapshot_id"]
        self._cache: dict = {}

    def path(self, rel: str) -> Path:
        p = self.files / rel
        if not p.is_file():
            raise FileNotFoundError(f"Insumo ausente na fotografia: {rel}")
        return p

    def json(self, rel: str):
        if rel not in self._cache:
            self._cache[rel] = read_json(self.path(rel))
        return self._cache[rel]

    def csv(self, rel: str) -> list[dict]:
        if rel not in self._cache:
            self._cache[rel] = read_csv(self.path(rel))
        return self._cache[rel]

    # --- CVM -------------------------------------------------------------------------
    def accounts(self) -> list[dict]:
        return self.csv("data/processed/cvm_accounts.csv")

    def scope_of(self, entity: str, period_end: str) -> str:
        """Consolidado quando publicado para o período; senão individual (Sabesp 2021–22, Sanepar)."""
        scopes = {r["scope"] for r in self.accounts() if r["entity_id"] == entity and r["period_end"] == period_end}
        return "consolidated" if "consolidated" in scopes else "individual"

    def cvm(self, entity: str, statement: str, period_end: str, code: str | None = None, name: str | None = None,
            period_start: str | None = None, required: bool = True) -> tuple[float | None, dict | None]:
        """Conta única por entidade/demonstração/período/escopo; última versão/referência elegível."""
        scope = self.scope_of(entity, period_end)
        rows = [r for r in self.accounts() if r["entity_id"] == entity and r["statement"] == statement and r["period_end"] == period_end
                and r["scope"] == scope]
        if period_start is not None:
            rows = [r for r in rows if (r["period_start"] or "") == period_start]
        if code is not None:
            rows = [r for r in rows if r["account_code"] == code]
        if name is not None:
            rx = re.compile(name, re.I)
            rows = [r for r in rows if rx.search(r["account_name"])]
        if not rows:
            if required:
                raise KeyError(f"Conta ausente {entity}/{statement}/{code or name}/{period_end}")
            return None, None
        rows.sort(key=lambda r: (r["reference_date"], int(r["version"] or 0)))
        # Publicação própria do período (não comparativo reapresentado); senão a mais recente.
        own = [r for r in rows if r["reference_date"] == period_end]
        chosen_ref = own[-1]["reference_date"] if own else rows[-1]["reference_date"]
        rows = [r for r in rows if r["reference_date"] == chosen_ref]
        codes = {r["account_code"] for r in rows}
        if len(codes) > 1:
            raise ValueError(f"Conta ambígua {entity}/{statement}/{name}/{period_end}: {sorted(codes)}")
        r = rows[-1]
        return float(r["value_brl_million"]), r

    def children(self, entity: str, statement: str, period_end: str, parent: str) -> list[dict]:
        depth = parent.count(".") + 1
        scope = self.scope_of(entity, period_end)
        rows = [r for r in self.accounts() if r["entity_id"] == entity and r["statement"] == statement and r["period_end"] == period_end
                and r["scope"] == scope and r["account_code"].startswith(parent + ".") and r["account_code"].count(".") == depth]
        if not rows:
            return []
        refs = {r["reference_date"] for r in rows}
        chosen = period_end if period_end in refs else max(refs)
        out = {}
        for r in sorted((r for r in rows if r["reference_date"] == chosen), key=lambda r: int(r["version"] or 0)):
            out[r["account_code"]] = r
        return list(out.values())

    # --- textos -----------------------------------------------------------------------
    def page_text(self, doc: str, page: int) -> str:
        rel = f"data/interim/pdf_text/{doc}.json"
        if not (self.files / rel).is_file():
            rel = f"derived/pdf_text/{doc}.json"
        pages = self.json(rel)["pages"]
        return next(p["text"] for p in pages if p["page"] == page)

    def html_text(self, rel: str) -> str:
        if rel not in self._cache:
            from bs4 import BeautifulSoup

            raw = self.path(rel).read_text(encoding="utf-8", errors="ignore")
            self._cache[rel] = re.sub(r"\s+", " ", BeautifulSoup(raw, "html.parser").get_text(" "))
        return self._cache[rel]

    def require_html(self, rel: str, *needles: str) -> str:
        text = self.html_text(rel)
        for n in needles:
            if re.sub(r"\s+", " ", n) not in text:
                raise AssertionError(f"Evidência não encontrada em {rel}: {n!r}")
        return text

    def require_text(self, doc: str, page: int, *needles: str) -> str:
        """Confere que o trecho citado existe na página antes de usar a evidência."""
        text = re.sub(r"\s+", " ", self.page_text(doc, page))
        for n in needles:
            if re.sub(r"\s+", " ", n) not in text:
                raise AssertionError(f"Evidência não encontrada em {doc} p{page}: {n!r}")
        return text


def loc_of(row: dict) -> str:
    return row["source_location"]


@dataclass
class Registry:
    bundle_id: str
    observations: dict = field(default_factory=dict)
    definitions: dict = field(default_factory=dict)
    sources: dict = field(default_factory=dict)
    assumptions: dict = field(default_factory=dict)
    claims: dict = field(default_factory=dict)

    # ---------------------------------------------------------------------------------
    def source(self, source_id: str, **row) -> str:
        if source_id not in self.sources:
            base = dict(source_id=source_id, issuer="", title="", url="", local_path="", published_at="", retrieved_at="",
                        sha256="", access_method="", reference_date="", version="", access_status="")
            base.update({k: v for k, v in row.items() if k in base})
            self.sources[source_id] = base
        return source_id

    def define(self, definition_id: str, *, metric_id: str, unit: str, methodology: str, entity_id: str = "", numerator: str = "",
               denominator: str = "", scope: str = "", source_ids=(), comparability_status: str = "source_specific",
               methodology_valid_from: str = "") -> str:
        self.definitions.setdefault(definition_id, dict(
            definition_id=definition_id, entity_id=entity_id, metric_id=metric_id, numerator=numerator, denominator=denominator,
            unit=unit, scope=scope, methodology=methodology, methodology_valid_from=methodology_valid_from,
            source_ids=list(source_ids), comparability_status=comparability_status))
        return definition_id

    def value(self, value_id: str, *, metric_id: str, value, unit: str, value_state: str, fact_type: str, entity_id: str = "",
              instrument_id: str = "", scale: float = 1, period_start: str = "", period_end: str = "", observed_at: str = "",
              scope: str = "", definition_id: str | None = None, source_refs=(), assumption_refs=(), calculation_ref: str = "",
              locator: str = "", note: str = "") -> str:
        if not ID_RE.match(value_id):
            raise ValueError(f"value_id inválido: {value_id}")
        if value_state not in VALUE_STATES or fact_type not in FACT_TYPES:
            raise ValueError(f"Estado/tipo inválido em {value_id}: {value_state}/{fact_type}")
        if value is not None:
            value = float(value)
            if not math.isfinite(value):
                raise ValueError(f"Valor não finito em {value_id}")
        if value_state in {"missing", "not_applicable"}:
            if value is not None or not note:
                raise ValueError(f"{value_id}: {value_state} exige null e motivo")
        elif value is None:
            raise ValueError(f"{value_id}: valor ausente exige value_state missing/not_applicable")
        if value_state == "observed" and not source_refs:
            raise ValueError(f"{value_id}: observação exige fonte")
        if value_state == "assumed" and not assumption_refs:
            raise ValueError(f"{value_id}: premissa exige assumption_ref")
        if value_state == "derived" and not calculation_ref:
            raise ValueError(f"{value_id}: derivado exige cálculo")
        if definition_id is None:
            definition_id = self.define(f"DEF.{metric_id}" + (f".{entity_id}" if entity_id else ""), metric_id=metric_id, unit=unit,
                                        entity_id=entity_id, scope=scope, methodology=note or "Ver calculation_ref/source_location.",
                                        source_ids=source_refs)
        row = dict(value_id=value_id, entity_id=entity_id, instrument_id=instrument_id, metric_id=metric_id, value=value,
                   value_state=value_state, unit=unit, scale=float(scale), period_start=period_start, period_end=period_end,
                   observed_at=observed_at, scope=scope, definition_id=definition_id, fact_type=fact_type,
                   source_refs=list(source_refs), assumption_refs=list(assumption_refs), calculation_ref=calculation_ref,
                   source_location=locator, note=note)
        old = self.observations.get(value_id)
        if old is not None and old != row:
            raise ValueError(f"value_id reutilizado com conteúdo diferente: {value_id}")
        self.observations[value_id] = row
        return value_id

    def get(self, value_id: str) -> float | None:
        return self.observations[value_id]["value"]

    def assumption(self, assumption_id: str, *, entity_id: str, driver: str, year: str, base, adverse, favorable, unit: str,
                   rationale: str, supporting_obs_ids=(), source_id: str = "", source_location: str = "",
                   approval_status: str = "proposed_not_human_reviewed") -> str:
        for x in (base, adverse, favorable):
            if x is not None and not math.isfinite(float(x)):
                raise ValueError(f"Premissa não finita: {assumption_id}")
        refs = {}
        for case, v in (("base", base), ("adverse", adverse), ("favorable", favorable)):
            if v is None:
                continue
            vid = f"A.{assumption_id}.{case}"
            # Premissas próprias citam sua origem; o valor da alternativa é registrado como 'assumed'.
            self.observations[vid] = dict(
                value_id=vid, entity_id=entity_id, instrument_id="", metric_id=f"assumption.{driver}", value=float(v),
                value_state="assumed", unit=unit, scale=1.0, period_start="", period_end=str(year) if year else "",
                observed_at="", scope="model_assumption", definition_id=self.define(
                    f"DEF.assumption.{driver}", metric_id=f"assumption.{driver}", unit=unit,
                    methodology="Premissa do caso revisado; ver assumptions.csv (rationale/alternativas)."),
                fact_type="assumption", source_refs=[source_id] if source_id else [], assumption_refs=[assumption_id],
                calculation_ref="", source_location=source_location, note="")
            refs[case] = vid
        self.assumptions[assumption_id] = dict(
            assumption_id=assumption_id, entity_id=entity_id, driver=driver, year=year, base=base, adverse=adverse,
            favorable=favorable, unit=unit, rationale=rationale, supporting_obs_ids=list(supporting_obs_ids), owner="agente_analise",
            reviewer="grupo_H08", approval_status=approval_status, source_id=source_id, source_location=source_location,
            value_refs=refs)
        return assumption_id

    def claim(self, claim_id: str, *, claim_type: str, text_template: str, value_refs=(), source_refs=(), assumption_refs=(),
              calculation_refs=(), status: str = "proposed", limitations: str = "") -> str:
        tokens = re.findall(r"\{\{value:([^}]+)\}\}", text_template)
        missing = [t for t in tokens if t not in self.observations]
        if missing:
            raise KeyError(f"Claim {claim_id} referencia valores inexistentes: {missing}")
        refs = list(dict.fromkeys(list(value_refs) + tokens))
        if claim_type in {"fact"} and not source_refs:
            raise ValueError(f"Claim factual sem fonte: {claim_id}")
        if claim_type == "assumption" and not assumption_refs:
            raise ValueError(f"Claim de hipótese sem premissa: {claim_id}")
        self.claims[claim_id] = dict(claim_id=claim_id, claim_type=claim_type, text_template=text_template, value_refs=refs,
                                     source_refs=list(source_refs), assumption_refs=list(assumption_refs),
                                     calculation_refs=list(calculation_refs), status=status, limitations=limitations)
        return claim_id


def file_source(reg: Registry, base: Baseline, source_id: str, rel_path: str, **kw) -> str:
    """Registra fonte a partir de arquivo copiado na fotografia, com hash conferido."""
    p = base.files / rel_path
    sha = sha256_file(p) if p.is_file() else kw.pop("sha256", "")
    return reg.source(source_id, local_path=rel_path, sha256=sha, **kw)
