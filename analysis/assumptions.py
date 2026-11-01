"""AN06 — trajetórias operacionais, regulação e taxa de desconto (C13, C14).

Cada driver tem base/adversa/favorável, unidade, justificativa e evidência. Nenhum valor é
ajustado para atingir cotação; a única calibração usa dados operacionais (EBIT 2025 → base
remunerada implícita) e é testada contra o crescimento observado no 1º semestre de 2026.
"""
from __future__ import annotations

from .data import Baseline, Registry

YEARS = list(range(2026, 2036))
TAX = 0.34


def macro(reg: Registry, base: Baseline) -> dict:
    out = {}
    for r in base.csv("data/processed/estimate_snapshots.csv"):
        y = int(r["forecast_period"])
        out[y] = reg.value(f"V.macro.ipca_focus.{y}", metric_id="ipca_expectation", value=float(r["value"]), unit="ratio",
                           value_state="observed", fact_type="fact", period_start=f"{y}-01-01", period_end=f"{y}-12-31",
                           observed_at=r["snapshot_date"], scope="Brasil; mediana Focus", source_refs=[r["source_id"]],
                           locator=r["source_location"], note="Expectativa de mercado (mediana) — fato sobre a pesquisa, não sobre a inflação futura.")
    reg.assumption("ipca_long_run", entity_id="", driver="ipca_after_2030", year="2031-2035", base=reg.get(out[2030]),
                   adverse=reg.get(out[2030]) + 0.005, favorable=reg.get(out[2030]) - 0.005, unit="ratio",
                   rationale="Focus termina em 2030; anos seguintes repetem a mediana de 2030 (meta 3%+desvio histórico).",
                   supporting_obs_ids=[out[2030]], source_id="SRC_bcb_focus_ipca_2030_d5044e13", source_location="Focus 2030")
    actual = {}
    obs = [r for r in base.csv("data/processed/observations.csv") if r["metric_id"] == "ipca_monthly"]
    for y in (2021, 2022, 2023, 2024, 2025):
        months = [float(r["value"]) for r in obs if r["period_end"].startswith(f"{y}-")]
        if len(months) != 12:
            raise ValueError(f"IPCA mensal incompleto em {y}")
        acc = 1.0
        for m in months:
            acc *= 1 + m
        actual[y] = reg.value(f"V.macro.ipca_actual.{y}", metric_id="ipca_actual_annual", value=acc - 1, unit="ratio",
                              value_state="derived", fact_type="derived", period_start=f"{y}-01-01", period_end=f"{y}-12-31",
                              source_refs=["SRC_bcb_sgs_433_a47db5ed"], calculation_ref="produto de 12 variações mensais SGS 433",
                              note="IPCA realizado no ano.")
    return {"focus": out, "actual": actual}


def inflation_path(reg: Registry, m: dict, case: str = "base") -> dict[int, float]:
    lr = reg.get(reg.assumptions["ipca_long_run"]["value_refs"][case])
    return {y: (reg.get(m["focus"][y]) if y <= 2030 else lr) for y in YEARS}


def build(reg: Registry, base: Baseline, rec: dict, cap: dict, m: dict) -> dict:
    a = {}
    # ---------------- Taxa de desconto de mercado (C14) ----------------------------------
    tes = base.json("derived/tesouro_20261030.json")["rows"]
    ntnb = next(r for r in tes if r["Tipo Titulo"] == "Tesouro IPCA+" and r["Data Vencimento"] == "15/05/2035")
    rf_real = float(ntnb["Taxa Compra Manha"].replace(",", ".")) / 100
    rf_id = reg.value("V.macro.ntnb_2035_real.2026-10-30", metric_id="real_risk_free", value=rf_real, unit="ratio", value_state="observed",
                      fact_type="fact", period_end="2026-10-30", observed_at="2026-10-30", scope="Tesouro IPCA+ 15/05/2035, taxa de compra manhã",
                      source_refs=["SRC_tesouro_taxas_84f53c4b"], locator=ntnb["locator"], note="Taxa real soberana; não é WACC.")
    reg.assumption("beta", entity_id="", driver="equity_beta", year="", base=0.80, adverse=0.95, favorable=0.65, unit="ratio",
                   rationale="Beta de utility regulada (faixa usual 0,6–1,0 em saneamento brasileiro); regressão N22 omitida (C29).")
    reg.assumption("erp", entity_id="", driver="equity_risk_premium", year="", base=0.050, adverse=0.060, favorable=0.040, unit="ratio",
                   rationale="Prêmio de risco de ações sobre a taxa real soberana local; sem estimativa própria, faixa explícita.")
    reg.assumption("debt_spread", entity_id="", driver="debt_real_spread_over_ntnb", year="", base=0.010, adverse=0.015, favorable=0.005,
                   unit="ratio", rationale="Debêntures incentivadas de saneamento negociam próximas à NTN-B (Sabesp: CDI−0,20% em 2025, DF2025 p13).")
    reg.assumption("leverage", entity_id="", driver="debt_to_capital", year="", base=0.40, adverse=0.30, favorable=0.50, unit="ratio",
                   rationale="Estrutura-alvo; Sabesp reporta índice de alavancagem de 40% (dívida líquida/capital total, DF2025 p14).",
                   source_id="local_45586543e35a", source_location="DF2025 p14 'Índice de Alavancagem 40%'")
    lr = reg.get(reg.assumptions["ipca_long_run"]["value_refs"]["base"])

    def wacc(case):
        g = lambda k: reg.get(reg.assumptions[k]["value_refs"][case])
        ke_real = rf_real + g("beta") * g("erp")
        kd_real_after = (rf_real + g("debt_spread")) * (1 - TAX)
        real = (1 - g("leverage")) * ke_real + g("leverage") * kd_real_after
        return (1 + real) * (1 + lr) - 1, real
    w_base, w_real = wacc("base")
    w_adv, _ = wacc("adverse")
    w_fav, _ = wacc("favorable")
    rounded = round(w_base * 400) / 400  # arredonda a 0,25 p.p.
    reg.assumption("wacc_nominal", entity_id="", driver="wacc_nominal_after_tax", year="", base=rounded, adverse=round(w_adv * 400) / 400,
                   favorable=round(w_fav * 400) / 400, unit="ratio",
                   rationale=(f"CAPM local real: NTN-B 2035 {rf_real:.2%} + beta×ERP; Kd real = NTN-B + spread, após 34%; "
                              f"pesos 60/40; convertido a nominal com IPCA de longo prazo {lr:.2%}. Valor calculado {w_base:.4%} "
                              f"(real {w_real:.4%}), arredondado a 0,25 p.p. Não é WACC regulatório nem XTIR."),
                   supporting_obs_ids=[rf_id], source_id="SRC_tesouro_taxas_84f53c4b", source_location=ntnb["locator"])
    a["wacc"] = reg.assumptions["wacc_nominal"]["value_refs"]
    a["rf"] = rf_id

    # ---------------- Regulação: remuneração e defasagem (C13/C15) --------------------------
    base.require_text("doc_sapr_itr", 62, "(8,08% a.a. em termos reais)")
    base.require_text("doc_csmg_2t26", 24, "WACC pré -impostos de 13,70% (equivalente a 9,79% pós -impostos")
    base.require_text("local_85acbb6423e6", 10, "remunerando-a sobre sua base de ativos regulatórios")
    reg.value("V.sanepar.wacc_reg_real_after_tax", metric_id="regulatory_wacc_real_after_tax", entity_id="sanepar", value=0.0808,
              unit="ratio", value_state="observed", fact_type="fact", period_end="2026-06-30", scope="ciclo tarifário vigente (RTP 2025–28)",
              source_refs=["SRC_doc_sapr_itr_d93332d6", "SRC_doc_sapr_prec_39f99f35"], locator="ITR 2T26 nota 20 p62; fato relevante 23/06/2026",
              note="WACC regulatório real líquido de impostos.")
    reg.value("V.copasa.wacc_reg_real_after_tax", metric_id="regulatory_wacc_real_after_tax", entity_id="copasa", value=0.0979,
              unit="ratio", value_state="observed", fact_type="fact", period_end="2026-06-30", scope="3ª RTP Arsae-MG (2026–29)",
              source_refs=["SRC_doc_csmg_2t26_1996f20b"], locator="Release 2T26 p24", note="Equivalente pós-impostos ao WACC pré-impostos de 13,70%.")
    reg.value("V.copasa.wacc_reg_real_pre_tax", metric_id="regulatory_wacc_real_pre_tax", entity_id="copasa", value=0.1370,
              unit="ratio", value_state="observed", fact_type="fact", period_end="2026-06-30", scope="3ª RTP Arsae-MG (2026–29)",
              source_refs=["SRC_doc_csmg_2t26_1996f20b"], locator="Release 2T26 p24", note="WACC pré-impostos (nova metodologia).")
    base.require_text("urae1_anexo_viii", 26, "WACC real após impostos 7,86%", "WACC real antes de impostos 11,91%",
                      "deverá ser mantido constante nos REAJUSTES anuais do 1º CICLO TARIFÁRIO")
    reg.value("V.sabesp.wacc_reg_real_after_tax", metric_id="regulatory_wacc_real_after_tax", entity_id="sabesp", value=0.0786, unit="ratio",
              value_state="observed", fact_type="fact", scope="Contrato URAE-1, 1º ciclo tarifário (até 2029)", source_refs=["SRC_urae1_anexo_viii_2025"],
              locator="Anexo VIII item 10.7, Tabela 5 (p26)", note="Fixo nos reajustes anuais do 1º ciclo; recalculado pela Arsesp na 1ª revisão periódica (2º ciclo).")
    reg.value("V.sabesp.wacc_reg_real_pre_tax", metric_id="regulatory_wacc_real_pre_tax", entity_id="sabesp", value=0.1191, unit="ratio",
              value_state="observed", fact_type="fact", scope="Contrato URAE-1, 1º ciclo tarifário (até 2029)", source_refs=["SRC_urae1_anexo_viii_2025"],
              locator="Anexo VIII item 10.7, Tabela 5 (p26)", note="WACC real antes de impostos usado na remuneração do capital.")
    reg.assumption("sabesp_wacc_reg", entity_id="sabesp", driver="regulatory_wacc_real_after_tax", year="", base=0.0786, adverse=0.0750,
                   favorable=0.0850, unit="ratio",
                   rationale=("Base = 7,86% real pós-impostos (11,91% pré), fixado no Anexo VIII do contrato URAE-1 e mantido nos reajustes do "
                              "1º ciclo (até 2029). As alternativas 7,5%/8,5% testam a revisão do 2º ciclo (2030+) e, por simplificação, "
                              "valem para todo o horizonte: exageram o efeito antes de 2030."),
                   supporting_obs_ids=["V.sabesp.wacc_reg_real_after_tax"], source_id="SRC_urae1_anexo_viii_2025",
                   source_location="Anexo VIII item 10.7, Tabela 5 (p26)")
    reg.assumption("sanepar_wacc_reg_case", entity_id="sanepar", driver="regulatory_wacc_real_after_tax", year="", base=0.0808,
                   adverse=0.0758, favorable=0.0808, unit="ratio",
                   rationale="Valor vigente (8,08%); adversa reflete risco de redução na próxima revisão (2029).",
                   supporting_obs_ids=["V.sanepar.wacc_reg_real_after_tax"], source_id="SRC_doc_sapr_itr_d93332d6", source_location="nota 20 p62")
    reg.assumption("copasa_wacc_reg_case", entity_id="copasa", driver="regulatory_wacc_real_after_tax", year="", base=0.0979,
                   adverse=0.0929, favorable=0.0979, unit="ratio",
                   rationale="Valor da 3ª RTP (9,79% pós; 13,70% pré); adversa −0,5 p.p. no ciclo seguinte.",
                   supporting_obs_ids=["V.copasa.wacc_reg_real_after_tax"], source_id="SRC_doc_csmg_2t26_1996f20b", source_location="p24")
    a["reg_wacc"] = {"sabesp": reg.assumptions["sabesp_wacc_reg"]["value_refs"],
                     "sanepar": reg.assumptions["sanepar_wacc_reg_case"]["value_refs"],
                     "copasa": reg.assumptions["copasa_wacc_reg_case"]["value_refs"]}
    reg.assumption("recognition_lag", entity_id="", driver="regulatory_recognition_lag_years", year="", base=2, adverse=3, favorable=1,
                   unit="years",
                   rationale=("Capex entra na base remunerada após revisão/reajuste (Sabesp: revisão anual retrospectiva da base; Copasa: "
                              "reconhecimento anual na 3ª RTP; Sanepar: ciclo 2025–28 com investimentos projetados). Com defasagem de 1 ano "
                              "o EBITDA-modelo de 2026 cresceria 15–18%, acima do observado no 1º semestre (6–10% nominal; ver QA de calibração); "
                              "base usa 2 anos."),
                   source_id="local_85acbb6423e6", source_location="DFP 2024 p10 (reajustes anuais com incorporação de base)")
    reg.assumption("recognition_share", entity_id="", driver="share_of_regulated_return_captured", year="", base=1.0, adverse=0.85,
                   favorable=1.0, unit="ratio",
                   rationale="Fração da remuneração regulatória efetivamente capturada (glosas, Fator U de até 10% na Sabesp, diferimentos).",
                   source_id="SRC_an_sabesp_inst_2025", source_location="Apresentação institucional fev/2025 p8, p10 (Fator U)")
    reg.assumption("opex_shock", entity_id="", driver="opex_deviation_share_of_revenue", year="2026-2035", base=0.0, adverse=0.02,
                   favorable=-0.01, unit="ratio",
                   rationale="Desvio de custos não reconhecido na tarifa (adverso, ~margem −2 p.p.) ou eficiência retida (favorável; Sabesp retém 100% até 2029).",
                   source_id="SRC_an_sabesp_inst_2025", source_location="p8: sem compartilhamento de eficiência até 2029")
    a["lag"], a["share"], a["opex"] = (reg.assumptions[k]["value_refs"] for k in ("recognition_lag", "recognition_share", "opex_shock"))

    # ---------------- Capex por empresa (C06, C08, C13) ------------------------------------
    base.require_text("doc_sbsp_2t26", 1, "investir cerca de R$20 bilhões em CapEx ao longo do ano")
    base.require_text("local_45586543e35a", 13, "CAPEX totalizou R$ 15.202 milhões", "cerca de R$ 70 bilhões")
    cash_ratio = reg.get("V.sabesp.capex_cash.2025") / 15202.0
    reg.value("V.sabesp.capex_cash_to_accrual.2025", metric_id="capex_cash_to_accrual", entity_id="sabesp", value=cash_ratio, unit="ratio",
              value_state="derived", fact_type="derived", period_end="2025-12-31", source_refs=["local_45586543e35a"],
              calculation_ref="capex caixa DFC 2025 / CAPEX release 15.202 (DF2025 p13)", note="Converte guidance por competência em caixa.")
    sab_plan = {2026: 20000.0, 2027: (70000.0 - 15202.0 - 20000.0) / 3, 2028: (70000.0 - 15202.0 - 20000.0) / 3,
                2029: (70000.0 - 15202.0 - 20000.0) / 3}
    capex = {"sabesp": {}, "copasa": {}, "sanepar": {}}
    for y, v in sab_plan.items():
        reg.assumption(f"capex_sabesp_{y}", entity_id="sabesp", driver="capex_cash", year=str(y), base=v * cash_ratio,
                       adverse=v * cash_ratio * 1.10, favorable=v * cash_ratio, unit="BRL million",
                       rationale=("2026: guidance ~R$ 20 bi (release 2T26 p1); 2027–29: saldo do envelope de ~R$ 70 bi do 1º ciclo "
                                  "(2025–29) após R$ 15,2 bi em 2025, repartido igualmente; convertido a caixa pela razão 2025. "
                                  "Adversa: +10% de execução."),
                       supporting_obs_ids=["V.sabesp.capex_cash_to_accrual.2025"], source_id="SRC_doc_sbsp_2t26_65d19d49",
                       source_location="Release 2T26 p1; DF2025 p13")
        capex["sabesp"][y] = reg.assumptions[f"capex_sabesp_{y}"]["value_refs"]
    cop_plan = {2026: 3100.0, 2027: 3900.0, 2028: 4800.0, 2029: 4700.0, 2030: 4500.0}
    base.require_text("doc_csmg_2t26", 1, "Capex no 1S26: R$1,5 bilhão")
    for y, v in cop_plan.items():
        reg.assumption(f"capex_copasa_{y}", entity_id="copasa", driver="capex_cash", year=str(y), base=v, adverse=v * 1.17, favorable=v,
                       unit="BRL million",
                       rationale=("Plano 2026–30 divulgado pela companhia (DF 2025 item 6.2, controladora, sem capitalizações) e transcrito "
                                  "na planilha original. Em 12/03/2026 a Copasa descontinuou as projeções ('deixam de ser válidas'; Diário do "
                                  "Comércio, 13/03/2026) e, após a desestatização (jun/2026), o novo controlador revisará o plano: é premissa do "
                                  "analista, não guia vigente. 1S26 = R$ 1,5 bi é coerente com 2026. Adversa: +17% de capitalizações (nota da planilha)."),
                       source_id="local_f91e2b9dc863", source_location="Modelo_TIR_Copasa.xlsx Dados_RI!C34:G34 e notas A51")
        capex["copasa"][y] = reg.assumptions[f"capex_copasa_{y}"]["value_refs"]
    san = {2026: (2134.7, 3.9, 186.5, 258.9), 2027: (1878.2, 0.2, 191.4, 307.6), 2028: (1596.9, 0.2, 202.1, 323.8),
           2029: (1624.0, 0.0, 216.5, 1089.6), 2030: (2086.2, 0.0, 232.0, 531.5)}
    for y, (r_, s_, c_, p_) in san.items():
        b = r_ + s_ + c_
        reg.assumption(f"capex_sanepar_{y}", entity_id="sanepar", driver="capex_cash", year=str(y), base=b, adverse=(b + p_) * 1.10,
                       favorable=b, unit="BRL million",
                       rationale=("Capex regulatório + resíduos/água industrial + capitalizações do plano 2026–30 (p1); exclui doações de "
                                  "redes (sem caixa) e parcerias. Adversa: parcerias desembolsadas pela empresa e +10% de execução."),
                       source_id="SRC_sanepar_plano_capex_2026_2030_89a39155", source_location="Plano de investimentos p1")
        capex["sanepar"][y] = reg.assumptions[f"capex_sanepar_{y}"]["value_refs"]
    reg.assumption("rab_real_growth_after_plan", entity_id="", driver="real_growth_of_regulated_base_after_plan", year="post-plan",
                   base=0.01, adverse=0.0, favorable=0.02, unit="ratio",
                   rationale=("Após o plano divulgado, capex = depreciação regulatória + crescimento real da base (ligações/universalização "
                              "residual). Também é o crescimento real no terminal."))
    a["capex"], a["rab_g"] = capex, reg.assumptions["rab_real_growth_after_plan"]["value_refs"]
    reg.assumption("eligible_share", entity_id="", driver="capex_share_entering_regulated_base", year="", base=1.0, adverse=0.9,
                   favorable=1.0, unit="ratio",
                   rationale="Capex próprio entra na base salvo glosa (adversa 10%). Investimento não oneroso do precatório não entra (AN07).")
    a["eligible"] = reg.assumptions["eligible_share"]["value_refs"]
    reg.assumption("tax_rate", entity_id="", driver="income_tax_rate", year="2026-2035", base=TAX, adverse=TAX, favorable=TAX, unit="ratio",
                   rationale="IR+CSLL nominal 34% sobre EBIT; alíquotas efetivas extraordinárias (Sanepar 2025) não perpetuadas; JCP não projetado.")
    a["tax"] = reg.assumptions["tax_rate"]["value_refs"]
    reg.assumption("terminal_horizon", entity_id="", driver="terminal_method", year="2036+", base=1, adverse=0, favorable=1, unit="flag",
                   rationale="1 = perpetuidade com reinvestimento (continuidade/renovação assumida); 0 = fim da concessão com indenização.")
    reg.assumption("indemnity_share", entity_id="", driver="indemnity_of_residual_base", year="", base=1.0, adverse=0.5, favorable=1.0,
                   unit="ratio", rationale="Ativos reversíveis não amortizados indenizados no fim do contrato (Sabesp: ativo financeiro de indenização, DF2025 p12).",
                   source_id="local_45586543e35a", source_location="DF2025 p12")
    a["indemnity"] = reg.assumptions["indemnity_share"]["value_refs"]
    for e, yr, src, loc in (("sabesp", 2060, "SRC_sabesp_ambiente_regulatorio_ff446d05", "Contrato URAE-1, vencimento 19/10/2060"),
                            ("sanepar", 2048, "SRC_doc_sapr_2t26_e40a8cc1", "343 contratos prorrogados até 05/06/2048 (p3)")):
        reg.value(f"V.{e}.concession_end_year", metric_id="concession_end_year", entity_id=e, value=yr, unit="year", value_state="observed",
                  fact_type="fact", source_refs=[src], locator=loc, note="Fim do contrato principal; exceções municipais não modeladas.")
    base.require_text("doc_csmg_2t26", 22, "prazo médio ponderado das concessões é de aproximadamente 29 anos")
    base.require_text("doc_csmg_2t26", 21, "todos com vigência até 07.02.2073", "37,5% da receita")
    reg.value("V.copasa.concession_end_year", metric_id="concession_end_year", entity_id="copasa", value=2055, unit="year",
              value_state="derived", fact_type="derived", source_refs=["SRC_doc_csmg_2t26_1996f20b"],
              calculation_ref="2026 + prazo médio ponderado das concessões (~29 anos em 10/08/2026)", locator="Release 2T26 p21–22",
              note=("Horizonte único aproximado: 43 contratos até 07/02/2073 (~37,5% da receita), 10 maiores com vencimentos de 2034 a 2073, "
                    "58 municípios com prazo vencido (~5,2% da receita) seguem operados. Não é prazo contratual de um contrato."))
    return a
