"""Conteúdo editorial da apresentação final (plano 14): 12 slides, falas, perguntas e guia.

Base: o PPT reorganizado pelo grupo, com a narrativa revisada e o texto no estilo das cartas ao
investidor. Regras: nenhum número digitado à mão (valores entram por {{value:ID}}); o modelo de
alocação só aparece no slide 2; nada de setas, símbolos ou títulos de efeito.
"""
from __future__ import annotations

P = "V.SAPR11.close.2026-10-30"
SB, CS, SP = "sabesp", "copasa", "sanepar"

# ------------------------------------------------------------------------------------------------
# Páginas: id, falante, tempo planejado (s), slot do contrato e afirmações que a página sustenta.
PAGES = [
    dict(id="S01", block="S01", voice="Rodrigo", seconds=14, slot="lead", kind="cover",
         kicker="Desafio Safra Top Gestor 2026 · Análise setorial ESG",
         title="Saneamento: onde está o valor do setor listado",
         subtitle="Na 2ª carta, o modelo de alocação pôs Sabesp na carteira. Fomos ao setor entender onde está o valor.",
         claims=[]),
    dict(id="S02", block="S02", voice="Rodrigo", seconds=40, slot="lead", kind="origin",
         kicker="Ponto de partida · 2ª carta ao investidor",
         title="Na 2ª carta, o modelo comprou Sabesp sem uma tese nossa sobre a empresa",
         subtitle="O Black-Litterman parte do carrego de cada ativo e soma as nossas opiniões, que estavam no petróleo e no real mais fraco.",
         claims=["CL.lead.origin"]),
    dict(id="S03", block="S03", voice="Rodrigo", seconds=28, slot="lead", kind="question",
         kicker="A pergunta",
         title="Fomos ao setor com um olhar fundamentalista",
         subtitle="Fizemos com as três empresas listadas o caminho completo: setor, riscos, indicadores ESG ligados ao caixa e valor contra preço.",
         claims=[]),
    dict(id="S04", block="S04", voice="Lorenzo", seconds=50, slot="sector", kind="sector",
         kicker="01 · O setor no Brasil",
         title="{{value:OBS_002589}} da população tem coleta de esgoto; a meta é {{value:V.sector.target_sewer_2033}} até 2033",
         subtitle="Fechar a diferença exige investimento. O retorno do acionista depende de a tarifa remunerar esse capital.",
         claims=["CL.sector.coverage", "CL.sector.targets", "CL.sector.treatment_gap"]),
    dict(id="S05", block="S05", voice="Lorenzo", seconds=65, slot="swot", kind="swot",
         kicker="02 · SWOT do setor",
         title="Demanda estável e contratos longos; o risco está na regulação e nos juros",
         subtitle="O serviço é essencial. O retorno depende de quanto o regulador remunera o investimento e de quanto custa o capital.",
         claims=["CL.swot.strength", "CL.swot.weakness", "CL.swot.opportunity", "CL.swot.threat"]),
    dict(id="S06", block="S06", voice="Navarro", seconds=55, slot="medium_term", kind="medium",
         kicker="03 · Médio prazo",
         title="Até 2030, regulação, competição e tecnologia decidem quem ganha",
         subtitle="A regulação define quanto rende cada real investido; competição e tecnologia definem quem executa melhor.",
         claims=["CL.mt.regulation", "CL.mt.competition", "CL.mt.technology"]),
    dict(id="S07", block="S07", voice="Michel", seconds=70, slot="esg", kind="matrix",
         kicker="04 · Matriz ESG",
         title="Cada indicador ESG chega ao caixa por um caminho diferente",
         subtitle="Não damos nota única: as empresas medem coisas diferentes, em períodos diferentes.",
         claims=["CL.esg.matrix", "CL.esg.losses", "CL.esg.sewer", "CL.esg.governance"]),
    dict(id="S08", block="S08", voice="Michel", seconds=40, slot="bridge", kind="esg_value",
         kicker="05 · Do ESG ao valor",
         title="Medimos uma alavanca: {{value:A.energy_saving.base}} a menos na conta de energia",
         subtitle="O indicador mexe num custo, numa receita ou num investimento; o regulador decide quanto fica com a empresa.",
         claims=["CL.bridge.energy"]),
    dict(id="S09", block="S09", voice="Rodrigo", seconds=55, slot="valuation_method", kind="calc",
         kicker="06 · Cálculo fundamentalista",
         title="Do caixa da empresa ao valor do acionista",
         subtitle="Projetamos o fluxo de caixa livre até 2035. O investimento só vira receita quando entra na base que a tarifa remunera.",
         claims=["CL.bridge.rab", "CL.method.fcff", "CL.method.recurring", "CL.method.precatorio"]),
    dict(id="S10", block="S10", voice="Rodrigo", seconds=45, slot="valuation_result", kind="tir",
         kicker="06 · Cálculo fundamentalista: a TIR",
         title="Ao preço de 30/10, só a Sanepar rende acima do nosso custo de capital",
         subtitle="TIR da firma: quanto rende comprar a empresa inteira pelo preço de mercado, com a dívida, e receber o caixa livre que ela gera.",
         claims=["CL.result.implied"]),
    dict(id="S11", block="S11", voice="Rodrigo", seconds=50, slot="valuation_result", kind="value_price",
         kicker="07 · Valor contra preço",
         title="A Sanepar vale {{value:V.case.sanepar.base.paper_value}} por unit; o mercado paga {{value:V.SAPR11.close.2026-10-30}}",
         subtitle="Valor por ação no caso-base, com o precatório inteiro já descontado, contra o fechamento de 30/10/2026, já depois da semana do segundo turno.",
         claims=["CL.result.values", "CL.result.market_view", "CL.lead.price", "CL.result.election_week"]),
    dict(id="S12", block="S12", voice="Navarro", seconds=58, slot="conclusion", kind="conclusion",
         kicker="08 · Conclusão",
         title="Compramos Sanepar até {{value:V.sanepar.max_entry_price}} por unit; Sabesp e Copasa já estão no preço",
         subtitle="Margem de segurança de {{value:A.margin_of_safety.base}} sobre o valor do caso-base e três gatilhos de revisão.",
         claims=["CL.conclusion.decision", "CL.lead.decision", "CL.lead.thesis", "CL.risk.scenarios", "CL.risk.trigger.regulation",
                 "CL.risk.trigger.execution", "CL.risk.trigger.rates", "CL.risk.objection"]),
]

# ------------------------------------------------------------------------------------------------
# Textos de tela por página (tokens resolvidos pelo consumidor).
SCREEN = {
    "S01": dict(team="Lorenzo · Michel · Navarro · Rodrigo", tickers="SBSP3 · SAPR11 · CSMG3"),
    "S02": dict(
        chart_title="Ações na carteira da 2ª carta, em % do patrimônio",
        stocks=[("petrobras", "Petrobras", "view"), ("vale", "Vale", "view"), ("weg", "WEG", "view"), ("suzano", "Suzano", "view"),
                ("bradesco", "Bradesco", "model"), ("sabesp", "Sabesp", "model")],
        legend={"view": "Tese nossa", "model": "Escolha do modelo"},
        stat_value="V.carta2.weight.sabesp",
        stat_text="do patrimônio em Sabesp, a única empresa de saneamento da carteira",
        reason_label="Motivo registrado na carta",
        steps=[("Nossas teses", "Petrobras pelo petróleo; Vale, WEG e Suzano pelo real mais fraco."),
               ("O que o modelo fez", "Acrescentou Bradesco e Sabesp pelo prêmio de risco."),
               ("Nossa reação", "Peso escolhido pelo modelo não é tese. Fomos estudar o setor.")]),
    "S03": dict(
        steps=[("Setor", "Déficit de cobertura, metas de 2033 e as três empresas listadas"),
               ("Riscos", "SWOT e as forças de médio prazo: regulação, competição e tecnologia"),
               ("ESG", "Cada indicador ligado a uma linha do caixa"),
               ("Valor", "Fluxo de caixa das três empresas contra o preço de 30/10/2026")],
        questions_label="Perguntas que guiaram o trabalho",
        questions=["Existe valor no saneamento listado ao preço de hoje?", "A Sabesp é a melhor forma de investir no setor?"]),
    "S04": dict(
        chart_title="Brasil, ano-base 2024, contra as metas de 2033 (% da população)",
        bars=[("Água (rede)", "OBS_002588", "V.sector.target_water_2033"),
              ("Esgoto (coleta)", "OBS_002589", "V.sector.target_sewer_2033"),
              ("Esgoto tratado", "OBS_002590", "V.sector.target_sewer_2033")],
        legend=("Brasil 2024", "Meta 2033"),
        note="Esgoto tratado é a parcela do esgoto gerado que recebe tratamento; a meta de 2033 vale para coleta e tratamento.",
        companies_label="As três empresas listadas que comparamos",
        companies=[dict(entity=SB, ticker="SBSP3", line1="São Paulo · controle privado",
                        line2="Contrato até {{value:V.sabesp.concession_end_year}} · EBITDA recorrente 2025 de {{value:V.sabesp.ebitda_recurring.2025}}"),
                   dict(entity=SP, ticker="SAPR11", line1="Paraná · controle estadual · unit com 1 ON e 4 PN",
                        line2="Concessões até {{value:V.sanepar.concession_end_year}} · EBITDA recorrente 2025 de {{value:V.sanepar.ebitda_recurring.2025}}"),
                   dict(entity=CS, ticker="CSMG3", line1="Minas Gerais · desestatizada em junho de 2026",
                        line2="Equatorial com {{value:V.copasa.reference_investor_share}} · EBITDA recorrente 2025 de {{value:V.copasa.ebitda_recurring.2025}}")]),
    "S05": dict(quadrants=[
        dict(id="S", label="Forças", bullets=["Serviço essencial, com demanda estável",
                                              "Contratos longos: Sabesp até {{value:V.sabesp.concession_end_year}}, Sanepar até {{value:V.sanepar.concession_end_year}}"],
             effect="Fluxo de caixa previsível, desde que a regulação seja estável."),
        dict(id="W", label="Fraquezas", bullets=["O país perde {{value:OBS_002592}} da água distribuída",
                                                 "Capital intensivo: a Sabesp desembolsou {{value:V.sabesp.capex_cash.2025}} em 2025"],
             effect="O retorno depende de o investimento entrar na tarifa."),
        dict(id="O", label="Oportunidades", bullets=["Expansão do esgoto até as metas de 2033", "Eficiência em perdas, energia e medição"],
             effect="Cria valor onde a remuneração supera o custo de capital, como na Copasa: {{value:V.copasa.rab_value_ratio.base}} por real investido."),
        dict(id="T", label="Ameaças", bullets=["Juros reais altos: NTN-B 2035 a {{value:V.macro.ntnb_2035_real.2026-10-30}}",
                                               "A Agepar destinou todo o precatório da Sanepar aos usuários e deu reajuste de {{value:V.sanepar.tariff_adjustment.2026}} em 2026, com IPCA de {{value:V.macro.ipca_actual.2025}} em 2025"],
             effect="É o principal risco da tese."),
    ]),
    "S06": dict(cards=[
        dict(label="Regulação", big="V.copasa.wacc_reg_real_after_tax", big_label="WACC regulatório real da Copasa na 3ª revisão tarifária",
             text="WACC regulatório é o retorno que o regulador reconhece sobre o capital investido. A Sanepar remunera a {{value:V.sanepar.wacc_reg_real_after_tax}} e a Sabesp a {{value:V.sabesp.wacc_reg_real_after_tax}}, fixo no contrato até 2029.",
             effect="Acima do custo de capital, crescer cria valor; abaixo, destrói."),
        dict(label="Competição", big="V.sector.aegea_para_capex", big_label="investimento mínimo previsto pela Aegea no Pará, em 99 municípios",
             text="A Copasa foi desestatizada em junho de 2026, com a Equatorial como investidora de referência ({{value:V.copasa.reference_investor_share}} do capital).",
             effect="Ganha concessões quem capta mais barato e executa melhor."),
        dict(label="Tecnologia", big="V.copasa.distribution_loss_reduction_pp", big_label="a menos de perdas na distribuição da Copasa em 12 meses",
             text="A Sabesp contratou {{value:V.sabesp.self_production_contracted_mwm}} de autoprodução de energia.",
             effect="Reduz custo de energia, químicos e água perdida; quanto do ganho fica com a empresa depende do contrato."),
    ]),
    "S07": dict(columns=["Fator", "Como chega ao caixa", "Sanepar", "Sabesp", "Copasa"],
                factor_labels={"ESG.water_efficiency": ("E", "Perdas de água"), "ESG.sewer_expansion": ("E", "Esgoto e expansão"),
                               "ESG.resilience": ("E", "Resiliência e energia"), "ESG.access": ("S", "Acesso e tarifa social"),
                               "ESG.governance": ("G", "Governança e regulação")},
                channels={"ESG.water_efficiency": "Energia, químicos e capex de redução de perdas",
                          "ESG.sewer_expansion": "Investimento que entra na base remunerada pela tarifa",
                          "ESG.resilience": "Custo de operação e continuidade do serviço",
                          "ESG.access": "Arrecadação e equilíbrio da tarifa",
                          "ESG.governance": "Quem fica com o ganho: remuneração e obrigações"},
                cells={"ESG.water_efficiency": {"sanepar": ("{{value:OBS_002597}}", "12 meses até jun/26"),
                                                "sabesp": ("{{value:OBS_002593}}", "2024"),
                                                "copasa": ("{{value:OBS_002594}}", "12 meses até jun/26")},
                       "ESG.sewer_expansion": {"sanepar": ("{{value:OBS_002599}} de atendimento urbano", "todo o esgoto coletado é tratado"),
                                               "sabesp": ("{{value:V.sabesp.capex_cash.2025}} investidos em 2025", "universalização até 2029"),
                                               "copasa": ("{{value:OBS_002596}} de cobertura", "jun/26")},
                       "ESG.resilience": {"sanepar": ("{{value:V.sanepar.water_energy_expense_sinisa.2024}} em energia", "serviço de água, 2024"),
                                          "sabesp": ("{{value:V.sabesp.water_energy_expense_sinisa.2024}} em energia", "{{value:V.sabesp.self_production_contracted_mwm}} de autoprodução contratada"),
                                          "copasa": ("{{value:V.copasa.water_energy_expense_sinisa.2024}} em energia", "serviço de água, 2024")},
                       "ESG.access": {"sanepar": ("{{value:OBS_002601}} de evasão de receitas", "jun/26"),
                                      "sabesp": ("{{value:V.sabesp.social_tariff_mix_effect.2025}} na receita", "efeito da tarifa social em 2025"),
                                      "copasa": ("Sem indicador comparável", "não divulgado no mesmo formato")},
                       "ESG.governance": {"sanepar": ("Controle estadual", "WACC regulatório de {{value:V.sanepar.wacc_reg_real_after_tax}}"),
                                          "sabesp": ("Controle privado", "WACC regulatório de {{value:V.sabesp.wacc_reg_real_after_tax}}, fixo até 2029"),
                                          "copasa": ("Desestatizada em 2026", "WACC regulatório de {{value:V.copasa.wacc_reg_real_after_tax}}")}},
                note="Perdas em litros por ligação por dia. Definições, perímetros e períodos diferem; a matriz não ordena as empresas."),
    "S08": dict(chain=[("Indicador ESG", "perdas, esgoto, energia, acesso, governança"),
                       ("Linha do caixa", "custo evitado, receita regulada, investimento"),
                       ("Tarifa e base remunerada", "quanto o regulador reconhece e remunera"),
                       ("Valor do acionista", "fluxo descontado ao custo de capital")],
                chart_title="Quanto {{value:A.energy_saving.base}} a menos de energia permite investir sem perder valor (R$ milhões)",
                legend=("Empresa fica com metade do ganho", "Empresa fica com todo o ganho"),
                note="Sensibilidade com a despesa de energia da água (SINISA 2024). Não é economia realizada e não entra no caso-base."),
    "S09": dict(r1_title="Quanto vale R$ 1 investido em expansão",
                r1_sub="remunerado pela tarifa e descontado ao nosso custo de capital de {{value:A.wacc_nominal.base}}",
                r1_note="Acima de R$ 1, crescer cria valor; abaixo, destrói. O cálculo já desconta isso: expansão não é valor automático.",
                bridge_title="Sanepar: do valor da firma ao do acionista (R$ bilhões)",
                bridge_labels={"start": "Valor da firma", "net_debt_october_estimate": "Dívida líquida", "debt_like": "PPP, pensões e outros",
                               "grantor_net": "Poder concedente", "obligation_pv": "Precatório", "end": "Patrimônio"},
                bridge_note="Dívida de 30/06/2026 levada a 30/10 pelo caixa projetado; precatório a valor presente.",
                params=[("A.wacc_nominal.base", "WACC, o custo médio do capital: CAPM local com NTN-B de {{value:V.macro.ntnb_2035_real.2026-10-30}} real"),
                        ("A.recognition_lag.base", "até o investimento entrar na base remunerada"),
                        ("A.rab_real_growth_after_plan.base", "de crescimento real da base no longo prazo")]),
    "S10": dict(steps=[("Pagamos o preço de hoje", "valor de mercado mais dívida líquida"),
                       ("Recebemos o caixa livre", "de 2026 a 2035, mais o valor terminal"),
                       ("A TIR é a taxa que iguala os dois", "acima do custo de capital, o preço está barato")],
                chart_title="TIR da firma ao preço de 30/10/2026",
                wacc_label="Nosso custo de capital",
                esg_label="Como o ESG entrou na conta",
                esg=[("E", "Expansão do esgoto", "O investimento só vira caixa quando entra na base remunerada, {{value:A.recognition_lag.base}} depois."),
                     ("G", "Regulação", "Cada contrato com seu WACC regulatório: {{value:V.sabesp.wacc_reg_real_after_tax}} na Sabesp, {{value:V.sanepar.wacc_reg_real_after_tax}} na Sanepar e {{value:V.copasa.wacc_reg_real_after_tax}} na Copasa."),
                     ("G", "Precatório", "{{value:V.sanepar.obligation_pv.base}} a valor presente saem do valor da Sanepar: o dinheiro é dos usuários."),
                     ("S", "Acesso e energia", "Perda de arrecadação entra no cenário adverso, como custo de {{value:A.opex_shock.adverse}} da receita; eficiência energética fica fora do caso-base.")]),
    "S11": dict(chart_title="Valor no caso-base contra o preço de 30/10/2026 (R$ por ação ou unit)",
                legend=("Valor no caso-base", "Preço em 30/10/2026"),
                upside_label="Diferença entre valor e preço",
                week_label="Semana do segundo turno: fechamento de 23/10 e de 30/10",
                week_tickers=["SAPR11", "SBSP3", "CSMG3"],
                week_note="NTN-B 2035 de {{value:V.macro.ntnb_2035_real.2026-10-23}} para {{value:V.macro.ntnb_2035_real.2026-10-30}}; o caso-base já usa a taxa de 30/10.",
                grid_note="Testamos custo de capital de {{grid_w_lo}} a {{grid_w_hi}} e crescimento real de {{grid_g_lo}} a {{grid_g_hi}}. No pior ponto, a Sanepar vale {{grid_min}}, ainda acima do preço."),
    "S12": dict(ruler_title="SAPR11 por unit (R$): preço, limite de compra e cenários",
                labels=dict(price="Preço", limit="Limite", value="Valor-base", buy="faixa de compra",
                            adverse="Adverso", rates="Juros mais altos", favorable="Favorável"),
                triggers_title="Gatilhos de revisão",
                triggers=[("Regulação", "Reajuste de maio de 2027 de novo abaixo do IPCA, ou WACC regulatório abaixo de {{value:V.sanepar.wacc_reg_real_after_tax}}"),
                          ("Execução", "Investimento desviando mais de 10% do plano por dois trimestres; primeira leitura no ITR de 12/11"),
                          ("Juros", "NTN-B 2035 acima de {{value:V.trigger.ntnb_threshold}} (hoje {{value:V.macro.ntnb_2035_real.2026-10-30}}): suspendemos as compras")],
                closing=[(SB, "Sabesp", "A que mais investe entre as três ({{value:V.sabesp.capex_cash.2025}} em 2025), mas o preço de {{value:V.SBSP3.close.2026-10-30}} só é alcançado no cenário favorável ({{value:V.case.sabesp.favorable.paper_value}})."),
                         (CS, "Copasa", "A única em que R$ 1 investido vale mais de R$ 1, mas o preço de {{value:V.CSMG3.close.2026-10-30}} supera até o cenário favorável ({{value:V.case.copasa.favorable.paper_value}})."),
                         (SP, "Sanepar", "O desconto se abriu na semana do segundo turno, e os juros de 30/10 já estão no caso-base. O valor fica acima do preço em toda a grade testada.")]),
}

# ------------------------------------------------------------------------------------------------
# Falas por slide (cerca de 140 palavras por minuto). Escritas para serem ditas em voz alta.
SPEECH = {
    "S01": ("Somos a asset.dev: Lorenzo, Michel, Navarro e eu, Rodrigo. Esta é a nossa análise do saneamento listado, e ela começou "
            "dentro da nossa própria carteira."),
    "S02": ("Na segunda carta, a carteira tinha seis ações. Quatro vinham das nossas teses: Petrobras, pelo petróleo, e Vale, WEG e Suzano, pelo real "
            "mais fraco, com {{value:V.carta2.weight.petrobras}} cada. As outras duas foram escolha do modelo de alocação, pelo prêmio de risco: Bradesco, "
            "com {{value:V.carta2.weight.bradesco}}, e Sabesp, com {{value:V.carta2.weight.sabesp}} do patrimônio. Nenhuma análise nossa pedia Sabesp. "
            "Um peso escolhido pelo modelo não é tese, e foi isso que nos levou a estudar o setor."),
    "S03": ("Fizemos o caminho que faríamos com qualquer empresa: entender o setor, olhar os riscos de médio prazo, ligar os indicadores ESG ao caixa e "
            "calcular o valor das três companhias listadas contra o preço de mercado. Duas perguntas guiaram o trabalho: existe valor no saneamento "
            "listado ao preço de hoje? E a Sabesp é a melhor forma de investir no setor? Lorenzo começa pelo setor."),
    "S04": ("O ponto de partida é o déficit. No ano-base de 2024, {{value:OBS_002588}} da população tinha rede de água e {{value:OBS_002589}} tinha coleta "
            "de esgoto. O Marco Legal pede {{value:V.sector.target_water_2033}} e {{value:V.sector.target_sewer_2033}} até 2033. E coletar não basta: do "
            "esgoto gerado, só {{value:OBS_002590}} recebe tratamento. O setor vai investir; a questão para o acionista é se a tarifa vai remunerar esse "
            "investimento acima do custo do capital. Comparamos as três empresas listadas: a Sabesp, em São Paulo, privatizada; a Sanepar, no Paraná, "
            "controlada pelo estado; e a Copasa, em Minas Gerais, desestatizada em junho."),
    "S05": ("Na SWOT, a força é a previsibilidade: o serviço é essencial e os contratos são longos, o da Sabesp até {{value:V.sabesp.concession_end_year}} "
            "e os da Sanepar até {{value:V.sanepar.concession_end_year}}. A fraqueza é a intensidade de capital: o país perde {{value:OBS_002592}} da água "
            "distribuída, e só a Sabesp desembolsou {{value:V.sabesp.capex_cash.2025}} em 2025. A oportunidade é expandir o esgoto e ganhar eficiência, "
            "mas isso só cria valor quando a remuneração supera o custo de capital. A ameaça vem de dois lados. Os juros reais estão altos, com a NTN-B a "
            "{{value:V.macro.ntnb_2035_real.2026-10-30}}. E o regulador pode intervir: no Paraná, a Agepar destinou aos usuários todo o precatório que a "
            "Sanepar recebeu da União e deu reajuste de {{value:V.sanepar.tariff_adjustment.2026}} em 2026, abaixo da inflação de "
            "{{value:V.macro.ipca_actual.2025}} do ano anterior. A demanda está garantida; o risco está na regulação e nos juros. Navarro, o que muda até 2030?"),
    "S06": ("Vemos três forças. A primeira é a regulação. O WACC regulatório é o retorno que o regulador reconhece sobre o capital investido: a Copasa "
            "passou a {{value:V.copasa.wacc_reg_real_after_tax}} na revisão de 2026, a Sanepar está em {{value:V.sanepar.wacc_reg_real_after_tax}} e a "
            "Sabesp em {{value:V.sabesp.wacc_reg_real_after_tax}}, fixo até 2029. A segunda é a competição por concessões e por capital: a Aegea venceu "
            "o Pará prevendo mais de {{value:V.sector.aegea_para_capex}} em investimentos, e a Copasa foi desestatizada em junho, com a Equatorial como investidora de "
            "referência. A terceira é a tecnologia: a Copasa reduziu as perdas em {{value:V.copasa.distribution_loss_reduction_pp}} em doze meses, e a "
            "Sabesp contratou {{value:V.sabesp.self_production_contracted_mwm}} de autoprodução de energia. Michel, como isso aparece nos indicadores ESG?"),
    "S07": ("Ligamos cinco fatores ESG ao caixa, sem dar nota única, porque as empresas medem coisas diferentes. Em perdas, a Sanepar registra "
            "{{value:OBS_002597}}, a Copasa {{value:OBS_002594}} e a Sabesp {{value:OBS_002593}}; os períodos diferem, então não ordenamos as três. "
            "Perda de água vira custo de energia, químicos e manutenção. Em esgoto, a Sanepar atende {{value:OBS_002599}} da área urbana e trata todo o "
            "esgoto que coleta; a Copasa tem {{value:OBS_002596}} de cobertura. Aqui o caminho até o caixa é o investimento remunerado. Em acesso, o "
            "efeito da tarifa social na receita da Sabesp foi de {{value:V.sabesp.social_tariff_mix_effect.2025}} em 2025, e a evasão de receita da Sanepar é de "
            "{{value:OBS_002601}}. Em governança, a pergunta é quem fica com o ganho: na Sanepar, o passivo do precatório era de "
            "{{value:V.sanepar.regulatory_liability.2026-06-30}} em junho."),
    "S08": ("A matriz diz por onde o ESG chega ao caixa; agora, quanto. Testamos uma alavanca concreta: reduzir em {{value:A.energy_saving.base}} a "
            "conta de energia da água. Na Sanepar, isso permite investir até {{value:V.case.sanepar.energy.r50.capex_break_even}} sem perder valor, se a "
            "empresa ficar com metade do ganho, ou {{value:V.case.sanepar.energy.r100.capex_break_even}}, se ficar com tudo. É uma sensibilidade, não uma "
            "economia já feita, e por isso não entra no caso-base."),
    "S09": ("O elo central é quanto vale cada real investido em expansão. Se o regulador remunera esse investimento acima do custo de capital, crescer "
            "cria valor; abaixo, destrói. Ao nosso custo de capital de {{value:A.wacc_nominal.base}}, cada real vale {{value:V.copasa.rab_value_ratio.base}} "
            "na Copasa, {{value:V.sanepar.rab_value_ratio.base}} na Sanepar e {{value:V.sabesp.rab_value_ratio.base}} na Sabesp. Projetamos o caixa livre "
            "das três até 2035, com o investimento entrando na base remunerada depois de {{value:A.recognition_lag.base}}. Do valor da firma, tiramos a "
            "dívida, os outros compromissos e, na Sanepar, o precatório inteiro, de {{value:V.sanepar.obligation_pv.base}} a valor presente. O que sobra "
            "é do acionista."),
    "S10": ("Antes de comparar valor e preço, uma pergunta simples: se comprássemos a empresa inteira hoje, pagando o valor de mercado e assumindo a "
            "dívida, quanto ela renderia por ano? Essa é a TIR da firma. Ao preço de 30 de outubro, a Sanepar rende "
            "{{value:V.sanepar.implied_wacc.2026-10-30}}, acima do nosso custo de capital de {{value:A.wacc_nominal.base}}. A Sabesp rende "
            "{{value:V.sabesp.implied_wacc.2026-10-30}} e a Copasa {{value:V.copasa.implied_wacc.2026-10-30}}, abaixo dele."),
    "S11": ("O resultado: a Sanepar vale {{value:V.case.sanepar.base.paper_value}} por unit, contra {{value:V.SAPR11.close.2026-10-30}} no mercado. "
            "A Sabesp vale {{value:V.case.sabesp.base.paper_value}} contra {{value:V.SBSP3.close.2026-10-30}}, e a Copasa "
            "{{value:V.case.copasa.base.paper_value}} contra {{value:V.CSMG3.close.2026-10-30}}. Um cuidado com a data: em 23 de outubro, último pregão "
            "antes do segundo turno, a Sanepar fechou a {{value:V.SAPR11.close.2026-10-23}}, perto do nosso valor. Na semana da eleição, as três caíram "
            "juntas, e a NTN-B foi de {{value:V.macro.ntnb_2035_real.2026-10-23}} para {{value:V.macro.ntnb_2035_real.2026-10-30}}. Nosso custo de capital "
            "já usa a taxa nova, e ainda assim a Sanepar fica acima do preço em todos os pontos que testamos. Navarro, o que pode dar errado?"),
    "S12": ("Testamos cenários. No base, a Sanepar vale {{value:V.case.sanepar.base.paper_value}}. Com o custo de capital em "
            "{{value:V.case.sanepar.rates_up.wacc}}, cai para {{value:V.case.sanepar.rates_up.paper_value}}, perto do preço, como a TIR de "
            "{{value:V.sanepar.implied_wacc.2026-10-30}} já indicava. Com pior execução e regulação, vai a "
            "{{value:V.case.sanepar.execution_adverse.paper_value}}: esse é o risco da tese. Por isso compramos só até "
            "{{value:V.sanepar.max_entry_price}} e revisamos se um de três gatilhos disparar: reajuste de 2027 de novo abaixo da inflação, investimento "
            "desviando mais de 10% do plano, ou NTN-B acima de {{value:V.trigger.ntnb_threshold}}. Respondendo às duas perguntas: existe valor no setor, e "
            "ele está na Sanepar. A Sabesp, que nos trouxe até aqui, é uma boa empresa, mas o preço já paga mais do que o nosso caso-base. Se estivermos "
            "errados, os gatilhos dizem onde."),
}
BLOCK_VOICE = {p["block"]: p["voice"] for p in PAGES}
BLOCK_SECONDS = {p["block"]: p["seconds"] for p in PAGES}
BLOCK_CLAIMS = {p["block"]: p["claims"] for p in PAGES}

# ------------------------------------------------------------------------------------------------
QUESTIONS = [
    ("Por que a Sanepar, se ela é controlada pelo estado e o regulador acabou de destinar o precatório aos usuários?",
     "Porque o nosso valor já desconta o precatório inteiro, a valor presente ({{value:V.sanepar.obligation_pv.base|precise}}), e ainda assim fica em "
     "{{value:V.case.sanepar.base.paper_value}} contra {{value:V.SAPR11.close.2026-10-30}}. O risco estadual existe: no cenário adverso o valor cai para "
     "{{value:V.case.sanepar.execution_adverse.paper_value}}. Por isso compramos com preço-limite e gatilhos."),
    ("Por que não a Sabesp, que é privatizada e investe mais que todas?",
     "Porque o preço já paga mais do que o nosso caso-base: ela vale {{value:V.case.sabesp.base.paper_value}} contra {{value:V.SBSP3.close.2026-10-30}} "
     "e só alcança o preço no cenário favorável ({{value:V.case.sabesp.favorable.paper_value}}). Ao preço de hoje, a TIR da firma é "
     "{{value:V.sabesp.implied_wacc.2026-10-30}}, abaixo do nosso custo de capital."),
    ("E a Copasa, que teve o WACC regulatório elevado?",
     "É a única em que cada real investido vale mais de um real ({{value:V.copasa.rab_value_ratio.base}}), mas o preço de "
     "{{value:V.CSMG3.close.2026-10-30}} supera até o cenário favorável ({{value:V.case.copasa.favorable.paper_value}}). O mercado parece pagar por "
     "ganhos do novo controlador, depois da desestatização de junho, que não incluímos."),
    ("Como o ESG entra no valuation, e não só no discurso?",
     "Pela base remunerada: o investimento em água e esgoto vira tarifa. Ao custo de capital de {{value:A.wacc_nominal.base}}, R$ 1 investido vale "
     "{{value:V.sanepar.rab_value_ratio.base}} na Sanepar. A energia entra como sensibilidade separada, fora do caso-base."),
    ("De onde vem o custo de capital de vocês?",
     "De um CAPM local: NTN-B 2035 a {{value:V.macro.ntnb_2035_real.2026-10-30}} real, beta de {{value:A.beta.base|plain}} e prêmio de "
     "{{value:A.erp.base}}, com {{value:A.leverage.base}} de dívida. Dá {{value:A.wacc_nominal.base}} nominal. Não é o WACC regulatório."),
    ("Vocês não estão contando o precatório duas vezes?",
     "Não. O dinheiro recebido em 2025 está na dívida líquida; a obrigação entra uma única vez, pelo valor presente dos descontos e dos investimentos; "
     "e a receita de 2025 ficou fora do EBITDA recorrente."),
    ("O que acontece se os juros subirem?",
     "Com custo de capital de {{value:V.case.sanepar.rates_up.wacc}}, a Sanepar vale {{value:V.case.sanepar.rates_up.paper_value}}, perto do preço. Acima "
     "de {{value:V.trigger.ntnb_threshold}} na NTN-B, o potencial some e suspendemos as compras."),
    ("A base remunerada de vocês é a oficial?",
     "Usamos a base implícita no lucro operacional recorrente de 2025 e a conferimos com a base oficial da Sanepar na 3ª revisão tarifária. A nossa "
     "difere em {{value:V.sanepar.implied_vs_official_brr}} da oficial atualizada ({{value:V.sanepar.brr_official_net.2024_at_2025_prices}}): ficamos do "
     "lado conservador. Na nota técnica da revisão, a base oficial estava em fiscalização pela Agepar."),
    ("O WACC regulatório da Sabesp pode mudar?",
     "Até 2029, não: o contrato fixa {{value:V.sabesp.wacc_reg_real_after_tax}} real após impostos. Testamos {{value:A.sabesp_wacc_reg.adverse}} e "
     "{{value:A.sabesp_wacc_reg.favorable}} para a revisão seguinte, e a conclusão sobre a Sabesp não muda."),
    ("Os preços de 30/10 não estão distorcidos pela eleição?",
     "Estão depois do choque, e de propósito: preço e juros são do mesmo dia. Em 23/10, último pregão antes do segundo turno, a Sanepar fechou a "
     "{{value:V.SAPR11.close.2026-10-23}}; em 30/10, a {{value:V.SAPR11.close.2026-10-30}}. A NTN-B 2035 subiu de {{value:V.macro.ntnb_2035_real.2026-10-23}} "
     "para {{value:V.macro.ntnb_2035_real.2026-10-30}}, e o nosso custo de capital já usa a taxa nova. Se os juros cederem, o valor sobe; se passarem de "
     "{{value:V.trigger.ntnb_threshold}}, suspendemos as compras."),
    ("Qual é a melhor objeção à tese?",
     "Que o desconto da Sanepar seja uma armadilha: controle estadual, regulador intervindo e cada real investido valendo "
     "{{value:V.sanepar.rab_value_ratio.base}}. Isso já está no caso-base; o cenário adverso mostra o que invalidaria a tese, e os gatilhos dizem quando sair."),
    ("Como vocês sabem que a conta está certa?",
     "Conciliamos 64 células históricas com as demonstrações da CVM, recalculamos a planilha num segundo software e testamos o código. Isso garante a "
     "conta; as premissas continuam sendo julgamento, e por isso mostramos cenários."),
    ("O que faria vocês mudarem de ideia amanhã?",
     "Qualquer um dos três gatilhos: reajuste de 2027 abaixo da inflação, investimento desviando mais de 10% do plano, ou NTN-B acima de "
     "{{value:V.trigger.ntnb_threshold}}. E o preço: acima de {{value:V.sanepar.max_entry_price}}, não compramos."),
]

GUIDE = """# Guia de gravação

A apresentação final tem 12 slides, em três formatos com o mesmo conteúdo: HTML (`outputs/draft/html/apresentacao_esg.html`), PDF e PPTX.

1. Abra o HTML no navegador em tela cheia (F11). Avance com a seta para a direita, a barra de espaço ou um clique; volte com a seta para a esquerda. Os slides não têm botões nem elementos clicáveis.
2. Se for gravar a câmera por cima da tela, a tecla `G` reduz o slide e libera o canto direito para a imagem da câmera; `Esc` volta ao normal.
3. Cada integrante grava a fala dos seus slides em `script_apresentacao.md`, olhando para a câmera. O teleprompter individual está em `teleprompter/<nome>.md`. As fontes no rodapé dos slides não são fala.
4. Clipes separados vão para `data/raw/gravacao/` com os nomes de `config/video_segments.json`. A montagem só roda com todos os clipes reais.
5. Depois de dois ensaios cronometrados (registrar em `data/interim/feedback_ensaio.md`), regrave o que passar do tempo. Não acelere o áudio.
"""
