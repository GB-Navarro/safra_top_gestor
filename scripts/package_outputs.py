"""Auditable Excel workbooks, coverage, decision handoff and hash manifests."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import xlsxwriter

from common import ROOT, now, read_csv, read_json, sha256, write_csv, write_json
from analysis_outputs import br, text

OUT=ROOT/'outputs/draft'


def table(writer,name,rows):
    rows=list(rows)
    if not rows:return
    rows=[{k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows]
    df=pd.DataFrame(rows)
    df.to_excel(writer,sheet_name=name,index=False)
    ws=writer.sheets[name];ws.freeze_panes(1,0)
    ws.autofilter(0,0,len(df),len(df.columns)-1)
    for i,c in enumerate(df.columns):
        width=min(60,max(len(str(c))+2,min(38,int(df[c].astype(str).str.len().quantile(.8))+2)))
        ws.set_column(i,i,width)


def books():
    rows=[dict(chave='Estado',valor='RASCUNHO AUDITÁVEL; revisão econômica pendente'),
          dict(chave='Corte',valor=read_json('config/collection.json')['scope']['information_cutoff']),
          dict(chave='Mercado',valor='30/10/2026; provedor público; confirmação Bloomberg recomendada'),
          dict(chave='Financeiros',valor='CVM: última versão recebida antes do corte; consolidado quando disponível, individual nos demais. Sanepar individual; Sabesp2021–22 individual. Escopo por linha.'),
          dict(chave='Unidade financeira',valor='R$ milhões, salvo metadado específico. Lucro por ação preservado bruto, não dividido pela escala MIL.'),
          dict(chave='CVM',valor='Contas hierárquicas não devem ser somadas indiscriminadamente. DRE ITR pode conter acumulado e trimestre.'),
          dict(chave='SINISA',valor='271.856 observações municipais no CSV; Excel inclui apenas o resumo de energia por escopo. Sem média simples de perdas.'),
          dict(chave='Premissas',valor='Trajetórias herdadas e premissas propostas identificadas; não são fatos ou consenso.'),
          dict(chave='Fórmulas',valor='Projecoes e Terminal mostram trechos recalculáveis de FCFF/PV com caches. Entradas operacionais são resultados do Python; alterar margens isoladamente não atualiza todo o modelo econômico. Regenerar pelo script.'),
          dict(chave='Modelo executável',valor='scripts/model.py; python scripts/run_esg.py --stage all --offline'),
          dict(chave='Aprovação',valor='Nenhuma aprovação humana foi presumida. Consultar PROXIMOS_PASSOS.md e relatório QA.')]
    specs=[('Entidades','entities'),('Instrumentos','instruments'),('Fontes','sources'),('Observacoes','observations'),
           ('Definicoes','definitions'),('Contas_CVM','cvm_accounts'),('Documentos_CVM','cvm_documents'),
           ('Premissas','assumptions'),('Ajustes','adjustments'),('Regulacao','regulatory_terms'),
           ('Focus','estimate_snapshots'),('Cobertura','coverage'),('Claims','claims')]
    base_tables={name:read_csv(f'data/processed/{file}.csv') for name,file in specs}
    base_tables.update(Mercado=read_json('data/processed/market_reference.json'),
        Capital=[dict(entity_id=e,**v) for e,v in read_json('data/processed/capital_reference.json').items()],
        Matriz_ESG=read_json('data/processed/esg_matrix.json'),Energia_agua=read_json('data/processed/sinisa_energy.json'),
        Auditoria_195=read_csv('outputs/qa/extended_input_audit.csv'),
        Balancos=read_json('data/processed/balance_bridges.json'))
    for target,model in [('coleta/base_dados_coletados.xlsx',False),('base_modelo_auditavel.xlsx',True)]:
        (OUT/target).parent.mkdir(parents=True,exist_ok=True)
        with pd.ExcelWriter(OUT/target,engine='xlsxwriter',engine_kwargs={'options':{'strings_to_formulas':False,'strings_to_urls':False}}) as writer:
            table(writer,'LEIA',rows)
            for name,data in base_tables.items():table(writer,name,data)
            if model:model_sheets(writer)
        print('Workbook',target,flush=True)


def model_sheets(writer):
    vals=read_json('data/processed/valuation.json')
    table(writer,'Resumo_modelo',[dict(entity_id=e,ticker=r['ticker'],preco_referencia=r['price_reference'],
        valor_experimental=None if r['common_base']['equity_floor_applied'] else r['unadjusted_paper_value'],
        residuo_patrimonio=r['common_base']['equity_residual_before_floor'],
        deducao_nominal_diagnostico=r['diagnostic_full_deduction_paper_value'],
        limite_terminal_2048_diagnostico=r['finite_2048_stress_paper_value'],status=r['status'],limites=r['critical_limitations']) for e,r in vals.items()])
    table(writer,'Cenarios',[dict(entity_id=e,**s) for e,r in vals.items() for s in r['scenarios']])
    table(writer,'Sensibilidade',[dict(entity_id=e,**s) for e,r in vals.items() for s in r['sensitivity']])
    table(writer,'Ponte_ESG',[{k:v for k,v in b.items() if k!='years'} for b in read_json('data/processed/esg_bridge.json')])
    table(writer,'Ponte_ESG_fluxos',[dict(entity_id=b['entity_id'],**f) for b in read_json('data/processed/esg_bridge.json') for f in b['years']])
    table(writer,'Replica_originais',read_json('outputs/qa/model_replication.json')['results'])
    workbook=writer.book
    ws=workbook.add_worksheet('Projecoes');writer.sheets['Projecoes']=ws
    headers=['Empresa','Ano','Receita','Margem EBITDA','D&A','IR normalizado','Capex','Delta CG','Fração','Anos desconto','WACC','EBIT','NOPAT','FCFF integral','FCFF após fração','PV FCFF']
    header=workbook.add_format({'bold':True,'bg_color':'#09283D','font_color':'white'})
    num=workbook.add_format({'num_format':'#,##0.000'});pct=workbook.add_format({'num_format':'0.00%'})
    ws.write_row(0,0,headers,header);ws.freeze_panes(1,2);ws.set_column(0,0,16);ws.set_column(1,15,18)
    ri=1
    for entity,r in vals.items():
        b=r['common_base']
        for f in b['flows']:
            ws.write_row(ri,0,[entity,f['year'],f['revenue'],f['margin'],f['depreciation'],b['tax'],f['capex'],f['delta_working_capital'],f['partial_factor'],f['time_years'],b['wacc']])
            i=ri+1
            ebit=f['revenue']*f['margin']-f['depreciation']
            for col,formula,value in [(11,f'=C{i}*D{i}-E{i}',ebit),(12,f'=L{i}-MAX(L{i},0)*F{i}',f['nopat']),
                (13,f'=M{i}+E{i}-G{i}-H{i}',f['full_fcff']),(14,f'=N{i}*I{i}',f['fcff']),
                (15,f'=O{i}/(1+K{i})^J{i}',f['discounted_fcff'])]:ws.write_formula(ri,col,formula,num,value)
            ri+=1
    ws.autofilter(0,0,ri-1,15)
    for c in [3,5,10]:ws.set_column(c,c,18,pct)
    terminal=workbook.add_worksheet('Terminal');writer.sheets['Terminal']=terminal
    terminal.write_row(0,0,['Empresa','NOPAT 2035','g','ROIC terminal','WACC','FCFF 2036','TV 2035','Anos PV','PV terminal','PV explícito','EV','Dívida líquida','Minoritários','Outros ajust. adicionais','Resíduo equity','Equity piso','Milhões ações','Valor médio ação','Limitação'],header)
    terminal.set_column(0,0,16);terminal.set_column(1,17,18);terminal.set_column(18,18,65);terminal.freeze_panes(1,1)
    for ri,(entity,r) in enumerate(vals.items(),1):
        b=r['common_base'];i=ri+1
        terminal.write_row(ri,0,[entity,b['flows'][-1]['nopat'],b['g'],.125,b['wacc']])
        terminal.write_formula(ri,5,f'=B{i}*(1+C{i})*(1-C{i}/D{i})',num,b['terminal_fcff'])
        terminal.write_formula(ri,6,f'=F{i}/(E{i}-C{i})',num,b['terminal_fcff']/(b['wacc']-b['g']))
        terminal.write_number(ri,7,b['flows'][-1]['time_years'])
        terminal.write_formula(ri,8,f'=G{i}/(1+E{i})^H{i}',num,b['pv_terminal'])
        terminal.write_formula(ri,9,f'=SUMIF(Projecoes!A2:A31,A{i},Projecoes!P2:P31)',num,b['pv_explicit'])
        terminal.write_formula(ri,10,f'=I{i}+J{i}',num,b['enterprise_value'])
        terminal.write_row(ri,11,[b['net_debt'],b['minority'],0])
        terminal.write_formula(ri,14,f'=K{i}-L{i}-M{i}-N{i}',num,b['equity_residual_before_floor'])
        terminal.write_formula(ri,15,f'=MAX(0,O{i})',num,b['equity_value'])
        shares=read_json('data/processed/capital_reference.json')[entity]['outstanding_million']
        terminal.write_number(ri,16,shares)
        terminal.write_formula(ri,17,f'=P{i}/Q{i}',num,b['average_share_value'])
        terminal.write(ri,18,'Média por ação de todas as classes, não preço de PN/unit. Zero é piso, não alvo. Ajustes/fluxos e terminal pendentes.')
    for col in [2,3,4]:terminal.set_column(col,col,18,pct)


def handoff():
    text('outputs/draft/PROXIMOS_PASSOS.md','''# O que o grupo precisa fazer agora

O pacote reúne pesquisa parcial, cálculos de diagnóstico, slides e falas de revisão. Consulte o [estado central](../../ESTADO_DO_PROJETO.md). Os controles técnicos foram registrados para a execução anterior; não há vídeo ou envio realizado.

**Trabalho ainda devido pelo agente:** fechar histórico/recorrência, receita regulatória versus capex, obrigações datadas sem dupla contagem, balanço/capital e justificativa das projeções; só então consolidar recomendação e atualizar os materiais. Essa pesquisa pública e conciliação não são dependências humanas. H07 pode avançar em paralelo; H08/H09 serão a revisão dos julgamentos fundamentados que o grupo defenderá.

1. **Navarro — confirmar as instruções recebidas do Safra (H07).** Localize a mensagem de 16/10 e a live de 20/10, salve em `data/raw/orientacoes/` e anote horário, canal, formato, tamanho máximo e alterações. O regulamento público 2026 foi verificado: vídeo de até dez minutos com todos os ativos, SWOT, médio prazo, empresa/recomendação e matriz ESG; entrega indicada em 02/11. O horário e o canal não estão confirmados. Por que: são requisitos da submissão que a pesquisa pública não substitui.

2. **Rodrigo com o grupo — fechar as cinco decisões econômicas (H08).** Leia `conciliacao_financeira.md`, `auditoria_modelos.md` e as abas Premissas/Auditoria_195/Terminal da planilha. Registre em `data/interim/decisoes_equipe.md` a premissa adotada, fonte/motivo, alternativa rejeitada e efeito na conclusão. Priorize: receita regulatória versus capex; EBITDA e imposto recorrentes; WACC; reinvestimento/continuidade; precatório e demais obrigações sem dupla contagem. Aponte qualquer contrato/fluxo privado que a equipe já tenha. Por que: fórmulas corretas com premissas incompatíveis produzem uma decisão ruim. O agente já entrega os dados e as diferenças; o julgamento que vocês defenderão é de vocês.

3. **Grupo — adotar a mensagem da recomendação (H09).** A proposta atual seleciona Sanepar para uma tese condicional e NÃO sustenta compra a mercado nesta configuração. Não apresentem a faixa de dedução nominal como preço-alvo validado. Escolham a conclusão e as condições que defenderão e atualizem a fonte dos números antes de regenerar os arquivos. Por que: a preferência relativa das simulações não comprova retorno esperado ou margem de segurança. Se as hipóteses não se sustentarem, uma conclusão de aguardar é mais defensável que forçar valorização; precisa estar claramente justificada frente ao pedido de recomendação.

4. **Operador Bloomberg — confirmação útil, sem bloqueio da pesquisa (H01).** O SDK está instalado, mas o endpoint Desktop API local8194 estava inativo no teste. Abra e autentique o Terminal para possibilitar uma tentativa posterior de coleta pelo agente, ou exporte fechamento de30/10 dos cinco papéis, moeda, horário, fonte, ações por classe, tesouraria e eventos posteriores a junho. Salve em `data/raw/bloomberg/01_mercado_20261030.xlsx`. Referências públicas já coletadas: SBSP3 24,70; CSMG3 48,11; SAPR3 6,50; SAPR4 6,03; SAPR11 30,85. Confirme eventos de capital e proventos entre junho e outubro. Por que: o preço público foi obtido, mas capital/balanço de junho não são observações de outubro. Consenso e alvos de analistas são opcionais e não foram usados.

5. **Os quatro — dois ensaios com cronômetro (H10).** Usem PDF, notas do PPTX e teleprompter individual; gravem os tempos por bloco em `data/interim/feedback_ensaio.md`. Meta planejada 9:20 e margem de quarenta segundos até o teto público. O tempo real ainda não foi medido. Ajustem os trechos lentos e treinem as doze perguntas em `perguntas_banca.md`.

6. **Os quatro — gravar os clipes reais (H11).** Sigam `guia_gravacao.md` e o manifesto em `config/video_segments.json`. Salvem as tomadas em `data/raw/gravacao/`. O agente pode montar os slides com os clipes; não pode substituir a participação real dos integrantes. Os PDFs e PPTX já foram exportados, portanto H12 não é necessário para essa parte.

7. **Responsável pelo envio — revisar o vídeo inteiro e submeter (H13).** Depois de montado, confiram duração real, som, nomes, presença dos quatro e legibilidade. Enviem pelo canal confirmado em H07 e guardem o comprovante. A pasta `outputs/final/` permanece sem uma versão certificada enquanto esses requisitos estiverem pendentes.

Não é necessário fazer todas as exportações Bloomberg do plano antigo. Os substitutos públicos disponíveis já abastecem a pesquisa. Não acrescentem ratings, consenso, beta ou impacto causal que não foram medidos.
''')
    text('outputs/draft/perguntas_banca.md','''# Doze perguntas para a banca

1. **Por que Sanepar?** É candidata relativa na configuração testada, não compra incondicional. SAPR11 a R$ 30,85 versus R$ 29,14 no experimento sem ajuste incremental não prova desconto; obrigações e retorno regulatório podem mudar a conclusão. Evidência: `decisao_proposta.md`, aba Resumo_modelo.
2. **Por que não usar a TIR original como retorno da ação?** O investimento inicial representa valor da firma e os fluxos são FCFF. Retorno acionário exigiria fluxos ao acionista, financiamento e instrumento coerentes. Evidência: fórmulas preservadas nos modelos originais e reconstrução em `scripts/model.py`.
3. **ESG cria quanto de valor?** A ponte mede teto de investimento para economia hipotética de energia, não economia já obtida. Sanepar: aproximadamente R$ 10–20 milhões com retenção de 50–100%, 2027–35, nas hipóteses propostas. Evidência: Ponte_ESG e seus fluxos.
4. **Os números de perdas são comparáveis?** Mesma unidade não basta: Sabesp IPGR anual 2024; Copasa e Sanepar LTM jun/26, com metodologias e perímetros distintos. Não foi feito ranking automático. Evidência: páginas e definições da matriz.
5. **Tratar 100% do esgoto significa universalização?** Não. Pode significar 100% apenas do que foi coletado. População coberta e volume tratado têm denominadores diferentes. Evidência: SINISA água p20 / esgoto p20 e releases.
6. **Por que não deduzir todo o precatório da Sanepar?** O passivo regulatório nominal de R$ 4.407,957 milhões precisa virar fluxos datados. Descontos e investimentos não onerosos podem já estar na projeção; dedução integral pode duplicar efeito. Evidência: ITR jun/26, nota 20 p61–62 e ajustes.
7. **Qual o WACC correto?** Não foi estabelecido um WACC verdadeiro único. 12,5% nominal é hipótese comum de comparação, testada em faixa; WACC regulatório real pós-impostos de 8,08% da regra do precatório não pode ser transplantado como nominal de mercado. Evidência: Premissas e Sensibilidade.
8. **Como tratar o terminal?** O original usa capex terminal ligado à D&A. O experimento explicita FCFF = NOPAT × (1 − g/ROIC), sem excesso de retorno perpétuo, e estressa horizonte. Continuidade/renovação exige julgamento contratual. Evidência: Terminal, contratos e diagnóstico.
9. **Por que Copasa não tem alvo no gráfico?** O caso experimental produz resíduo patrimonial negativo. É alerta sobre as trajetórias e o reconhecimento do capex; não preço negativo ou prova de insolvência. Não ajustamos premissas para forçar um alvo positivo. Evidência: Resumo_modelo e Projecoes.
10. **O gasto de energia compara eficiência?** O valor absoluto reflete porte e geografia, e o escopo é serviço municipal de água 2024 reportado ao SINISA. Ele não é despesa consolidada nem custo marginal de água perdida. Evidência: Energia_agua e `sinisa_municipal.csv`.
11. **O que muda a decisão?** Preço com margem de segurança proposta, desvios persistentes de entrega/capex e mudanças regulatórias; limites são disciplina proposta, não covenant. O calendário oficial prevê ITR da Sanepar em 12/11 e reunião em 13/11, posteriores ao prazo público da etapa. Evidência: decisão e calendário oficial salvo.
12. **Como garantiram a origem e a correção?** Arquivos imutáveis com hash, versão/data CVM, conta/linha, definição e perímetro. Reproduzimos três DCFs, conciliamos entradas e testamos unidades/classes/datas/ponte ESG. Isso verifica o escopo descrito; não garante projeções futuras. Evidência: relatório QA e manifestos.
''')
    text('outputs/draft/guia_gravacao.md','''# Gravação e montagem

Fechem H07–H09 antes da tomada definitiva. Confirmem no regulamento/orientações se há exigência adicional de enquadramento ou aparição simultânea; o roteiro atual dá fala real aos quatro integrantes.

- Ensaio: dois passes com cronômetro. Tempo planejado 9:20, sem duração humana observada. Não acelerem artificialmente o áudio para caber.
- Ambiente: fundo simples, câmera na altura dos olhos, luz frontal, áudio próximo e local silencioso. Gravem alguns segundos de silêncio antes/depois para permitir cortes.
- Cada bloco tem um slide e um texto nas notas do PPTX. O teleprompter individual organiza as falas. No encerramento, os nomes e “Todos:” são marcações de produção e não devem ser pronunciados.
- Gravem os arquivos indicados em `config/video_segments.json`; ele prevê B1–B8 e os cinco trechos curtos do encerramento. Para câmera sobreposta, retrato 9:16 facilita o espaço reservado à direita. A última fala pode ser uma tomada conjunta real. Não incluam o apoio técnico automaticamente no vídeo de dez minutos.
- Guardem originais e anotem a tomada preferida. Corte/edição deve preservar sentido, fonte e participação. O montador local usa os clipes reais e o slide correspondente; não fabrica vozes nem pessoas.
- Depois dos clipes: `python scripts/assemble_video.py --check` informa ausências e durações reais. `python scripts/assemble_video.py` gera `outputs/draft/video_esg_rascunho.mp4` se todos os requisitos técnicos estiverem presentes. O comando nunca envia o arquivo.
- Assistam ao resultado inteiro. Confiram duração ≤10 minutos, ausência de silêncios acidentais, áudio inteligível, gráficos, valores, nomes e canal/formato exigidos. Só então façam a entrega humana e salvem o comprovante.

PDF e PPTX foram produzidos localmente com LibreOffice, sem dependência de exportação humana. Montagem e vídeo continuam condicionados à existência dos clipes e à revisão real.
''')
    text('outputs/draft/LEIA_PRIMEIRO.md','''# Pacote da etapa ESG — rascunho para revisão

Abra `apresentacao_esg.pdf` para leitura, `apresentacao_esg.pptx` para edição/notas e `script_apresentacao.md` para a fala exata. São nove slides; o apoio técnico tem sete páginas. Quatro figuras estão em PNG, SVG e CSV.

O [estado central](../../ESTADO_DO_PROJETO.md) registra as fases e a próxima ação. O pacote é resultado parcial: o agente ainda deve concluir conciliações e fundamentação econômica. O grupo revisa os julgamentos propostos; não recebe a obrigação de refazer a pesquisa pública.

`base_modelo_auditavel.xlsx` reúne fontes, contas, premissas, auditoria, cenários, sensibilidades e cálculos. `coleta/base_dados_coletados.xlsx` é a base de pesquisa. O CSV municipal SINISA completo fica em `data/processed/`, sem duplicá-lo inteiro no Excel.

Leia `PROXIMOS_PASSOS.md`: contém responsáveis, procedimento e motivo das pendências humanas. `decisao_proposta.md` explica a conclusão; `conciliacao_financeira.md` e `auditoria_modelos.md` mostram limitações e correções. `outputs/qa/relatorio_validacao.md` informa exatamente o que foi verificado.

Todos os valores de valuation são condicionais. Os materiais não certificam premissas ou previsão de cotação. A recomendação deve ser assumida pelo grupo após revisão. Não há vídeo, ensaio real nem submissão concluída; `outputs/final/` não foi promovida artificialmente.

Reprodução: `.venv/Scripts/python.exe scripts/run_esg.py --stage all --offline`. Consulte o contexto de execução na raiz. Os arquivos originais de cartas/modelos/documentos permanecem preservados.
''')
    text('outputs/draft/pendencias.md','''# Pendências e limites

O [estado central](../../ESTADO_DO_PROJETO.md) governa prioridades, responsáveis e critérios de fechamento. O plano inteiro não foi concluído.

**Agente — fechamento econômico prioritário:** conciliar conceitos históricos e recorrência; capex caixa/receita regulatória; dívida/caixa/capital e ponte temporal; cronograma econômico das obrigações; fundamentação das projeções e comparação/recomendação. A auditoria e as sensibilidades existentes não encerraram esses trabalhos. Atualizar gráficos, slides e falas após as correções.

**Grupo — antes da apresentação definitiva:** H07 instruções privadas; H08/H09 revisão das hipóteses e da recomendação fundamentadas pelo agente. Essa revisão não transfere conciliação contábil/pesquisa ao humano. Os controles técnicos aprovados não removem as pendências econômicas.

**Antes do vídeo e envio:** H10 dois ensaios reais; H11 clipes reais; H13 assistir ao resultado inteiro, enviar e guardar comprovante. H12 exportação PDF foi resolvido pelo agente; edição adicional só exigirá ajuda se a ferramenta falhar.

**Cobertura pública ainda parcial:** histórico ESG comparável, contratos/regulações materiais, recorrência/CG, reconhecimento tarifário, obrigações e eventos de capital após junho. Completar o que sustenta a tese e explicitar limites do restante. Não é necessário concluir todos os anexos municipais ou EV/BRR para cobrir o núcleo; EV/BRR é extensão P2. Os resultados atuais são diagnósticos, sem preços-alvo certificados.

**Agente — liberação técnica final:** `--mode final` é recusado incondicionalmente no código atual. Implementar/testar uma liberação baseada em critérios do estágio correspondente; não basta responder H07–H13 para o comando se desbloquear sozinho. Não remover o bloqueio apenas para renomear um rascunho.

**Opcionais omitidos sem bloquear o núcleo:** consenso/analistas Bloomberg, regressões de privatização/juros, VPL por ligação, índices e financiamento verde sem prova específica. Não existem resultados desses estudos neste pacote.

**Confirmação Bloomberg útil:** fechamento e capital, eventos e proventos até outubro. As cinco referências públicas já existem; a falta dessa exportação não impediu as demais etapas.
''')


def manifest(folder):
    files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha256(p))
           for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='manifest.json']
    return dict(created_at=now(),status='draft_with_economic_and_human_review_pending',
        information_cutoff=read_json('config/collection.json')['scope']['information_cutoff'],
        market_asof='2026-10-30',files=files,validation_report='outputs/qa/execution_validation.json',
        video_present=(OUT/'video_esg_rascunho.mp4').is_file(),competition_submission_completed=False,economic_certification=False)


def package():
    handoff();books()
    collection='outputs/draft/coleta/'
    write_json(collection+'model_inputs.json',dict(status='draft_inputs_only',
        balance_date='2026-06-30',market=read_json('data/processed/market_reference.json'),
        capital=read_json('data/processed/capital_reference.json'),
        financial_table='data/processed/cvm_accounts.csv',observations='data/processed/observations.csv',
        proposed_assumptions='data/processed/assumptions.csv',unresolved_adjustments=read_csv('data/processed/adjustments.csv'),
        not_economically_certified=True))
    text(collection+'LEIA_PRIMEIRO.md','''# Base de coleta — rascunho

Dados e origens estão em `base_dados_coletados.xlsx`. Cada observação tem fonte, localização, período, unidade, escala e definição. O arquivo bruto e seu hash estão na aba Fontes. Valores não publicados e projeções não foram preenchidos como realizados.

Há substitutos públicos para as exportações Bloomberg opcionais. Preços de provedor público e capital de junho exigem leitura das limitações. Contas CVM são hierárquicas e não aditivas entre todos os níveis. Os registros municipais completos estão em `data/processed/sinisa_municipal.csv`.

Consulte cobertura, pendências e manifesto. Este pacote não equivale a um modelo econômico final ou a conformidade integral de submissão.
''')
    coverage=read_csv('data/processed/coverage.csv')
    write_csv(collection+'pendencias.csv',[r for r in coverage if r['status'] not in ['acquired_extracted','completed_scope']])
    text(collection+'relatorio_cobertura.md','# Cobertura da coleta\n\n'+
        '\n'.join(f"- **{r['topic']} — {r['status']}**: {r['note']}" for r in coverage)+
        '\n\nO grau de revisão varia por tabela; aquisição não significa conciliação econômica completa. A conclusão permanece em rascunho.\n')
    write_json(collection+'manifest.json',manifest(OUT/'coleta'))
    write_json('outputs/draft/manifest.json',manifest(OUT))
    from sync_project_docs import sync
    sync()
    print('Draft package generated; documentation synchronized; no final promotion or submission.')


if __name__=='__main__':package()
