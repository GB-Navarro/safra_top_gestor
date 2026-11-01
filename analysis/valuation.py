"""AN08 — casos do ramo revisado: cenários, grade WACC×g, terminal finito, alternativas de classe/ponte.

Cada caso (inclusive cada ponto de grade) guarda resíduo bruto, piso, validade, premissas e
value_refs que coincidem com observações registradas. N/D nunca vira preço zero.
"""
from __future__ import annotations

from . import dcf, obligations
from .assumptions import inflation_path
from .data import Baseline, Registry

ENTITIES = {"sabesp": "SBSP3", "copasa": "CSMG3", "sanepar": "SAPR11"}
DEBT_LIKE = ("lease_separate", "ppp", "derivatives_liab", "dividends_payable", "post_employment", "supplier_finance")
SCENARIOS = {
    "base": "Base",
    "rates_up": "Juros maiores (WACC +1,5 p.p.)",
    "execution_adverse": "Pior execução e regulação",
    "favorable": "Ambiente favorável",
}
OBSERVED_GROWTH = {  # EBITDA ajustado observado (fonte, período) para o teste de calibração
    "sabesp": (3503.0 / 3617.0 - 1, "SRC_doc_sbsp_2t26_65d19d49", "Release 2T26 p1/p3: EBITDA ajustado 2T26 3.503 vs 2T25 3.617", "2T26 vs 2T25"),
    "copasa": ((762.145 + 787.411) / (682.070 + 726.435) - 1, "SRC_doc_csmg_2t26_1996f20b", "Release 2T26 p14: EBITDA ajustado 2T26/2T25/1T26/1T25", "6M26 vs 6M25"),
    "sanepar": (1643.4 / 1515.3 - 1, "SRC_doc_sapr_2t26_e40a8cc1", "Release 2T26 p11: EBITDA ajustado de itens não recorrentes 6M26 1.643,4 vs 1.515,3", "6M26 vs 6M25"),
}


def _ref(reg, a, key, case):
    return reg.get(a[key][case])


def _params(reg: Registry, rec: dict, a: dict, m: dict, entity: str, case: dict) -> dcf.Params:
    b = rec["basis"][entity]
    infl = inflation_path(reg, m, case.get("infl", "base"))
    infl[2024], infl[2025] = reg.get(m["actual"][2024]), reg.get(m["actual"][2025])
    r_post = reg.get(a["reg_wacc"][entity][case.get("reg", "base")])
    tax = reg.get(a["tax"]["base"])
    if entity == "copasa":
        # Equivalência pré/pós publicada pela Arsae-MG (13,70% ↔ 9,79%); preserva a razão para alternativas.
        r_pre = r_post * reg.get("V.copasa.wacc_reg_real_pre_tax") / reg.get("V.copasa.wacc_reg_real_after_tax")
    else:
        r_pre = r_post / (1 - tax)
    hist = {y: reg.get(f"V.{entity}.capex_cash.{y}") for y in (2023, 2024, 2025)}
    plan = {y: reg.get(v[case.get("capex", "base")]) for y, v in a["capex"][entity].items()}
    wacc = case["wacc"] if "wacc" in case else _ref(reg, a, "wacc", case.get("wacc_case", "base")) + case.get("wacc_shift", 0.0)
    g_real = case["g_real"] if "g_real" in case else reg.get(a["rab_g"][case.get("g_case", "base")])
    return dcf.Params(entity=entity, ebitda0=reg.get(b["ebitda_2025"]), da0=reg.get(b["da_2025"]), revenue0=reg.get(b["revenue_2025"]),
                      wc_ratio=reg.get(b["wc_ratio"]), r_pre=r_pre, r_post=r_post, tax=tax,
                      lag=int(reg.get(a["lag"][case.get("lag", "base")])), share=reg.get(a["share"][case.get("share", "base")]),
                      opex_shock=reg.get(a["opex"][case.get("opex", "base")]), eligible=reg.get(a["eligible"][case.get("eligible", "base")]),
                      capex_plan=plan, capex_hist=hist, infl=infl, g_real=g_real, wacc=wacc,
                      terminal=case.get("terminal", "perpetuity"), finite_years=case.get("finite_years"),
                      indemnity=reg.get(a["indemnity"][case.get("indemnity", "base")]))


def _record(reg, cid, entity, field, value, unit, calc, note=""):
    return reg.value(f"V.case.{cid}.{field}", metric_id=f"case.{field}", entity_id=entity, value=value, unit=unit,
                     scale=1e6 if unit == "BRL" else 1, value_state="derived", fact_type="derived", period_end="2026-10-30",
                     calculation_ref=calc, note=note or f"Resultado do caso {cid}")


def run_case(reg, base, rec, cap, bal, a, m, entity, cid, scenario_id, dims, case, assumption_refs, limitations):
    ticker = ENTITIES[entity]
    price_ref = cap["prices"][ticker]
    items = bal["items"][entity]
    try:
        p = _params(reg, rec, a, m, entity, case)
        out = dcf.run(p)
    except ValueError as exc:
        return dict(case_id=cid, entity_id=entity, instrument_id=ticker, scenario_id=scenario_id, dimensions=dims,
                    value_refs={"price": price_ref}, wacc=None, g=None, terminal_method=case.get("terminal", "perpetuity"),
                    equity_residual_before_floor=None, equity_floor_applied=False, paper_value=None, target_validity="unresolved",
                    assumption_refs=assumption_refs, limitations=limitations + [f"Caso não calculável: {exc}"])
    debt_like = sum(reg.get(items[k]) for k in DEBT_LIKE if k in items)
    if case.get("contingencies") and "contingencies" in items:
        debt_like += reg.get(items["contingencies"])
    grantor = reg.get(items["grantor"]) if "grantor" in items else 0.0
    obligation_pv = 0.0
    if entity == "sanepar":
        flows = obligations.precatorio_schedule(reg, base, p.infl, case.get("precatorio", "base"))
        fut, past = obligations.pv_flows(flows, p.wacc)
        obligation_pv = fut + past
    br = dcf.bridge(out["enterprise_value"], out["fcff_2026_full"] * case.get("rollforward_scale", 1.0), reg.get(items["net_debt"]),
                    debt_like, grantor, out["rab_value_ratio"], obligation_pv)
    resid = br["equity_residual"]
    calc = f"analysis.dcf.run/bridge — caso {cid}"
    refs = {"price": price_ref,
            "wacc": _record(reg, cid, entity, "wacc", p.wacc, "ratio", calc),
            "g": _record(reg, cid, entity, "g", out["g"], "ratio", calc, "Crescimento nominal terminal = (1+IPCA LP)(1+g real)−1"),
            "enterprise_value": _record(reg, cid, entity, "enterprise_value", out["enterprise_value"], "BRL", calc),
            "pv_explicit": _record(reg, cid, entity, "pv_explicit", out["pv_explicit"], "BRL", calc),
            "pv_terminal": _record(reg, cid, entity, "pv_terminal", out["pv_terminal"], "BRL", calc),
            "net_debt_october_estimate": _record(reg, cid, entity, "net_debt_october_estimate", br["net_debt_october_estimate"], "BRL", calc,
                                                 "Dívida líquida de junho rolada pelo FCFF jul–out (estimativa, não observação)"),
            "debt_like": _record(reg, cid, entity, "debt_like", debt_like, "BRL", calc),
            "obligation_pv": _record(reg, cid, entity, "obligation_pv", obligation_pv, "BRL", calc),
            "grantor_net": _record(reg, cid, entity, "grantor_net", br["grantor"] - br["grantor_regulatory_credit"], "BRL", calc),
            "equity_residual_before_floor": _record(reg, cid, entity, "equity_residual", resid, "BRL", calc),
            "ebitda_2026": _record(reg, cid, entity, "ebitda_2026", out["ebitda_2026"], "BRL", calc),
            "terminal_share": _record(reg, cid, entity, "terminal_share", out["terminal_share"], "ratio", calc)}
    shares = reg.get(cap["shares"][entity]["total"])
    if resid > 0:
        if entity == "sanepar":
            k = case.get("class_ratio")
            if k is None:
                paper = resid * reg.get(cap["class_weights"]["sapr11_per_mcap"])
            else:
                on, pn = reg.get(cap["shares"]["sanepar"]["common"]), reg.get(cap["shares"]["sanepar"]["preferred"])
                paper = resid / (on + k * pn) * (1 + 4 * k)
        else:
            paper = resid / shares
        refs["paper_value"] = _record(reg, cid, entity, "paper_value", paper, "BRL/unit" if entity == "sanepar" else "BRL/share", calc)
        refs["upside"] = _record(reg, cid, entity, "upside", paper / reg.get(price_ref) - 1, "ratio", calc, "Valor condicional/preço − 1")
        validity = "conditional_value"
    else:
        paper, validity = None, "no_meaningful_target"
    return dict(case_id=cid, entity_id=entity, instrument_id=ticker, scenario_id=scenario_id, dimensions=dims, value_refs=refs,
                wacc=p.wacc, g=out["g"], terminal_method=p.terminal, equity_residual_before_floor=resid, equity_floor_applied=resid <= 0,
                paper_value=paper, target_validity=validity, assumption_refs=assumption_refs, limitations=limitations,
                diagnostics=dict(b0_real=out["b0"], delta=out["delta"], margin0=out["margin0"], rab_value_ratio=out["rab_value_ratio"],
                                 fcff_2026_full=out["fcff_2026_full"], terminal_fcff=out["terminal_fcff"], flows=out["rows"]))


def _paper_value(reg, base, rec, cap, bal, a, m, entity, case) -> float | None:
    """Mesmo cálculo de run_case, sem registrar valores (para busca do WACC implícito)."""
    p = _params(reg, rec, a, m, entity, case)
    out = dcf.run(p)
    items = bal["items"][entity]
    debt_like = sum(reg.get(items[k]) for k in DEBT_LIKE if k in items)
    grantor = reg.get(items["grantor"]) if "grantor" in items else 0.0
    obl = 0.0
    if entity == "sanepar":
        fut, past = obligations.pv_flows(obligations.precatorio_schedule(reg, base, p.infl, "base"), p.wacc)
        obl = fut + past
    resid = dcf.bridge(out["enterprise_value"], out["fcff_2026_full"], reg.get(items["net_debt"]), debt_like, grantor,
                       out["rab_value_ratio"], obl)["equity_residual"]
    if resid <= 0:
        return None
    if entity == "sanepar":
        return resid * reg.get(cap["class_weights"]["sapr11_per_mcap"])
    return resid / reg.get(cap["shares"][entity]["total"])


def implied_wacc(reg, base, rec, cap, bal, a, m, entity) -> float | None:
    """WACC nominal que iguala o valor do caso-base ao preço de 30/10 (bisseção; demais premissas no base)."""
    price = reg.get(cap["prices"][ENTITIES[entity]])
    lo, hi = 0.07, 0.25

    def f(w):
        v = _paper_value(reg, base, rec, cap, bal, a, m, entity, {"wacc": w})
        return (v if v is not None else 0.0) - price
    if f(lo) < 0 or f(hi) > 0:
        return None
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def build(reg: Registry, base: Baseline, rec: dict, cap: dict, bal: dict, a: dict, m: dict) -> dict:
    common_assumptions = ["wacc_nominal", "recognition_lag", "recognition_share", "opex_shock", "eligible_share", "tax_rate",
                          "rab_real_growth_after_plan", "ipca_long_run", "terminal_horizon"]
    common_limits = ["Base remunerada implícita no EBIT de 2025 (BRR oficial não obtida)",
                     "Dívida/caixa de 30/06/2026 rolados até 30/10 por FCFF uniforme — não é balanço de outubro",
                     "Resultado condicional às premissas; não é preço-alvo aprovado nem previsão de cotação"]
    scen_specs = {
        "base": {},
        "rates_up": {"wacc_shift": 0.015},
        "execution_adverse": {"lag": "adverse", "share": "adverse", "opex": "adverse", "eligible": "adverse", "capex": "adverse",
                              "reg": "adverse", "contingencies": True, "precatorio": "adverse", "g_case": "adverse"},
        "favorable": {"wacc_case": "favorable", "lag": "favorable", "opex": "favorable", "reg": "favorable", "precatorio": "favorable",
                      "g_case": "favorable"},
    }
    cases = []
    for entity in ENTITIES:
        reg_key = {"sabesp": "sabesp_wacc_reg", "copasa": "copasa_wacc_reg_case", "sanepar": "sanepar_wacc_reg_case"}[entity]
        capex_keys = [k for k in reg.assumptions if k.startswith(f"capex_{entity}_")]
        arefs = common_assumptions + [reg_key] + capex_keys
        for sid, spec in scen_specs.items():
            dims = {"scenario": {"option_id": sid, "label": SCENARIOS[sid], "value_ref": None}}
            cases.append(run_case(reg, base, rec, cap, bal, a, m, entity, f"{entity}.{sid}", sid, dims, spec, arefs, common_limits))
        # Grade WACC × g real (demais premissas no caso-base).
        w0 = reg.get(a["wacc"]["base"])
        for dw in (-0.01, -0.005, 0.0, 0.005, 0.01):
            for gr in (0.0, 0.01, 0.02):
                cid = f"{entity}.grid.w{round((w0 + dw) * 10000):d}.g{round(gr * 10000):d}"
                wv = reg.value(f"V.grid.wacc.{round((w0 + dw) * 10000):d}", metric_id="grid.wacc_option", value=w0 + dw, unit="ratio",
                               value_state="derived", fact_type="derived", calculation_ref="WACC-base ± passo da grade",
                               note="Opção de WACC nominal da grade")
                gv = reg.value(f"V.grid.g_real.{round(gr * 10000):d}", metric_id="grid.g_real_option", value=gr, unit="ratio",
                               value_state="derived", fact_type="derived", calculation_ref="opção da grade", note="Crescimento real da base no terminal")
                dims = {"wacc": {"option_id": f"w{round((w0 + dw) * 10000):d}", "label": f"WACC {100 * (w0 + dw):.2f}%", "value_ref": wv},
                        "g_real": {"option_id": f"g{round(gr * 10000):d}", "label": f"g real {100 * gr:.1f}%", "value_ref": gv}}
                cases.append(run_case(reg, base, rec, cap, bal, a, m, entity, cid, "grid", dims, {"wacc": w0 + dw, "g_real": gr}, arefs,
                                      common_limits))
        # Terminal finito com indenização (fim do contrato principal).
        end_ref = f"V.{entity}.concession_end_year"
        end_year = reg.get(end_ref)
        spec = {"terminal": "finite", "finite_years": int(end_year) - 2035 if end_year else None}
        dims = {"terminal": {"option_id": "finite_indemnity", "label": "Fim da concessão com indenização", "value_ref": end_ref}}
        lim = common_limits + (["Prazo contratual não obtido: caso não calculado"] if not end_year else
                               ["Horizonte = prazo médio ponderado do portfólio (~29 anos); contratos até 2073 e vencidos não diferenciados"]
                               if entity == "copasa" else ["Um único prazo para todos os contratos; exceções municipais não modeladas"])
        cases.append(run_case(reg, base, rec, cap, bal, a, m, entity, f"{entity}.terminal_finite", "terminal_finite", dims, spec,
                              arefs + ["indemnity_share"], lim))
        # Sazonalidade da ponte junho→outubro.
        for label, scale in (("rollforward_low", 0.5), ("rollforward_high", 1.5)):
            dims = {"bridge": {"option_id": label, "label": f"FCFF jul–out × {scale}", "value_ref": None}}
            cases.append(run_case(reg, base, rec, cap, bal, a, m, entity, f"{entity}.{label}", label, dims, {"rollforward_scale": scale},
                                  arefs, common_limits + ["Sensibilidade de sazonalidade da ponte temporal"]))
    for k, label in ((1.0, "direitos econômicos iguais ON=PN"), (1.1, "PN = 1,1 × ON (adicional de dividendos)")):
        kv = reg.value(f"V.sanepar.class_ratio_option.{int(k * 100)}", metric_id="class_ratio_option", entity_id="sanepar", value=k,
                       unit="ratio", value_state="derived", fact_type="derived", calculation_ref="alternativa de alocação entre classes",
                       note="Alternativa à relação de preços observada; não é regra estatutária.")
        dims = {"class_allocation": {"option_id": f"pn_on_{int(k * 100)}", "label": label, "value_ref": kv}}
        cases.append(run_case(reg, base, rec, cap, bal, a, m, "sanepar", f"sanepar.class_{int(k * 100)}", "class_allocation", dims,
                              {"class_ratio": k}, ["wacc_nominal"], common_limits))
    calibration = {}
    for entity, (obs, src, loc, period) in OBSERVED_GROWTH.items():
        oid = reg.value(f"V.{entity}.ebitda_adjusted_growth_observed.2026H1", metric_id="ebitda_adjusted_growth_observed", entity_id=entity,
                        value=obs, unit="ratio", value_state="derived", fact_type="derived", period_end="2026-06-30", source_refs=[src],
                        calculation_ref=f"razão de EBITDA ajustado publicado ({period})", locator=loc, note="Crescimento observado para teste de calibração.")
        basecase = next(c for c in cases if c["case_id"] == f"{entity}.base")
        model_growth = basecase["diagnostics"]["flows"][0]["ebitda"] / reg.get(rec["basis"][entity]["ebitda_2025"]) - 1
        mid = reg.value(f"V.{entity}.ebitda_growth_model.2026", metric_id="ebitda_growth_model_2026", entity_id=entity, value=model_growth,
                        unit="ratio", value_state="derived", fact_type="derived", calculation_ref=f"case {entity}.base EBITDA2026/EBITDA2025 − 1",
                        note="Crescimento do EBITDA no caso-base.")
        calibration[entity] = {"observed_ref": oid, "model_ref": mid, "gap_pp": round(100 * (model_growth - obs), 2), "period": period,
                               "status": "within_5pp" if abs(model_growth - obs) <= 0.05 else "model_above_observed"}
    implied = {}
    for entity in ENTITIES:
        w = implied_wacc(reg, base, rec, cap, bal, a, m, entity)
        if w is None:
            implied[entity] = reg.value(f"V.{entity}.implied_wacc.2026-10-30", metric_id="implied_wacc_nominal", entity_id=entity, value=None,
                                        unit="ratio", value_state="not_applicable", fact_type="derived",
                                        note="Sem raiz no intervalo 7–25% com as demais premissas do caso-base.")
        else:
            implied[entity] = reg.value(f"V.{entity}.implied_wacc.2026-10-30", metric_id="implied_wacc_nominal", entity_id=entity, value=w,
                                        unit="ratio", value_state="derived", fact_type="derived", period_end="2026-10-30",
                                        calculation_ref="bisseção: WACC tal que valor do caso-base = preço de 30/10/2026",
                                        note="Retorno nominal da firma implícito no preço sob as demais premissas do caso-base; não é retorno esperado da ação.")
    return {"cases": cases, "calibration": calibration, "implied_wacc": implied, "brr_check": brr_check(reg, base, rec, a, m)}


def brr_check(reg, base, rec, a, m) -> dict:
    """Compara a base implícita da Sanepar (B0 = EBIT 2025 / r_pre) com a BRR líquida oficial da 3ª RTP (Agepar).

    A BRR 2024 (data-base dez/2024, ativos até dez/2023) está a preços de dez/2020; é atualizada pelo IPCA de 2021–2025
    para a base de preços de 2025 do motor. Com defasagem de 2 anos, B0 equivale à base de 2023 remunerada em 2025.
    É verificação de ordem de grandeza, não substituição: a BRR está em fiscalização e tem glosa prudencial.
    """
    base.require_text("agepar_nt_006_2025", 81, "o valor da BRR em 2024, a preços de dezembro de 2020", "R$ 16.846.830.100,73")
    base.require_text("agepar_nt_006_2025", 25, "12,24% a.a., equivalente a um WACC líquido real", "8,08% ao ano")
    off = reg.value("V.sanepar.brr_official_net.2024", metric_id="regulated_asset_base_official_net", entity_id="sanepar", value=16846.83010073,
                    unit="BRL", scale=1e6, value_state="observed", fact_type="fact", period_end="2024-12-31", scope="Preços de dez/2020",
                    source_refs=["SRC_agepar_nt_006_2025"], locator="NT Agepar 006/2025 p81, Tabela 32",
                    note="BRR líquida da 3ª RTP; sujeita ao plano de fiscalização (Resolução Agepar 40/2024) e a ajustes compensatórios.")
    factor = 1.0
    for y in (2021, 2022, 2023, 2024, 2025):
        factor *= 1 + reg.get(m["actual"][y])
    upd = reg.value("V.sanepar.brr_official_net.2024_at_2025_prices", metric_id="regulated_asset_base_official_net_updated", entity_id="sanepar",
                    value=reg.get(off) * factor, unit="BRL", scale=1e6, value_state="derived", fact_type="derived", period_end="2024-12-31",
                    source_refs=["SRC_agepar_nt_006_2025", "SRC_bcb_sgs_433_a47db5ed"],
                    calculation_ref="BRR dez/2020 × produto do IPCA 2021–2025 (SGS 433)", note="Mesma base de preços do motor (2025).")
    p = _params(reg, rec, a, m, "sanepar", {})
    imp = reg.value("V.sanepar.implied_base.2025", metric_id="regulated_base_implied", entity_id="sanepar", value=(p.ebitda0 - p.da0) / p.r_pre,
                    unit="BRL", scale=1e6, value_state="derived", fact_type="derived", period_end="2025-12-31",
                    calculation_ref="(EBITDA recorrente 2025 − D&A 2025) / WACC regulatório real pré-impostos (12,24%)",
                    note="Base remunerada implícita do motor (caso-base); preços de 2025.")
    gap = reg.value("V.sanepar.implied_vs_official_brr", metric_id="implied_base_vs_official_brr", entity_id="sanepar",
                    value=reg.get(imp) / reg.get(upd) - 1, unit="ratio", value_state="derived", fact_type="derived",
                    calculation_ref="base implícita / BRR oficial atualizada − 1", note="Diferença relativa; positiva = base implícita maior.")
    return {"official": off, "official_updated": upd, "implied": imp, "gap": gap}
