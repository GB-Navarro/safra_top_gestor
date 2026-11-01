"""Editable slides, figures and spoken scripts generated from one data snapshot."""
from __future__ import annotations

import json
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

from common import ROOT, read_csv, read_json, write_csv, write_json
from analysis_outputs import br, text

OUT=ROOT/"outputs/draft"
FIG=OUT/"figuras"
NAVY="09283D"; TEAL="007F82"; BLUE="3267A0"; GREY="506273"; LIGHT="EDF4F6"


def figure(name, fig, rows):
    FIG.mkdir(parents=True,exist_ok=True)
    fig.savefig(FIG/f"{name}.png",dpi=180,bbox_inches="tight",facecolor="white")
    fig.savefig(FIG/f"{name}.svg",bbox_inches="tight",facecolor="white")
    plt.close(fig)
    write_csv(f"outputs/draft/figuras/{name}.csv",rows)


def charts():
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":13,"axes.spines.top":False,"axes.spines.right":False})
    vals=read_json("data/processed/valuation.json")
    bridge=read_json("data/processed/esg_bridge.json")
    f,ax=plt.subplots(figsize=(10,3.7))
    national=read_json('data/processed/presentation_facts.json')['national']
    coverage=[100*national['water'],100*national['sewer']]
    y=np.arange(2)
    ax.barh(y,coverage,color=["#3267A0","#007F82"],height=.42)
    for i,v,target in zip(y,coverage,[99,90]):
        ax.text(v+1,i,f"{v:.1f}%".replace(".",","),va="center",fontsize=17,fontweight="bold")
        ax.plot([target,target],[i-.32,i+.32],color="#09283D",lw=2)
        ax.text(target,i+.44,f"Meta {target}%",ha="center",fontsize=11)
    ax.set_yticks(y,["Água: população com rede","Esgoto: população com coleta"])
    ax.set_xlim(0,110);ax.set_ylim(-.65,1.65);ax.invert_yaxis()
    ax.set_xlabel("Brasil, ano-base 2024 • % da população total")
    ax.grid(axis="x",alpha=.15);ax.set_axisbelow(True)
    f.tight_layout()
    figure("s02_cobertura",f,[{"service":"agua","coverage":coverage[0],"target":99},{"service":"coleta_esgoto","coverage":coverage[1],"target":90}])
    f,ax=plt.subplots(figsize=(10,3.8))
    names=[r["entity_id"].capitalize() for r in bridge];low=[r["capex_break_even_50pct_retention"] for r in bridge];high=[r["capex_break_even_upper"] for r in bridge]
    x=np.arange(3)
    ax.bar(x-.18,low,.32,label="Retenção de 50%",color="#3267A0")
    ax.bar(x+.18,high,.32,label="Retenção de 100%",color="#007F82")
    for xx,v in list(zip(x-.18,low))+list(zip(x+.18,high)):ax.text(xx,v+.8,br(v,1),ha="center",fontsize=13)
    ax.set_xticks(x,names);ax.set_ylabel("R$ milhões • teto de investimento inicial")
    ax.set_ylim(0,max(high)*1.26);ax.legend(frameon=False,ncol=2,loc="upper right",fontsize=11)
    ax.grid(axis="y",alpha=.15);ax.set_axisbelow(True);f.tight_layout()
    figure("s06_energia",f,[{"entity_id":r["entity_id"],"retention_50pct":r["capex_break_even_50pct_retention"],"retention_100pct":r["capex_break_even_upper"]} for r in bridge])
    f,ax=plt.subplots(figsize=(10,3.8));rows=[]
    for i,(entity,r) in enumerate(vals.items()):
        original=r["legacy"]["average_share_value"]
        if entity=="sanepar":
            from model import allocate_sanepar
            original=allocate_sanepar(r["legacy"]["equity_value"])["SAPR11"]
        a=100*original/r["price_reference"]
        b=None if r["common_base"]["equity_floor_applied"] else 100*r["unadjusted_paper_value"]/r["price_reference"]
        ax.scatter(a,i-.1,color="#3267A0",s=110)
        ax.text(a+3,i-.1,br(a,0),va="center",fontsize=13)
        if b is not None:
            ax.scatter(b,i+.15,color="#007F82",s=110,marker="D");ax.text(b+3,i+.15,br(b,0),va="center",fontsize=13)
        else:ax.text(5,i+.2,"N/D: resíduo negativo",va="center",color="#506273",fontsize=12)
        rows.append(dict(entity_id=entity,ticker=r["ticker"],market_reference=r["price_reference"],legacy_percent_of_price=a,common_percent_of_price=b))
    ax.axvline(100,color="#09283D",ls="--",lw=1.8)
    ax.set_yticks(range(3),[r["ticker"] for r in vals.values()]);ax.invert_yaxis();ax.set_xlim(0,155)
    ax.set_xlabel("Preço público de referência = 100 • simulações condicionais")
    ax.scatter([],[],color="#3267A0",label="Original + rateio por classe")
    ax.scatter([],[],color="#007F82",marker="D",label="Configuração comum experimental")
    ax.legend(frameon=False,loc="upper right",fontsize=10);ax.grid(axis="x",alpha=.15);f.tight_layout()
    figure("s07_modelos",f,rows)
    r=vals["sanepar"];rows=r["scenarios"]
    f,ax=plt.subplots(figsize=(6.2,3.9))
    labels=["Base experimental","WACC +1,5 p.p.","Margem −2 p.p. / capex +10%","WACC −1 p.p. / margem +2 p.p."]
    v=[x["paper_value"] for x in rows]
    ax.barh(range(4),v,color=["#3267A0","#7D96AA","#9AB0BB","#007F82"],height=.5)
    for i,val in enumerate(v):ax.text(val+.4,i,br(val,1),va="center",fontsize=13)
    ax.axvline(r["price_reference"],ls="--",color="#09283D",lw=1.6)
    ax.set_yticks(range(4),labels,fontsize=10);ax.invert_yaxis();ax.set_xlim(0,max(v+[r["price_reference"]])*1.24)
    ax.set_xlabel("SAPR11 • R$/unit • cenários, não previsões")
    ax.grid(axis="x",alpha=.15);f.tight_layout()
    figure("s08_cenarios",f,rows)


def box(slide,x,y,w,h,fill=LIGHT):
    shape=slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid();shape.fill.fore_color.rgb=RGBColor.from_string(fill)
    shape.line.fill.background()
    return shape


def label(slide,value,x,y,w,h,size=20,color=NAVY,bold=False):
    tb=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=tb.text_frame;tf.word_wrap=True
    tf.margin_left=tf.margin_right=Inches(.03)
    tf.margin_top=tf.margin_bottom=Inches(.02)
    for i,line in enumerate(str(value).split("\n")):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.text=line;p.font.name="Arial";p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=RGBColor.from_string(color)
        p.space_after=Pt(6)
    return tb


def base(prs,title,index,source):
    s=prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid();s.background.fill.fore_color.rgb=RGBColor(255,255,255)
    box(s,0,0,13.333,.12,TEAL)
    label(s,"asset.dev  •  Saneamento e valor",.58,.28,9,.32,12,TEAL,True)
    label(s,title,.58,.79,12.0,.9,29,NAVY,True)
    label(s,"EM REVISÃO",11.55,.3,1.3,.35,11,GREY,True)
    box(s,11.35,1.85,1.42,.045,TEAL)
    label(s,f"{index:02}",11.42,2.05,1.2,.8,40,TEAL,True)
    # Deliberately leave bottom-right space empty for genuine camera overlay.
    label(s,source,.58,6.75,10.55,.54,12,GREY)
    return s


SCRIPTS = [
("B1","Rodrigo","0:00–0:50", "Selecionamos a Sanepar como candidata a uma tese de investimento condicionada a preço e regulação. O ponto central é simples: melhorar saneamento pode criar valor, mas o acionista só recebe a parcela que permanece na empresa depois de investimentos, impostos e regras tarifárias. Nossa comparação envolve Sabesp, Copasa e Sanepar. A referência pública de SAPR11 é trinta reais e oitenta e cinco centavos em trinta de outubro. Ela ainda deve ser conferida no Terminal. Nesta configuração de trabalho, a compra a mercado não está sustentada. Vamos mostrar o potencial operacional, o efeito financeiro de uma alavanca ESG e as condições que precisam sobreviver à revisão."),
("B2","Lorenzo","0:50–1:40", "A oportunidade setorial começa na diferença entre serviço disponível e serviço necessário. O SINISA, com ano-base dois mil e vinte e quatro, informa que oitenta e quatro vírgula um por cento da população brasileira tinha rede de água e sessenta e dois vírgula três por cento tinha rede coletora de esgoto. São medidas populacionais. Tratar todo o esgoto que já foi coletado é outro indicador e não significa que toda a população esteja atendida. As metas nacionais de noventa e nove por cento para água e noventa para esgoto orientam a expansão, mas cada contrato tem seu cronograma. Para o investidor, o desafio é financiar e executar essa expansão com remuneração adequada."),
("B3","Lorenzo","1:40–2:55", "Na SWOT, as forças do setor são a essencialidade do serviço e a possibilidade de planejar receitas e investimentos por contratos longos. Isso ajuda a organizar a operação, embora consumo, arrecadação e tarifa não sejam garantidos. As fraquezas são a necessidade elevada de capital, o retorno demorado e as perdas em redes que exigem manutenção. As oportunidades estão na expansão do esgoto e na eficiência: medição, redução de desperdício e melhor uso de energia podem aumentar a produtividade. Para gerar valor, porém, o benefício precisa superar o investimento necessário. Entre as ameaças, destacamos estiagem, energia cara, atraso de obras e mudanças regulatórias. Juros maiores pressionam tanto o financiamento quanto o valor presente. A conclusão da SWOT é que crescimento de investimento não basta. Precisamos avaliar quando o ativo entra em operação, quanto é reconhecido na tarifa e quem fica com o ganho. Essa lógica organiza nossa comparação das três empresas e evita tratar uma obrigação social como lucro automático."),
("B4","Navarro","2:55–3:55", "No médio prazo, observamos três frentes. A primeira é a regulação: a revisão tarifária da Copasa prevê reconhecimento anual de investimentos, o que torna o calendário de execução importante para a receita. A segunda é a competição por concessões e capital. A expansão da Aegea no Pará ilustra essa disputa, com investimentos anunciados ao longo de quarenta anos, e não num único exercício. Isso não significa várias redes concorrendo livremente na mesma rua. A terceira frente é a tecnologia. A Copasa documenta medição e combate a perdas; sua utilidade econômica depende de custo, resultado e retenção do ganho. Nossa leitura é que contrato, financiamento e operação precisam evoluir juntos. Anúncio de investimento e adoção de tecnologia, isoladamente, não comprovam criação de valor."),
("B5","Michel","3:55–5:25", "A matriz conecta cinco fatores a linhas de caixa. Em eficiência hídrica, mostramos perdas por ligação com suas datas e definições. A Sabesp divulga IPGR anual de dois mil e vinte e quatro; Copasa e Sanepar trazem indicadores de doze meses encerrados em junho. A unidade comum não elimina essas diferenças, por isso não criamos um ranking automático. Em esgoto, distinguimos cobertura de coleta e tratamento do coletado. Em resiliência, examinamos a exposição de custos e a continuidade do serviço. No acesso, tarifa social e inadimplência afetam arrecadação, mas subsídio pode ter compensação tarifária. Em governança e regulação, a pergunta é quem retém os benefícios. A Sanepar é o caso mais material: seu balanço de junho registra aproximadamente quatro bilhões e quatrocentos milhões de reais de passivo regulatório ligado ao precatório. Esse saldo contábil exige uma conciliação com descontos, investimentos e caixa. Somá-lo integralmente à dívida sem olhar os fluxos também pode duplicar custo. Assim, a matriz orienta o valuation, em vez de funcionar como uma coleção de selos ESG."),
("B6","Michel","5:25–6:30", "Quantificamos uma sensibilidade de eficiência energética, usando despesas municipais do serviço de água reportadas ao SINISA em dois mil e vinte e quatro. A hipótese é reduzir essa despesa em um por cento entre dois mil e vinte e sete e dois mil e trinta e cinco. Atualizamos a base por inflação, aplicamos os impostos e o desconto propostos e variamos a parcela retida pela empresa. Na Sanepar, o investimento inicial que zera o valor incremental fica aproximadamente entre dez e vinte milhões de reais nessas condições. Isso é um teto condicionado para um projeto hipotético, não economia realizada nem projeto identificado. O investimento efetivo e a regra de compartilhamento podem reduzir o valor. Também não adicionamos esse benefício ao DCF sem verificar se ele já está embutido na margem. A ponte explicita operação, caixa e valor."),
("B7","Rodrigo","6:30–7:55", "Reproduzimos os três DCFs existentes em um motor independente. Os resultados coincidiram numericamente, mas reproduzir fórmula não valida premissa. A TIR das planilhas parte do valor da firma e usa FCFF; ela não deve ser apresentada como retorno esperado da ação. Atualizamos referências de preço, capital e balanço e testamos uma configuração comum de custo de capital, inflação e reinvestimento terminal. Na Copasa, o patrimônio residual dessa configuração fica negativo: isso sinaliza uma limitação do caso modelado e não um preço negativo da ação ou insolvência comprovada. Na Sanepar, o resultado é muito sensível ao tratamento das obrigações regulatórias. Deduzir todo o saldo nominal é apenas um diagnóstico, pois pagamentos e investimentos podem já estar nos fluxos. Além disso, a dívida líquida publicada é de junho, e a continuidade após as concessões é hipótese. A preferência condicional pela Sanepar surge da comparação nesse conjunto de premissas, mas não representa uma compra robusta ao preço observado. Precisamos exigir que a conclusão sobreviva a essas reconciliações."),
("B8","Navarro","7:55–8:55", "Testamos quatro situações: base, juros maiores, pior execução e um ambiente favorável. Os números são valores condicionais do modelo, não previsões de preço nem perdas observadas. Mantemos três critérios de revisão. Primeiro, preço: uma margem de segurança de vinte por cento sobre o valor revisado é a regra proposta, depois de fechar as hipóteses. Segundo, execução: divergência persistente de investimento ou entregas em relação à trajetória precisa alterar a análise. O limite de dez por cento por dois períodos é uma proposta de disciplina, não um covenant. Terceiro, regulação: mudança na remuneração ou na obrigação aceita exige recalcular. O principal contra-argumento à tese é que o aparente desconto represente caixa comprometido e dependência do terminal. Nossa resposta é conciliar e testar, antes de assumir retorno."),
("B9","Todos","8:55–9:20", "Rodrigo: Nossa escolha é uma tese condicional na Sanepar. Lorenzo: A oportunidade está na expansão e na eficiência do saneamento. Michel: O ganho só cria valor quando supera seu custo e permanece com a empresa. Navarro: Exigimos preço compatível e revisamos a tese quando execução ou regulação mudam. Todos: Esse é o nosso processo de investimento.")
]


def build():
    values=read_json("data/processed/valuation.json");bridges=read_json("data/processed/esg_bridge.json")
    observed=read_csv('data/processed/observations.csv')
    national={}
    obs_ids={}
    for key,metric in [('water','national_water_coverage'),('sewer','national_sewer_coverage')]:
        found=[r for r in observed if r['metric_id']==metric]
        if len(found)!=1:raise ValueError('National presentation metric must be unique: '+metric)
        national[key]=float(found[0]['value']);obs_ids[key]=found[0]['obs_id']
    facts=dict(prices={e:r['price_reference'] for e,r in values.items()},energy_capex={r['entity_id']:dict(low=r['capex_break_even_50pct_retention'],high=r['capex_break_even_upper']) for r in bridges},national=national,national_observation_ids=obs_ids,status='review_draft')
    write_json('data/processed/presentation_facts.json',facts)
    charts();OUT.mkdir(parents=True,exist_ok=True)
    prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
    s=base(prs,"Sanepar: tese condicionada a preço e regulação",1,"Fontes: Sanepar ITR/release 2T26; mercado público 30/10/2026. Simulações e premissas propostas.")
    box(s,.62,1.95,10.3,1.3,NAVY);label(s,"ESG cria valor quando o ganho é retido",.86,2.17,9.8,.78,28,"FFFFFF",True)
    for y,title_,body in [(3.65,"Candidata: SAPR11","Referência pública: R$ 30,85 • 30/10/2026"),(4.55,"Condição econômica","Preço, execução e obrigações devem preservar margem de segurança"),(5.45,"Conclusão desta versão","Compra a mercado ainda sem sustentação nesta configuração")]:
        label(s,title_,.72,y,3.0,.55,19,TEAL,True);label(s,body,3.6,y,7.0,.72,19)
    s=base(prs,"A expansão exige capital e execução",2,"Fontes: SINISA 2025, Água p20 / Esgoto p20 (base 2024); Marco Legal. Metas contratuais podem diferir.")
    s.shapes.add_picture(str(FIG/'s02_cobertura.png'), Inches(.6), Inches(1.8),width=Inches(10.5))
    label(s,"Coleta, tratamento e cobertura têm denominadores distintos.",.9,6.0,9.8,.45,18,TEAL,True)
    s=base(prs,"SWOT: crescimento precisa remunerar o capital",3,"Fontes: SINISA, Marco Legal e relatórios das três empresas. Síntese analítica do grupo.")
    for x,y,title_,body in [(.65,1.9,"FORÇAS","Serviço essencial\nContratos de longo prazo"),(5.95,1.9,"FRAQUEZAS","Capex e retorno demorado\nPerdas e manutenção da rede"),(.65,4.05,"OPORTUNIDADES","Expansão do esgoto\nMedição e eficiência de energia"),(5.95,4.05,"AMEAÇAS","Juros, seca e energia\nExecução e mudança regulatória")]:
        box(s,x,y,4.98,1.85);label(s,title_,x+.16,y+.15,4.6,.42,17,TEAL,True);label(s,body,x+.16,y+.65,4.6,1.0,21)
    s=base(prs,"Três frentes alteram o retorno de médio prazo",4,"Fontes: Copasa release 2T26 p4/p24; Aegea, concessão Pará, 14/04/2025. Anúncio não é execução.")
    for x,title_,body in [( .65,"REGULAÇÃO","Copasa: reconhecimento\nanual de investimentos\n\nCalendário afeta o caixa"),(4.18,"COMPETIÇÃO","Aegea no Pará:\ncontratos e capital\n\n> R$ 15 bi em 40 anos"),(7.71,"TECNOLOGIA","Medição e combate\na perdas\n\nBenefício deve pagar\no investimento")]:
        box(s,x,2.0,3.3,3.95);label(s,title_,x+.15,2.2,3.0,.55,18,TEAL,True);label(s,body,x+.15,3.05,3.0,2.6,21)
    s=base(prs,"Matriz ESG: o indicador precisa chegar ao caixa",5,"Fontes: Sabesp Sust.2024 p173; releases Copasa/Sanepar 2T26; Sanepar ITR nota20. Datas e perímetros distintos.")
    table=s.shapes.add_table(6,5, Inches(.6), Inches(1.9), Inches(10.5), Inches(4.32)).table
    widths=[1.75,2.0,2.0,2.0,2.75]
    # Normalize to the actual table width; avoid right-edge overflow.
    widths=[w*10.5/sum(widths) for w in widths]
    for c,w in zip(table.columns,widths):c.width=Inches(w)
    data=[['Fator','Sabesp','Copasa','Sanepar','Canal financeiro'],['Eficiência\nhídrica','262 L/lig.dia\nIPGR 2024','233,6 L/lig.dia\nLTM jun/26','216,28 L/lig.dia\nLTM jun/26','Custos e capex;\nsem ranking automático'],['Esgoto e\nmetas','URAE-1:\nmeta em 2029','Cobertura 80,1%\njun/26¹','IARCE urbano\n82,9% jun/26','Receita, entrega e\nreconhecimento'],['Resiliência','Rede, energia\ne investimento','Rede, energia\ne investimento','Rede, energia\ne investimento','Continuidade do\nserviço e custo'],['Acesso','Metas e\nsubsídios','Tarifa social\ne arrecadação','Evasão 1,89%\njun/26','Quem paga e\nquem compensa?'],['Governança /\nregulação','Controle\nprivado','RTP\n2026–2029','Precatório:\nR$ 4,4 bi²','Retenção, obrigação\ne remuneração']]
    for i,row in enumerate(data):
        for j,val in enumerate(row):
            cell=table.cell(i,j);cell.text=val
            cell.margin_left=cell.margin_right=Inches(.06);cell.margin_top=Inches(.08);cell.margin_bottom=Inches(.03)
            cell.fill.solid();cell.fill.fore_color.rgb=RGBColor.from_string(NAVY if i==0 else LIGHT if i%2 else "FFFFFF")
            for p in cell.text_frame.paragraphs:p.font.name="Arial";p.font.size=Pt(14 if i else 15);p.font.color.rgb=RGBColor.from_string("FFFFFF" if i==0 else NAVY);p.font.bold=i==0
    label(s,"¹ Controladora + Patos. ² Saldo contábil; não é PV. Coleta ≠ tratamento do coletado.",.7,6.3,10.3,.35,11,GREY)
    s=base(prs,"Eficiência: qual investimento ainda cria valor?",6,"Fonte: SINISA GFI2004, água municipal 2024. Sensibilidade 2027–35: economia 1%, imposto 34%, WACC 12,5%; sem terminal.")
    s.shapes.add_picture(str(FIG/'s06_energia.png'), Inches(.62), Inches(1.85),width=Inches(10.45))
    label(s,"Teto condicionado: investimento efetivo, evitabilidade e retenção ainda precisam ser testados.",.75,6.02,10.2,.58,17,TEAL,True)
    s=base(prs,"O valor depende de reinvestimento e regulação",7,"Fontes: modelos originais, CVM, preços públicos 30/10. WACC 12,5%, g 3,5%, ROIC terminal 12,5% no caso comum. Não são alvos.")
    s.shapes.add_picture(str(FIG/'s07_modelos.png'), Inches(.62), Inches(1.85),width=Inches(10.45))
    label(s,"Copasa: N/D indica resíduo negativo do caso modelado, não preço negativo da ação.",.75,5.91,10.2,.46,16,GREY)
    label(s,"Sanepar: obrigações podem alterar a conclusão; evitar dupla contagem de caixa e capex.",.75,6.31,10.2,.35,15,TEAL,True)
    s=base(prs,"Riscos precisam mudar a decisão",8,"Fonte: motor FCFF; cenários propostos. Sem dedução incremental das obrigações nesta figura; dívida de junho é proxy.")
    s.shapes.add_picture(str(FIG/'s08_cenarios.png'), Inches(.55), Inches(1.95),width=Inches(6.35))
    label(s,"GATILHOS PROPOSTOS",7.2,2.0,3.75,.5,18,TEAL,True)
    label(s,"Preço\nMargem de segurança sobre o valor revisado",7.2,2.7,3.75,1.0,18)
    label(s,"Execução\nDesvio persistente de entregas / capex",7.2,3.9,3.75,1.0,18)
    label(s,"Regulação\nRemuneração ou obrigação fora da faixa aceita",7.2,5.1,3.75,1.1,18)
    s=base(prs,"Investir exige preço compatível com o risco",9,"Proposta para revisão do grupo. Hipóteses, obrigações e capital devem ser conciliados antes da versão definitiva.")
    label(s,"Sanepar • tese de investimento condicional",.8,2.05,10.2,.9,30,TEAL,True)
    for y,body in [(3.4,"Expansão e eficiência oferecem oportunidades"),(4.35,"Ganho cria valor quando supera custo e é retido"),(5.3,"Preço e gatilhos disciplinam a decisão")]:
        box(s,.8,y,.11,.6,TEAL);label(s,body,1.12,y,9.7,.7,24)
    # Notes carry exact text and evidence without cluttering the spoken slide.
    for slide,(block,speaker,timing,spoken) in zip(prs.slides,SCRIPTS):
        slide.notes_slide.notes_text_frame.text=f"{block} | {speaker} | {timing}\n\n{spoken}\n\nRessalvas e fontes completas no apoio técnico e auditoria_modelos.md."
    prs.save(OUT/'apresentacao_esg.pptx')
    write_scripts()
    build_support()
    from sync_project_docs import sync
    sync()
    print('Slides and scripts generated; documentation synchronized')


def write_scripts():
    script="# Script de apresentação — versão para ensaio\n\nFalas com premissas propostas; a duração depende do ensaio real. Marcadores de integrante no fechamento orientam a distribuição.\n\n"
    narrative="# Roteiro narrativo\n\nProblema setorial → diferenças materiais → ponte financeira → preço e incerteza → decisão condicional.\n\n"
    by_person={n:[] for n in ['Rodrigo','Lorenzo','Michel','Navarro']}
    counts=[]
    for i,(block,speaker,timing,spoken) in enumerate(SCRIPTS,1):
        words=len(spoken.split());counts.append(dict(block=block,speaker=speaker,time=timing,words=words))
        script+=f"## {block} — {speaker} — {timing}\n\n{spoken}\n\n"
        narrative+=f"- S{i}/{block}: {speaker}, {timing}; {words} palavras. Evidência e conclusão precisam coincidir com o slide.\n"
        if speaker in by_person:by_person[speaker].append(f"## {block} — {timing}\n\n{spoken}\n")
    closing={"Rodrigo":"Nossa escolha é uma tese condicional na Sanepar.","Lorenzo":"A oportunidade está na expansão e na eficiência do saneamento.","Michel":"O ganho só cria valor quando supera seu custo e permanece com a empresa.","Navarro":"Exigimos preço compatível e revisamos a tese quando execução ou regulação mudam."}
    for person,parts in by_person.items():
        parts.append("## B9 — fechamento coletivo\n\n"+closing[person]+"\n\nTodos: Esse é o nosso processo de investimento.\n")
        text(f"outputs/draft/teleprompter/{person.lower()}.md",f"# {person}\n\n"+"\n".join(parts))
    text("outputs/draft/script_apresentacao.md",script)
    text("outputs/draft/roteiro_narrativo.md",narrative)
    write_json("outputs/qa/script_word_counts.json",dict(total_words=sum(r['words'] for r in counts),planned_seconds=560,blocks=counts,note="Planned slots only; no human rehearsal or voice participation has occurred"))


def build_support():
    prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
    pages=[
    ("Como ler os resultados",["Versão de trabalho; fonte observada, hipótese e sensibilidade são distintas.","Cotações públicas de 30/10; confirmação de capital/eventos em outubro recomendada.","Dívida/caixa publicados em junho; ponte temporal não observada.","Reprodução matemática não certifica premissas econômicas."]),
    ("Conciliação: empresa e instrumento",["Sabesp: capital de junho e minoritários; balanço atualizado.","Copasa: release expressa ações em milhares; CSV não tem escala uniforme por emissor.","Sanepar: contas individuais; ON/PN e unit 1 ON + 4 PN.","PN: dividendo 10% maior não equivale a prêmio de preço garantido."]),
    ("Precatório: quem recebe o caixa?",["Passivo regulatório jun/26: R$ 4.407,957 milhões.","Regra: recursos destinados a usuários via tarifas e investimentos não onerosos.","Cronograma, atualização, imposto e capex determinam efeito econômico.","Dedução integral nominal é diagnóstico; pode duplicar fluxos já projetados."]),
    ("Reinvestimento e terminal",["Original: capex terminal = 110% da D&A.","Experimento: FCFF terminal = NOPAT × (1 − g/ROIC), ROIC = WACC.","WACC nominal 12,5% e g 3,5% são hipóteses; testar faixas.","Corte uniforme em 2048 é estresse, não descrição de todos os contratos."]),
    ("Ponte ESG: energia da água",["SINISA GFI2004: despesas municipais de água 2024, por prestador e UF.","Economia de 1%, retenção de 50–100%, 2027–35; hipótese, não resultado.","Sem terminal e sem benefício fiscal de capex; teto condicionado do investimento.","Volume e perdas não foram agregados por média simples; evitar dupla contagem na margem."]),
    ("Fonte e reprodução",["CVM DFP 2021–25 / ITR 2025–26: conta, versão, documento e linha preservados.","SINISA 2025: relatórios e planilhas base 2024, inclusive retificação.","Releases 2T26; estatuto Sanepar abril/26; plano de investimento dez/25.","Fontes/consultas/hashes e premissas no XLSX e nos CSVs de processed."]),
    ("O que exige decisão antes do envio",["Conferir orientações complementares, horário e canal do Safra.","Revisar margens, capex/receita regulatória, WACC, terminal e obrigações.","Assumir a recomendação e suas condições; ensaiar os quatro.","Gravar participação real, revisar arquivo inteiro e enviar pelo canal confirmado."])]
    for i,(title_,lines) in enumerate(pages,1):
        slide=base(prs,title_,i,"Material de apoio • não acrescentar automaticamente ao vídeo de dez minutos.")
        for j,line in enumerate(lines):label(slide,"• "+line,.8,2.0+j*1.0,10.2,.88,21)
    prs.save(OUT/'apoio_tecnico.pptx')


if __name__=="__main__":build()
