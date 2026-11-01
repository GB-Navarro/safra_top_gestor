"""AN04 — saldos e obrigações identificadas (C10) e AN07 — precatório e ponte temporal (C11, C12).

Cada obrigação entra uma única vez: no fluxo, na base/tarifa ou na ponte EV→acionista.
Saldos contábeis não são tratados como PV quando há fluxo próprio (precatório).
"""
from __future__ import annotations

import re
from datetime import date

from .data import Baseline, Registry, loc_of

JUNE = "2026-06-30"
VALUATION = date(2026, 10, 30)
ADJ_HEADER = ["adjustment_id", "entity_id", "reference_date", "adjustment_type", "amount", "unit", "scale", "economic_treatment",
              "source_ids", "source_location", "review_status", "double_counting_check", "value_id", "bridge_case"]
SCHEDULE_HEADER = ["schedule_id", "obligation_id", "entity_id", "component", "flow_date", "indexer", "nominal_value", "unit", "scale",
                   "tax_treatment", "economic_line", "already_recognized_in", "source_refs", "hypothesis", "discount_convention", "status"]

# (rótulo, demonstração, código-pai, padrão de nome)
COMPONENTS = {
    "lease_separate": [("BPP", "2.01.05.02", r"Arrendamento"), ("BPP", "2.02.02.02", r"Arrendamento")],
    "ppp": [("BPP", "2.01.05.02", r"Parceria|PPP"), ("BPP", "2.02.02.02", r"Parceria|PPP")],
    "derivatives_liab": [("BPP", "2.01.05.02", r"Derivativ"), ("BPP", "2.02.02.02", r"Derivativ")],
    "grantor": [("BPP", "2.01.05.02", r"Poder Concedente"), ("BPP", "2.02.02.02", r"Poder Concedente")],
    "dividends_payable": [("BPP", "2.01.05.02", r"Dividendos")],
    "post_employment": [("BPP", "2.02.02.02", r"Previdenci|Aposentadoria"), ("BPP", "2.01.06.02", r"Aposentadoria"),
                        ("BPP", "2.02.04.02", r"Aposentadoria")],
    "supplier_finance": [("BPP", "2.01.05.02", r"Risco Sacado")],
    "regulatory_liability": [("BPP", "2.01.05.02", r"Passivo Regulat"), ("BPP", "2.02.02.02", r"Passivo Regulat")],
    "contingencies": [("BPP", "2.02.04.01", r"."), ("BPP", "2.02.04.02", r"^Provis[õo]es$"), ("BPP", "2.01.06.02", r"Trabalhistas")],
}
TREATMENT = {
    "lease_separate": ("debt_like_base", "Passivo de arrendamento fora de 'Empréstimos' (valor presente contábil). Pagamentos não estão no EBITDA pós-IFRS16."),
    "ppp": ("debt_like_base", "Parcela de capital das PPPs (VP contábil); contraprestação de serviço segue no custo."),
    "derivatives_liab": ("debt_like_base", "Derivativos de proteção da dívida (líquidos de ativos); compõem o custo econômico da dívida."),
    "grantor": ("debt_like_base_with_rab_credit", "Obrigação com poder concedente (VP contábil); valores repassados entram na BRR (release 2T26 p20) — crédito pelo valor regulatório na ponte."),
    "dividends_payable": ("debt_like_base", "Proventos declarados até junho pertencem a acionistas de datas anteriores (preço de 30/10 ex)."),
    "post_employment": ("debt_like_base", "Déficit atuarial de benefícios pós-emprego (VP atuarial) não incluído no FCFF."),
    "supplier_finance": ("debt_like_base", "Risco sacado: financiamento de fornecedor."),
    "regulatory_liability": ("schedule_pv", "Precatório: não deduzido pelo saldo; PV do cronograma AN07."),
    "contingencies": ("adverse_only", "Provisões contingenciais (prováveis): só no cenário adverso; base supõe que desembolsos recorrentes estão no EBITDA."),
}


def _match(base: Baseline, entity: str, stmt: str, parent: str, pattern: str) -> list[dict]:
    kids = base.children(entity, stmt, JUNE, parent)
    if not kids:
        return []
    rx = re.compile(pattern, re.I)
    return [k for k in kids if rx.search(k["account_name"]) and abs(float(k["value_brl_million"])) > 0]


def balances(reg: Registry, base: Baseline) -> dict:
    out, adj_rows = {}, []
    for entity in ("sabesp", "copasa", "sanepar"):
        d = {}
        debt_parts = [base.cvm(entity, "BPP", JUNE, code=c) for c in ("2.01.04", "2.02.01")]
        cash_parts = [base.cvm(entity, "BPA", JUNE, code=c, required=False) for c in ("1.01.01", "1.01.02")]
        cash_parts = [p for p in cash_parts if p[0] is not None]
        src = debt_parts[0][1]["source_id"]
        d["gross_debt"] = reg.value(f"V.{entity}.gross_debt.{JUNE}", metric_id="gross_financial_debt", entity_id=entity,
                                    value=sum(p[0] for p in debt_parts), unit="BRL", scale=1e6, value_state="derived", fact_type="derived",
                                    period_end=JUNE, scope=debt_parts[0][1]["scope"], source_refs=[src], calculation_ref="BPP 2.01.04 + 2.02.01",
                                    locator=" | ".join(loc_of(p[1]) for p in debt_parts),
                                    note="Empréstimos, financiamentos e debêntures (inclui arrendamentos/PPP quando a companhia os classifica aí).")
        d["cash"] = reg.value(f"V.{entity}.cash.{JUNE}", metric_id="cash_and_investments", entity_id=entity,
                              value=sum(p[0] for p in cash_parts), unit="BRL", scale=1e6, value_state="derived", fact_type="derived",
                              period_end=JUNE, scope=debt_parts[0][1]["scope"], source_refs=[src], calculation_ref="BPA 1.01.01 + 1.01.02",
                              locator=" | ".join(loc_of(p[1]) for p in cash_parts),
                              note="Caixa e aplicações circulantes; exclui caixa restrito/vinculado e aplicações de longo prazo.")
        d["net_debt"] = reg.value(f"V.{entity}.net_debt.{JUNE}", metric_id="net_financial_debt", entity_id=entity,
                                  value=reg.get(d["gross_debt"]) - reg.get(d["cash"]), unit="BRL", scale=1e6, value_state="derived",
                                  fact_type="derived", period_end=JUNE, calculation_ref=f"{d['gross_debt']} − {d['cash']}",
                                  note="Dívida líquida financeira de junho/2026 (último balanço publicado antes do corte).")
        adj_rows.append(dict(adjustment_id=f"ADJ.{entity}.net_debt", entity_id=entity, reference_date=JUNE, adjustment_type="net_financial_debt",
                             amount=reg.get(d["net_debt"]), unit="BRL", scale=1e6, economic_treatment="debt_base; rolada até 30/10 por FCFF jul–out (AN07)",
                             source_ids=[src], source_location="BPP 2.01.04+2.02.01; BPA 1.01.01+1.01.02", review_status="reconciled_cvm",
                             double_counting_check="Juros fora do FCFF; caixa do precatório (Sanepar) incluído aqui e obrigação no PV AN07.",
                             value_id=d["net_debt"], bridge_case="all"))
        for comp, specs in COMPONENTS.items():
            rows = []
            for stmt, parent, pat in specs:
                rows += _match(base, entity, stmt, parent, pat)
            if comp == "post_employment":
                rows = [r for r in rows if not re.search(r"Trabalhist", r["account_name"], re.I)]
            if comp == "contingencies" and not rows:
                # Sabesp publica provisões só no nível agregado em 2026; pós-emprego está em 2.02.02.02.
                rows = [base.cvm(entity, "BPP", JUNE, code=c)[1] for c in ("2.01.06", "2.02.04")]
            amount = sum(float(r["value_brl_million"]) for r in rows)
            if comp == "derivatives_liab":
                assets = [r for r in base.children(entity, "BPA", JUNE, "1.01.08.03") + base.children(entity, "BPA", JUNE, "1.02.01.10")
                          if re.search(r"Derivativ", r["account_name"], re.I)]
                amount -= sum(float(r["value_brl_million"]) for r in assets)
                rows += assets
            if not rows:
                continue
            treat, why = TREATMENT[comp]
            vid = reg.value(f"V.{entity}.{comp}.{JUNE}", metric_id=f"obligation_{comp}", entity_id=entity, value=amount, unit="BRL",
                            scale=1e6, value_state="derived", fact_type="derived", period_end=JUNE, scope=rows[0]["scope"],
                            source_refs=[rows[0]["source_id"]], calculation_ref=" + ".join(f"{r['statement']} {r['account_code']}" for r in rows),
                            locator=" | ".join(loc_of(r) for r in rows), note=why)
            d[comp] = vid
            adj_rows.append(dict(adjustment_id=f"ADJ.{entity}.{comp}", entity_id=entity, reference_date=JUNE, adjustment_type=comp,
                                 amount=amount, unit="BRL", scale=1e6, economic_treatment=treat, source_ids=[rows[0]["source_id"]],
                                 source_location="; ".join(f"{r['account_code']} {r['account_name']}" for r in rows),
                                 review_status="balance_reconciled_cvm_treatment_proposed", double_counting_check=why, value_id=vid,
                                 bridge_case="adverse" if treat == "adverse_only" else "all"))
        out[entity] = d
    # Conferência com o release da Copasa (poder concedente fora da dívida do modelo original).
    base.require_text("doc_csmg_2t26", 20, "será incorporada à Base de Remuneração Regulatória")
    return {"items": out, "adjustments": adj_rows}


def _month_dates(start: tuple[int, int], end: tuple[int, int]) -> list[date]:
    y, m = start
    out = []
    while (y, m) <= end:
        out.append(date(y, m, 15))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def precatorio_schedule(reg: Registry, base: Baseline, infl: dict[int, float], case: str = "base") -> list[dict]:
    """Fluxos datados do precatório a partir de 01/07/2026 (saldo de 30/06/2026).

    Regra Agepar (23/06/2026): 100% aos usuários, 50% descontos tarifários (até mai/2029) e 50% investimentos
    não onerosos (até dez/2030), atualizados por 8,08% real + IPCA. A parcela circulante (R$ 1.128,65 mi)
    é a estimativa da própria companhia para os 12 meses seguintes.
    """
    base.require_text("doc_sapr_itr", 62, "R$4.407.957", "Passivo Circulante (R$1.128.650)", "Passivo Não Circulante (R$3.279.307)",
                      "até maio de 2029 para tarifas e até dezembro de 2030 para CAPEX")
    base.require_text("doc_sapr_prec", 1, "desconto de 25% na tarifa mínima")
    total, current = 4407.957, 1128.650
    share = {"base": 1.0, "adverse": 1.0, "favorable": 0.75}[case]
    disc_end = (2029, 5) if case != "adverse" else (2029, 2)
    real = 0.0808

    def monthly_rate(d: date) -> float:
        return ((1 + real) * (1 + infl[d.year])) ** (1 / 12) - 1

    flows = []
    # Descontos: início 24/08/2026 → primeiro faturamento afetado em set/2026; anuidade re-resolvida mês a mês.
    bal = total * 0.5 * share
    months = _month_dates((2026, 7), disc_end)
    for i, d in enumerate(months):
        bal *= 1 + monthly_rate(d)
        if d < date(2026, 9, 1):
            continue
        n_left = sum(1 for x in months[i:] if x >= date(2026, 9, 1))
        r = monthly_rate(d)
        pay = bal * r / (1 - (1 + r) ** (-n_left)) if r > 0 else bal / n_left
        bal -= pay
        flows.append({"date": d, "component": "tariff_discount", "nominal": pay})
    disc_12m = sum(f["nominal"] for f in flows if f["date"] < date(2027, 7, 1))
    # Investimento não oneroso: parcela de 12 meses implícita no passivo circulante; restante até dez/2030.
    capex_bal = total * 0.5 * share
    capex_12m = max(current * share - disc_12m, 0.0)
    first = _month_dates((2026, 7), (2027, 6))
    for d in first:
        capex_bal *= 1 + monthly_rate(d)
        pay = capex_12m / len(first)
        capex_bal -= pay
        flows.append({"date": d, "component": "non_onerous_capex", "nominal": pay})
    rest = _month_dates((2027, 7), (2030, 12))
    for i, d in enumerate(rest):
        capex_bal *= 1 + monthly_rate(d)
        r = monthly_rate(d)
        n_left = len(rest) - i
        pay = capex_bal * r / (1 - (1 + r) ** (-n_left))
        capex_bal -= pay
        flows.append({"date": d, "component": "non_onerous_capex", "nominal": pay})
    tax_shield = 0.34 if case == "favorable" else 0.0
    for f in flows:
        f["after_tax"] = f["nominal"] * (1 - tax_shield) if f["component"] == "tariff_discount" else f["nominal"]
    return flows


def pv_flows(flows: list[dict], wacc: float, key: str = "after_tax") -> tuple[float, float]:
    """PV em 30/10/2026; fluxos jul–out (passados) são capitalizados até a data e separados."""
    pv_future, past = 0.0, 0.0
    for f in flows:
        t = (f["date"] - VALUATION).days / 365
        if t < 0:
            past += f[key] * (1 + wacc) ** (-t)
        else:
            pv_future += f[key] * (1 + wacc) ** (-t)
    return pv_future, past


def schedule_rows(flows_by_case: dict) -> list[dict]:
    rows = []
    for case, flows in flows_by_case.items():
        for i, f in enumerate(flows):
            rows.append(dict(schedule_id=f"OS.sanepar.precatorio.{case}.{i:03d}", obligation_id="OBL.sanepar.precatorio", entity_id="sanepar",
                             component=f["component"], flow_date=f["date"].isoformat(), indexer="IPCA + 8,08% real até a aplicação",
                             nominal_value=round(f["nominal"], 6), unit="BRL", scale=1e6,
                             tax_treatment="sem benefício fiscal" if f["after_tax"] == f["nominal"] else "benefício de 34% sobre desconto",
                             economic_line="receita (desconto tarifário)" if f["component"] == "tariff_discount" else "capex fora da base remunerada",
                             already_recognized_in="nenhuma linha do FCFF; EBITDA-base 2025 é anterior aos descontos; plano de 11/12/2025 é anterior à decisão",
                             source_refs=["SRC_doc_sapr_itr_d93332d6", "SRC_doc_sapr_prec_39f99f35", "SRC_agepar_precatorio_20260819_e549038f"],
                             hypothesis={"base": "100% (decisão Agepar 23/06/2026); descontos set/2026–mai/2029; capex até dez/2030",
                                         "adverse": "100%; descontos concentrados até fev/2029 (estimativa Agepar de ~30 meses)",
                                         "favorable": "75% (regra anterior, se a contestação judicial prosperar) e benefício fiscal no desconto"}[case],
                             discount_convention="WACC nominal do caso; mês no dia 15; fluxos jul–out capitalizados até 30/10 na ponte",
                             status="cronograma estimado; calendário mensal não divulgado"))
    return rows
