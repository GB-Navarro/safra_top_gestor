"""Ramo legado: reprodução das três planilhas originais (porta de scripts/model.py::value).

Origem fixada pelo hash de scripts/model.py registrado em snapshot.json (role legacy_module_readonly).
Mantido separado do ramo revisado; não lê caches mutáveis além da cópia na fotografia.
"""
from __future__ import annotations

from datetime import date

MODEL_NAMES = {"sabesp": "Modelo_TIR_Sabesp.xlsx", "copasa": "Modelo_TIR_Copasa.xlsx", "sanepar": "Modelo_para_TIR_Sanepar.xlsx"}


def value(model: dict) -> dict:
    cells = model["cells"]

    def get(sheet, address):
        return cells.get(sheet, {}).get(address, {}).get("cached")
    wacc, growth, tax = get("Premissas", "C9"), get("Premissas", "C10"), get("Premissas", "C8")
    origin = date.fromisoformat(get("Premissas", "C6")[:10])
    prior_revenue, working_capital = get("Dados_RI", "G21"), get("Dados_RI", "G27")
    flows = []
    for k, year in enumerate(range(2026, 2036)):
        column = chr(67 + k)
        revenue = prior_revenue * (1 + get("Premissas", column + "18")) * (1 + get("Premissas", column + "17")) * (1 + get("Premissas", column + "19"))
        margin = get("Premissas", column + "20")
        depreciation = revenue * get("Premissas", column + "21")
        ebit = revenue * margin - depreciation
        nopat = ebit - max(ebit, 0) * tax
        plan = get("Dados_RI", column + "34")
        capex = float(plan) if isinstance(plan, (int, float)) else revenue * get("Premissas", column + "22")
        next_wc = revenue * get("Premissas", column + "23")
        full_fcff = nopat + depreciation - capex - (next_wc - working_capital)
        years = (date(year, 12, 31) - origin).days / 365
        partial = years if k == 0 and get("Premissas", "C7") == 1 else 1
        flows.append(dict(year=year, revenue=revenue, fcff=full_fcff * partial, discounted=full_fcff * partial / (1 + wacc) ** years, time=years))
        prior_revenue, working_capital = revenue, next_wc
    last = flows[-1]
    t_rev = last["revenue"] * (1 + growth)
    t_da = depreciation * (1 + growth)
    t_ebit = t_rev * margin - t_da
    t_fcff = t_ebit - max(t_ebit, 0) * tax + t_da - t_da * get("Premissas", "C13") - get("Premissas", "L23") * last["revenue"] * growth
    pv_terminal = t_fcff / (wacc - growth) / (1 + wacc) ** last["time"]
    ev = sum(f["discounted"] for f in flows) + pv_terminal
    equity = max(0.0, ev - get("Dados_RI", "C44") - get("Dados_RI", "C42"))
    return dict(enterprise_value=ev, average_share_value=equity / get("Dados_RI", "C39"))


def replicate(models: dict) -> list[dict]:
    out = []
    for entity, name in MODEL_NAMES.items():
        m = models[name]
        r = value(m)
        cached_share, cached_ev = m["cells"]["TIR"]["B42"]["cached"], m["cells"]["TIR"]["B38"]["cached"]
        out.append(dict(entity_id=entity, workbook=name, calculated_share=r["average_share_value"], cached_share=cached_share,
                        share_abs_error=abs(r["average_share_value"] - cached_share), ev_abs_error=abs(r["enterprise_value"] - cached_ev),
                        passed=abs(r["average_share_value"] - cached_share) < 1e-6 and abs(r["enterprise_value"] - cached_ev) < 1e-5))
    return out
