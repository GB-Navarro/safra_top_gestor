"""AN09 — decisão proposta, cenários, riscos/gatilhos, claims, slots narrativos e visões (C19, C20).

A escolha sai de uma regra registrada (margem de segurança e robustez na grade), não de
preferência herdada do rascunho. Decisão permanece 'proposed' até registros reais H08/H09.
"""
from __future__ import annotations

from .data import Registry

ENT_NAME = {"sabesp": "Sabesp", "copasa": "Copasa", "sanepar": "Sanepar"}
SLOTS = ["lead", "sector", "swot", "medium_term", "esg", "bridge", "valuation_method", "valuation_result", "risks", "conclusion"]


def _case(val, cid):
    return next(c for c in val["cases"] if c["case_id"] == cid)


def _market_view(reg, c, val):
    """Leitura do preço de Sabesp/Copasa gerada a partir dos casos (nenhuma afirmação fixa)."""
    parts, refs = [], []
    for e in ("sabesp", "copasa"):
        fav = _case(val, f"{e}.favorable")
        price_ref = fav["value_refs"]["price"]
        tok_price = "{{value:" + price_ref + "}}"
        if fav["paper_value"] is None:
            parts.append(f"{ENT_NAME[e]} não tem valor positivo nem no caso favorável (preço {tok_price})")
        else:
            tok_fav = "{{value:" + fav["value_refs"]["paper_value"] + "}}"
            if fav["paper_value"] >= reg.get(price_ref):
                parts.append(f"{ENT_NAME[e]} só alcança o preço ({tok_price}) no caso favorável ({tok_fav})")
            else:
                parts.append(f"{ENT_NAME[e]} fica abaixo do preço ({tok_price}) mesmo no caso favorável ({tok_fav})")
        refs.append(fav["case_id"])
    text = ("; ".join(parts) + ". O preço embute premissas além do caso-base proposto (eficiência retida, ganhos da Copasa sob o novo "
            "controlador, remuneração acima da modelada).")
    return c("CL.result.market_view", claim_type="inference", text_template=text, calculation_refs=refs,
             limitations="Inferência sobre o preço; não é recomendação de venda.")


def build(reg: Registry, rec: dict, cap: dict, bal: dict, a: dict, val: dict, sec: dict) -> dict:
    v, c = reg.value, reg.claim
    reg.assumption("margin_of_safety", entity_id="", driver="required_upside_vs_base_value", year="", base=0.20, adverse=0.30,
                   favorable=0.10, unit="ratio", rationale="Proposta do agente para H08: compra só se o valor-base superar o preço em ≥20%.")
    mos = reg.get("A.margin_of_safety.base")
    # ---------------- Regra de decisão -------------------------------------------------------
    screen = {}
    for e in ENT_NAME:
        b = _case(val, f"{e}.base")
        grid = [x for x in val["cases"] if x["entity_id"] == e and x["scenario_id"] == "grid"]
        price = reg.get(b["value_refs"]["price"])
        grid_ok = all(x["paper_value"] is not None and x["paper_value"] > price for x in grid)
        up = b["paper_value"] / price - 1 if b["paper_value"] is not None else None
        screen[e] = dict(base_upside=up, grid_all_above_price=grid_ok, passes=bool(up is not None and up >= mos and grid_ok))
    chosen = [e for e, s in screen.items() if s["passes"]]
    entity = chosen[0] if len(chosen) == 1 else (max(chosen, key=lambda e: screen[e]["base_upside"]) if chosen else None)
    ticker = {"sabesp": "SBSP3", "copasa": "CSMG3", "sanepar": "SAPR11"}.get(entity)
    # Limiar da NTN-B que leva o WACC proposto ao WACC implícito no preço (demais componentes constantes).
    implied_ref = val["implied_wacc"].get("sanepar")
    if implied_ref and reg.get(implied_ref) is not None:
        lev, tax = reg.get("A.leverage.base"), reg.get("A.tax_rate.base")
        pi_lr = reg.get("A.ipca_long_run.base")
        sens = ((1 - lev) + lev * (1 - tax)) * (1 + pi_lr)  # ∂WACC nominal / ∂ taxa real soberana
        thr = reg.get("V.macro.ntnb_2035_real.2026-10-30") + (reg.get(implied_ref) - reg.get("A.wacc_nominal.base")) / sens
        v("V.trigger.ntnb_threshold", metric_id="trigger_real_risk_free_threshold", value=thr, unit="ratio", value_state="derived",
          fact_type="derived", calculation_ref=f"NTN-B + (WACC implícito − WACC proposto)/{sens:.4f}",
          note="NTN-B 2035 em que o WACC proposto alcança o WACC implícito no preço da SAPR11.")
    if entity:
        bcase = _case(val, f"{entity}.base")
        v(f"V.{entity}.max_entry_price", metric_id="max_entry_price", entity_id=entity, instrument_id=ticker,
          value=bcase["paper_value"] * (1 - mos), unit="BRL/unit" if entity == "sanepar" else "BRL/share", value_state="derived",
          fact_type="derived", calculation_ref=f"valor caso-base × (1 − margem {mos:.0%})", note="Condição de entrada proposta (H08).")
    # ---------------- Claims: abertura -------------------------------------------------------
    s = "sanepar"
    sb, sr, sa, sf = (_case(val, f"{s}.{k}") for k in ("base", "rates_up", "execution_adverse", "favorable"))
    if entity != s:
        raise RuntimeError(f"Regra de decisão selecionou {entity}; os textos desta versão descrevem a Sanepar e precisam ser revistos.")
    lead = [c("CL.lead.decision", claim_type="inference", status="proposed",
              text_template=("Proposta: " + ENT_NAME[entity] + " (" + ticker + ") como compra condicionada — único caso em que o valor do "
                             "caso-base ({{value:%s}} por unit) supera o preço de 30/10 ({{value:%s}}) com margem acima de "
                             "{{value:A.margin_of_safety.base}} e em todos os pontos da grade WACC×g.") % (sb["value_refs"]["paper_value"], sb["value_refs"]["price"]),
              assumption_refs=["margin_of_safety", "wacc_nominal"], calculation_refs=[sb["case_id"]],
              limitations="Proposta do agente; decisão do grupo (H09) não registrada."),
            c("CL.lead.thesis", claim_type="inference",
              text_template=("Tese: no saneamento, ESG entra no valor pela base remunerada. Mesmo deduzindo o precatório integral "
                             "(PV {{value:V.sanepar.obligation_pv.base}}) e tratando o retorno regulatório abaixo do custo de capital, "
                             "o valor-base da Sanepar supera o preço; o desconto de mercado remunera o risco regulatório estadual."),
              calculation_refs=[sb["case_id"]], limitations="Inferência condicional ao modelo revisado."),
            c("CL.lead.price", claim_type="fact", text_template="SAPR11 fechou a {{value:V.SAPR11.close.2026-10-30}} em 30/10/2026.",
              source_refs=["SRC_market_public_sapr11_485069a6"], limitations="Provedor público; confirmação Bloomberg/B3 (H01) não obtida.")]
    # ---------------- Setor, SWOT, médio prazo -----------------------------------------------
    sector = [c("CL.sector.coverage", claim_type="fact",
                text_template="Em 2024, {{value:OBS_002588}} da população tinha rede de água e {{value:OBS_002589}} rede coletora de esgoto (SINISA).",
                source_refs=["SRC_sinisa_agua_2025_b3a812a4", "SRC_sinisa_esgoto_2025_b3c3c185"],
                limitations="Medidas populacionais; tratamento do coletado é outro indicador."),
              c("CL.sector.targets", claim_type="fact",
                text_template="O Marco Legal fixa {{value:V.sector.target_water_2033}} de acesso à água e {{value:V.sector.target_sewer_2033}} de coleta e tratamento até 2033.",
                source_refs=["SRC_marco_legal_9270810f"], limitations="Metas nacionais; contratos têm cronogramas próprios."),
              c("CL.sector.treatment_gap", claim_type="fact",
                text_template="Do esgoto gerado, {{value:OBS_002590}} é tratado; do coletado, {{value:OBS_002591}} (SINISA 2024).",
                source_refs=["SRC_sinisa_esgoto_2025_b3c3c185"], limitations="Bases de volume distintas.")]
    swot = [c("CL.swot.strength", claim_type="fact",
              text_template="Força: contratos longos — Sabesp até {{value:V.sabesp.concession_end_year}} e Sanepar até {{value:V.sanepar.concession_end_year}} (343 contratos).",
              source_refs=["SRC_sabesp_ambiente_regulatorio_ff446d05", "SRC_doc_sapr_2t26_e40a8cc1"], limitations="Exceções municipais existem."),
            c("CL.swot.weakness", claim_type="fact",
              text_template="Fraqueza: perdas na distribuição de {{value:OBS_002592}} no país (2024) e capex elevado — Sabesp desembolsou {{value:V.sabesp.capex_cash.2025}} em 2025.",
              source_refs=["SRC_sinisa_agua_2025_b3a812a4", "SRC_cvm_dfp_2025_cdce6cc0"], limitations="Perda física e de faturamento diferem."),
            c("CL.swot.opportunity", claim_type="inference",
              text_template="Oportunidade: expandir esgoto e eficiência; investimento cria valor quando a remuneração regulatória supera o custo de capital (Copasa: {{value:%s}} por R$ investido)." % sec["value_ratio"]["copasa"],
              calculation_refs=["copasa.base"], limitations="Razão de valor depende do WACC de mercado proposto."),
            c("CL.swot.threat", claim_type="fact",
              text_template="Ameaça: juros reais altos (NTN-B 2035 a {{value:V.macro.ntnb_2035_real.2026-10-30}}) e intervenção regulatória — a Agepar destinou 100% do precatório aos usuários e homologou reajuste de {{value:V.sanepar.tariff_adjustment.2026}} em 2026 contra IPCA de {{value:V.macro.ipca_actual.2025}} em 2025.",
              source_refs=["SRC_tesouro_taxas_84f53c4b", "SRC_doc_sapr_itr_d93332d6", "SRC_doc_sapr_2t26_e40a8cc1", "SRC_bcb_sgs_433_a47db5ed"],
              limitations="Reajuste de 2026 aplica-se à tarifa de equilíbrio do ciclo; comparação com IPCA é indicativa.")]
    medium = [c("CL.mt.regulation", claim_type="fact",
                text_template="Regulação: a 3ª RTP da Copasa elevou o WACC regulatório para {{value:V.copasa.wacc_reg_real_after_tax}} real pós-impostos com reconhecimento anual de investimentos; a Sanepar opera a {{value:V.sanepar.wacc_reg_real_after_tax}}.",
                source_refs=["SRC_doc_csmg_2t26_1996f20b", "SRC_doc_sapr_itr_d93332d6"], limitations="Ciclos e metodologias diferentes."),
              c("CL.mt.competition", claim_type="fact",
                text_template=("Competição por concessões e capital: a Aegea venceu o Pará com compromisso de {{value:V.sector.aegea_para_capex}} "
                               "em 99 municípios; a Copasa foi desestatizada em junho de 2026, com a Equatorial como investidora de referência "
                               "({{value:V.copasa.reference_investor_share}} do capital)."),
                source_refs=["SRC_competicao_b978a92a", "SRC_copasa_fr_20260611", "SRC_doc_csmg_2t26_1996f20b"],
                limitations="Compromisso de investimento não é execução; o plano da Copasa será revisto pelo novo controlador."),
              c("CL.mt.technology", claim_type="fact",
                text_template="Tecnologia e eficiência: a Copasa reduziu o índice de perdas na distribuição em {{value:V.copasa.distribution_loss_reduction_pp}} em 12 meses; a Sabesp contratou {{value:V.sabesp.self_production_contracted_mwm}} de autoprodução de energia.",
                source_refs=["SRC_doc_csmg_2t26_1996f20b", "local_45586543e35a"], limitations="Efeito no caixa não quantificado pelas empresas.")]
    brr = val["brr_check"]
    c("CL.method.brr_check", claim_type="inference",
      text_template=("Verificação da base: a base remunerada implícita da Sanepar ({{value:%s}}) difere em {{value:%s}} (implícita ÷ oficial − 1) da BRR "
                     "líquida oficial da 3ª RTP atualizada pelo IPCA ({{value:%s}}), o que confere a ordem de grandeza do motor." % (brr["implied"], brr["gap"], brr["official_updated"])),
      value_refs=[brr["implied"], brr["gap"], brr["official_updated"], brr["official"]],
      source_refs=["SRC_agepar_nt_006_2025", "SRC_bcb_sgs_433_a47db5ed"],
      limitations="BRR em fiscalização, com glosa prudencial; datas-base diferem (BRR dez/2024 com ativos até 2023; base implícita de 2023 remunerada em 2025).")
    # ---------------- ESG e ponte -------------------------------------------------------------
    esg = [c("CL.esg.matrix", claim_type="inference",
             text_template="A matriz liga cinco fatores (perdas, esgoto, resiliência, acesso, governança) a linhas de caixa; definições diferentes impedem ranking sintético.",
             limitations="Sem score ESG."),
           c("CL.esg.losses", claim_type="fact",
             text_template="Perdas por ligação: Sabesp {{value:OBS_002593}} (IPGR 2024), Copasa {{value:OBS_002594}} e Sanepar {{value:OBS_002597}} (LTM jun/26).",
             source_refs=["SRC_sabesp_sustentabilidade_2024_7e111812", "SRC_doc_csmg_2t26_1996f20b", "SRC_doc_sapr_2t26_e40a8cc1"],
             limitations="Períodos e perímetros distintos."),
           c("CL.esg.sewer", claim_type="fact",
             text_template="Esgoto: Sanepar {{value:OBS_002599}} de atendimento urbano e {{value:OBS_002600}} do coletado tratado; Copasa {{value:OBS_002596}} de cobertura (jun/26).",
             source_refs=["SRC_doc_sapr_2t26_e40a8cc1", "SRC_doc_csmg_2t26_1996f20b"], limitations="Cobertura ≠ tratamento."),
           c("CL.esg.governance", claim_type="fact",
             text_template="Governança: o passivo regulatório do precatório da Sanepar era {{value:V.sanepar.regulatory_liability.2026-06-30}} em 30/06/2026; a companhia contesta judicialmente, sem liminar.",
             source_refs=["SRC_doc_sapr_itr_d93332d6"], limitations="Desfecho judicial incerto.")]
    br = [c("CL.bridge.rab", claim_type="inference",
            text_template=("Canal ESG→valor: cada R$ investido em expansão e remunerado vale {{value:%s}} na Sanepar, {{value:%s}} na Sabesp e "
                           "{{value:%s}} na Copasa ao WACC de mercado proposto ({{value:A.wacc_nominal.base}}).") %
                          (sec["value_ratio"]["sanepar"], sec["value_ratio"]["sabesp"], sec["value_ratio"]["copasa"]),
            assumption_refs=["wacc_nominal"], calculation_refs=["sanepar.base", "sabesp.base", "copasa.base"],
            limitations="Razão de perpetuidade; depende do WACC regulatório vigente e do proposto."),
          c("CL.bridge.energy", claim_type="assumption",
            text_template="Sensibilidade de energia: reduzir 1% da despesa de energia da água da Sanepar justifica investir até {{value:V.case.sanepar.energy.r50.capex_break_even}}–{{value:V.case.sanepar.energy.r100.capex_break_even}} (retenção 50–100%).",
            assumption_refs=["energy_saving", "wacc_nominal"], calculation_refs=["sanepar.energy.r50", "sanepar.energy.r100"],
            limitations="Hipotético; não somado ao DCF-base.")]
    # ---------------- Método e resultado -----------------------------------------------------
    method = [c("CL.method.fcff", claim_type="assumption",
                text_template=("FCFF com vínculo capex→base remunerada: EBIT de 2025 define a base implícita; capex entra na remuneração com "
                               "defasagem de {{value:A.recognition_lag.base}}; desconto a {{value:A.wacc_nominal.base}} (CAPM local com NTN-B "
                               "{{value:V.macro.ntnb_2035_real.2026-10-30}})."),
                assumption_refs=["recognition_lag", "wacc_nominal"], limitations="BRR oficial não obtida; base implícita."),
              c("CL.method.recurring", claim_type="fact",
                text_template="Bases 2025 recorrentes: EBITDA Sabesp {{value:V.sabesp.ebitda_recurring.2025}}, Copasa {{value:V.copasa.ebitda_recurring.2025}}, Sanepar {{value:V.sanepar.ebitda_recurring.2025}} — sem construção, ativo financeiro e não recorrentes.",
                source_refs=["SRC_cvm_dfp_2025_cdce6cc0", "local_45586543e35a", "SRC_sanepar_release_2025_5f7297a2"],
                limitations="Sabesp: valor da planilha (13.221) fica como alternativa."),
              c("CL.method.precatorio", claim_type="inference",
                text_template="Precatório tratado uma única vez: PV de {{value:V.sanepar.obligation_pv.base}} na ponte (atualização ≈ WACC, logo PV ≈ saldo atualizado), sem benefício fiscal no caso-base.",
                calculation_refs=["sanepar.base"], limitations="Calendário mensal estimado; benefício fiscal incerto.")]
    result = [c("CL.result.values", claim_type="inference",
                text_template=("Caso-base (30/10/2026): Sanepar {{value:%s}}/unit vs {{value:%s}}; Sabesp {{value:%s}} vs {{value:%s}}; "
                               "Copasa {{value:%s}} vs {{value:%s}}.") % (
                    sb["value_refs"]["paper_value"], sb["value_refs"]["price"], _case(val, "sabesp.base")["value_refs"]["paper_value"],
                    _case(val, "sabesp.base")["value_refs"]["price"], _case(val, "copasa.base")["value_refs"]["paper_value"],
                    _case(val, "copasa.base")["value_refs"]["price"]),
                calculation_refs=["sanepar.base", "sabesp.base", "copasa.base"], limitations="Valores condicionais, não preços-alvo aprovados."),
              c("CL.result.implied", claim_type="inference",
                text_template=("WACC implícito no preço: Sanepar {{value:%s}}, Sabesp {{value:%s}}, Copasa {{value:%s}} — contra {{value:A.wacc_nominal.base}} proposto.") %
                              tuple(val["implied_wacc"][e] for e in ("sanepar", "sabesp", "copasa")),
                assumption_refs=["wacc_nominal"], limitations="Demais premissas no caso-base; não é retorno esperado da ação."),
              _market_view(reg, c, val)]
    risks = [c("CL.risk.scenarios", claim_type="inference",
               text_template=("Sanepar por cenário: base {{value:%s}}, juros +1,5 p.p. {{value:%s}}, pior execução/regulação {{value:%s}}, favorável {{value:%s}}.") %
                             (sb["value_refs"]["paper_value"], sr["value_refs"]["paper_value"], sa["value_refs"]["paper_value"], sf["value_refs"]["paper_value"]),
               calculation_refs=[x["case_id"] for x in (sb, sr, sa, sf)], limitations="Sem probabilidades atribuídas."),
             c("CL.risk.trigger.regulation", claim_type="assumption",
               text_template="Gatilho 1 — regulação: se o reajuste anual de 2027 (IRT, maio) também ficar abaixo do IPCA de 12 meses, ou o WACC regulatório cair abaixo de {{value:V.sanepar.wacc_reg_real_after_tax}}, recalcular o caso adverso e sair se o valor ficar abaixo do preço.",
               assumption_refs=["margin_of_safety"], limitations="Regra proposta (H08)."),
             c("CL.risk.trigger.execution", claim_type="assumption",
               text_template="Gatilho 2 — execução/precatório: capex caixa divergindo mais de 10% do plano por dois trimestres (próxima leitura: ITR 3T26 em 12/11/2026) ou cronograma do precatório com PV acima de {{value:V.sanepar.obligation_pv.base}} → rever posição.",
               assumption_refs=["capex_sanepar_2026"], source_refs=["SRC_sanepar_calendario_2026_f2d6875e"], limitations="Limite de 10% é disciplina proposta."),
             c("CL.risk.trigger.rates", claim_type="assumption",
               text_template=("Gatilho 3 — juros: NTN-B 2035 acima de {{value:V.trigger.ntnb_threshold}} (hoje {{value:V.macro.ntnb_2035_real.2026-10-30}}) "
                              "leva o WACC proposto ao WACC implícito no preço ({{value:%s}}) e elimina o potencial → suspender compras e "
                              "recalcular.") % val["implied_wacc"]["sanepar"],
               assumption_refs=["wacc_nominal", "beta", "erp", "debt_spread", "leverage"],
               limitations="Mantém beta, prêmio, spread e estrutura constantes; monitoramento diário; regra proposta."),
             c("CL.risk.objection", claim_type="inference",
               text_template=("Melhor objeção: o desconto é armadilha — controle estadual, precatório 100%% aos usuários e remuneração regulatória abaixo "
                              "do custo de capital (cada R$ investido vale {{value:%s}}). Resposta: o caso-base já deduz o PV integral do precatório e "
                              "trata o capex como destruidor de valor; o caso adverso ({{value:%s}}) mostra o que invalidaria a tese.") %
                             (sec["value_ratio"]["sanepar"], sa["value_refs"]["paper_value"]),
               calculation_refs=["sanepar.base", "sanepar.execution_adverse"], limitations="Objeção não eliminada; mitigada por gatilhos.")]
    concl = [c("CL.conclusion.decision", claim_type="inference", status="proposed",
               text_template=("Conclusão proposta: comprar SAPR11 abaixo de {{value:V.sanepar.max_entry_price}} por unit, com os três gatilhos ativos; "
                              "não comprar Sabesp e Copasa ao preço de 30/10 nesta configuração."),
               calculation_refs=["sanepar.base"], assumption_refs=["margin_of_safety"],
               limitations="Exige adoção real pelo grupo (H09) e revisão das cinco premissas (H08).")]
    slots = {"lead": [x for x in lead], "sector": sector, "swot": swot, "medium_term": medium, "esg": esg, "bridge": br,
             "valuation_method": method, "valuation_result": result, "risks": risks, "conclusion": concl}
    decision = dict(status="proposed" if entity else "unresolved", entity_id=entity, instrument_id=ticker,
                    rationale_claim_refs=["CL.lead.decision", "CL.lead.thesis", "CL.result.values", "CL.result.implied", "CL.method.precatorio"],
                    alternative_claim_refs=["CL.result.market_view", "CL.risk.scenarios"],
                    trigger_claim_refs=["CL.risk.trigger.regulation", "CL.risk.trigger.execution", "CL.risk.trigger.rates"],
                    human_record_refs=[], rule=dict(margin_of_safety_ref="A.margin_of_safety.base",
                                                     description="Passa quem tem valor-base ≥ preço×(1+margem) e todos os pontos da grade acima do preço."),
                    screen=screen, objection_claim_ref="CL.risk.objection",
                    h08_judgments=[
                        dict(id="H08.1", topic="Custo de capital", proposal_ref="A.wacc_nominal.base", alternatives=["A.wacc_nominal.adverse", "A.wacc_nominal.favorable"]),
                        dict(id="H08.2", topic="WACC regulatório Sabesp (contrato fixa 7,86% até 2029; alternativas = 2º ciclo)", proposal_ref="A.sabesp_wacc_reg.base", alternatives=["A.sabesp_wacc_reg.adverse", "A.sabesp_wacc_reg.favorable"]),
                        dict(id="H08.3", topic="Defasagem/captura da remuneração", proposal_ref="A.recognition_lag.base", alternatives=["A.recognition_lag.adverse", "A.recognition_share.adverse"]),
                        dict(id="H08.4", topic="Precatório (100%, sem benefício fiscal)", proposal_ref="V.sanepar.obligation_pv.base", alternatives=["sanepar.favorable", "sanepar.execution_adverse"]),
                        dict(id="H08.5", topic="Terminal (perpetuidade vs fim da concessão)", proposal_ref="A.rab_real_growth_after_plan.base", alternatives=["sanepar.terminal_finite", "sabesp.terminal_finite", "copasa.terminal_finite"]),
                    ])
    # ---------------- Visões para a apresentação ------------------------------------------
    def pt(pid, label, y, case=None, claims=(), role="ordinary", x=None):
        d = dict(point_id=pid, label=label, y_value_ref=y, claim_refs=list(claims), point_role=role)
        if case:
            d["case_ref"] = case
        if x:
            d["x_value_ref"] = x
        return d
    views = [
        dict(view_id="VW.sector.coverage", slot="sector", view_type="bar", title="Cobertura nacional e metas 2033",
             claim_refs=["CL.sector.coverage", "CL.sector.targets"],
             series=[dict(series_id="S.coverage", label="Brasil 2024", points=[pt("P.water", "Água", "OBS_002588"), pt("P.sewer", "Esgoto (coleta)", "OBS_002589")]),
                     dict(series_id="S.target", label="Meta 2033", points=[pt("P.water.t", "Água", "V.sector.target_water_2033"), pt("P.sewer.t", "Esgoto", "V.sector.target_sewer_2033")])]),
        dict(view_id="VW.esg.matrix", slot="esg", view_type="matrix", title="Matriz ESG: indicador → canal de caixa",
             claim_refs=["CL.esg.matrix", "CL.esg.losses", "CL.esg.sewer", "CL.esg.governance"],
             series=[dict(series_id=f"S.{e}", label=ENT_NAME[e],
                          points=[pt(f"P.{row['row_id']}.{e}", row["factor"], row["cells"][e]["value_refs"][0]) for row in sec["matrix"] if row["cells"][e]["value_refs"]])
                     for e in ENT_NAME]),
        dict(view_id="VW.esg.energy", slot="bridge", view_type="bar", title="Teto de investimento por 1% de economia de energia",
             claim_refs=["CL.bridge.energy"],
             series=[dict(series_id=f"S.r{r}", label=f"Retenção {r}%",
                          points=[pt(f"P.{e}.r{r}", ENT_NAME[e], f"V.case.{e}.energy.r{r}.capex_break_even", case=f"{e}.energy.r{r}") for e in ENT_NAME])
                     for r in (50, 100)]),
        dict(view_id="VW.valuation.value_vs_price", slot="valuation_result", view_type="scatter", title="Valor condicional vs preço (30/10/2026)",
             claim_refs=["CL.result.values"],
             series=[dict(series_id="S.value", label="Valor caso-base",
                          points=[pt(f"P.{e}.value", ENT_NAME[e], _case(val, f"{e}.base")["value_refs"]["paper_value"], case=f"{e}.base") for e in ENT_NAME]),
                     dict(series_id="S.price", label="Preço 30/10",
                          points=[pt(f"P.{e}.price", ENT_NAME[e], _case(val, f"{e}.base")["value_refs"]["price"], case=f"{e}.base") for e in ENT_NAME])]),
    ]
    # Ponte EV→patrimônio da Sanepar com deltas declarados pelo produtor.
    vr = sb["value_refs"]
    deltas = []
    for key, label in (("net_debt_october_estimate", "Dívida líquida (out, estimada)"), ("debt_like", "Outros direitos de terceiros"),
                       ("obligation_pv", "Precatório (PV)")):
        did = v(f"V.case.sanepar.base.delta.{key}", metric_id="bridge_delta", entity_id="sanepar", value=-reg.get(vr[key]), unit="BRL", scale=1e6,
                value_state="derived", fact_type="derived", calculation_ref=f"−{vr[key]}", note=f"Delta da ponte: {label}")
        deltas.append(pt(f"P.bridge.{key}", label, did, case="sanepar.base", role="delta"))
    views.append(dict(view_id="VW.valuation.bridge_sanepar", slot="valuation_method", view_type="bridge", title="Sanepar: da firma ao acionista (R$ mi)",
                      claim_refs=["CL.method.precatorio"],
                      series=[dict(series_id="S.bridge", label="Caso-base",
                                   points=[pt("P.bridge.ev", "Valor da firma", vr["enterprise_value"], case="sanepar.base", role="start")] + deltas +
                                          [pt("P.bridge.equity", "Patrimônio", vr["equity_residual_before_floor"], case="sanepar.base", role="end")])]))
    for e in ENT_NAME:
        grid = [x for x in val["cases"] if x["entity_id"] == e and x["scenario_id"] == "grid"]
        series = {}
        for x in grid:
            go = x["dimensions"]["g_real"]
            series.setdefault(go["option_id"], dict(series_id=f"S.{e}.{go['option_id']}", label=go["label"], points=[]))
            y = x["value_refs"].get("paper_value") or x["value_refs"].get("equity_residual_before_floor")
            series[go["option_id"]]["points"].append(pt(f"P.{x['case_id']}", x["dimensions"]["wacc"]["label"], y, case=x["case_id"],
                                                        x=x["dimensions"]["wacc"]["value_ref"]))
        views.append(dict(view_id=f"VW.grid.{e}", slot="valuation_result", view_type="heatmap", title=f"{ENT_NAME[e]}: valor por WACC × g real",
                          claim_refs=["CL.result.values"], series=list(series.values())))
    views.append(dict(view_id="VW.scenarios", slot="risks", view_type="bar", title="Valor por cenário (N/D quando resíduo ≤ 0)",
                      claim_refs=["CL.risk.scenarios"],
                      series=[dict(series_id=f"S.{e}", label=ENT_NAME[e],
                                   points=[pt(f"P.{e}.{sid}", sid, _case(val, f"{e}.{sid}")["value_refs"].get("paper_value") or
                                              _case(val, f"{e}.{sid}")["value_refs"]["equity_residual_before_floor"], case=f"{e}.{sid}")
                                           for sid in ("base", "rates_up", "execution_adverse", "favorable")]) for e in ENT_NAME]))
    views.append(dict(view_id="VW.triggers", slot="risks", view_type="table", title="Gatilhos de revisão",
                      claim_refs=["CL.risk.trigger.regulation", "CL.risk.trigger.execution", "CL.risk.trigger.rates"],
                      series=[dict(series_id="S.triggers", label="Limiares", points=[
                          pt("P.t1", "WACC regulatório mínimo", "V.sanepar.wacc_reg_real_after_tax", claims=["CL.risk.trigger.regulation"]),
                          pt("P.t2", "PV máximo do precatório", "V.sanepar.obligation_pv.base", claims=["CL.risk.trigger.execution"]),
                          pt("P.t3", "NTN-B 2035 limite", "V.trigger.ntnb_threshold", claims=["CL.risk.trigger.rates"],
                             x="V.macro.ntnb_2035_real.2026-10-30")])]))
    return {"slots": {k: list(v) for k, v in slots.items()}, "decision": decision, "views": views}
