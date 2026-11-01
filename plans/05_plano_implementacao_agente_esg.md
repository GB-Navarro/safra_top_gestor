# Plano principal do agente — da pesquisa à apresentação ESG

<!-- PROJECT_STATUS:START -->
> [Estado central do projeto](../ESTADO_DO_PROJETO.md) · Revisão documental: 01/11/2026. Plano de método e critérios; conclusão de cada fase depende de evidência.
<!-- PROJECT_STATUS:END -->

Versão consolidada de 31/10/2026. Este é o documento principal para um agente implementar a etapa. O [plano humano](06_plano_executivo_grupo_esg.md) descreve as ações complementares do usuário/grupo. O [anexo técnico de coleta](07_plano_coleta_dados_agente.md) detalha os contratos de dados; o [anexo de exportações](08_plano_coleta_dados_humano.md) ajuda o operador da Bloomberg.

Execução realizada em31/10/2026: coletores, extrações, cálculos, gráficos, nove slides, PDFs e falas implementados como rascunho. Ver [contexto de execução](../EXECUTION_CONTEXT.md), [QA](../outputs/qa/relatorio_validacao.md) e [pendências](../outputs/draft/pendencias.md). Este plano prescreve o trabalho; não prova conclusão integral. Pontes econômicas e apresentação humana continuam pendentes.

## 1. Missão e autonomia

Produzir a análise comparativa de Sabesp, Copasa e Sanepar, a recomendação proposta, sua ligação quantitativa com ESG, os gráficos, nove slides, roteiro, falas dos quatro integrantes e material de gravação. Auxiliar a montagem do vídeo quando receber clipes reais e tiver ferramentas. Executar a pesquisa pública, a extração, a conciliação, a programação e a produção editorial dentro deste repositório.

Ao receber a ordem de implementar, avançar pelas fases abaixo sem pedir autorização para cada leitura, download público permitido, instalação de dependência no ambiente virtual, cálculo, gráfico, rascunho ou correção local reversível. Consultar as fontes disponíveis antes de transferir uma pesquisa ao usuário. Resolver escolhas operacionais rotineiras com justificativa registrada.

Concentrar pedidos humanos nos acessos e ações descritos por H01–H13. Pedir um insumo específico, com destino, finalidade, alternativa e efeito de sua ausência. Continuar todas as tarefas independentes enquanto aguarda. Uma ausência deve bloquear apenas a conclusão que depende dela.

O agente propõe premissas e recomendação, mostra evidências e calcula alternativas. H08/H09 registram o julgamento que o grupo assumirá na apresentação. Preparar rascunhos antes dessas respostas e incorporar o retorno depois. Não inventar respostas, assinatura de revisor ou participação em vídeo. Gravação real e envio ao Safra ficam com o grupo; não enviar mensagens ou publicar arquivos externamente.

## 2. O que a entrega precisa demonstrar

Cobrir SWOT do setor; médio prazo com tecnologia, novos participantes e competição; recomendação de empresa; matriz ESG ligada à avaliação. Requisitos, teto de dez minutos e participação dos ativos confirmados no [regulamento oficial2026](https://www.safra.com.br/data/files/76/64/7B/85/0ABCE910FDA2D4E9E3ADF9C2/Regulamento_Safra_Top_Gestor_2026.pdf), p9, itens3.3.1–3.3.2, por leitura via ferramenta web.

H07 ainda deve fornecer horário/canal/formato e alterações das orientações privadas de16/10/live20/10. O PDF2026 foi verificado via web apesar do HTTP direto403: prazo02/11 no cronograma p12; peso setorial25% na classificação p10. Nove slides, alvo9:20, limite interno9:45 e MP4/1080p continuam escolhas de produção adaptáveis.

A [página pública Safra2026](https://www.safra.com.br/lp/safra-top-gestor.htm) informa cinco finalistas; o regulamento admite ampliar até dez discricionariamente. O grupo quer ao menos o3º e relata13º; não temos notas/distâncias para calcular recuperação, embora o peso25% esteja confirmado. Maximizar qualidade significa cobrir critérios e corrigir erros materiais, sem prometer classificação.

## 3. Arquivos, recorte e fonte de verdade

Ler o README, este plano, o contexto consolidado, o diagnóstico 04, os catálogos e os originais necessários. Os HTMLs 01–03 são históricos; decisões operacionais desta revisão prevalecem sobre distribuições antigas de trabalho.

Preservar cartas e arquivos em `resources/`. Modelos ficam em `resources/modelos_originais/{sabesp,copasa,sanepar}/`; PDFs preexistentes em `resources/documentos_financeiros/sabesp/`; rascunho em `resources/roteiros/sugestao_roteiro_rodrigo.txt`. Os três PDFs locais não suprem Copasa/Sanepar. O mapa de reorganização explica movimentos já realizados; não executá-los novamente.

Usar `config/collection.json` como configuração comum. Quando implementar a análise, acrescentar opções analíticas documentadas, preservando os campos existentes. Não criar um segundo recorte independente em YAML. Valores e rotas existentes são ponto de partida, não fatos financeiros validados.

### 3.1 Datas

Preservar preço/avaliação em 30/10/2026 enquanto esse for o recorte do projeto. Separar preço, período do dado, publicação, captura e vigência contratual.

Na implementação, se H07 trouxer um recorte prescrito, aplicá-lo. Sem recorte prescrito, o agente pode registrar o instante real de início da execução como `information_cutoff`, com fuso/offset, e documentar a convenção de pesquisa. Isso fixa uma fotografia informacional, sem afirmar que ela estava integralmente disponível no pregão de 30/10. Se o objetivo exigir informação disponível naquele pregão, usar esse limite e tratar versões/publicações posteriores separadamente. Não retroagir a captura nem inventar precisão de horário.

O corte efetivo é `2026-10-31T18:25:27-03:00`, já registrado. A revisão documental de01/11/2026 não altera a fotografia informacional. Manter preço/avaliação30/10/2026 e versionar mudanças posteriores.

### 3.2 Dados

Manter CSV UTF-8/JSON como base canônica e gerar XLSX a partir deles. `entities.csv` contém três empresas; `instruments.csv`, cinco papéis. Demonstrações ligam-se ao emissor; preços/classes, ao papel. Unit não é capital adicional.

Dinheiro: BRL em milhões, escala numérica 1000000; ações: milhões; taxas: razão decimal; preço: BRL por papel; volume: m³. Preservar valor/unidade/escala original e transformação em `interim/`. Escalas convertem uma vez. Pessoa, família e ligação social mantêm sua unidade efetiva.

Usar os cabeçalhos preparados para fontes, observações, definições, ajustes, eventos de capital, termos regulatórios, consenso, premissas, afirmações e cobertura. Arquivos brutos ficam imutáveis em `raw/`; candidatos e conflitos em `interim/`; valores selecionados em `processed/`. URL descoberta, documento adquirido, extração candidata e valor conciliado são estados distintos. Ausência não é zero.

Cadeia obrigatória: afirmação → fonte/página/consulta → observação ou premissa → cálculo → figura → slide → fala. Cada escolha entre fontes deve explicar definição, versão, período e arredondamento. Não exigir revisão humana de toda célula; o agente verifica a evidência e encaminha ao grupo os julgamentos materiais.

## 4. Fases que o agente deve executar

As dependências abaixo indicam o necessário para fechar uma fase. Aquisição parcial, desenhos e rascunhos podem avançar em paralelo. O detalhamento de dados de A02/A03 está no plano 07.

| Fase | O que fazer | Como fazer | Por que / saída verificável |
| --- | --- | --- | --- |
| A01 | Preparar ambiente, inventário e pedidos | Conferir arquivos/hashes preservados, configuração e ferramentas; criar venv; identificar recorte; registrar H01/H07 primeiro | Evitar perda de originais e descobrir limitações cedo; inventário e diagnóstico de capacidade |
| A02 | Buscar/importar os dados | Coletar CVM, RI, reguladores, SINISA e BCB; importar exportações autorizadas; começar pelo último anual e intermediário elegível, completando histórico | Alimentar análise sem esperar todos os arquivos; fontes locais com consulta/data/hash |
| A03 | Normalizar e conciliar | Extrair por empresa/período, conferir definições, escalas, capital e ajustes; manter conflitos e cobertura | Impedir recomendação baseada em sinal, classe ou obrigação incorreta; base rastreável |
| A04 | Reconstruir os três valuations | Motor FCFF comum, datas corretas, hipóteses justificadas, ponte patrimônio/papel, terminal e sensibilidades | Comparar empresas por fundamento; resultados reproduzíveis e cinco premissas decisivas para H08 |
| A05 | Construir matriz e ponte ESG | Cinco fatores comparativos; escolher alavanca com insumos suficientes e recalcular o DCF | Demonstrar como ESG afeta caixa/risco/valor; matriz e diferença de valor auditável |
| A06 | Propor recomendação e riscos | Comparar alternativas, calcular quatro cenários, três gatilhos e a melhor objeção; enviar síntese H09 | Produzir escolha defensável sem escolher pela maior TIR inicial |
| A07 | Gerar as visualizações | Consumir JSON/CSVs aprovados mecanicamente; exportar figuras, tabelas-fonte e metadados | Evitar números diferentes entre peças; gráficos regeneráveis |
| A08 | Produzir slides e falas | Nove slides editáveis, apoio técnico, narrativa e script individual; atualizar com H08/H09 | Entregar conteúdo pronto para ensaio, sem pedir ao usuário que escreva a apresentação |
| A09 | Validar e renderizar | Testes materiais, consistência entre arquivos, exportação PDF e inspeção das páginas | Verificar conteúdo e aparência; relatório de QA e pedido H12 apenas se necessário |
| A10 | Apoiar ensaio e montar vídeo | Incorporar tempos/feedback H10; usar clipes reais H11; editar/verificar se houver ferramentas | Transformar material em apresentação real; vídeo ou instrução concreta de montagem |
| A11 | Empacotar e preparar envio | Gerar índice, versões/hashes, pendências e checklist do canal confirmado | Usuário consegue executar H13 com arquivo correto; envio não é feito pelo agente |

### A01 — ambiente e capacidade real

Na inspeção desta revisão, Python e `requests/pandas/openpyxl/pypdf/numpy/scipy/matplotlib` estavam disponíveis; `python-pptx` não estava. FFmpeg, FFprobe, LibreOffice e PowerPoint não foram encontrados no PATH. Isso não prova ausência de instalação fora dele. Verificar caminhos/registro/COM antes de decidir fallback; não presumir que outra máquina terá as mesmas condições.

Instalar dependências necessárias na venv do projeto e registrar versões. `python-pptx` cria PPTX, mas não substitui o renderizador. Antes de pedir operação manual, testar a rota técnica disponível e preparar todos os arquivos necessários. Não gastar a janela de ensaio instalando ferramentas opcionais.

### A02 — pesquisa pública e importação

Executar os 33 itens de `collection_backlog.csv` como fila de dados; o agente é executor dos trabalhos públicos e das importações. Contatos humanos ali indicados ajudam em exceções; não significam que precisam refazer a coleta. Solicitações H01–H13 estão no catálogo de ações humanas, que mantém o nome legado `manual_export_requests.csv`.

CVM: cadastro, dicionários e DFP 2021–2025/ITR 2025–2026. Baixar uma vez por pacote, filtrar as empresas, selecionar versão/publicação/período e consolidado apropriados. Releases/notas podem alimentar candidatos antes de todos os ZIPs; não exigir a conclusão dos dois canais para iniciar a análise. Contas sintéticas/filhas não podem ser somadas duas vezes.

RI/regulação: receitas, construção, EBITDA/ajustes, D&A, giro, capex, dívida/caixa e obrigações; metas/tarifas/contratos, resiliência, perdas, esgoto e tarifa social. Documento inacessível deve acionar CVM equivalente ou obtenção manual específica. Não concluir ausência de divulgação pela falha de um robô.

BCB: SGS 432/433 e Focus por indicador/ano/base, preservando data efetiva. Focus deve codificar espaços como %20, conforme teste anterior; taxa Selic anual não vira retorno diário; inflação mensal acumula por produto. Previsões após o último ano disponível são hipóteses, não novos dados Focus. Tesouro é apoio P1 com título/vencimento/horário definidos.

Bloomberg: importar H01–H06; sessão/API Desktop apenas se disponível e autorizada. Limitar tentativa inicial a 15 minutos; sem acesso, usar exportação do operador. Confirmar campos no Terminal, sem mnemônicos inventados. B3 fica em importação de arquivo obtido manualmente conforme a rota já documentada; não automatizar a coleta restringida.

HTTP: timeout, até três tentativas transitórias, cache, validação de conteúdo, hash e registro da consulta. Fonte indisponível: após cerca de 20 minutos de tentativas úteis, acionar alternativa. Não repetir 403 em loop. Exportações licenciadas permanecem locais.

### A03 — conciliações que podem inverter a tese

1. Sabesp: usar como candidato `Modelo_TIR_Sabesp.xlsx`; a versão `TIR_Sabesp.xlsx` tem erro de sinal de construção. Reconciliar receitas/custos de construção, remuneração de ativo financeiro e itens não caixa; atualizar balanço, ações, aquisições e minoritários.
2. Copasa: reconciliar dívida/caixa com leases, derivativos e outorga; documentar diferenças de escopo. Ligar capex à execução, ativo reconhecido e tarifa, quando essa relação sustentar a hipótese.
3. Sanepar: conferir capital ON/PN e unit; preço médio de ações não equivale automaticamente a valor justo da unit. Ler estatuto/direitos e justificar alocação entre classes.
4. Sanepar: reconciliar precatório, caixa, passivo regulatório, descontos, capex não oneroso e remuneração ao longo do tempo. Saldo nominal não é automaticamente valor presente. Evitar ajustar o patrimônio e descontar os mesmos fluxos outra vez.
5. Todas: estoque é datado; DFC pode ser acumulada; unidade e perímetro precisam coincidir. TTM de fluxo pode usar anual + acumulado atual − acumulado comparável; balanço não se anualiza.

Registrar observação preferida, candidatos e motivo. A cor de uma célula ou relato de conferência não promove entrada local a fato. H08 recebe as questões econômicas que restarem materiais depois do trabalho do agente.

### A04 — DCF e hipóteses

Usar FCFF explícito até 2035, método comum aos três casos, e valor terminal justificado. EV/BRR é teste secundário P2, não mistura oportunista de métodos.

```text
FCFF = EBIT − imposto operacional caixa + D&A − capex − Δgiro operacional
EV = VP dos FCFF futuros + VP do terminal
Patrimônio = EV + ativos não operacionais − dívida líquida − outros direitos de terceiros
Valor do papel = alocação do patrimônio aos direitos/classes correspondentes
Potencial condicional = valor estimado do papel / preço de referência − 1
```

Impostos caixa podem exigir trajetória própria; alíquota efetiva extraordinária negativa não é alíquota perpétua. Manter leases, capex, D&A, dívida e impostos consistentes. FCFF nominal pede WACC nominal compatível. Sob bases consistentes, `1+r_nominal=(1+r_real)*(1+inflação)`. WACC regulatório, custo econômico e taxa soberana são conceitos diferentes.

Modelar o fluxo remanescente de 2026: em outubro, o FCFF de janeiro a outubro não é integralmente futuro. Documentar a ponte entre último balanço e data de avaliação. Se houver estimativa de sazonalidade ou rateio, identificá-la e testar impacto, sem fabricar realizado.

Para cada hipótese de volume, tarifa, margem, capex, D&A, giro, imposto, WACC e g: histórico, fonte/contrato, escolha proposta e faixa. Não ajustar hipóteses para alcançar uma recomendação desejada. Preparar para H08 os cinco julgamentos mais decisivos e a sensibilidade da conclusão, com proposta base pronta.

Terminal: exigir WACC > g; crescimento e reinvestimento compatíveis; testar duração dos contratos, renovação onerosa/prazo finito e indenização documentada sem duplicação. Mostrar PV do período explícito e peso do terminal. Acima de 100% pode refletir FCFF explícito negativo e precisa de explicação.

As XTIRs existentes partem de EV/FCFF e terminal dependente de WACC. Não chamá-las de retorno acionário ou descoberta independente do retorno implícito. Priorizar preço versus faixa de valor. Referência: [Damodaran/NYU](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/lectures/val.html).

Recalcular em Python e reconciliar com os originais sob as mesmas hipóteses, explicando erros/diferenças. `openpyxl(data_only=True)` lê cache, não recalcula fórmulas. XLSX deve receber valores calculados pelo motor ou recálculo efetivo identificado.

### A05 — matriz ESG e ponte financeira

Cinco fatores: eficiência hídrica; expansão/qualidade do esgoto; resiliência hídrica; acesso/capacidade de pagamento; governança/regulação. Por fator/empresa: KPI/definição/período, evidência, efeito econômico, linha do modelo e quem absorve custo/retém benefício. Ausência de dado não é pior desempenho; métrica incompatível não entra em ranking.

Meta de qualidade do grupo: ao menos uma ponte quantitativa bem sustentada. Essa quantidade não está confirmada como obrigação numérica do Safra.

Se houver perdas físicas p e volume entregue C compatíveis:

```text
Produção = C/(1−p)
Volume evitado = C/(1−p_base) − C/(1−p_melhor)
Benefício = volume evitado × custo variável evitável
ΔFCFF = benefício retido após impostos/regulação − capex incremental − Δgiro
Δvalor = DCF do caso melhor − DCF do caso base
```

Um ponto percentual corresponde a 0,01. Considerar calendário, limite técnico, custo de redução e compartilhamento tarifário. Perdas aparentes exigem conta distinta; não somar recuperação de faturamento e economia física do mesmo volume.

Se faltarem esses insumos, selecionar energia/intensidade ou execução/atraso de expansão com dados melhores. Não trocar por um número inventado. Se só houver sensibilidade financeira, identificá-la e declarar o elo operacional não mensurado. Uma ponte de expansão exige capex, entrega, receita/custo, reconhecimento, impostos e retenção; benefício já no base não se soma novamente.

Recalcular cenários no mesmo motor. Duas alavancas podem interagir; waterfall deve fechar com a diferença total e explicitar interação. Rating/índice ESG é contexto, não prova de valor.

### A06 — proposta de decisão

Calcular base, juros/custo de capital adverso, operação/regulação adversa e execução favorável. Registrar choques/duração e valor do papel; separar sensibilidade WACC × g de cenário econômico conjunto. Não atribuir probabilidades sem suporte.

A terceira carta orienta a preocupação do grupo com prêmio de risco. Seus eventos de catorze pregões não devem ser copiados como fluxos de dez anos. Sensibilidade WACC não é beta empírico nem perda observada da ação.

Preparar `outputs/draft/decisao_proposta.md`: empresa preferida, comparação com as outras duas, preço/data, faixa, alavanca ESG, três riscos, três gatilhos com métrica/limite/data/ação, melhor contra-argumento e cinco premissas críticas. H09 revisa essa proposta, sem ter de criar a tese do zero.

Se todas parecerem caras, auditar inputs/método e preservar o resultado. Propor condição de entrada e conferir H07 quanto ao formato da recomendação. Não tornar a melhor entre três automaticamente uma compra atrativa. Incerteza material que inverte a escolha mantém a recomendação provisória; continuar as demais peças em rascunho.

### A07–A08 — gráficos, slides e script

Gerar `valuation.json`, `scenarios.json`, `esg_matrix.json`, `esg_bridge.json` e `presentation_facts.json`. Usar este último para números formatados de slides e falas; corrigir na fonte, não em cópias divergentes.

Gráficos: déficit/metas, SWOT, médio prazo, matriz, ponte ESG, preço/faixa e cenários/gatilhos. Entregar CSV-fonte, PNG e SVG quando útil. Faixa de cenários não é IC de 95%. Se normalizar comparação entre papéis, usar preço atual=100 e identificar. Preço nominal baixo não significa desconto.

Layout 16:9, título 28–32 pt, texto 18–24 pt, fontes 12–14 pt como referência a testar no vídeo. Área de câmera livre; matriz condensada com definições no apoio; cores consistentes e legíveis sem depender apenas de vermelho/verde. PPTX tem títulos/tabelas/elementos editáveis; gráfico em imagem vem com código/dados, sem promessa falsa de SVG editável.

| Slide / bloco | Tempo / palavras | Voz proposta | Entrega do agente |
| --- | --- | --- | --- |
| S1/B1 — recomendação | 0:00–0:50 / 100 | Rodrigo | Escolha/ticker, preço/data, tese e condição; concluir depois da análise |
| S2/B2 — contexto | 0:50–1:40 / 105 | Lorenzo | Déficit nacional com ano-base e linha de metas |
| S3/B3 — SWOT | 1:40–2:55 / 160 | Lorenzo | Matriz setorial 2×2, até dois itens por quadrante, com efeito econômico |
| S4/B4 — médio prazo | 2:55–3:55 / 125 | Navarro | Regulação, participantes e tecnologia, um exemplo documentado por frente |
| S5/B5 — matriz ESG | 3:55–5:25 / 190 | Michel | Cinco fatores, três empresas, consequência financeira e ressalvas |
| S6/B6 — ponte ESG | 5:25–6:30 / 135 | Michel | Operação → caixa retido → diferença no valor, com custo e hipóteses |
| S7/B7 — valuation | 6:30–7:55 / 180 | Rodrigo | Preço versus faixa, alternativas, WACC/g e dependência do terminal |
| S8/B8 — riscos | 7:55–8:55 / 125 | Navarro | Cenários e três gatilhos de revisão |
| S9/B9 — conclusão | 8:55–9:20 / 55 | Todos | Mesma recomendação, condição e risco, com falas curtas dos quatro |

Total planejado: 560 segundos e 1.175 palavras. Inclui transições; ensaio H10 determina a duração real. Todos têm participação substantiva antes do fechamento coletivo.

Entregar `roteiro_narrativo.md` com a lógica; `script_apresentacao.md` com fala exata, integrante, tempo, transição e ação visual; teleprompter por pessoa. Separar marcações de fonte da fala pronunciada. Produzir 12 perguntas de banca com resposta/evidência.

Revisar o rascunho Rodrigo: corrigir alegação de que apenas Sanepar divulga perdas, confusões de esgoto, TIR acionária, superioridade tecnológica sem prova e promessas de θ/beta/VPL ausentes. O agente escreve e revisa; o grupo ensaia e assume a argumentação.

### A09 — testes, renderização e revisão

Testar os erros materiais: classes não duplicam financeiros; escala/conversão única; fonte/publicação/definição presentes; ausência preservada; construção e precatório sem dupla contagem; FCFF/ponte patrimônio conhecidos; datas do fluxo remanescente; WACC > g; ponte ESG zero gera delta zero; custos/impostos reduzem benefício no caso de teste; cenários fecham com os dados usados na fala.

Propriedades de sensibilidade dependem dos sinais dos fluxos; não impor monotonicidade cegamente. Teste de código aprovado não certifica a hipótese econômica. Relatar resultados, diferenças e limitações em `outputs/qa/relatorio_validacao.md` e JSON.

Criar PPTX com [python-pptx](https://python-pptx.readthedocs.io/en/latest/). Exportar pelo [PowerPoint](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.presentation.exportasfixedformat) instalado ou ferramenta local equivalente; verificar disponibilidade real. Depois renderizar o PDF em PNGs, por exemplo com [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/recipes-images.html), e inspecionar todas as páginas. Renderizador de PDF não substitui conversão de PPTX para PDF.

Se não houver conversor operacional, preparar PPTX e instrução H12 para o usuário exportar. Retomar a inspeção ao receber o PDF. Conferir cortes, fonte substituída, sobreposições, eixos, rodapés e área de câmera. Não declarar revisão visual concluída a partir apenas de XML válido.

### A10–A11 — ensaio, vídeo e pacote

Após H10, ajustar duração e clareza. Se exceder 9:45, cortar repetição e detalhes do apoio, preservando requisitos/ressalvas. Não acelerar artificialmente a fala para caber.

Receber clipes reais H11 em `data/raw/gravacao/`, nomeados por bloco/integrante. Se [FFmpeg](https://ffmpeg.org/ffmpeg.html) e ferramentas de inspeção estiverem operacionais, montar cortes/transições e ajustar áudio, preservando os originais; medir duração/resolução/streams. Se não estiverem, gerar ordem de edição, tempos e arquivos de apoio em H12. Não fabricar voz/participação.

O agente verifica o que suas ferramentas permitirem e explicita o que ainda exige assistir/ouvir. O grupo assiste ao vídeo inteiro, confirma compreensão e executa H13. Não considerar vídeo existente ou envio concluído por haver slides/script.

## 5. Pedidos ao usuário e dependências reais

| ID | O que vem do humano | Quando afeta a conclusão do agente | Alternativa / avanço independente |
| --- | --- | --- | --- |
| H01 | Mercado/capital Bloomberg ou arquivo permitido equivalente | Preço/classes se não houver acesso autorizado já utilizável pelo agente | RI/CVM para capital; importação B3 manual; restante da pesquisa segue |
| H02–H06 | Financeiros, consenso, analistas, ESG e título, quando disponíveis | Apenas a comparação adicional que depender da exportação | Fontes públicas/premissas próprias identificadas; P1 não bloqueia o núcleo |
| H07 | Orientações atuais do Safra, prazo/canal | Conformidade e envio; pode alterar formato | Conteúdo de referência continua em rascunho com origem declarada |
| H08 | Revisão das premissas/questões materiais propostas | Versão que será assumida pelo grupo | Modelar alternativas e preparar rascunhos enquanto aguarda |
| H09 | Decisão sobre a recomendação proposta e suas condições | Fechamento da mensagem do grupo | Preparar proposta fundamentada e atualizar títulos ao receber retorno |
| H10 | Tempos e feedback de dois ensaios | Duração/clareza reais | Script, teleprompter e perguntas são preparados antes |
| H11 | Clipes reais dos quatro | Vídeo final | Slides e guia de gravação independem dos clipes |
| H12 | Operação técnica pontual, se ferramenta/acesso faltar | Apenas a obtenção de documento, exportação ou edição não concluída pelo agente | Entregar URL/arquivos, destino e instrução exata; marcar não aplicável se o agente fizer |
| H13 | Envio e comprovante pelo canal oficial | Submissão | Pacote local completo fica pronto para o usuário |

H08/H09 são revisão de escolhas, não tarefa de coletar tudo ou programar. Para cada pergunta, levar proposta, evidência, diferença entre alternativas e efeito na tese. Questão puramente operacional não deve virar pedido de aprovação.

H12 pode ser acionada em momentos diferentes: documento durante A02; PDF depois de A08; edição depois de H11. Cada ocorrência recebe seu pedido/destino e resultado. Não impor uma dependência única de H12 para todas as fases: esperar a edição antes de renderizar criaria um ciclo com ensaio e gravação.

## 6. Entregáveis e critérios de conclusão

O [contrato09](09_contrato_de_fechamento.md) detalha o fechamento por requisito C01–C29, com dados/correções, fontes, procedimento, dependências, aceite e alternativa. Seu catálogo vincula A/D/H/N e as células abertas; não substitui estes critérios nem declara trabalho concluído. A [extensão HTML10](10_plano_html_interativo.md) tem perfil separado dos nove slides atuais e ainda não foi implementada.

Dados: `outputs/final/coleta/` com base_dados_coletados.xlsx, relatorio_cobertura.md, pendencias.csv, model_inputs.json, manifest.json e LEIA_PRIMEIRO.md. O plano 07 detalha esse pacote. Ele pode ficar pronto com H07 ainda pendente, sem afirmar conformidade com o concurso.

Apresentação: `outputs/final/` com base_modelo_auditavel.xlsx; apresentacao_esg.pptx/.pdf; apoio_tecnico.pptx/.pdf; roteiro_narrativo.md; script_apresentacao.md; teleprompter/; perguntas_banca.md; guia_gravacao.md; figuras/; manifest.json; pendencias.md e LEIA_PRIMEIRO.md. Vídeo recebe nome/formato conforme H07 e só aparece como pronto depois de montado/revisado.

`draft` admite pendência visível. `final` exige fonte/rastreabilidade, ajustes críticos tratados, recomendação consistente, matriz e ponte, conteúdo pedido, números iguais entre peças e revisão do estágio correspondente. Separar os estados: dados prontos; análise pronta; material visual pronto; vídeo pronto; enviado. Não usar um único “concluído” para todos.

A aceitação final da etapa audiovisual exige também orientações conferidas, participação dos quatro, duração/legibilidade/áudio verificados e comprovante do envio humano. A ausência de clipes não impede encerrar a entrega analítica com a pendência audiovisual visível.

## 7. Implementação existente e comandos

A entrada `scripts/run_esg.py`, o coletor e os módulos auxiliares existem. A execução completa usa processos por estágio para limitar memória. Os comandos abaixo são atuais. Importação Bloomberg genérica, seleção por `--task` e liberação final ainda não estão implementadas.

```powershell
python scripts/run_esg.py --stage collect --config config/collection.json --mode draft
python scripts/run_esg.py --stage model --config config/collection.json --mode draft
python scripts/run_esg.py --stage charts --config config/collection.json --mode draft
python scripts/run_esg.py --stage slides --config config/collection.json --mode draft
python scripts/run_esg.py --stage validate --config config/collection.json --mode draft
python scripts/run_esg.py --stage package --config config/collection.json --mode draft --offline
python scripts/run_esg.py --stage docs
python scripts/sync_project_docs.py --check
```

Cache e `--stage all --offline` existem; `--refresh` reextrai CVM/SINISA. `--mode final` é recusado incondicionalmente no código atual: implementar/testar liberação por evidências é pendência A11. Empacotar rascunho não certifica fechamento econômico. A documentação é sincronizada após os estágios; seu texto de andamento deve ser revisado pelo agente conforme AGENTS.md.

## 8. Prioridades e tempo

P0: conteúdo da etapa, dados/ajustes que mudam a escolha, DCF, matriz, ponte financeira sustentada, cenários/gatilhos, slides e fala legíveis. P1: segunda ponte, consenso, histórico adicional, financiamentos/índices. P2: θ, beta empírico, EV/BRR, VPL por ligação e reverse DCF. Insumo da ponte selecionada sobe para P0. Retirar uma análise exige remover sua promessa de todos os materiais.

No `n_status.csv`, N01–N03 são preços; N05 passa a DCF/valor versus preço, sem retorno acionário mal rotulado; N07–N14/N18–N20/N25 abastecem o núcleo; N06/N15–N17/N24 são apoio; N04/N21–N23 são extras. Dado coletado recebe `inputs_ready`, não `analysis_completed`.

Começar A01/A02 imediatamente na execução; entregar rascunho de dados cedo; desenvolver setor/layout em paralelo; fechar números antes da gravação. Para o prazo interno de 02/11, buscar análise/material e gravação em 01/11, condicionado ao horário real de H07. Reservar ao menos duas horas antes do prazo para exportação/upload/correção. São metas de organização, não duração garantida. Replanejar se a execução começar depois ou a janela for menor; não eliminar revisão/gravação para concluir P2.

## 9. Validação crítica deste plano

| Falha encontrada na divisão anterior | Correção |
| --- | --- |
| Pesquisa pública e conciliação atribuídas aos humanos | Agente executa A02–A06; humanos tratam acesso, julgamento e participação |
| Humanos precisarem escrever a tese e a fala do zero | Agente entrega proposta completa, alternativas, slides e script |
| Agente parar por qualquer exportação ausente | Bloqueio por dependência; dados públicos e rascunhos seguem |
| Todos os ZIPs serem pré-requisito para iniciar financeiros | Releases/notas e extração por arquivo alimentam candidatos em paralelo |
| Duas configurações de datas e ordens diferentes de leitura | Configuração comum e planos 05/06 principais, 07/08 como apoio |
| Hora de corte virar uma escolha operacional obrigatória do usuário | Agente registra instante real da execução quando não houver recorte prescrito |
| Supor que geração de PPTX implica renderização/vídeo | Verificação real de ferramentas e H12 condicional |
| “Validado” confundir roteiro com resultados financeiros | QA documental nesta revisão; QA dos dados/modelos só na implementação |
| Misturar dados, análise, vídeo e envio num estado único | Estados de prontidão separados e comprovante humano para submissão |

Conferir links, IDs, responsáveis, dependências, tempos e entregáveis. `outputs/qa/plans_validation.json` preserva a revisão histórica do plano; a execução técnica registrada está em `execution_validation.json` e a documentação atual em `documentation_validation.json`, sob outputs/qa. O fechamento econômico permanece parcial, conforme o estado central; esses relatórios não certificam previsões ou aprovação humana.
