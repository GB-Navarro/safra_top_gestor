"""Generate review documents and analysis ledgers from computed outputs."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path

import pandas as pd

from common import ROOT, acquisitions, now, read_csv, read_json, sha256, sync_sources, write_csv, write_json


def text(path, value):
    target=ROOT/path
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(value,encoding="utf-8")


def br(x, places=2):
    return f"{x:,.{places}f}".replace(",","_").replace(".",",").replace("_",".")


def register_local():
    for directory in ["resources/modelos_originais","resources/documentos_financeiros"]:
        for path in (ROOT/directory).rglob("*"):
            if path.suffix not in (".xlsx",".pdf"):
                continue
            digest=sha256(path)
            key="local_"+digest[:12]
            write_json(f"data/interim/acquisitions/{key}.json",dict(key=key,status="downloaded",source_id=key,local_path=path.relative_to(ROOT).as_posix(),sha256=digest,bytes=path.stat().st_size,url="",retrieved_at=now(),published_at="",issuer=path.parent.name,title=path.name,access_method="local_original_read_this_execution",note="Read timestamp is not original acquisition/publication date"))
    sync_sources()


def make_assumptions():
    models=read_json("data/interim/original_models.json")
    rows=[]
    drivers={17:"volume_growth",18:"inflation",19:"real_tariff_gain",20:"ebitda_margin",21:"da_ratio",22:"capex_ratio",23:"working_capital_ratio"}
    for name,model in models.items():
        if name=="TIR_Sabesp.xlsx":continue
        source="local_"+model["sha256"][:12]
        for row,driver in drivers.items():
            for year,col in zip(range(2026,2036),"CDEFGHIJKL"):
                value=model["cells"]["Premissas"][f"{col}{row}"]["cached"]
                rows.append(dict(assumption_id=f"LEGACY_{model['entity_id']}_{driver}_{year}",entity_id=model["entity_id"],driver=driver,year=year,base=value,adverse="",favorable="",unit="ratio",rationale="Original proposed trajectory; not an observed fact. Scenario preserves it to identify terminal/accounting effects.",supporting_obs_ids="",owner="agente",reviewer="grupo_H08",approval_status="proposed_not_human_reviewed",source_id=source,source_location=f"Premissas!{col}{row}"))
        for driver,value,rationale in [("common_wacc",.125,"Common nominal after-tax WACC assumption; sensitivity 10.5-14.5%, not a measured CAPM"),("terminal_g",.035,"Long-run nominal growth aligned with final Focus year, not a 2035 consensus"),("terminal_roic",.125,"No perpetual excess-return assumption; not observed company ROIC"),("tax",.34,"Illustrative normalized rate; fiscal regimes and tax shields need review")]:
            rows.append(dict(assumption_id=f"COMMON_{model['entity_id']}_{driver}",entity_id=model["entity_id"],driver=driver,year="terminal_or_common",base=value,adverse="",favorable="",unit="ratio",rationale=rationale,supporting_obs_ids="",owner="agente",reviewer="grupo_H08",approval_status="proposed_not_human_reviewed",source_id="",source_location="config/analysis outputs; model.py"))
    for driver,value,why in [("energy_expense_reduction",.01,"Sensitivity, no project or achieved saving assumed"),("energy_gain_retention_low",.5,"Regulatory retention sensitivity; not a contractual estimate"),("energy_gain_retention_high",1,"Upper retention case for this horizon; no terminal savings")]:
        rows.append(dict(assumption_id="ESG_"+driver,entity_id="all",driver=driver,year="2027-2035",base=value,adverse="",favorable="",unit="ratio",rationale=why,supporting_obs_ids="",owner="agente",reviewer="grupo_H08",approval_status="proposed_not_human_reviewed",source_id="",source_location="model.py energy sensitivity"))
    write_csv("data/processed/assumptions.csv",rows)


def build_outputs():
    register_local();make_assumptions()
    valuations=read_json("data/processed/valuation.json")
    bridges=read_json("data/processed/esg_bridge.json")
    sources={r["key"]:r for r in acquisitions() if r["status"]=="downloaded"}
    matrix=[
        dict(factor="Eficiência hídrica",sabesp="262 L/lig.dia; IPGR 2024",copasa="233,6 L/lig.dia; LTM jun/26",sanepar="216,28 L/lig.dia; LTM jun/26",channel="Energia, água e capex; métricas/datas não permitem ranking automático",source_ids=[sources[k]["source_id"] for k in ["sabesp_sustentabilidade_2024","doc_csmg_2t26","doc_sapr_2t26"]]),
        dict(factor="Esgoto e expansão",sabesp="Universalização URAE-1 em 2029; plano e execução",copasa="Cobertura 80,1%; controladora+Patos, jun/26",sanepar="IARCE urbano 82,9%; 100% do coletado tratado",channel="Receita e capex; cobertura ≠ tratamento; população/área distintas",source_ids=[sources[k]["source_id"] for k in ["doc_sbsp_2t26","doc_csmg_2t26","doc_sapr_2t26"]]),
        dict(factor="Resiliência e eficiência",sabesp="Energia água 2024: R$ 1.239,4 mi",copasa="Energia água 2024: R$ 552,2 mi",sanepar="Energia água 2024: R$ 460,7 mi",channel="Custos e disponibilidade; porte/geografia impedem ranking pelo gasto absoluto",source_ids=[sources["sinisa_agua_planilhas"]["source_id"]]),
        dict(factor="Acesso e capacidade de pagar",sabesp="Metas, subsídios e elegibilidade social: perímetro próprio",copasa="Tarifa social e inadimplência: definições próprias",sanepar="Evasão 1,89% em jun/26; tarifa social compensada",channel="Arrecadação e equilíbrio tarifário; não presumir subsídio como perda integral",source_ids=[sources[k]["source_id"] for k in ["doc_sbsp_2t26","doc_csmg_2t26","doc_sapr_2t26"]]),
        dict(factor="Governança e regulação",sabesp="Controle privado; metas e remuneração contratual",copasa="RTP 2026-29; reconhecimento anual de investimentos",sanepar="Precatório: saldo regulatório R$ 4.407,957 mi",channel="Quem retém o ganho? Obrigações, reconhecimento e execução alteram o valor",source_ids=[sources[k]["source_id"] for k in ["doc_sbsp_2t26","doc_csmg_2t26","doc_sapr_itr"]])]
    write_json("data/processed/esg_matrix.json",matrix)
    public_rule=dict(source_url="https://www.safra.com.br/data/files/76/64/7B/85/0ABCE910FDA2D4E9E3ADF9C2/Regulamento_Safra_Top_Gestor_2026.pdf",access_method="web.run cached official PDF; original HTTP download returned 403",verified_at=now(),document="Regulamento Safra Top Gestor 2026, junho/2026",confirmed={"sectorial_video_minutes_max":10,"all_active_members":True,"content":["SWOT setorial","médio prazo: tecnologia, competição e participantes","empresa e justificativa de investimento","matriz ESG ligada à avaliação"],"sectorial_weight_qualification":.25,"sectorial_submission_date":"2026-11-02","finalists_standard":5,"finalists_discretionary_max":10},locations={"content":"p9, itens 3.3.1–3.3.2","weight_finalists":"p10, item 3.4.2","deadline":"p12, cronograma"},remaining="Orientações recebidas em 16/10/live de 20/10: horário, canal, formato e alterações pontuais não fornecidos")
    write_json("data/raw/orientacoes/regulamento_2026_verificado_via_web.json",public_rule)
    # Claims link the presentation's observed facts to actual observation IDs.
    observed=read_csv("data/processed/observations.csv")
    claims=[]
    for item in matrix:
        claims.append(dict(claim_id=f"MATRIX_{len(claims)+1}",text=item["factor"]+": "+item["channel"],claim_type="analytical_inference",source_ids=";".join(item["source_ids"]),obs_ids=";".join(r["obs_id"] for r in observed if r["source_id"] in item["source_ids"] and r["metric_id"] in ["loss_per_connection_day","sewer_coverage","regulatory_liability_current","regulatory_liability_noncurrent"]),calculation_id="",slide_id="S5",script_block="B5",status="documented_scope_qualified",caveat="No synthetic ESG score; definitions/periods differ"))
    write_csv("data/processed/claims.csv",claims)
    adjustments=[]
    for entity,row in valuations.items():
        adjustments.append(dict(adjustment_id="BOOK_EXTRA_"+entity,entity_id=entity,reference_date="2026-06-30",adjustment_type="additional_book_obligations_diagnostic",amount=row["obligations_identified_book"],unit="BRL",scale=1000000,economic_treatment="Diagnostic 0-to-full book deduction only; actual PV and cash-flow overlap not resolved",source_ids=sources["cvm_itr_2026"]["source_id"],source_location="CVM BPP codes explicitly selected in model.py",review_status="book_amount_verified_economic_treatment_pending",double_counting_check="UNRESOLVED; do not treat as definitive equity adjustment"))
    write_csv("data/processed/adjustments.csv",adjustments)
    # Do not turn a negative residual into a negative share price.
    lines=[]
    for entity,row in valuations.items():
        label="resíduo negativo; sem preço-alvo" if row["common_base"]["equity_floor_applied"] else "R$ "+br(row["unadjusted_paper_value"])
        lines.append(f"| {row['ticker']} | R$ {br(row['price_reference'])} | {label} | {br(row['common_base']['net_debt'],1)} |")
    decision="# Proposta para discussão — Sanepar sob condições\n\n"
    decision+="Selecionar Sanepar/SAPR11 como candidata de investimento condicionada a preço, obrigações e execução; não há suporte, nesta configuração, para compra incondicional a mercado. O preço público de referência é R$ 30,85 em 30/10/2026, sujeito à conferência de H01. A escolha final do grupo é H09.\n\n"
    decision+="A operação divulga 82,9% de atendimento urbano de esgoto, 100% do coletado tratado e 216,28 L/ligação/dia no LTM de junho. Esses dados têm definições próprias e não provam causalidade de controle ou superioridade universal. O argumento econômico é que a ação precisa remunerar execução e risco regulatório: caixa associado a obrigação não é caixa livre.\n\n"
    decision+="| Papel | Preço público | Configuração experimental comum | Dívida líquida jun/26, R$ mi |\n|---|---:|---|---:|\n"+"\n".join(lines)+"\n\n"
    decision+="Os resultados acima NÃO são preços-alvo aprovados. Usam WACC nominal de 12,5%, g de 3,5%, ROIC terminal igual ao WACC, inflação Focus e trajetórias operacionais herdadas. A normalização de reinvestimento afeta especialmente a Copasa; resíduo negativo é um diagnóstico do modelo, não preço negativo da ação nem conclusão de insolvência. A ligação de capex a receita regulatória precisa ser discutida antes de usar o modelo como recomendação final.\n\n"
    sane=valuations["sanepar"]
    decision+=f"Na Sanepar, a configuração comum sem dedução incremental dessas obrigações gera R$ {br(sane['unadjusted_paper_value'])}/unit; deduzir integralmente o saldo nominal identificado gera R$ {br(sane['diagnostic_full_deduction_paper_value'])}/unit. Esse intervalo é DIAGNÓSTICO: a ponta inferior pode duplicar capex/tarifas já projetados; a superior não prova ausência de custo. O passivo de R$ 4.407,957 milhões é contábil, não PV automaticamente. A faixa não é intervalo estatístico.\n\n"
    decision+="A preferência condicional se apoia na menor distância relativa entre preço e configuração experimental, não em rating ESG ou TIR da firma. Não transformar essa comparação em ranking definitivo enquanto as bases operacionais, o capital e a regulação estiverem sob revisão. Sabesp oferece execução contratual acelerada; Copasa tem reconhecimento anual de investimentos. Ambos precisam de projeções que remunerem corretamente seu capex.\n\n"
    decision+="## H08 — cinco decisões propostas\n\n1. WACC comum de 12,5%: confrontar prêmio/estrutura de capital e faixa 10,5–14,5%.\n2. Margens, tarifas e capex: manter as trajetórias originais apenas como proposta, com reconhecimento regulatório explícito.\n3. Terminal: testar reinvestimento/ROIC e concessões; continuidade após o contrato é hipótese.\n4. Precatório, outorgas, PPP e derivativos: reconciliar pagamentos e evitar dupla contagem.\n5. Datas: dívida/caixa de junho são proxy; ponte até outubro e sazonalidade do stub permanecem hipóteses.\n\n"
    decision+="## Gatilhos propostos\n\n- Preço: margem de segurança de 20% sobre valor revisado é proposta do agente para revisão do grupo, sem aprovação registrada; recalcular depois de H08.\n- Execução: rever a tese se o capex/entregas divergir mais de 10% da trajetória adotada em dois períodos comparáveis; limite é regra proposta, não covenant.\n- Regulação: qualquer alteração que reduza a remuneração ou torne a obrigação economicamente maior que a faixa aceita exige nova avaliação.\n\nA melhor objeção: o aparente desconto pode ser apenas caixa comprometido, menor retorno regulatório e dependência do terminal. A resposta não é um selo ESG: é conciliar fluxos, testar as hipóteses e exigir preço compatível.\n"
    text("outputs/draft/decisao_proposta.md",decision)
    audit="# Auditoria dos modelos e limites da conclusão\n\n"
    checks=read_csv("outputs/qa/workbook_input_checks.csv")
    selected=[r for r in checks if r["workbook"]!="TIR_Sabesp.xlsx"]
    audit+=f"Foram comparadas {len(selected)} entradas de receita, LAIR e IR/CSLL dos três arquivos candidatos com a CVM: todas dentro de R$ 0,1 milhão, compatível com arredondamento. Isso não valida todas as outras entradas. Cinco divergências de sinal de imposto pertencem ao arquivo antigo TIR_Sabesp.xlsx, que também contém o erro de construção já identificado.\n\n"
    audit+="A reconstrução independente dos DCFs reproduziu os três caches originais com erro por ação inferior a 10⁻⁶. As planilhas já usam stub de 62/365 em 2026. O problema restante é a hipótese de rateio e a ponte de balanço, não ausência do mecanismo. XTIR usa firma/FCFF, não retorno acionário.\n\n"
    audit+="## Correções e ressalvas\n\n- Cotações originais são de 29/10 ou intradiárias; o pacote usa referências públicas de 30/10 com fonte e confirmação recomendada.\n- Sabesp: o capital líquido de junho difere da extrapolação simples da DFP 2025; há minoritários e balanço mais recente.\n- Copasa: o CSV de capital traz valores em milhares neste emissor; foi usada a unidade expressa no release, sem inferir escala pela magnitude.\n- Sanepar: contas individuais, enquanto as outras duas são consolidadas; a ausência de NCI se refere a esse perímetro. Units não somam capital e o adicional de dividendos PN não determina sozinho preço justo.\n- Sanepar: plano 2026–30 é R$ 13.077 milhões, incluindo R$ 212,8 milhões de doações de redes e parcerias/capitalizações. Total anunciado não é capex caixa automaticamente.\n- Derivativos/PPP/outorgas e precatório exigem ajuste compatível com os fluxos; a dedução integral nominal é diagnóstico, não tratamento aprovado.\n- ROIC terminal, WACC, impostos e trajetórias são premissas propostas. Resíduo de patrimônio negativo não é preço negativo nem prova de insolvência.\n- O custo de energia SINISA é soma municipal do serviço de água em 2024, não despesa consolidada e nem custo marginal de perdas.\n- Não foram feitas médias simples de indicadores municipais ou comparações de perdas de faturamento com perdas físicas.\n\n"
    audit+="## Ponte ESG calculada\n\nSensibilidade: redução hipotética de 1% da despesa de energia da água entre 2027–35, custo 2024 atualizado por IPCA/Focus, imposto de 34%, WACC 12,5%, sem ganho terminal. O teto de investimento é condicionado a horizonte, evitabilidade e retenção. Não somar à margem-base sem reconciliação.\n\n| Empresa | Custo água 2024, R$ mi | Capex equilíbrio com 50% de retenção | Com 100% |\n|---|---:|---:|---:|\n"
    audit+="\n".join(f"| {r['entity_id']} | {br(r['base_energy_expense'],1)} | {br(r['capex_break_even_50pct_retention'],1)} | {br(r['capex_break_even_upper'],1)} |" for r in bridges)+"\n\nO cálculo é uma sensibilidade, não economia realizada, projeto identificado ou recomendação de investir esse montante.\n"
    text("outputs/draft/auditoria_modelos.md",audit)
    rules="# Regras verificadas da etapa 2026\n\n"
    rules+="O regulamento oficial de junho/2026 foi lido pela ferramenta web. Confirma vídeo de até 10 minutos com os membros ativos, SWOT setorial, médio prazo/tecnologia/competição, empresa recomendada e matriz ESG ligada ao valor. A análise pesa 25% na classificação; a seleção padrão é de cinco equipes, com possibilidade discricionária de até dez. O cronograma fixa envio em 02/11/2026. Localização: páginas 9, 10 e 12.\n\n"
    rules+="Fonte: "+public_rule["source_url"]+"\n\nO download HTTP permaneceu 403; o JSON ao lado registra verificação via web, não os bytes do PDF original. Ainda faltam as orientações complementares do grupo para horário, canal, formato e eventuais alterações.\n"
    text("outputs/draft/regras_2026_verificadas.md",rules)
    pins=[]
    for name in ["requests","pandas","openpyxl","pypdf","numpy","scipy","matplotlib","python-pptx","PyMuPDF","Pillow","beautifulsoup4","XlsxWriter","imageio-ffmpeg"]:
        pins.append(name+"=="+importlib.metadata.version(name))
    text("requirements.txt","\n".join(pins)+"\n")
    from sync_project_docs import sync
    sync()
    print("Review documents, assumptions and ESG matrix generated; documentation synchronized")


if __name__=="__main__":
    build_outputs()
