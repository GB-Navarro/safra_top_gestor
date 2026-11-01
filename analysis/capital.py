"""AN03 — mercado, capital, classes e eventos (C09).

Preço e denominador na mesma convenção de data: fechamentos públicos de 30/10/2026 e
composição de capital CVM de 30/06/2026, com eventos entre dezembro/2025 e o corte.
"""
from __future__ import annotations

from .data import Baseline, Registry

INSTRUMENTS = {"SBSP3": "sabesp", "CSMG3": "copasa", "SAPR3": "sanepar", "SAPR4": "sanepar", "SAPR11": "sanepar"}
CA_HEADER = ["event_id", "entity_id", "instrument_id", "event_type", "announcement_date", "effective_date", "factor", "source_id",
             "source_location", "review_status", "reflected_in", "value_effect"]


def build(reg: Registry, base: Baseline) -> dict:
    out = {"prices": {}, "shares": {}, "events": [], "class_weights": {}}
    for m in base.json("data/processed/market_reference.json"):
        iid = m["instrument_id"]
        out["prices"][iid] = reg.value(f"V.{iid}.close.2026-10-30", metric_id="close_price", entity_id=INSTRUMENTS[iid], instrument_id=iid,
                                       value=m["close"], unit="BRL/share" if iid != "SAPR11" else "BRL/unit", value_state="observed",
                                       fact_type="fact", period_end="2026-10-30", observed_at="2026-10-30", scope="B3 fechamento",
                                       source_refs=[m["source_id"]], locator=m["source_location"],
                                       note="Referência pública de provedor; confirmação Bloomberg/B3 (H01) não obtida.")
    comp = base.json("derived/cvm_capital_composition.json")["rows"]
    june = {r["entity_id"]: r for r in comp if r["DT_REFER"] == "2026-06-30"}
    dec = {r["entity_id"]: r for r in comp if r["DT_REFER"] == "2025-12-31"}
    march = {r["entity_id"]: r for r in comp if r["DT_REFER"] == "2026-03-31"}
    # Copasa: arquivo CVM em milhares de ações (conferido com release 2T26 p26, 'milhares').
    base.require_text("doc_csmg_2t26", 26, "379.181")
    scale = {"sabesp": 1e-6, "sanepar": 1e-6, "copasa": 1e-3}
    for entity, r in june.items():
        total = float(r["QT_ACAO_TOTAL_CAP_INTEGR"]) * scale[entity]
        treasury = float(r["QT_ACAO_TOTAL_TESOURO"]) * scale[entity]
        common = float(r["QT_ACAO_ORDIN_CAP_INTEGR"]) * scale[entity] - float(r["QT_ACAO_ORDIN_TESOURO"]) * scale[entity]
        pref = float(r["QT_ACAO_PREF_CAP_INTEGR"]) * scale[entity] - float(r["QT_ACAO_PREF_TESOURO"]) * scale[entity]
        src = "SRC_cvm_itr_2026_eaac6b78"
        out["shares"][entity] = {
            "total": reg.value(f"V.{entity}.shares_outstanding.2026-06-30", metric_id="shares_outstanding", entity_id=entity,
                               value=total - treasury, unit="shares", scale=1e6, value_state="derived", fact_type="derived",
                               period_end="2026-06-30", scope="capital integralizado menos tesouraria", source_refs=[src],
                               calculation_ref="QT_ACAO_TOTAL_CAP_INTEGR − QT_ACAO_TOTAL_TESOURO", locator=r["locator"],
                               note="Ações econômicas em circulação; Sabesp inclui 1 PN especial (golden share, sem direito econômico relevante)."),
            "common": reg.value(f"V.{entity}.shares_common.2026-06-30", metric_id="shares_common_outstanding", entity_id=entity,
                                value=common, unit="shares", scale=1e6, value_state="derived", fact_type="derived", period_end="2026-06-30",
                                source_refs=[src], calculation_ref="ON integralizadas − ON tesouraria", locator=r["locator"],
                                note="ON em circulação."),
            "preferred": reg.value(f"V.{entity}.shares_preferred.2026-06-30", metric_id="shares_preferred_outstanding", entity_id=entity,
                                   value=pref, unit="shares", scale=1e6, value_state="derived", fact_type="derived", period_end="2026-06-30",
                                   source_refs=[src], calculation_ref="PN integralizadas − PN tesouraria", locator=r["locator"],
                                   note="PN em circulação."),
        }
    # Sanepar: unit = 1 ON + 4 PN; capitalização ponderada por classe no mesmo pregão.
    p3, p4, p11 = (reg.get(out["prices"][k]) for k in ("SAPR3", "SAPR4", "SAPR11"))
    on, pn = reg.get(out["shares"]["sanepar"]["common"]), reg.get(out["shares"]["sanepar"]["preferred"])
    mcap = p3 * on + p4 * pn
    out["class_weights"]["sanepar_market_cap"] = reg.value(
        "V.sanepar.market_cap_class_weighted.2026-10-30", metric_id="market_cap", entity_id="sanepar", value=mcap, unit="BRL",
        scale=1e6, value_state="derived", fact_type="derived", period_end="2026-10-30",
        calculation_ref="SAPR3 × ON + SAPR4 × PN (ações de 30/06/2026)", note="Capitalização por classe; unit não adiciona ações.")
    out["class_weights"]["sapr11_per_mcap"] = reg.value(
        "V.sanepar.unit_to_market_cap.2026-10-30", metric_id="unit_price_to_market_cap", entity_id="sanepar", instrument_id="SAPR11",
        value=p11 / mcap, unit="BRL/unit per BRL million", value_state="derived", fact_type="derived", period_end="2026-10-30",
        calculation_ref="preço SAPR11 / capitalização ponderada",
        note="Converte valor do patrimônio em valor por unit mantendo a relação de preços entre classes observada no pregão.")
    out["class_weights"]["pn_on_ratio"] = reg.value(
        "V.sanepar.pn_on_price_ratio.2026-10-30", metric_id="pn_on_price_ratio", entity_id="sanepar", value=p4 / p3, unit="ratio",
        value_state="derived", fact_type="derived", period_end="2026-10-30", calculation_ref="SAPR4/SAPR3",
        note="Razão observada; não é regra estatutária de preço.")
    for entity in ("sabesp", "copasa"):
        tic = "SBSP3" if entity == "sabesp" else "CSMG3"
        out["class_weights"][f"{entity}_market_cap"] = reg.value(
            f"V.{entity}.market_cap.2026-10-30", metric_id="market_cap", entity_id=entity, value=reg.get(out["prices"][tic]) *
            reg.get(out["shares"][entity]["total"]), unit="BRL", scale=1e6, value_state="derived", fact_type="derived",
            period_end="2026-10-30", calculation_ref=f"{tic} × ações em circulação 30/06/2026", note="Capitalização de mercado.")

    # Eventos societários com evidência; ausência após agosto não é afirmada.
    base.require_text("doc_sbsp_2t26", 1, "desdobramento de ações na proporção de 1:5", "AGE de 28 de abril de 2026")
    base.require_text("local_45586543e35a", 15, "0,029646975 nova ação")
    split_check = float(june["sabesp"]["QT_ACAO_ORDIN_CAP_INTEGR"]) / float(march["sabesp"]["QT_ACAO_ORDIN_CAP_INTEGR"])
    bonus_check = float(dec["sabesp"]["QT_ACAO_ORDIN_CAP_INTEGR"]) - 683509868
    base.require_text("doc_sapr_itr", 62, "não distribuição de Juros sobre o Capital Próprio (JCP) referente ao 1º semestre de 2026")
    base.require_text("doc_csmg_2t26", 1, "JCP declarados no 1S26: R$320,1 milhões")
    out["events"] = [
        dict(event_id="CA.sabesp.split_1x5_2026", entity_id="sabesp", instrument_id="SBSP3", event_type="split", announcement_date="2026-04-28",
             effective_date="2026-04-29", factor=5.0, source_id="SRC_doc_sbsp_2t26_65d19d49", source_location="Release 2T26 p1, nota 1",
             review_status="verified_primary", reflected_in=f"composição CVM 30/06/2026 (razão jun/mar = {split_check:.6f})",
             value_effect="Denominador de junho já pós-desdobramento; preço de 30/10 na mesma base."),
        dict(event_id="CA.sabesp.bonus_2025", entity_id="sabesp", instrument_id="SBSP3", event_type="bonus_issue", announcement_date="2025-12-18",
             effective_date="2025-12-23", factor=1.029646975, source_id="local_45586543e35a", source_location="DF 2025 p14–15",
             review_status="verified_primary", reflected_in=f"composição CVM 31/12/2025 (+{bonus_check:,.0f} ações vs 683.509.868)",
             value_effect="Sem efeito adicional: já no denominador."),
        dict(event_id="CA.sabesp.buyback_2025_2026", entity_id="sabesp", instrument_id="SBSP3", event_type="buyback_program",
             announcement_date="2025-05-12", effective_date="2025-05-13/2026-11-12", factor=None, source_id="local_45586543e35a",
             source_location="DF 2025 p14", review_status="verified_primary_execution_after_june_unobserved",
             reflected_in="tesouraria de 30/06/2026", value_effect="Recompras jul–out não observadas; limite do programa ~1% das ações."),
        dict(event_id="CA.copasa.jcp_1s26", entity_id="copasa", instrument_id="CSMG3", event_type="interest_on_equity",
             announcement_date="2026-H1", effective_date="", factor=None, source_id="SRC_doc_csmg_2t26_1996f20b",
             source_location="Release 2T26 p1", review_status="verified_primary",
             reflected_in="dividendos/JCP a pagar em 30/06/2026 deduzidos na ponte", value_effect="Saldo a pagar de junho tratado como direito de terceiros/ex-data."),
        dict(event_id="CA.copasa.secondary_offering_2026", entity_id="copasa", instrument_id="CSMG3", event_type="secondary_offering_control_change",
             announcement_date="2026-06-11", effective_date="2026-06-16", factor=1.0, source_id="SRC_copasa_fr_20260611",
             source_location="Fato relevante 11/06/2026 p1; Release 2T26 p25–26", review_status="verified_primary",
             reflected_in="ações em circulação 379.181 mil antes e depois (Release 2T26 p26)",
             value_effect="Oferta secundária do Estado (R$ 49,03/ação; Equatorial investidora de referência): sem emissão, sem efeito no denominador."),
        dict(event_id="CA.sanepar.no_jcp_1s26", entity_id="sanepar", instrument_id="SAPR11", event_type="dividend_suspension",
             announcement_date="2026-06-24", effective_date="", factor=None, source_id="SRC_doc_sapr_itr_d93332d6",
             source_location="ITR 2T26 nota 20 p62", review_status="verified_primary",
             reflected_in="sem saldo relevante a pagar em 30/06/2026", value_effect="Nenhum provento deduzido além do saldo de junho."),
    ]
    base.require_text("copasa_fr_20260611", 1, "aprovou o preço por ação ordinária de emissão da Companhia de R$ 49,03",
                      "114.075.921", "Investidor de Referência Selecionado")
    base.require_text("doc_csmg_2t26", 26, "379.181")
    reg.value("V.copasa.reference_investor_shares", metric_id="reference_investor_shares", entity_id="copasa", instrument_id="CSMG3",
              value=114075921.0, unit="shares", value_state="observed", fact_type="fact", period_end="2026-06-11",
              source_refs=["SRC_copasa_fr_20260611"], locator="Fato relevante 11/06/2026 p1",
              note="Ações alocadas à Gerais Saneamento S.A. (Equatorial) como investidora de referência.")
    reg.value("V.copasa.reference_investor_share", metric_id="reference_investor_share_of_capital", entity_id="copasa", value=114075921 / 379181000,
              unit="ratio", value_state="derived", fact_type="derived", source_refs=["SRC_copasa_fr_20260611", "SRC_doc_csmg_2t26_1996f20b"],
              calculation_ref="114.075.921 / 379.181.000 ações", note="Participação da investidora de referência após a oferta secundária.")
    out["search_record"] = {
        "searched_at_snapshot": base.snapshot_id,
        "scope": ("Releases/ITR 2T26, DF 2025 e fatos relevantes na fotografia; pesquisa pública de 01/11/2026 (Plano 13) em RI e imprensa "
                  "para jul–out/2026: oferta secundária da Copasa (jun), debêntures da Sabesp, fatos da Sanepar de 26 e 28/10."),
        "result": ("Nenhuma alteração de quantidade de ações entre 30/06 e 30/10/2026 identificada (a oferta da Copasa foi secundária). "
                   "Confirmação pelo Terminal (H01) não feita; recompras da Sabesp após junho não observadas."),
    }
    return out
