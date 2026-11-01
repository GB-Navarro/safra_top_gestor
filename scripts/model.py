"""Independent FCFF reconstruction. Conditional valuations, not stock return forecasts."""
from __future__ import annotations

from datetime import date, datetime
from math import prod

from common import read_csv, read_json, write_json

MODEL_NAMES = {"sabesp": "Modelo_TIR_Sabesp.xlsx", "copasa": "Modelo_TIR_Copasa.xlsx", "sanepar": "Modelo_para_TIR_Sanepar.xlsx"}


def value(model, changes=None):
    changes = changes or {}
    cells = model["cells"]
    def get(sheet, address):
        return cells.get(sheet, {}).get(address, {}).get("cached")
    wacc = changes.get("wacc", get("Premissas", "C9"))
    growth = changes.get("g", get("Premissas", "C10"))
    tax = changes.get("tax", get("Premissas", "C8"))
    if wacc <= growth or wacc <= 0:
        raise ValueError("DCF requires WACC > g and WACC > 0")
    origin = date.fromisoformat(get("Premissas", "C6")[:10])
    prior_revenue = get("Dados_RI", "G21")
    working_capital = get("Dados_RI", "G27")
    flows = []
    for k, year in enumerate(range(2026, 2036)):
        column = chr(67 + k)
        inflation = changes.get("inflation", {}).get(str(year), get("Premissas", column + "18"))
        volume = get("Premissas", column + "17")
        real_tariff = get("Premissas", column + "19")
        revenue = prior_revenue * (1 + inflation) * (1 + volume) * (1 + real_tariff)
        margin = changes.get("fixed_margin", get("Premissas", column + "20")) + changes.get("margin_delta", 0)
        ebitda = revenue * margin
        depreciation = revenue * get("Premissas", column + "21")
        ebit = ebitda - depreciation
        nopat = ebit - max(ebit, 0) * tax
        plan = get("Dados_RI", column + "34")
        capex = float(plan) if isinstance(plan, (int, float)) else revenue * get("Premissas", column + "22")
        capex *= changes.get("capex_multiplier", 1)
        next_working_capital = revenue * get("Premissas", column + "23")
        delta_working_capital = next_working_capital - working_capital
        full_fcff = nopat + depreciation - capex - delta_working_capital
        flow_date = date(year, 12, 31)
        years = (flow_date - origin).days / 365
        partial = (flow_date - origin).days / 365 if k == 0 and get("Premissas", "C7") == 1 else 1
        fcff = full_fcff * partial
        flows.append(dict(year=year, time_years=years, partial_factor=partial, revenue=revenue, margin=margin, ebitda=ebitda, depreciation=depreciation, nopat=nopat, capex=capex, delta_working_capital=delta_working_capital, full_fcff=full_fcff, fcff=fcff, discounted_fcff=fcff / (1 + wacc)**years))
        prior_revenue, working_capital = revenue, next_working_capital
    last = flows[-1]
    terminal_revenue = last["revenue"] * (1 + growth)
    terminal_da = last["depreciation"] * (1 + growth)
    terminal_ebit = terminal_revenue * last["margin"] - terminal_da
    terminal_nopat = terminal_ebit - max(terminal_ebit, 0) * tax
    if changes.get("terminal_method") == "roic":
        terminal_roic = changes.get("terminal_roic", wacc)
        if terminal_roic <= growth:
            raise ValueError("Terminal ROIC must exceed g in this reinvestment specification")
        terminal_fcff = terminal_nopat * (1 - growth / terminal_roic)
    else:
        terminal_fcff = terminal_nopat + terminal_da - terminal_da * get("Premissas", "C13") - get("Premissas", "L23") * last["revenue"] * growth
    terminal_value = terminal_fcff / (wacc - growth)
    if changes.get("terminal_years") is not None:
        terminal_value *= 1 - ((1 + growth) / (1 + wacc)) ** changes["terminal_years"]
    pv_terminal = terminal_value / (1 + wacc)**last["time_years"]
    pv_explicit = sum(r["discounted_fcff"] for r in flows)
    net_debt = changes.get("net_debt", get("Dados_RI", "C44"))
    minority = changes.get("minority", get("Dados_RI", "C42"))
    extra = changes.get("extra_obligations", 0)
    equity_residual = pv_explicit + pv_terminal - net_debt - minority - extra
    equity = max(0.0, equity_residual)
    shares = changes.get("shares", get("Dados_RI", "C39"))
    return dict(wacc=wacc, g=growth, tax=tax, pv_explicit=pv_explicit, pv_terminal=pv_terminal, terminal_share_of_ev=pv_terminal/(pv_explicit+pv_terminal), enterprise_value=pv_explicit+pv_terminal, net_debt=net_debt, minority=minority, extra_obligations=extra, equity_residual_before_floor=equity_residual, equity_floor_applied=equity_residual<0, equity_value=equity, average_share_value=equity/shares, terminal_fcff=terminal_fcff, terminal_method=changes.get("terminal_method", "legacy_da"), flows=flows)


def allocate_sanepar(equity, preferred_dividend_ratio=1.1):
    """Explicit equal-risk/distribution assumption; not a statutory price formula."""
    ordinary, preferred = 503.735259, 1007.470260
    on = equity / (ordinary + preferred_dividend_ratio * preferred)
    pn = preferred_dividend_ratio * on
    return dict(SAPR3=on, SAPR4=pn, SAPR11=on + 4 * pn)


def account(entity, code, statement="BPP", end="2026-06-30"):
    all_rows = [r for r in read_csv("data/processed/cvm_accounts.csv") if r["entity_id"] == entity and r["statement"] == statement and r["period_end"] == end]
    rows = [r for r in all_rows if r["account_code"] == code]
    if code == "2.03.09" and not rows and all_rows and {r["scope"] for r in all_rows} == {"individual"}:
        # Non-controlling equity is not a line in individual statements. This
        # explicitly concerns this perimeter; other absent values still fail.
        return 0.0
    if len(rows) != 1:
        raise ValueError(f"Expected unique account {entity}/{code}/{end}: {len(rows)}")
    return float(rows[0]["value_brl_million"])


def build():
    models = read_json("data/interim/original_models.json")
    market = read_json("data/processed/market_reference.json")
    prices = {r["instrument_id"]: r["close"] for r in market}
    capital = read_json("data/processed/capital_reference.json")
    focus = {r["forecast_period"]: float(r["value"]) for r in read_csv("data/processed/estimate_snapshots.csv")}
    macro = {str(y): focus.get(str(y), focus["2030"]) for y in range(2026, 2036)}
    results, replication = {}, []
    for entity, name in MODEL_NAMES.items():
        model = models[name]
        legacy = value(model)
        original_target = model["cells"]["TIR"]["B42"]["cached"]
        original_ev = model["cells"]["TIR"]["B38"]["cached"]
        replication.append(dict(entity_id=entity, calculated_share=legacy["average_share_value"], cached_share=original_target, absolute_error=abs(legacy["average_share_value"]-original_target), ev_error=abs(legacy["enterprise_value"]-original_ev)))
        debt = account(entity, "2.01.04") + account(entity, "2.02.01")
        cash = account(entity, "1.01.01", "BPA") + account(entity, "1.01.02", "BPA")
        minority = account(entity, "2.03.09")
        shares = capital[entity]["outstanding_million"]
        common = dict(wacc=.125, g=.035, tax=.34, inflation=macro, terminal_method="roic", terminal_roic=.125, net_debt=debt-cash, minority=minority, shares=shares)
        # Legacy operational trajectories are retained as proposals; not promoted to forecasts.
        base = value(model, common)
        if entity == "sanepar":
            full_adjustment = account(entity, "2.01.05.02.09") + account(entity, "2.02.02.02.10")
        elif entity == "copasa":
            full_adjustment = sum(account(entity,c) for c in ["2.01.05.02.09","2.02.02.02.08","2.01.05.02.10","2.01.05.02.11","2.02.02.02.10"])
        else:
            full_adjustment = sum(account(entity,c) for c in ["2.01.05.02.12","2.01.05.02.07","2.02.02.02.06"])
        # Not a definitive adjustment: cash-flow overlap and timing remain explicit.
        with_adjustment = value(model, {**common, "extra_obligations": full_adjustment})
        def paper(result):
            if entity == "sanepar":
                return allocate_sanepar(result["equity_value"])["SAPR11"]
            return result["average_share_value"]
        ticker = {"sabesp":"SBSP3","copasa":"CSMG3","sanepar":"SAPR11"}[entity]
        scenarios = []
        specs = [("Base ilustrativo", {}), ("WACC +1,5 p.p.", {"wacc":.14}), ("Margem -2 p.p.; capex +10%", {"margin_delta":-.02,"capex_multiplier":1.1}), ("WACC -1 p.p.; margem +2 p.p.", {"wacc":.115,"margin_delta":.02})]
        for label, extra in specs:
            calculated = value(model, {**common, **extra})
            scenarios.append(dict(label=label, paper_value=paper(calculated), enterprise_value=calculated["enterprise_value"], extra_obligations=0, assumptions=extra))
        sensitivity = []
        for w in [.105,.115,.125,.135,.145]:
            for g in [.025,.035,.045]:
                calculated = value(model, {**common, "wacc":w, "g":g})
                sensitivity.append(dict(wacc=w,g=g,paper_value=paper(calculated)))
        finite = value(model, {**common, "terminal_years":13})
        results[entity] = dict(entity_id=entity, ticker=ticker, status="conditional_draft_not_economic_certification", price_reference=prices[ticker], price_date="2026-10-30", price_status="public_provider_pending_terminal_confirmation", balance_date="2026-06-30", balance_roll_forward_status="not_observed_october; explicit sensitivity required", legacy=legacy, common_base=base, obligations_identified_book=full_adjustment, obligations_treatment="0 to full nominal balance is a diagnostic overlap range, not a validated PV adjustment", unadjusted_paper_value=paper(base), diagnostic_full_deduction_paper_value=paper(with_adjustment), finite_2048_stress_paper_value=paper(finite), finite_stress_caveat="Uniform tail cutoff is a sensitivity, not a claim that every contract expires in 2048", market_cap_class_weighted=prices["SAPR3"]*503.735259+prices["SAPR4"]*1007.470260 if entity=="sanepar" else prices[ticker]*shares, scenarios=scenarios, sensitivity=sensitivity, class_allocation_assumption="PN/ON=1.1 for equal-risk recurring distributions; control/terminal rights may change this" if entity=="sanepar" else "ordinary outstanding shares", critical_limitations=["operating assumptions inherited as proposals; H08 review", "net debt is last published June balance, not observed October", "concession renewal and terminal ROIC assumptions", "additional obligations may overlap cash flows; no definitive adjusted price target"])
        results[entity]["net_debt_sensitivity"] = [{"net_debt_delta": delta, "paper_value": paper(value(model, {**common, "net_debt": debt-cash+delta}))} for delta in [-.1*abs(debt-cash), 0, .1*abs(debt-cash)]]
        results[entity]["financial_scope"] = "individual; non-controlling equity not applicable in this perimeter" if entity == "sanepar" else "consolidated"
        accounting_only = value(model, {"net_debt":debt-cash,"minority":minority,"shares":shares})
        normalized_legacy_terminal = value(model, {**common,"terminal_method":"legacy_da"})
        results[entity]["accounting_update_only_paper_value"] = paper(accounting_only)
        results[entity]["common_macro_legacy_terminal_paper_value"] = paper(normalized_legacy_terminal)
        results[entity]["equity_floor_warning"] = "Nonpositive DCF residual: no meaningful share price target from this case; zero is limited-liability floor, not fair-value certification" if base["equity_floor_applied"] else ""
    write_json("data/processed/valuation.json", results)
    write_json("data/processed/scenarios.json", {e:r["scenarios"] for e,r in results.items()})
    write_json("outputs/qa/model_replication.json", {"results":replication,"passed":all(r["absolute_error"]<1e-6 and r["ev_error"]<1e-5 for r in replication),"scope":"Mathematical replication only; does not certify inputs or assumptions"})
    # Quantitative ESG bridge: energy saving threshold, water-only SINISA scope.
    energy = read_json("data/processed/sinisa_energy.json")
    bridge = []
    for item in energy:
        entity = item["entity_id"]
        base_cost = item["value_brl_million"]
        # Inflate 2024 to 2025 using actual monthly IPCA, 2026+ by Focus/proposed curve.
        ipca25 = [float(r["value"]) for r in read_csv("data/processed/observations.csv") if r["metric_id"]=="ipca_monthly" and r["period_end"].startswith("2025-")]
        if len(ipca25)!=12:raise ValueError('Energy bridge requires all 12 actual monthly IPCA readings for 2025')
        actual25 = prod(1+x for x in ipca25)-1
        cost26 = base_cost*(1+actual25)*(1+macro["2026"])
        max_capex=0
        yearly=[]
        cost=cost26
        for year in range(2027,2036):
            cost *= 1+macro[str(year)]
            saving=cost*.01*(1-.34)
            years=(date(year,12,31)-date(2026,10,30)).days/365
            pv=saving/(1+.125)**years
            max_capex+=pv
            yearly.append(dict(year=year,cost_baseline=cost,gross_saving=cost*.01,after_tax_saving=saving,pv=pv))
        bridge.append(dict(entity_id=entity,source_id=item["source_id"],base_year=2024,scope=item["scope"],base_energy_expense=base_cost,saving_fraction=.01,tax=.34,wacc=.125,years=yearly,capex_break_even_upper=max_capex,capex_break_even_50pct_retention=max_capex*.5,interpretation="Sensitivity: 1% lower water electricity expense, not achieved result or identified project. Conditional upfront capex ceiling for this horizon and retention assumptions; no terminal saving or capex tax shield. Do not add to base DCF without reconciling gains already in margins.",operational_limit="Expense reduction is assumed; average energy expense is not a measured marginal water-loss cost; scope is municipal water service."))
    write_json("data/processed/esg_bridge.json", bridge)
    print("Model replication",replication)
    print("Conditional values",{e:(r["unadjusted_paper_value"],r["diagnostic_full_deduction_paper_value"]) for e,r in results.items()})


if __name__ == "__main__":
    build()
