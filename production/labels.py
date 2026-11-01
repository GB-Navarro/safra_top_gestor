"""Rótulos legíveis para fontes e métricas nas peças (apresentação; não altera dados do pacote)."""
from __future__ import annotations

SOURCE_PREFIX = [
    ("SRC_cvm_dfp_", lambda s: f"CVM — DFP {s.split('_')[3]}"), ("SRC_cvm_itr_", lambda s: f"CVM — ITR {s.split('_')[3]}"),
    ("SRC_cvm_cadastro", lambda s: "CVM — cadastro de companhias"),
    ("SRC_doc_sapr_2t26", lambda s: "Sanepar — Release de resultados 2T26"), ("SRC_doc_sapr_itr", lambda s: "Sanepar — ITR 2T26 (notas)"),
    ("SRC_doc_sapr_prec", lambda s: "Sanepar — Fato relevante de 23/06/2026"), ("SRC_doc_csmg_2t26", lambda s: "Copasa — Release de resultados 2T26"),
    ("SRC_doc_sbsp_2t26", lambda s: "Sabesp — Release de resultados 2T26"), ("local_45586543e35a", lambda s: "Sabesp — Demonstrações financeiras 2025"),
    ("local_85acbb6423e6", lambda s: "Sabesp — DFP 2024"), ("local_63d5afcacc50", lambda s: "Sabesp — Demonstrações financeiras 2022"),
    ("local_87ac99e100be", lambda s: "Planilha original da equipe — Sabesp"), ("local_f91e2b9dc863", lambda s: "Planilha original da equipe — Copasa"),
    ("local_deba687d6685", lambda s: "Planilha original da equipe — Sanepar"),
    ("SRC_sinisa_agua_planilhas", lambda s: "SINISA — planilhas de água (base 2024)"), ("SRC_sinisa_agua", lambda s: "SINISA — relatório de água (base 2024)"),
    ("SRC_sinisa_esgoto", lambda s: "SINISA — relatório de esgoto (base 2024)"), ("SRC_marco_legal", lambda s: "Marco Legal do Saneamento (metas 2033)"),
    ("SRC_competicao", lambda s: "Aegea — concessão do Pará (14/04/2025)"), ("SRC_market_public_", lambda s: f"Cotação de fechamento 30/10/2026 — {s.split('_')[3].upper()}"),
    ("SRC_tesouro_taxas", lambda s: "Tesouro Nacional — taxas de 30/10/2026"), ("SRC_bcb_focus", lambda s: "Banco Central — Boletim Focus"),
    ("SRC_bcb_sgs", lambda s: "Banco Central — séries de IPCA/Selic"), ("SRC_sanepar_release_2025", lambda s: "Sanepar — Release de resultados 4T25"),
    ("SRC_sanepar_plano_capex", lambda s: "Sanepar — Plano de investimentos 2026–2030"), ("SRC_sanepar_calendario", lambda s: "Sanepar — Calendário de eventos 2026"),
    ("SRC_sabesp_sustentabilidade", lambda s: "Sabesp — Relatório de sustentabilidade 2024"),
    ("SRC_sabesp_ambiente_regulatorio", lambda s: "Sabesp — Ambiente regulatório (RI)"), ("SRC_sabesp_universalizacao", lambda s: "Sabesp — Indicadores de universalização (RI)"),
    ("SRC_agepar_precatorio", lambda s: "Agepar — decisão sobre o precatório (19/08/2026)"), ("SRC_agepar", lambda s: "Agepar — portal"),
    ("SRC_an_sabesp_inst_2025", lambda s: "Sabesp — Apresentação institucional (fev/2025)"), ("SRC_ri_sapr", lambda s: "Sanepar — portal de RI"),
    ("SRC_sapr_estatuto", lambda s: "Sanepar — Estatuto social (29/04/2026)"),
]
METRIC = {
    "loss_per_connection_day": "Perdas por ligação", "distribution_loss_rate": "Índice de perdas na distribuição",
    "distribution_loss_reduction": "Redução do índice de perdas em 12 meses", "sewer_coverage": "Atendimento/cobertura de esgoto",
    "collected_sewage_treated": "Esgoto coletado que é tratado", "billing_loss_rate": "Perdas no faturamento", "capex_cash": "Investimento pago (capex em caixa)",
    "value_per_unit_of_regulated_base": "Valor de R$ 1 investido e remunerado", "water_electricity_expense_sinisa": "Despesa de energia do serviço de água",
    "energy_self_production_contracted": "Autoprodução de energia contratada", "revenue_mix_effect_social_tariff": "Efeito da tarifa social na receita",
    "default_rate": "Evasão de receitas", "regulatory_wacc_real_after_tax": "WACC regulatório real pós-impostos",
    "assumption.regulatory_wacc_real_after_tax": "WACC regulatório real pós-impostos (premissa)", "regulatory_obligation_pv": "Precatório a valor presente",
}


def source(row: dict) -> str:
    sid = row["source_id"]
    for prefix, fn in SOURCE_PREFIX:
        if sid.startswith(prefix):
            return fn(sid)
    return f"{row.get('issuer', '')} — {row.get('title', sid)}".strip(" —")


def metric(mid: str) -> str:
    return METRIC.get(mid, mid.replace("_", " "))
