"""Conteúdo editorial das peças (EN03/EN06): textos de tela, falas, perguntas e guias.

Regra: nenhum número, empresa recomendada ou definição digitada à mão. Valores entram por
{{value:ID}}, a empresa/papel por {{entity:decision}}/{{ticker:decision}}; o resto é texto.
Datas de calendário e contagens estruturais (três gatilhos, cinco fatores) são permitidas.
"""
from __future__ import annotations

P = "V.SAPR11.close.2026-10-30"
SB, CS, SP = "sabesp", "copasa", "sanepar"

# ------------------------------------------------------------------------------------------------
# Páginas do perfil html10 (P01–P10). O perfil pptx9 funde P07+P08 no slide 7.
PAGES = [
    dict(id="P01", slide9=1, block="B1", voice="Rodrigo", seconds=50, slot="lead", kind="thesis",
         kicker="Recomendação proposta",
         title="{{entity:decision}}: compra condicionada",
         subtitle="O valor do nosso caso-base supera o preço de mercado mesmo depois de descontar todo o precatório.",
         claims=["CL.lead.decision", "CL.lead.thesis", "CL.lead.price", "CL.conclusion.decision"]),
    dict(id="P02", slide9=2, block="B2", voice="Lorenzo", seconds=50, slot="sector", kind="sector",
         kicker="O problema",
         title="O Brasil ainda precisa investir muito, sobretudo em esgoto",
         subtitle="Quem financia e quem é remunerado por esse investimento define o retorno do acionista.",
         claims=["CL.sector.coverage", "CL.sector.targets", "CL.sector.treatment_gap"]),
    dict(id="P03", slide9=3, block="B3", voice="Lorenzo", seconds=75, slot="swot", kind="swot",
         kicker="SWOT do setor",
         title="A demanda não é o risco; regulação e custo de capital são",
         subtitle="Clique em cada quadrante para ver a evidência e o efeito na tese.",
         claims=["CL.swot.strength", "CL.swot.weakness", "CL.swot.opportunity", "CL.swot.threat"]),
    dict(id="P04", slide9=4, block="B4", voice="Navarro", seconds=60, slot="medium_term", kind="medium",
         kicker="Médio prazo",
         title="Três forças mudam o retorno até o fim da década",
         subtitle="Regulação define quanto cada real investido rende; competição e tecnologia definem quem executa melhor.",
         claims=["CL.mt.regulation", "CL.mt.competition", "CL.mt.technology"]),
    dict(id="P05", slide9=5, block="B5", voice="Michel", seconds=90, slot="esg", kind="matrix",
         kicker="Matriz ESG",
         title="Cada indicador ESG precisa chegar ao caixa",
         subtitle="Sem nota sintética: definições e períodos diferem. Clique numa célula para ver definição, período e fonte.",
         claims=["CL.esg.matrix", "CL.esg.losses", "CL.esg.sewer", "CL.esg.governance"]),
    dict(id="P06", slide9=6, block="B6", voice="Michel", seconds=65, slot="bridge", kind="bridge",
         kicker="Do ESG ao valor",
         title="Investir só cria valor se a tarifa remunerar acima do custo de capital",
         subtitle="Quanto vale cada R$ 1 investido em expansão, ao nosso custo de capital, e um teste de eficiência energética.",
         claims=["CL.bridge.rab", "CL.bridge.energy"]),
    dict(id="P07", slide9=7, block="B7.a", voice="Rodrigo", seconds=40, slot="valuation_method", kind="method",
         kicker="Como calculamos",
         title="Do caixa da empresa ao valor do acionista",
         subtitle="Valor da firma menos dívida e compromissos: o que sobra é do acionista.",
         claims=["CL.method.fcff", "CL.method.recurring", "CL.method.precatorio"]),
    dict(id="P08", slide9=7, block="B7.b", voice="Rodrigo", seconds=45, slot="valuation_result", kind="result",
         kicker="Valor contra preço",
         title="Só a {{entity:decision}} fica acima do preço, em toda a grade testada",
         subtitle="Escolha a empresa e um ponto da grade de custo de capital × crescimento.",
         claims=["CL.result.values", "CL.result.implied", "CL.result.market_view"]),
    dict(id="P09", slide9=8, block="B8", voice="Navarro", seconds=60, slot="risks", kind="risks",
         kicker="Riscos e gatilhos",
         title="O risco da tese é regulatório; três gatilhos dizem quando revisar",
         subtitle="Valores condicionais do modelo, não previsões de preço. Sem probabilidades atribuídas.",
         claims=["CL.risk.scenarios", "CL.risk.trigger.regulation", "CL.risk.trigger.execution", "CL.risk.trigger.rates", "CL.risk.objection"]),
    dict(id="P10", slide9=9, block="B9", voice="Todos", seconds=25, slot="conclusion", kind="decision",
         kicker="Decisão",
         title="Nossa proposta: {{entity:decision}}, com preço e gatilhos",
         subtitle="Proposta do agente para adoção pelo grupo (H09).",
         claims=["CL.conclusion.decision", "CL.lead.decision"]),
]

# Textos curtos de tela por página (tokens resolvidos pelo consumidor).
SCREEN = {
    "P01": dict(
        hero=[dict(label="Valor no caso-base", value="V.case.sanepar.base.paper_value", note="por unit"),
              dict(label="Preço em 30/10/2026", value=P, note="fechamento SAPR11"),
              dict(label="Potencial", value="V.case.sanepar.base.upside", style="signed1", note="valor/preço − 1")],
        chips=[dict(icon="target", text="Comprar só até {{value:V.sanepar.max_entry_price}} por unit (margem de {{value:A.margin_of_safety.base}})"),
               dict(icon="shield", text="Precatório já deduzido: {{value:V.sanepar.obligation_pv.base|precise}} a valor presente"),
               dict(icon="flag", text="Três gatilhos de revisão: regulação, execução e juros")],
        source_panel="SAPR11 = 1 ação ON + 4 PN. Preço de provedor público em 30/10/2026; confirmação no Terminal (H01) não obtida."),
    "P02": dict(
        bars=[dict(id="water", label="Água (rede)", value="OBS_002588", target="V.sector.target_water_2033"),
              dict(id="sewer", label="Esgoto (coleta)", value="OBS_002589", target="V.sector.target_sewer_2033")],
        notes={"water": "População total com rede de água (SINISA, ano-base 2024). Meta legal de acesso até 2033.",
               "sewer": "População total com rede coletora (SINISA, ano-base 2024). Coletar não é tratar: do esgoto gerado, só {{value:OBS_002590}} é tratado; do coletado, {{value:OBS_002591}}."},
        callout="Coletar ≠ tratar: só {{value:OBS_002590}} do esgoto gerado recebe tratamento."),
    "P03": dict(quadrants=[
        dict(id="S", label="Forças", bullets=["Serviço essencial, demanda estável", "Contratos longos: Sabesp até {{value:V.sabesp.concession_end_year}}, Sanepar até {{value:V.sanepar.concession_end_year}}"],
             claim="CL.swot.strength", implication="Previsibilidade sustenta valuation de longo prazo — se a regulação for estável."),
        dict(id="W", label="Fraquezas", bullets=["Perdas de {{value:OBS_002592}} da água distribuída no país", "Capital intensivo: Sabesp investiu {{value:V.sabesp.capex_cash.2025}} em 2025"],
             claim="CL.swot.weakness", implication="Retorno depende de o investimento ser reconhecido na tarifa."),
        dict(id="O", label="Oportunidades", bullets=["Expansão do esgoto até as metas de 2033", "Eficiência: perdas, energia, medição"],
             claim="CL.swot.opportunity", implication="Cria valor só onde a remuneração supera o custo de capital (Copasa: {{value:V.copasa.rab_value_ratio.base}} por R$ 1)."),
        dict(id="T", label="Ameaças", bullets=["Juros reais altos: NTN-B a {{value:V.macro.ntnb_2035_real.2026-10-30}}", "Intervenção: precatório 100% aos usuários; reajuste de {{value:V.sanepar.tariff_adjustment.2026}} vs IPCA {{value:V.macro.ipca_actual.2025}}"],
             claim="CL.swot.threat", implication="É o principal risco da tese na Sanepar — vira gatilho de revisão."),
    ]),
    "P04": dict(cards=[
        dict(id="reg", label="Regulação", tabs=dict(
            fato="Copasa: WACC regulatório de {{value:V.copasa.wacc_reg_real_after_tax}} real pós-impostos, com reconhecimento anual de investimentos. Sanepar: {{value:V.sanepar.wacc_reg_real_after_tax}}. Sabesp: base de ativos com reajuste anual e WACC regulatório de {{value:V.sabesp.wacc_reg_real_after_tax}} fixo no contrato até 2029.",
            prazo="Copasa: ciclo 2026–2029. Sanepar: ciclo 2025–2028 e reajuste anual em maio. Sabesp: ciclos 2024–2029 e 2030–2034.",
            canal="Define quanto cada real investido rende. Acima do custo de capital, crescer cria valor; abaixo, destrói."),
            claim="CL.mt.regulation"),
        dict(id="comp", label="Competição", tabs=dict(
            fato="A Aegea venceu a concessão do Pará com compromisso de {{value:V.sector.aegea_para_capex}} em 99 municípios. A Copasa foi desestatizada em junho de 2026, com a Equatorial como investidora de referência ({{value:V.copasa.reference_investor_share}} do capital).",
            prazo="Concessões de décadas; anúncio não é execução.",
            canal="Disputa por concessões e por capital: quem capta mais barato e executa melhor ganha espaço."),
            claim="CL.mt.competition"),
        dict(id="tec", label="Tecnologia", tabs=dict(
            fato="A Copasa reduziu o índice de perdas em {{value:V.copasa.distribution_loss_reduction_pp}} em doze meses. A Sabesp contratou {{value:V.sabesp.self_production_contracted_mwm}} de autoprodução de energia.",
            prazo="Ganhos graduais; parte é compartilhada com o usuário nas revisões tarifárias.",
            canal="Reduz custo (energia, químicos, água perdida); o efeito no caixa depende de quanto a empresa retém."),
            claim="CL.mt.technology"),
    ]),
    "P06": dict(energy_saving="A.energy_saving.base"),
    "P07": dict(params=[dict(label="Custo de capital (WACC nominal)", value="A.wacc_nominal.base"),
                        dict(label="NTN-B 2035 (juro real soberano)", value="V.macro.ntnb_2035_real.2026-10-30"),
                        dict(label="Investimento entra na base remunerada após", value="A.recognition_lag.base"),
                        dict(label="Crescimento real da base no longo prazo", value="A.rab_real_growth_after_plan.base")]),
    "P09": dict(scenarios=[("base", "Base"), ("rates_up", "Juros maiores"), ("execution_adverse", "Adverso"), ("favorable", "Favorável")],
                scenario_notes={"base": "Premissas propostas: WACC {{value:A.wacc_nominal.base}}, defasagem {{value:A.recognition_lag.base}}, precatório 100%.",
                                "rates_up": "Mesmo caso, com custo de capital de {{value:V.case.sanepar.rates_up.wacc}}.",
                                "execution_adverse": "Captura de {{value:A.recognition_share.adverse}} da remuneração, custos acima do reconhecido, defasagem de {{value:A.recognition_lag.adverse}}, WACC regulatório menor, capex com parcerias e contingências.",
                                "favorable": "WACC {{value:A.wacc_nominal.favorable}}, defasagem {{value:A.recognition_lag.favorable}}, eficiência retida e precatório em 75% com benefício fiscal."},
                triggers=[
                    dict(id="reg", label="Regulação", metric="Reajuste anual Sanepar vs IPCA de 12 meses; WACC regulatório",
                         limit="Segundo reajuste abaixo do IPCA (maio/2027) ou WACC regulatório < {{value:V.sanepar.wacc_reg_real_after_tax}}",
                         when="Anual (reajuste de maio) e a cada decisão da Agepar", action="Recalcular o caso adverso; sair se valor < preço",
                         claim="CL.risk.trigger.regulation"),
                    dict(id="exe", label="Execução e precatório", metric="Capex caixa vs plano; cronograma do precatório",
                         limit="Desvio > 10% por dois trimestres ou PV do precatório > {{value:V.sanepar.obligation_pv.base|precise}}",
                         when="Trimestral — próximo ITR em 12/11/2026", action="Rever a posição", claim="CL.risk.trigger.execution"),
                    dict(id="rates", label="Juros", metric="NTN-B 2035 (taxa real)",
                         limit="Acima de {{value:V.trigger.ntnb_threshold}} (hoje {{value:V.macro.ntnb_2035_real.2026-10-30}})",
                         when="Diário", action="Suspender compras e recalcular", claim="CL.risk.trigger.rates")]),
    "P10": dict(points=[
        dict(label="Decisão", text="Comprar {{ticker:decision}} somente abaixo de {{value:V.sanepar.max_entry_price}} por unit"),
        dict(label="Por quê", text="Valor-base {{value:V.case.sanepar.base.paper_value}} contra preço {{value:V.SAPR11.close.2026-10-30}}, com o precatório inteiro já deduzido"),
        dict(label="Não comprar", text="Sabesp e Copasa: preço acima do valor no caso-base"),
        dict(label="Revisar quando", text="Regulação, execução ou juros cruzarem os limites dos três gatilhos")],
        ladder=dict(title="Faixa de compra da unit (R$)", price="Preço em 30/10/2026", limit="Limite de compra",
                    value="Valor no caso-base", buy="compra", margin="margem de segurança"),
        triggers_title="Gatilhos que reabrem a decisão"),
}

# ------------------------------------------------------------------------------------------------
# Falas (B1–B9; B7 dividido em B7.a/B7.b no perfil html10). ~140 palavras/min.
SPEECH = {
    "B1": ("Nós somos a asset.dev. Nossa recomendação é a {{entity:decision}}, pela unit {{ticker:decision}}, como compra condicionada. "
           "Em trinta de outubro, a unit fechou a {{value:V.SAPR11.close.2026-10-30}}. No nosso caso-base, ela vale {{value:V.case.sanepar.base.paper_value}}, "
           "um potencial de {{value:V.case.sanepar.base.upside}}. A ideia central é simples: no saneamento, ESG vira valor quando o investimento em água e esgoto "
           "é remunerado pela tarifa. E esse valor já desconta o precatório que a empresa terá de devolver aos usuários. Por isso a compra é condicionada: "
           "só abaixo de {{value:V.sanepar.max_entry_price}} e com três gatilhos de revisão, que mostramos no final. Lorenzo, começa pelo setor."),
    "B2": ("O ponto de partida é o déficit. No ano-base de 2024, {{value:OBS_002588}} da população tinha rede de água e só {{value:OBS_002589}} tinha coleta de esgoto. "
           "O Marco Legal pede {{value:V.sector.target_water_2033}} e {{value:V.sector.target_sewer_2033}} até 2033. E coletar não é tratar: do esgoto gerado, "
           "apenas {{value:OBS_002590}} é tratado. Fechar essa diferença exige muito investimento. Para o investidor, a pergunta não é se o setor vai investir, "
           "porque vai. A pergunta é se esse investimento será remunerado pela tarifa a uma taxa que pague o custo do capital."),
    "B3": ("Na SWOT, a força é a previsibilidade: serviço essencial e contratos longos, como o da Sabesp até {{value:V.sabesp.concession_end_year}} e o da Sanepar "
           "até {{value:V.sanepar.concession_end_year}}. A fraqueza é a intensidade de capital e as perdas: o país perde {{value:OBS_002592}} da água na distribuição, "
           "e só a Sabesp desembolsou {{value:V.sabesp.capex_cash.2025}} em investimentos em 2025. A oportunidade é a expansão do esgoto e a eficiência, mas ela só "
           "cria valor quando a remuneração regulatória supera o custo de capital. A ameaça é dupla: juros reais altos, com a NTN-B a "
           "{{value:V.macro.ntnb_2035_real.2026-10-30}}, e a intervenção do regulador. No Paraná, a Agepar mandou devolver todo o precatório aos usuários e "
           "homologou reajuste de {{value:V.sanepar.tariff_adjustment.2026}}, abaixo da inflação de {{value:V.macro.ipca_actual.2025}} do ano anterior. "
           "Conclusão da SWOT: a demanda não é o risco; regulação e custo de capital são. Navarro, o que muda daqui para frente?"),
    "B4": ("Vemos três forças no médio prazo. Primeiro, a regulação: a Copasa teve o WACC regulatório elevado para {{value:V.copasa.wacc_reg_real_after_tax}} real, "
           "com reconhecimento anual dos investimentos, e a Sanepar segue a {{value:V.sanepar.wacc_reg_real_after_tax}}. Isso define quanto cada real investido rende. "
           "Segundo, a competição por concessões e por capital: a Aegea venceu o Pará com compromisso de {{value:V.sector.aegea_para_capex}}, e a Copasa foi "
           "desestatizada em junho, com a Equatorial como investidora de referência. Terceiro, tecnologia e eficiência: a Copasa reduziu o índice de perdas em {{value:V.copasa.distribution_loss_reduction_pp}} "
           "em doze meses, e a Sabesp contratou {{value:V.sabesp.self_production_contracted_mwm}} de energia própria. Quem combinar regulação estável, capital "
           "barato e boa execução captura o ciclo. Michel, como isso entra na matriz ESG?"),
    "B5": ("Nossa matriz liga cinco fatores ESG ao caixa e não dá nota sintética, porque as empresas medem coisas diferentes. Em perdas, a Sanepar registra "
           "{{value:OBS_002597}}, a Copasa {{value:OBS_002594}} e a Sabesp {{value:OBS_002593}}; períodos e definições diferem, então não fazemos ranking. "
           "Perdas chegam ao caixa pelo custo de energia, químicos e manutenção. Em esgoto, a Sanepar atende {{value:OBS_002599}} da área urbana e trata "
           "{{value:OBS_002600}} do que coleta; a Copasa tem {{value:OBS_002596}} de cobertura. Aqui o canal é o investimento remunerado. Em resiliência, olhamos "
           "energia e continuidade do serviço. Em acesso, a tarifa social reduziu a receita da Sabesp em {{value:V.sabesp.social_tariff_mix_effect.2025}} pelo "
           "efeito mix, e a evasão de receita da Sanepar é de {{value:OBS_002601}}. Em governança, a pergunta é quem fica com o ganho: na Sanepar, o passivo do "
           "precatório era {{value:V.sanepar.regulatory_liability.2026-06-30}} em junho. A matriz não é uma coleção de selos: cada linha diz por onde o ESG "
           "mexe no caixa."),
    "B6": ("Quantificamos o elo mais importante: quanto vale cada real investido em expansão. Se o regulador remunera esse investimento acima do custo de capital, "
           "ele cria valor; abaixo, destrói. Ao nosso custo de capital de {{value:A.wacc_nominal.base}}, cada real investido vale "
           "{{value:V.copasa.rab_value_ratio.base}} na Copasa, {{value:V.sanepar.rab_value_ratio.base}} na Sanepar e {{value:V.sabesp.rab_value_ratio.base}} "
           "na Sabesp. Isso entra direto no valuation. Também testamos uma alavanca operacional: reduzir em {{value:A.energy_saving.base}} a conta de energia "
           "da água da Sanepar justificaria investir até {{value:V.case.sanepar.energy.r50.capex_break_even}} ou {{value:V.case.sanepar.energy.r100.capex_break_even}}, "
           "conforme a parte do ganho que fica com a empresa. É uma sensibilidade, não uma economia já realizada, e por isso não a somamos ao caso-base."),
    "B7.a": ("Como chegamos ao valor? Projetamos o fluxo de caixa livre das três empresas até 2035, com o investimento entrando na base remunerada depois de "
             "{{value:A.recognition_lag.base}}, e descontamos a {{value:A.wacc_nominal.base}}, um custo de capital construído a partir da NTN-B de "
             "{{value:V.macro.ntnb_2035_real.2026-10-30}} real. Do valor da firma, tiramos a dívida estimada para outubro, os outros compromissos e, na Sanepar, "
             "o precatório inteiro a valor presente: {{value:V.sanepar.obligation_pv.base}}. O que sobra é do acionista."),
    "B7.b": ("O resultado: a {{entity:decision}} vale {{value:V.case.sanepar.base.paper_value}} por unit contra {{value:V.SAPR11.close.2026-10-30}} no mercado. "
             "Sabesp e Copasa ficam abaixo do preço: {{value:V.case.sabesp.base.paper_value}} contra {{value:V.SBSP3.close.2026-10-30}}, e "
             "{{value:V.case.copasa.base.paper_value}} contra {{value:V.CSMG3.close.2026-10-30}}. Outro jeito de ver: o preço da Sanepar embute um custo de capital "
             "de {{value:V.sanepar.implied_wacc.2026-10-30}}, bem acima do nosso. E ela fica acima do preço em todas as combinações de custo de capital e "
             "crescimento que testamos. Navarro, o que pode dar errado?"),
    "B8": ("Testamos quatro cenários. No base, a Sanepar vale {{value:V.case.sanepar.base.paper_value}}. Com juros mais altos, cai para "
           "{{value:V.case.sanepar.rates_up.paper_value}}, perto do preço. Com pior execução e regulação, vai a {{value:V.case.sanepar.execution_adverse.paper_value}}: "
           "esse é o risco real da tese. No favorável, chega a {{value:V.case.sanepar.favorable.paper_value}}. Por isso definimos três gatilhos. Regulação: se o "
           "reajuste de 2027 também ficar abaixo da inflação, refazemos a conta e saímos se o valor cair abaixo do preço. Execução: investimento desviando mais de "
           "dez por cento do plano por dois trimestres; a primeira leitura é o resultado de 12 de novembro. Juros: NTN-B acima de {{value:V.trigger.ntnb_threshold}} "
           "elimina o potencial e suspende as compras."),
    "B9": ("Rodrigo: Nossa proposta é {{entity:decision}}, compra condicionada abaixo de {{value:V.sanepar.max_entry_price}}. "
           "Lorenzo: O setor precisa investir, e o investimento só vale quando é bem remunerado. "
           "Michel: ESG entra no valor pela base remunerada, não por selo. "
           "Navarro: E revisamos a tese quando regulação, execução ou juros mudam. "
           "Todos: Esse é o nosso processo de investimento."),
}
BLOCK_VOICE = {"B1": "Rodrigo", "B2": "Lorenzo", "B3": "Lorenzo", "B4": "Navarro", "B5": "Michel", "B6": "Michel", "B7.a": "Rodrigo",
               "B7.b": "Rodrigo", "B8": "Navarro", "B9": "Todos"}
BLOCK_SECONDS = {"B1": 50, "B2": 50, "B3": 75, "B4": 60, "B5": 90, "B6": 65, "B7.a": 40, "B7.b": 45, "B8": 60, "B9": 25}
BLOCK_CLAIMS = {p["block"]: p["claims"] for p in PAGES}

# ------------------------------------------------------------------------------------------------
QUESTIONS = [
    ("Por que a Sanepar, se ela é controlada pelo Estado e o regulador acabou de tirar o precatório dela?",
     "Porque o nosso valor já deduz o precatório inteiro, a valor presente ({{value:V.sanepar.obligation_pv.base|precise}}), e ainda assim fica em "
     "{{value:V.case.sanepar.base.paper_value}} contra {{value:V.SAPR11.close.2026-10-30}}. O risco estadual existe: no cenário adverso o valor cai para "
     "{{value:V.case.sanepar.execution_adverse.paper_value}}. Por isso a compra é condicionada e tem gatilhos."),
    ("Por que vocês não recomendam a Sabesp, que é privatizada e eficiente?",
     "Gostamos da execução, mas o preço já embute muito: no caso-base ela vale {{value:V.case.sabesp.base.paper_value}} contra {{value:V.SBSP3.close.2026-10-30}}, "
     "e só alcança o preço no cenário favorável ({{value:V.case.sabesp.favorable.paper_value}}). O preço embute um custo de capital de "
     "{{value:V.sabesp.implied_wacc.2026-10-30}}."),
    ("E a Copasa, que teve um WACC regulatório maior?",
     "É a única em que cada real investido cria valor ({{value:V.copasa.rab_value_ratio.base}} por R$ 1), mas o preço de {{value:V.CSMG3.close.2026-10-30}} "
     "supera até o caso favorável ({{value:V.case.copasa.favorable.paper_value}}). O mercado parece precificar ganhos do novo controlador após a desestatização de junho, que não modelamos."),
    ("Como o ESG entra no valuation, e não só no discurso?",
     "Pela base remunerada: o investimento em água e esgoto vira tarifa. Ao custo de capital de {{value:A.wacc_nominal.base}}, R$ 1 investido vale "
     "{{value:V.sanepar.rab_value_ratio.base}} na Sanepar. A energia entra como sensibilidade separada, não somada ao caso-base."),
    ("De onde vem o custo de capital de vocês?",
     "De um CAPM local: NTN-B 2035 a {{value:V.macro.ntnb_2035_real.2026-10-30}} real, beta {{value:A.beta.base|plain}} e prêmio {{value:A.erp.base}}, com "
     "{{value:A.leverage.base}} de dívida. Dá {{value:A.wacc_nominal.base}} nominal. Não é o WACC regulatório nem a TIR das planilhas."),
    ("Vocês não estão contando o precatório duas vezes?",
     "Não. O caixa recebido em 2025 está na dívida líquida; a obrigação entra uma única vez, pelo valor presente dos descontos e investimentos; a receita de "
     "2025 ficou fora do EBITDA recorrente. Como o saldo é corrigido perto do custo de capital, o valor presente fica próximo do saldo atualizado."),
    ("O que acontece se os juros subirem?",
     "Com custo de capital de {{value:V.case.sanepar.rates_up.wacc}}, a Sanepar vale {{value:V.case.sanepar.rates_up.paper_value}}, perto do preço. Acima de "
     "{{value:V.trigger.ntnb_threshold}} na NTN-B o potencial some e suspendemos as compras."),
    ("A base de remuneração de vocês é a oficial?",
     "Usamos a base implícita no lucro operacional recorrente de 2025 e a conferimos com a base oficial da Sanepar na terceira revisão tarifária. "
     "A implícita difere em {{value:V.sanepar.implied_vs_official_brr}} da oficial atualizada ({{value:V.sanepar.brr_official_net.2024_at_2025_prices}}): "
     "o motor fica do lado conservador. A base oficial ainda está em fiscalização pela Agepar; a de Sabesp e Copasa não foi obtida em fonte primária."),
    ("O WACC regulatório da Sabesp pode mudar?",
     "No primeiro ciclo, não: o contrato fixa {{value:V.sabesp.wacc_reg_real_after_tax}} real após impostos até 2029. Testamos "
     "{{value:A.sabesp_wacc_reg.adverse}} e {{value:A.sabesp_wacc_reg.favorable}} para a revisão seguinte, e a conclusão sobre a Sabesp não muda: "
     "ela só alcança o preço no cenário favorável."),
    ("Qual é a melhor objeção à tese?",
     "Que o desconto da Sanepar seja armadilha: controle estadual, regulador intervindo e cada real investido valendo {{value:V.sanepar.rab_value_ratio.base}}. "
     "Nossa resposta é que isso já está no caso-base; o caso adverso mostra o que invalidaria a tese, e os gatilhos dizem quando sair."),
    ("Como vocês sabem que o modelo está certo?",
     "Reproduzimos as planilhas originais, conciliamos 64 células históricas com as demonstrações da CVM, recalculamos a planilha num segundo software e "
     "testamos o código. Isso garante a conta; as premissas continuam sendo julgamento, e por isso mostramos cenários."),
    ("O que faria vocês mudarem de ideia amanhã?",
     "Qualquer um dos três gatilhos: reajuste de 2027 abaixo da inflação, execução do investimento desviando mais de dez por cento, ou NTN-B acima de "
     "{{value:V.trigger.ntnb_threshold}}. E o preço: acima de {{value:V.sanepar.max_entry_price}} não compramos."),
]

GUIDE = """# Guia de gravação

Perfil escolhido pelo grupo: **pptx9** (9 slides, PDF) ou **html10** (10 páginas, HTML interativo). Gravar com o mesmo perfil do roteiro usado no ensaio.

1. Abrir o HTML (`outputs/draft/html/apresentacao_esg.html`) e ativar o **modo gravação** (tecla `G`), que reserva a área da câmera à direita, ou usar o PDF do perfil pptx9.
2. Cada integrante grava os seus blocos do `script_apresentacao.md` como clipes separados (MP4 com áudio), salvos em `data/raw/gravacao/` com o nome do manifesto do perfil (`config/video_segments.json` ou `config/video_segments_html10.json`).
3. Fale olhando para a câmera; o teleprompter individual está em `teleprompter/<nome>.md`. Não leia as notas de fonte: elas não são fala.
4. Depois dos dois ensaios cronometrados (registrar em `data/interim/feedback_ensaio.md`), regravar os blocos que estourarem o tempo. Não acelerar o áudio.
5. A montagem (`python -m production.run --stage video`) só roda com todos os clipes reais; o arquivo final exige revisão integral do grupo antes do envio (H13).
"""
