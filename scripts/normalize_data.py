"""Canonical observations with explicit source/definition lineage."""
from __future__ import annotations

import json
from datetime import datetime

import pandas as pd

from common import ROOT, acquisitions, read_csv, read_json, write_csv, write_json

FIELDS = ["obs_id", "entity_id", "instrument_id", "metric_id", "value", "unit", "scale", "period_start", "period_end", "observed_at", "source_id", "source_location", "definition_id", "scope", "fact_type", "quality_status"]


def normalize():
    records, definitions, snapshots = [], {}, []
    def add(entity, metric, value, source, location, end, start="", unit="BRL", scale=1000000, scope="consolidated", fact_type="realizado", quality="verified_primary", instrument="", definition=None):
        def_id = definition or f"DEF_{entity or 'macro'}_{metric}_{scope}"
        row = dict(obs_id=f"OBS_{len(records)+1:06}", entity_id=entity, instrument_id=instrument, metric_id=metric, value=float(value), unit=unit, scale=scale, period_start=start, period_end=end, observed_at=end, source_id=source, source_location=location, definition_id=def_id, scope=scope, fact_type=fact_type, quality_status=quality)
        records.append(row)
        definitions.setdefault(def_id, dict(definition_id=def_id, entity_id=entity, metric_id=metric, numerator="conforme conta/tabela identificada", denominator="conforme fonte; nao presumir comparabilidade", unit=unit, scope=scope, methodology="Source-specific; see source_location", methodology_valid_from="", source_ids=source, comparability_status="source_specific"))
        return row
    accounts = read_csv("data/processed/cvm_accounts.csv")
    mapping = {("DRE", "3.01"): "revenue_total_reported", ("DRE", "3.05"): "ebit", ("DRE", "3.07"): "profit_before_tax_reported", ("DRE", "3.08"): "income_tax_expense_signed", ("BPA", "1.01.01"): "cash_equivalents_reported", ("BPA", "1.01.02"): "short_term_investments_reported", ("BPA", "1.01.03"): "receivables_reported", ("BPA", "1.01.04"): "inventories_operating", ("BPP", "2.01.02"): "payables_operating", ("BPP", "2.03.09"): "minority_interests", ("DFC_MI", "6.01"): "operating_cash_flow_reported"}
    for r in accounts:
        metric = mapping.get((r["statement"], r["account_code"]))
        if metric:
            add(r["entity_id"], metric, r["value_brl_million"], r["source_id"], r["source_location"], r["period_end"], r["period_start"], scope=r["scope"])
    grouped = {}
    for r in accounts:
        if r["statement"] == "BPP" and r["account_code"] in ("2.01.04", "2.02.01"):
            grouped.setdefault((r["entity_id"], r["period_end"], r["source_id"]), []).append(r)
    for (entity, end, source), items in grouped.items():
        if {r["account_code"] for r in items} == {"2.01.04", "2.02.01"}:
            add(entity, "gross_debt", sum(float(r["value_brl_million"]) for r in items), source, " + ".join(r["source_location"] for r in items), end, quality="verified_primary_sum")
    by_key = {s["key"]: s for s in acquisitions() if s["status"] == "downloaded"}
    for key in ["bcb_sgs_432", "bcb_sgs_433"]:
        s = by_key[key]
        for i, item in enumerate(read_json(s["local_path"])):
            end = datetime.strptime(item["data"], "%d/%m/%Y").date().isoformat()
            add("", "selic_target" if key.endswith("432") else "ipca_monthly", float(item["valor"].replace(",", ".")) / 100, s["source_id"], f"JSON[{i}]; data={item['data']}", end, unit="ratio", scale=1, scope="macro", quality="verified_api_snapshot_publication_time_unspecified")
    for year in range(2026, 2031):
        s = by_key[f"bcb_focus_ipca_{year}"]
        values = read_json(s["local_path"])["value"]
        if not values:
            continue
        v = values[0]
        forecast_row = add("", "ipca_expectation", v["Mediana"] / 100, s["source_id"], f"value[0]; IPCA; ano {year}; baseCalculo={v['baseCalculo']}; Data={v['Data']}", f"{year}-12-31", f"{year}-01-01", unit="ratio", scale=1, scope="macro", fact_type="consenso", quality="verified_api_snapshot")
        forecast_row["observed_at"] = v["Data"]
        snapshots.append(dict(snapshot_id=f"FOCUS_IPCA_{year}", entity_id="", metric_id="ipca_expectation", forecast_period=str(year), snapshot_date=v["Data"], statistic="Mediana", value=v["Mediana"] / 100, unit="ratio", scale=1, contributors=v.get("numeroRespondentes"), dispersion_type="DesvioPadrao", dispersion_value=v["DesvioPadrao"] / 100, source_id=s["source_id"], source_location="value[0]; baseCalculo=0"))
    evidence_path = ROOT / "config/verified_evidence.json"
    if evidence_path.exists():
        for item in read_json("config/verified_evidence.json"):
            source = by_key[item["source_key"]]
            evidence_row = add(item["entity_id"], item["metric_id"], item["value"], source["source_id"], item["location"], item["period_end"], item.get("period_start", ""), item.get("unit", "ratio"), item.get("scale", 1), item["scope"], item.get("fact_type", "realizado"), item.get("quality_status", "verified_primary_manual_context"), definition=item["definition_id"])
            if item.get("fact_type") == "plano_anunciado":
                evidence_row["observed_at"] = source["published_at"]
            definitions[item["definition_id"]]["methodology"] = item["definition"]
            definitions[item["definition_id"]]["comparability_status"] = item.get("comparability", "source_specific")
    if (ROOT / "data/processed/market_reference.json").exists():
        for item in read_json("data/processed/market_reference.json"):
            add("", "market_close", item["close"], item["source_id"], item["source_location"], item["date"], unit="BRL_per_instrument", scale=1, scope="instrument", fact_type="market_reference", quality="verified_public_provider_pending_terminal_confirmation", instrument=item["instrument_id"])
    if (ROOT / "data/processed/capital_reference.json").exists():
        for entity,item in read_json("data/processed/capital_reference.json").items():
            add(entity,"shares_outstanding",item["outstanding_million"],item["source_id"],item["source_location"],item["capital_date"],unit="shares",scale=1000000,scope="issuer_capital",quality="verified_primary_source_precision")
    write_csv("data/processed/observations.csv", records, FIELDS)
    write_csv("data/processed/definitions.csv", definitions.values())
    write_csv("data/processed/estimate_snapshots.csv", snapshots)
    # All observations must have an entry in the metric catalogue.
    dictionary = read_csv("data/catalog/metric_dictionary.csv")
    known = {r["metric_id"] for r in dictionary}
    for r in records:
        if r["metric_id"] not in known:
            dictionary.append(dict(metric_id=r["metric_id"], category="reported_financial", description=r["metric_id"], canonical_unit=r["unit"], canonical_scale=r["scale"], expected_scope="entity", period_type="source_defined", definition_notes="Reported concept; source-specific, not automatically cash or adjusted", priority="P0", required_condition="when_used"))
            known.add(r["metric_id"])
    write_csv("data/catalog/metric_dictionary.csv", dictionary)
    write_json("outputs/qa/normalization_status.json", {"observations": len(records), "definitions": len(definitions), "note": "Financial account mapping and explicit manual annotations; assumptions remain separate."})
    print("Observations", len(records))


if __name__ == "__main__":
    normalize()
