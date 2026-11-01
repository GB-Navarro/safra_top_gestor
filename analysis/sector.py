"""AN05 — contratos/regulação, matriz ESG, ponte de energia e fatos de setor (C15, C16, C17, C18).

Fatos têm fonte conferida no texto; inferências e hipóteses são rotuladas. Não há ranking ESG
sintético: definições e períodos diferentes permanecem lado a lado.
"""
from __future__ import annotations

from datetime import date

from .data import Baseline, Registry

LEGACY_OBS = ["OBS_002588", "OBS_002589", "OBS_002590", "OBS_002591", "OBS_002592", "OBS_002593", "OBS_002594", "OBS_002595",
              "OBS_002596", "OBS_002597", "OBS_002598", "OBS_002599", "OBS_002600", "OBS_002601"]
REG_HEADER = ["term_id", "entity_id", "contract_or_cluster", "regulator", "term_type", "term_text", "effective_from", "effective_to",
              "source_id", "source_location", "review_status", "value_refs", "model_use"]
RAW = {"marco": "data/raw/reguladores/marco_legal__9270810f078f.html", "aegea": "data/raw/ri/competicao__b978a92ac15b.html",
       "sab_univ": "data/raw/ri/sabesp/sabesp_universalizacao__8ff754a0b16d.html",
       "sab_reg": "data/raw/ri/sabesp/sabesp_ambiente_regulatorio__ff446d054fc8.html",
       "agepar": "data/raw/reguladores/agepar_precatorio_20260819__e549038f663f.html"}


def _import_legacy(reg: Registry, base: Baseline):
    rows = {r["obs_id"]: r for r in base.csv("data/processed/observations.csv")}
    for oid in LEGACY_OBS:
        r = rows[oid]
        reg.value(oid, metric_id=r["metric_id"], entity_id=r["entity_id"], value=float(r["value"]), unit=r["unit"], scale=float(r["scale"]),
                  value_state="observed", fact_type="fact", period_start=r["period_start"], period_end=r["period_end"],
                  observed_at=r["observed_at"], scope=r["scope"], source_refs=[r["source_id"]], locator=r["source_location"],
                  note=f"Observação existente (mesmo ID legado); definição {r['definition_id']}.")


def build(reg: Registry, base: Baseline, valuation: dict, cap: dict, m: dict, a: dict) -> dict:
    _import_legacy(reg, base)
    v = reg.value
    # ---------------- Fatos setoriais e de médio prazo -------------------------------------
    base.require_html(RAW["marco"], "até o final de 2033, 99% da população brasileira deverá ter acesso à água tratada, e 90% à coleta e tratamento do esgoto")
    v("V.sector.target_water_2033", metric_id="legal_target_water_access", value=0.99, unit="ratio", value_state="observed", fact_type="fact",
      period_end="2033-12-31", source_refs=["SRC_marco_legal_9270810f"], locator="HTML Marco Legal", note="Meta legal nacional (Lei 14.026/2020).")
    v("V.sector.target_sewer_2033", metric_id="legal_target_sewer_collection_treatment", value=0.90, unit="ratio", value_state="observed",
      fact_type="fact", period_end="2033-12-31", source_refs=["SRC_marco_legal_9270810f"], locator="HTML Marco Legal", note="Meta legal nacional.")
    base.require_html(RAW["aegea"], "investi rá mais de R$ 15 bilhões", "99 município s", "14/04/2025")
    v("V.sector.aegea_para_capex", metric_id="announced_concession_capex", value=15000.0, unit="BRL", scale=1e6, value_state="observed",
      fact_type="fact", period_end="2025-04-14", source_refs=["SRC_competicao_b978a92a"], locator="Aegea, notícia 14/04/2025",
      note="Compromisso anunciado ('mais de R$ 15 bilhões', 99 municípios, prazo contratual longo); anúncio não é execução.")
    base.require_text("doc_csmg_2t26", 1, "Perdas na distribuição em 06/2026: 35,0% (-260 bps)", "43 Contratos celebrados sob o novo modelo")
    v("V.copasa.distribution_loss_reduction_pp", metric_id="distribution_loss_reduction", entity_id="copasa", value=2.6,
      unit="percentage_points", value_state="observed", fact_type="fact", period_start="2025-06-30", period_end="2026-06-30",
      source_refs=["SRC_doc_csmg_2t26_1996f20b"], locator="Release 2T26 p1 ('35,0% (-260 bps)')",
      note="Redução do índice de perdas na distribuição: 37,6% (jun/25) → 35,0% (jun/26).")
    base.require_text("doc_csmg_2t26", 25, "Oferta Subsequente de Ações", "Investidor de Referência")
    reg.source("SRC_doc_csmg_2t26_1996f20b")
    base.require_text("local_45586543e35a", 12, "Casa dos Ventos (126 MWm)", "Engie (60 MWm)", "32 usinas fotovoltaicas")
    v("V.sabesp.self_production_contracted_mwm", metric_id="energy_self_production_contracted", entity_id="sabesp", value=186.0, unit="MWm",
      value_state="derived", fact_type="derived", period_end="2025-12-31", source_refs=["local_45586543e35a"],
      calculation_ref="126 MWm (Casa dos Ventos) + 60 MWm (Engie)", locator="DF2025 p12", note="Autoprodução contratada; economia não quantificada pela empresa.")
    base.require_text("local_45586543e35a", 12, "de 2,0M para 3,2M cadastros", "(1,8)% em mix")
    v("V.sabesp.social_tariff_mix_effect.2025", metric_id="revenue_mix_effect_social_tariff", entity_id="sabesp", value=-0.018, unit="ratio",
      value_state="observed", fact_type="fact", period_end="2025-12-31", source_refs=["local_45586543e35a"], locator="DF2025 p12",
      note="Efeito mix na receita líquida de saneamento 2025 (economias vulneráveis com tarifa subsidiada de 2,0 mi para 3,2 mi cadastros).")
    base.require_html(RAW["sab_univ"], "Última atualização em Setembro de 2026", "Dados a serem validados pela ARSESP")

    # ---------------- Termos regulatórios com vigência -------------------------------------
    terms = [
        dict(term_id="REG.sabesp.urae1", entity_id="sabesp", contract_or_cluster="URAE-1 (371 municípios)", regulator="Arsesp/URAE-1",
             term_type="asset_base_remuneration", term_text="Remuneração (WACC predefinido) sobre base de ativos regulatórios; reajustes anuais com incorporação de base nos ciclos 2024–29 e 2030–34; eficiência de opex retida até 2029.",
             effective_from="2024-07-23", effective_to="2060-10-19", source_id="SRC_urae1_anexo_viii_2025",
             source_location="Anexo VIII item 10.7 (WACC 7,86% pós / 11,91% pré, fixo no 1º ciclo); DFP2024 p10–11; DF2025 p12",
             review_status="verified_primary", value_refs=["V.sabesp.wacc_reg_real_after_tax", "V.sabesp.wacc_reg_real_pre_tax"],
             model_use="r_reg Sabesp (contrato), defasagem"),
        dict(term_id="REG.copasa.rtp3", entity_id="copasa", contract_or_cluster="Contratos de programa/novo modelo", regulator="Arsae-MG",
             term_type="tariff_review", term_text="3ª RTP (ciclo 2026–29): WACC pré-impostos 13,70% (9,79% pós; antes 7,92%), reconhecimento anual dos investimentos, catch-up 25%.",
             effective_from="2026-01-01", effective_to="2029-12-31", source_id="SRC_doc_csmg_2t26_1996f20b", source_location="Release 2T26 p24",
             review_status="verified_primary", value_refs=["V.copasa.wacc_reg_real_pre_tax", "V.copasa.wacc_reg_real_after_tax"], model_use="r_reg Copasa"),
        dict(term_id="REG.copasa.grantor", entity_id="copasa", contract_or_cluster="Belo Horizonte e municípios", regulator="Arsae-MG/municípios",
             term_type="grantor_payments", term_text="Valores repassados ao poder concedente incorporados à BRR (BH: R$ 1,3 bi entre 2026 e 2028).",
             effective_from="2026-01-01", effective_to="2028-12-31", source_id="SRC_doc_csmg_2t26_1996f20b", source_location="Release 2T26 p20",
             review_status="verified_primary", value_refs=["V.copasa.grantor.2026-06-30"], model_use="obrigação deduzida com crédito regulatório"),
        dict(term_id="REG.sanepar.rtp3", entity_id="sanepar", contract_or_cluster="343 contratos", regulator="Agepar", term_type="tariff_review",
             term_text=("3ª RTP ciclo 2025–28; WACC real 12,24% antes e 8,08% após impostos; BRR líquida 2024 de R$ 16.846,8 mi a preços de "
                        "dez/2020, sujeita ao plano de fiscalização da Agepar (ajustes compensatórios futuros)."),
             effective_from="2025-01-01", effective_to="2028-12-31", source_id="SRC_agepar_nt_006_2025",
             source_location="NT Agepar 006/2025 p25 (WACC), p79 e p81 (BRR); ITR 2T26 p25–26, p62",
             review_status="verified_primary", value_refs=["V.sanepar.wacc_reg_real_after_tax", "V.sanepar.brr_official_net.2024"],
             model_use="r_reg Sanepar; verificação da base implícita"),
        dict(term_id="REG.sanepar.precatorio", entity_id="sanepar", contract_or_cluster="Usuários Sanepar", regulator="Agepar",
             term_type="regulatory_liability", term_text="100% do precatório aos usuários: 50% descontos (25% da tarifa mínima, até mai/2029) e 50% investimentos não onerosos (até dez/2030), atualizados por 8,08% real + IPCA; contestação judicial sem liminar.",
             effective_from="2026-06-23", effective_to="2030-12-31", source_id="SRC_doc_sapr_itr_d93332d6", source_location="ITR 2T26 nota 20 p61–62; fato relevante 23/06/2026",
             review_status="verified_primary", value_refs=["V.sanepar.regulatory_liability.2026-06-30"], model_use="cronograma AN07"),
        dict(term_id="REG.sanepar.concessions", entity_id="sanepar", contract_or_cluster="343 contratos", regulator="Municípios",
             term_type="concession_duration", term_text="Prorrogação até 05/06/2048; exceções Maringá 2040, Andirá 2032, Porto União 03/2048.",
             effective_from="", effective_to="2048-06-05", source_id="SRC_doc_sapr_2t26_e40a8cc1", source_location="Release 2T26 p3",
             review_status="verified_primary", value_refs=["V.sanepar.concession_end_year"], model_use="terminal finito"),
        dict(term_id="REG.copasa.duration", entity_id="copasa", contract_or_cluster="Portfólio de concessões (636 municípios)", regulator="Municípios/Arsae-MG",
             term_type="concession_duration",
             term_text=("43 contratos no novo modelo até 07/02/2073 (~37,5% da receita, incluindo BH, Contagem e Betim); 10 maiores concessões "
                        "(~48% da receita) vencem entre 2034 e 2073; 58 municípios com prazo vencido (~5,2%) seguem operados; prazo médio "
                        "ponderado ~29 anos."),
             effective_from="2026-08-10", effective_to="2073-02-07", source_id="SRC_doc_csmg_2t26_1996f20b", source_location="Release 2T26 p20–22",
             review_status="verified_primary_portfolio_average", value_refs=["V.copasa.concession_end_year"],
             model_use="terminal finito por prazo médio ponderado (aproximação)"),
        dict(term_id="REG.copasa.privatization", entity_id="copasa", contract_or_cluster="Controle acionário", regulator="CVM/Estado de MG",
             term_type="control_change",
             term_text=("Desestatização concluída: oferta secundária de ações do Estado a R$ 49,03 (preço aprovado em 11/06/2026); Gerais "
                        "Saneamento (Equatorial) investidora de referência com 114,1 mi de ações; acordo de acionistas com o Estado; sem emissão."),
             effective_from="2026-06-11", effective_to="", source_id="SRC_copasa_fr_20260611", source_location="Fato relevante 11/06/2026 p1–2; Release 2T26 p25",
             review_status="verified_primary", value_refs=["V.copasa.reference_investor_share"],
             model_use="governança; sem efeito no número de ações; eficiência do novo controlador não modelada"),
        dict(term_id="REG.sanepar.sainp", entity_id="sanepar", contract_or_cluster="Sistema Integrado do Norte do PR (SAINP)", regulator="Sanepar (licitação)",
             term_type="asset_lease_tender",
             term_text=("Concorrência 170/2026: locação de ativos com obras do SAINP; Consórcio Águas do Paraná melhor classificado (28/10/2026), "
                        "locação mensal de R$ 9.031.100,05 por 20 anos e 6 meses; contrato não assinado até o corte."),
             effective_from="2026-10-28", effective_to="", source_id="SRC_sanepar_fr_20261028_sainp", source_location="Fato relevante 28/10/2026 p1",
             review_status="verified_primary", value_refs=[],
             model_use="não modelado (obrigação futura condicionada; pode substituir capex próprio)"),
    ]
    # ---------------- Ponte ESG de energia (C17) --------------------------------------------
    infl = {y: reg.get(m["focus"][y]) for y in range(2026, 2031)}
    infl.update({y: reg.get(reg.assumptions["ipca_long_run"]["value_refs"]["base"]) for y in range(2031, 2036)})
    wacc = reg.get(a["wacc"]["base"])
    reg.assumption("energy_saving", entity_id="", driver="energy_expense_reduction", year="2027-2035", base=0.01, adverse=0.0,
                   favorable=0.02, unit="ratio",
                   rationale="Sensibilidade: redução hipotética da despesa de energia do serviço de água; não é projeto identificado nem resultado realizado.")
    bridge_cases, energy_vals = [], {}
    for item in base.json("data/processed/sinisa_energy.json"):
        e = item["entity_id"]
        e_id = v(f"V.{e}.water_energy_expense_sinisa.2024", metric_id="water_electricity_expense_sinisa", entity_id=e,
                 value=item["value_brl_million"], unit="BRL", scale=1e6, value_state="observed", fact_type="fact",
                 period_start="2024-01-01", period_end="2024-12-31", scope=item["scope"], source_refs=[item["source_id"]],
                 locator=f"SINISA água 2024, GFI2004, {item['municipalities']} municípios", note="Despesa municipal reportada do serviço de água; não é consolidada.")
        energy_vals[e] = e_id
        cost = item["value_brl_million"] * (1 + reg.get(m["actual"][2025])) * (1 + infl[2026])
        pv = 0.0
        for y in range(2027, 2036):
            cost *= 1 + infl[y]
            t = (date(y, 7, 1) - date(2026, 10, 30)).days / 365
            pv += cost * 0.01 * (1 - 0.34) / (1 + wacc) ** t
        shares = reg.get(cap["shares"][e]["total"])
        for retention in (0.5, 1.0):
            cid = f"{e}.energy.r{int(retention * 100)}"
            rid = v(f"V.esg.retention.{int(retention * 100)}", metric_id="esg_retention_option", value=retention, unit="ratio",
                    value_state="derived", fact_type="derived", calculation_ref="opção de retenção do ganho pela empresa",
                    note="Parcela do ganho retida (não repassada à tarifa).")
            capex_id = v(f"V.case.{cid}.capex_break_even", metric_id="esg_capex_break_even", entity_id=e, value=pv * retention, unit="BRL",
                         scale=1e6, value_state="derived", fact_type="derived", period_end="2026-10-30",
                         calculation_ref="Σ2027–35 despesa×1%×(1−34%)×retenção / (1+WACC)^t; sem terminal",
                         note="Teto de investimento inicial que zera o VPL incremental; sensibilidade, não economia realizada.")
            ps_id = v(f"V.case.{cid}.value_per_share", metric_id="esg_value_per_share_upper_bound", entity_id=e,
                      value=pv * retention / shares, unit="BRL/share", value_state="derived", fact_type="derived", period_end="2026-10-30",
                      calculation_ref=f"{capex_id} / ações em circulação", note="Valor máximo por ação se o ganho viesse sem investimento (limite superior).")
            bridge_cases.append(dict(case_id=cid, entity_id=e, instrument_id={"sabesp": "SBSP3", "copasa": "CSMG3", "sanepar": "SAPR11"}[e],
                                     scenario_id="energy_sensitivity",
                                     dimensions={"retention": {"option_id": f"r{int(retention * 100)}", "label": f"Retenção {int(retention * 100)}%", "value_ref": rid}},
                                     value_refs={"base_expense": e_id, "capex_break_even": capex_id, "value_per_share": ps_id,
                                                 "saving_fraction": "A.energy_saving.base", "wacc": a["wacc"]["base"]},
                                     kpi="Despesa de energia do serviço de água (SINISA 2024)",
                                     chain=["Redução hipotética de 1% da despesa", "Economia após IR 34%", "Parcela retida",
                                            "VPL 2027–35 ao WACC-base", "Teto de investimento"],
                                     assumption_refs=["energy_saving", "wacc_nominal", "tax_rate"],
                                     limitations=["Escopo municipal de água 2024; não é custo consolidado nem custo marginal de perdas",
                                                  "Não somado ao DCF-base: a margem recorrente já pode conter ganhos de eficiência",
                                                  "Sem projeto, custo de implantação ou calendário observados"]))
    # ---------------- Matriz ESG (C16) — linhas com valores, não scores ---------------------
    base_cases = {c["entity_id"]: c for c in valuation["cases"] if c["scenario_id"] == "base"}
    vr = {e: v(f"V.{e}.rab_value_ratio.base", metric_id="value_per_unit_of_regulated_base", entity_id=e,
               value=base_cases[e]["diagnostics"]["rab_value_ratio"], unit="BRL_per_BRL", value_state="derived", fact_type="derived",
               calculation_ref=f"(r_reg real pós-impostos − g real)/(WACC real − g real) — caso {e}.base",
               note="Valor criado por R$ investido e remunerado: >1 cria valor, <1 destrói (WACC de mercado acima do regulatório).")
          for e in ("sabesp", "copasa", "sanepar")}
    reg.value("V.sanepar.obligation_pv.base", metric_id="regulatory_obligation_pv", entity_id="sanepar",
              value=reg.get(base_cases["sanepar"]["value_refs"]["obligation_pv"]), unit="BRL", scale=1e6, value_state="derived",
              fact_type="derived", calculation_ref=base_cases["sanepar"]["value_refs"]["obligation_pv"],
              note="PV em 30/10/2026 do precatório (fluxos futuros + aplicados jul–out capitalizados), caso-base AN07.")
    base.require_text("doc_sapr_2t26", 18, "homologado o percentual de reajuste tarifário de 2,4993%")
    v("V.sanepar.tariff_adjustment.2026", metric_id="annual_tariff_adjustment", entity_id="sanepar", value=0.024993, unit="ratio",
      value_state="observed", fact_type="fact", period_start="2026-05-17", period_end="2027-05-16", source_refs=["SRC_doc_sapr_2t26_e40a8cc1"],
      locator="Release 2T26 p18 (IRT 2026, Resolução 23/2026-Agepar)", note="Reajuste tarifário anual aplicado a partir de 17/05/2026.")
    rows = [
        dict(row_id="ESG.water_efficiency", factor="Eficiência hídrica (perdas)",
             cells={"sabesp": {"value_refs": ["OBS_002593"], "text": "IPGR 2024 (anual)"},
                    "copasa": {"value_refs": ["OBS_002594", "OBS_002595", "V.copasa.distribution_loss_reduction_pp"], "text": "LTM jun/26; COPASA+Patos"},
                    "sanepar": {"value_refs": ["OBS_002597", "OBS_002598"], "text": "LTM jun/26"}},
             channel="Custos de energia/químicos e capex de redução de perdas", value_link="Ponte de energia (sensibilidade) — esg_bridge",
             comparability="Definições, perímetros e períodos diferentes: sem ranking.",
             source_refs=["SRC_sabesp_sustentabilidade_2024_7e111812", "SRC_doc_csmg_2t26_1996f20b", "SRC_doc_sapr_2t26_e40a8cc1"]),
        dict(row_id="ESG.sewer_expansion", factor="Esgoto e expansão",
             cells={"sabesp": {"value_refs": ["V.sabesp.capex_cash.2025", vr["sabesp"]], "text": "Universalização URAE-1 até 2029 (Fator U)"},
                    "copasa": {"value_refs": ["OBS_002596", vr["copasa"]], "text": "Cobertura de esgoto jun/26"},
                    "sanepar": {"value_refs": ["OBS_002599", "OBS_002600", vr["sanepar"]], "text": "IARCE urbano; 100% do coletado tratado"}},
             channel="Receita regulada e capex: investimento entra na base remunerada",
             value_link="Valor por R$ investido = (r_reg − g)/(WACC − g): Copasa >1 cria valor; Sabesp/Sanepar <1 ao WACC de mercado",
             comparability="Cobertura ≠ tratamento; população/área distintas.",
             source_refs=["SRC_doc_csmg_2t26_1996f20b", "SRC_doc_sapr_2t26_e40a8cc1", "SRC_cvm_dfp_2025_cdce6cc0"]),
        dict(row_id="ESG.resilience", factor="Resiliência e energia",
             cells={"sabesp": {"value_refs": [energy_vals["sabesp"], "V.sabesp.self_production_contracted_mwm"], "text": "Autoprodução contratada"},
                    "copasa": {"value_refs": [energy_vals["copasa"]], "text": "Despesa de energia água 2024"},
                    "sanepar": {"value_refs": [energy_vals["sanepar"]], "text": "Despesa de energia água 2024"}},
             channel="Custo e continuidade", value_link="Teto de capex de eficiência (esg_bridge)",
             comparability="Porte e geografia impedem ranking pelo gasto absoluto.", source_refs=["SRC_sinisa_agua_planilhas_777eb5f8", "local_45586543e35a"]),
        dict(row_id="ESG.access", factor="Acesso e capacidade de pagar",
             cells={"sabesp": {"value_refs": ["V.sabesp.social_tariff_mix_effect.2025"], "text": "Tarifa social: efeito mix −1,8% na receita 2025"},
                    "copasa": {"value_refs": [], "text": "Indicador comparável não obtido (lacuna)"},
                    "sanepar": {"value_refs": ["OBS_002601"], "text": "Evasão de receitas jun/26"}},
             channel="Arrecadação e equilíbrio tarifário", value_link="Risco na margem (cenário adverso: opex/arrecadação −2% da receita)",
             comparability="Definições próprias; ausência não é pior desempenho.", source_refs=["local_45586543e35a", "SRC_doc_sapr_2t26_e40a8cc1"]),
        dict(row_id="ESG.governance", factor="Governança e regulação",
             cells={"sabesp": {"value_refs": ["V.sabesp.wacc_reg_real_after_tax"], "text": "Controle privado; contrato URAE-1, WACC fixo até 2029"},
                    "copasa": {"value_refs": ["V.copasa.wacc_reg_real_after_tax", "V.copasa.reference_investor_share"],
                               "text": "3ª RTP; desestatizada em jun/2026 (Equatorial investidora de referência)"},
                    "sanepar": {"value_refs": ["V.sanepar.wacc_reg_real_after_tax", "V.sanepar.obligation_pv.base"],
                                "text": "Controle estadual; precatório destinado 100% aos usuários"}},
             channel="Quem retém o ganho: remuneração regulatória, obrigações e risco de intervenção",
             value_link="r_reg no motor; PV do precatório na ponte EV→acionista", comparability="Regimes distintos.",
             source_refs=["SRC_urae1_anexo_viii_2025", "SRC_doc_csmg_2t26_1996f20b", "SRC_copasa_fr_20260611", "SRC_doc_sapr_itr_d93332d6"]),
    ]
    return {"terms": terms, "matrix": rows, "bridge_cases": bridge_cases, "value_ratio": vr}
