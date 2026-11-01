"""AN08 — motor FCFF do ramo revisado com vínculo capex → base remunerada → EBITDA.

Funções puras (sem I/O). Valores em R$ milhões nominais; base real em preços de 2025.

Base remunerada implícita: o EBIT recorrente de 2025 é tratado como retorno regulatório
pré-impostos sobre a base então remunerada (B0 = EBIT/r_pre). Capex próprio elegível entra
na base após L anos; a remuneração (r_pre + δ) é indexada ao IPCA. Não é a BRR oficial (não
obtida); é a base econômica consistente com o EBIT observado.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

VALUATION = date(2026, 10, 30)
STUB_FRACTION = (date(2026, 12, 31) - VALUATION).days / 365       # 62/365
ROLLFORWARD_FRACTION = (VALUATION - date(2026, 6, 30)).days / 365  # 122/365
YEARS = list(range(2026, 2036))


@dataclass
class Params:
    entity: str
    ebitda0: float
    da0: float
    revenue0: float
    wc_ratio: float
    r_pre: float              # remuneração regulatória real pré-impostos
    r_post: float             # remuneração regulatória real pós-impostos
    tax: float
    lag: int
    share: float              # fração capturada da remuneração
    opex_shock: float         # desvio de custo (fração da receita)
    eligible: float
    capex_plan: dict          # ano → capex caixa nominal (anos do plano)
    capex_hist: dict          # 2023..2025 capex caixa nominal
    infl: dict                # ano → IPCA (2024..2035)
    g_real: float
    wacc: float
    terminal: str = "perpetuity"   # ou "finite"
    finite_years: int | None = None
    indemnity: float = 1.0
    extra_ebitda: dict = field(default_factory=dict)  # ano → efeito ESG etc. (não usado no caso-base)


def _index(infl: dict) -> dict:
    """Índice de preços com 2025 = 1."""
    idx = {2025: 1.0}
    idx[2024] = 1 / (1 + infl[2025])
    idx[2023] = idx[2024] / (1 + infl[2024])
    idx[2022] = idx[2023]  # só usado como semente quando L=3 (sem capex)
    for y in YEARS:
        idx[y] = idx[y - 1] * (1 + infl[y])
    return idx


def run(p: Params) -> dict:
    if p.r_pre <= 0 or p.wacc <= 0:
        raise ValueError("Taxas devem ser positivas")
    idx = _index(p.infl)
    ebit0 = p.ebitda0 - p.da0
    if ebit0 <= 0:
        raise ValueError("EBIT-base não positivo: base remunerada implícita indefinida")
    b0 = ebit0 / p.r_pre
    delta = p.da0 / b0
    margin0 = p.ebitda0 / p.revenue0
    # Histórico da base total (preços 2025): R_2025 = K_{2025−L} = B0.
    k = {2025 - p.lag: b0}
    for s in range(2025 - p.lag + 1, 2026):
        k[s] = k[s - 1] * (1 - delta) + p.eligible * p.capex_hist[s] / idx[s]
    rows, rev_prev = [], p.revenue0
    for y in YEARS:
        if y in p.capex_plan:
            capex = p.capex_plan[y]
        else:
            capex = idx[y] * k[y - 1] * (delta + p.g_real) / p.eligible
        k[y] = k[y - 1] * (1 - delta) + p.eligible * capex / idx[y]
        remunerated = k[y - p.lag]
        ebitda_reg = (p.r_pre + delta) * remunerated * idx[y]
        revenue = ebitda_reg / margin0
        ebitda = p.share * ebitda_reg - p.opex_shock * revenue + p.extra_ebitda.get(y, 0.0)
        tax_da = delta * k[y - 1] * idx[y]
        tax = p.tax * max(ebitda - tax_da, 0.0)
        dwc = p.wc_ratio * (revenue - rev_prev)
        fcff = ebitda - tax - capex - dwc
        if y == 2026:
            t, weight = STUB_FRACTION / 2, STUB_FRACTION
        else:
            t, weight = (date(y, 7, 1) - VALUATION).days / 365, 1.0
        df = (1 + p.wacc) ** (-t)
        rows.append(dict(year=y, inflation=p.infl[y], price_index=idx[y], capex=capex, base_total_real=k[y],
                         base_remunerated_real=remunerated, ebitda_regulated=ebitda_reg, revenue=revenue, ebitda=ebitda,
                         tax_depreciation=tax_da, tax=tax, delta_wc=dwc, fcff=fcff, weight=weight, time_years=t,
                         discount_factor=df, pv=fcff * weight * df))
        rev_prev = revenue
    pi_lr = p.infl[2035]
    g = (1 + pi_lr) * (1 + p.g_real) - 1
    if p.wacc <= g:
        raise ValueError("DCF exige WACC > g")
    kt, it1 = k[2035], idx[2035] * (1 + pi_lr)
    ebitda_reg_t1 = (p.r_pre + delta) * kt * it1
    rev_t1 = ebitda_reg_t1 / margin0
    ebitda_t1 = p.share * ebitda_reg_t1 - p.opex_shock * rev_t1
    nopat_t1 = (ebitda_t1 - delta * kt * it1) * (1 - p.tax)
    fcff_t1 = nopat_t1 - p.g_real * kt * it1 - p.wc_ratio * rev_t1 * g / (1 + g)
    t_end = (date(2035, 12, 31) - VALUATION).days / 365
    if p.terminal == "perpetuity":
        tv = fcff_t1 / (p.wacc - g)
    elif p.terminal == "finite":
        if not p.finite_years or p.finite_years <= 0:
            raise ValueError("Horizonte finito exige anos restantes de concessão")
        n = p.finite_years
        annuity = (1 - ((1 + g) / (1 + p.wacc)) ** n) / (p.wacc - g)
        residual = p.indemnity * kt * idx[2035] * (1 + g) ** n
        tv = fcff_t1 * annuity + residual / (1 + p.wacc) ** n
    else:
        raise ValueError(p.terminal)
    pv_tv = tv * (1 + p.wacc) ** (-t_end)
    pv_explicit = sum(r["pv"] for r in rows)
    ev = pv_explicit + pv_tv
    wacc_real = (1 + p.wacc) / (1 + pi_lr) - 1
    return dict(b0=b0, delta=delta, margin0=margin0, rows=rows, g=g, terminal_fcff=fcff_t1, terminal_value=tv, pv_terminal=pv_tv,
                pv_explicit=pv_explicit, enterprise_value=ev, terminal_share=pv_tv / ev if ev else None,
                fcff_2026_full=rows[0]["fcff"], ebitda_2026=rows[0]["ebitda"], wacc_real=wacc_real,
                rab_value_ratio=(p.share * p.r_post - p.g_real) / (wacc_real - p.g_real))


def bridge(ev: float, fcff_2026_full: float, net_debt_june: float, debt_like: float, grantor: float, grantor_ratio: float,
           obligation_pv: float) -> dict:
    """EV(30/10) → patrimônio: dívida rolada de junho a outubro pelo FCFF jul–out (sazonalidade uniforme)."""
    rolled = net_debt_june - fcff_2026_full * ROLLFORWARD_FRACTION
    grantor_credit = grantor * grantor_ratio
    residual = ev - rolled - debt_like - grantor + grantor_credit - obligation_pv
    return dict(net_debt_october_estimate=rolled, debt_like=debt_like, grantor=grantor, grantor_regulatory_credit=grantor_credit,
                obligation_pv=obligation_pv, equity_residual=residual)
