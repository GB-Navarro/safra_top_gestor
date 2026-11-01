# Implementação da coleta e organização dos dados — agente de IA

<!-- PROJECT_STATUS:START -->
> [Estado central do projeto](../ESTADO_DO_PROJETO.md) · Revisão documental: 01/11/2026. Plano de método e critérios; conclusão de cada fase depende de evidência.
<!-- PROJECT_STATUS:END -->

Preparado em 31/10/2026. Este é o anexo técnico de dados do [plano principal do agente](05_plano_implementacao_agente_esg.md). O [plano principal humano](06_plano_executivo_grupo_esg.md) governa as ações do grupo; o [anexo de exportações](08_plano_coleta_dados_humano.md) detalha H01–H07. Em caso de distribuição antiga de responsabilidades, prevalecem 05/06.

## 1. Escopo e estado real do repositório

Para os dados exatos ainda necessários e correções abertas, usar o [contrato09](09_contrato_de_fechamento.md), cujo catálogo indica fontes/rotas, evidência existente, método, dependência e aceite por C01–C29. As64 células históricas abertas na auditoria de01/11 têm vínculo individual no mapa derivado. A geração do HTML10, descrita no [plano10](10_plano_html_interativo.md), consumirá uma exportação mínima e não todos os arquivos brutos.

Implementar uma rotina reproduzível que obtenha informações oficiais/públicas e importe exportações Bloomberg, preserve os documentos, extraia observações com procedência, normalize definições/unidades e entregue uma base utilizável na análise de Sabesp, Copasa e Sanepar. Os resultados alimentarão DCF, matriz ESG, gráficos e apresentação, que pertencem às etapas posteriores do plano 05.

**Já realizado nesta organização e revisão:** dez arquivos de `resources/` separados por tipo/empresa, mantendo seus bytes; cartas e planos nas pastas anteriores; referências locais atualizadas; configuração de coleta; cadastro inicial de três empresas e cinco instrumentos; catálogo com 21 rotas; fila com 33 tarefas; catálogo ampliado para 13 ações humanas H01–H13; dicionário inicial de 55 métricas; tabelas de trabalho com cabeçalhos. Há inventário anterior à reorganização e mapa de caminhos.

**Atualização da execução:** coletores, extração CVM/SINISA, observações, auditoria parcial e pacote XLSX/JSON/MD produzidos em `outputs/draft/coleta/`. Ver [cobertura efetiva](../outputs/draft/coleta/relatorio_cobertura.md) e [validação](../outputs/qa/relatorio_validacao.md). Pontes econômicas e séries ainda parciais estão identificadas; nenhum número das planilhas originais foi automaticamente promovido a fato. As seções abaixo seguem como contrato técnico, não declaração de conclusão de cada item.

Não mover novamente os materiais nem recriar a estrutura em outra pasta. Antes de começar, ler `README.md`, `config/collection.json`, este plano, os catálogos e os pontos de auditoria do plano 05. Não acessar a Bloomberg como se o acesso do usuário garantisse API disponível ao agente.

## 2. Estrutura e arquivos que governam a execução

| Local | Função |
| --- | --- |
| `cartas/` | Cartas originais, como histórico de opinião/posicionamento do grupo |
| `plans/01` a `03` | Planos históricos em HTML; usar para rastrear objetivos, não para sobrepor decisões atuais |
| `plans/04` a `06` | Diagnóstico e plano completo da etapa ESG |
| `resources/modelos_originais/{sabesp,copasa,sanepar}/` | Planilhas originais, sem sobrescrever; `TIR_Sabesp.xlsx` é referência com erro identificado |
| `resources/documentos_financeiros/sabesp/` | Três PDFs preexistentes, todos atribuídos à Sabesp na pesquisa anterior; confirmar título/período/páginas ao cadastrar |
| `resources/roteiros/` e relato textual no contexto do desafio | Rascunhos e explicação do colega, sem status de fonte primária contábil |
| `config/collection.json` | Recorte, origens, unidades, caminhos, política HTTP e verificações |
| `data/catalog/` | Inventário, rotas, tarefas, pedidos e definições-alvo |
| `data/raw/` | Documentos baixados e exportações originais, imutáveis |
| `data/interim/` | Texto/tabelas extraídos, candidatos, conflitos, cálculos de normalização e decisões |
| `data/processed/` | Observações e tabelas normalizadas com procedência e status |
| `outputs/qa/` | Logs e relatórios de validação |
| `outputs/draft/coleta/` e `outputs/final/coleta/` | Pacote para a equipe; versão final só após cumprir critérios |

O mapa `config/repository_layout.json` explica a migração, não é uma ordem para repeti-la. `data/catalog/original_files_manifest.json` preserva caminhos/hashes anteriores; `local_assets.csv` localiza os materiais e mantém `sha256_original`. O relatório `reorganization_audit.csv` distingue conteúdo preservado de Markdown atualizado.

### 2.1 Configuração e recorte

Manter preço/avaliação30/10/2026 e fuso `America/Sao_Paulo`. O corte efetivo é `2026-10-31T18:25:27-03:00`, já registrado em collection.json. A revisão documental de01/11 não altera dados ou datas. A fotografia de pesquisa não afirma disponibilidade integral no pregão30/10; manter período, publicação, captura e versão separados. Mudança prescrita por H07 exige versionamento explícito.

Separar cinco datas: referência do preço; período contábil/operacional; publicação; captura; eventual vigência contratual. O dado mais recente é o mais recente **publicado até o corte**, não necessariamente o período mais recente presente numa consulta atual. Não inserir 3T26 sem publicação elegível. Uma reapresentação posterior deve ficar identificada; se a versão histórica não for recuperável, registrar a limitação.

Anos-alvo: financeiros 2021–2025; ITRs 2025–2026 para comparações e atualização; ESG 2022–2025 e intermediários de 2026 quando divulgados com definição compatível. Não esperar que toda métrica tenha toda essa série; documentar cobertura real.

### 2.2 Identificadores, unidades e tabelas

`entities.csv` tem **uma linha por empresa** (`sabesp`, `copasa`, `sanepar`). `instruments.csv` tem uma por papel (`SBSP3`, `CSMG3`, `SAPR3`, `SAPR4`, `SAPR11`). Demonstrações e KPIs ligam-se à empresa; preços e classes ligam-se ao instrumento. Não juntar demonstrativos a cinco papéis e depois somar os valores duplicados. O contrato do plano 05 foi atualizado para essa separação.

Os cabeçalhos existentes são o contrato mínimo. Campos adicionais são permitidos com documentação e migração compatível; não renomear chaves sem atualizar consumidores.

| Tabela | Regra operacional |
| --- | --- |
| `sources.csv` | Uma linha por documento/versão/consulta adquirida; `source_id` único, caminho real, SHA-256, publicação/captura e status de acesso |
| `observations.csv` | Valor numérico com empresa/papel, métrica, unidade/escala, período, fonte/localização, definição, escopo, tipo e qualidade |
| `definitions.csv` | Definição efetiva da fonte: numerador, denominador, escopo, metodologia, vigência e comparabilidade; não presumir definição única entre empresas |
| `adjustments.csv` | Obrigações/ativos e possíveis ajustes de EV/patrimônio, com natureza e tratamento econômico; sem transformar saldo contábil automaticamente em ajuste de valuation |
| `corporate_actions.csv` | Eventos, anúncio, vigência, fator e fonte; necessário para preço/capital comparáveis |
| `regulatory_terms.csv` | Texto de regras, prazos, contratos/agrupamentos, regulador, vigência e fonte; informações não numéricas não cabem à força em `value` |
| `estimate_snapshots.csv` | Consenso, estatística, amostra/dispersão, período previsto, data da fotografia e fonte; preserva detalhes que não cabem numa observação isolada |
| `assumptions.csv` | Hipóteses propostas, justificativa, faixas e responsável; não registrar como fato realizado |
| `claims.csv` | Afirmações qualitativas ligadas às fontes; inferência/opinião separadas de fato |
| `coverage.csv` | Requisito/métrica/período, status, IDs de evidência, lacuna, materialidade, responsável e alternativa |
| `n_status.csv` | Situação dos N01–N25; não afirmar que uma análise foi executada porque seus insumos foram coletados |

Dinheiro operacional: BRL, escala numérica `1000000`; ações: escala `1000000`; taxa: razão decimal com escala `1`; preço: BRL por papel; volume: m³. `value * scale` recupera a quantidade na unidade-base correspondente. Preservar valor/unidade/escala originais e fator de transformação na camada intermediária. Converter uma única vez.

No caso de tarifa social, preservar se a unidade original é família, ligação ou pessoa; não converter silenciosamente tudo em “beneficiário” comparável. A unidade genérica do dicionário é um alerta para obter a definição. Demais exceções à unidade-alvo também exigem justificativa registrada, não coerção matemática impossível.

Métrica macro/setorial pode ter `entity_id` vazio e escopo explícito. Título soberano precisa de identificação própria quando usado; não atribuir sua taxa a um dos cinco papéis de ações. Datas de estoque usam data de referência; início do período pode ficar vazio. Vazios em CSV representam ausência, nunca zero.

## 3. Prioridades e fila de trabalho

Usar `data/catalog/collection_backlog.csv`, sem criar uma segunda fila desconectada. P0 reúne dados que sustentam a recomendação e os conteúdos da etapa; P1 melhora a comparação; P2 fica fora do caminho mínimo.

- **P0 primeiro:** cadastro/classes/preço; históricos e balanço recente; itens de construção/não caixa; dívida/caixa e demais ajustes materiais; precatório; indicadores ESG comparáveis; metas, capex, regulação e prazo de contratos; déficit nacional; casos de competição/tecnologia; calendário; inflação realizada/esperada para embasar hipóteses.
- **P1 depois ou em paralelo sem bloquear P0:** consenso, analistas, benchmark soberano, dados Bloomberg suplementares, segunda ponte, financiamentos/índices ESG documentados.
- **P2 adiado:** históricos adicionais para θ, regressão de juros, EV/BRR e VPL por ligação se o núcleo ainda não estiver pronto.

Promover para P0 os insumos da ponte ESG efetivamente escolhida: energia/custo por m³ deixam de ser opcionais se essa for a alavanca usada. Perdas físicas só são exigência do cálculo físico; se a fonte não separar componentes, selecionar outra ponte e registrar a decisão. Não inventar dados para fechar N12.

O agente executa pesquisa pública, extração, conciliação, normalização e produção da base. Rodrigo pode ajudar nos julgamentos financeiros; Lorenzo, nas definições; Michel, na regulação/ESG; Navarro, nas regras/operação. Esses contatos não são uma exigência de revisão humana de cada célula. O operador atende H01–H06 e H07 traz orientações atuais; H08/H09 tratam das escolhas econômicas depois da proposta do agente. A fila registra executor e contato humano separadamente. Resolver tarefas independentes enquanto aguarda.

## 4. Implementação em oito entregas

### E1 — inventário e contratos, antes de acessar redes

1. Validar configuração, caminhos e cadastros; conferir inventário e hashes dos materiais preservados. Não tratar hashes de Markdown mantido como se o conteúdo devesse permanecer idêntico.
2. Criar ambiente virtual e dependências mínimas efetivamente necessárias: `requests`, `pandas`, `openpyxl`, `pypdf`; acrescentar biblioteca apenas quando um parser justificar. Registrar versões utilizadas. Python 3.11.9 e esses módulos estavam disponíveis no ambiente consultado, mas não presumir instalação em outra máquina.
3. Implementar leitor único da configuração e schemas dos CSVs. Registrar execução com identificador, início/fim, recorte, versão do código/configuração e lista de artefatos.
4. Definir IDs estáveis, status e normalização de unidades. Preparar conjunto reduzido de amostras reais para testes sem copiar grandes bases licenciadas.

**Saída:** inventário revisado, configuração interpretada, contratos documentados e primeiro relatório estrutural. Nenhuma observação financeira inventada.

### E2 — aquisição pública com manifesto

Implementar cliente HTTP com timeout de 30 s, até três tentativas para erro transitório e paralelismo moderado, no máximo duas requisições simultâneas por host. Não repetir 403 incessantemente. Registrar URL final, parâmetros, status, tipo de conteúdo, captura e hash. Validar assinatura do arquivo: uma página de erro não é PDF/ZIP/CSV válido.

Salvar inicialmente em arquivo temporário e concluir a gravação apenas com resposta íntegra. Cada nova versão de conteúdo recebe nome com data de captura/hash, sem sobrescrever o original anterior. Para a mesma URL/hash, reutilizar cache. O catálogo de rotas tem `registry_id`; o arquivo adquirido recebe `source_id` próprio. Registrar a ligação entre ambos no manifesto de aquisição.

Validar caminhos de escrita/extração dentro do workspace, inclusive membros de ZIP. Não usar nomes externos como comandos. Guardar a consulta de API junto à resposta. Não registrar credenciais. O registro de fonte deve poder provar que o documento existe localmente e qual versão foi lida.

**Fontes e adaptadores:**

| Adaptador | Aquisição | Regras específicas |
| --- | --- | --- |
| CVM | Cadastro, dicionários e ZIPs DFP/ITR pelas rotas de `collection.json` | Baixar cada pacote anual uma vez; filtrar as três empresas após aquisição; verificar versão/publicação |
| BCB SGS | Séries 432 e 433, JSON em janelas limitadas | Data brasileira, valor textual, frequência/unidade; Selic anual não é retorno diário |
| BCB Focus | `ExpectativasMercadoAnuais`, consultas por indicador/ano/base | Codificar espaços como `%20`; ordenar pela data, filtrar até o corte e usar a data efetivamente retornada |
| Tesouro | Descoberta CKAN e CSV do recurso válido | Não assumir que toda URL do catálogo é CSV; escolher recurso por formato e validar cabeçalhos |
| RI/CVM e reguladores | PDFs/planilhas oficiais, com publicação e período | Se site exigir JS, localizar documento CVM equivalente ou obtenção humana; registrar a falha |
| SINISA | Relatório e planilhas ligados à página oficial | Registrar código/denominador e ano-base do indicador, separado do ano do relatório |

Referências: [DFP/CVM](https://dados.cvm.gov.br/dataset/cia_aberta-doc-dfp), [ITR/CVM](https://dados.cvm.gov.br/dataset/cia_aberta-doc-itr), [serviço Expectativas/BCB](https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/aplicacao), [Tesouro Transparente](https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto). Rotas e exemplo Focus também constam do plano 05. Não alegar que catálogos bastam para comprovar todos os campos: ler dicionários e respostas reais.

**Saída:** arquivos brutos, consultas/manifestos e registros de fonte adquirida. Documento ainda não extraído deve continuar com esse status.

### E3 — importação humana e documentos preexistentes

Processar H01–H07 do catálogo `manual_export_requests.csv`; o arquivo, com nome legado, também contém H08–H13 para revisão/apresentação, fora da importação de dados. Em `data/raw/bloomberg/`, esperar os seis pacotes descritos no plano humano 06 e no anexo 08, com aba de metadados e valores estáticos legíveis sem add-in. Registrar exportação, operador, data/hora, função/campo, ajustes, moeda, unidade, período e mensagens de indisponibilidade.

H01, mercado, é o pedido prioritário: fechamento de 30/10 dos cinco papéis; capital por classe com data; eventos relevantes. Confirmar identificadores/fields no Terminal, sem inventar mnemônicos. Usar consulta histórica de preço; consulta pontual corrente não comprova valor em 30/10. Quantidade emitida, quantidade fora de tesouraria e free float são conceitos distintos.

API Desktop Bloomberg é opcional, com limite inicial de 15 minutos para verificar sessão/permissão; falha aciona exportação manual. Acesso ao Terminal não é autorização técnica automática para toda API. [Biblioteca oficial Bloomberg](https://professional.bloomberg.com/support/api-library/).

Alternativa para preço: arquivo B3 obtido manualmente pelo operador, segundo os termos aplicáveis, em `data/raw/b3_manual/`. A [página de cotações históricas da B3](https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/mercado-a-vista/cotacoes-historicas/) restringe coleta automatizada; não implementar download alternativo para contornar a restrição. Importar TXT de largura fixa com layout oficial, ticker/mercado e duas casas decimais de preço. Cotação sem ajuste por proventos serve ao fechamento; não vira série de retorno total por renomeação.

Para os PDFs locais, cadastrar sua procedência real: documento local preexistente, emissor/período confirmados e URL/publicação apenas se identificados. Não inventar data de captura original. Se o documento oficial for localizado, ligar as versões por hash/conteúdo e evitar download/cadastro duplicado. Não copiar PDFs para `raw/` apenas para aparentar nova aquisição: `sources.local_path` pode apontar para o original preservado em `resources/`.

Planilhas de valuation: extrair suas entradas para candidatos, com caminho/aba/célula e status `local_workbook_unverified`. Hipóteses vão para a tabela de premissas propostas. Cor da célula, cache de fórmula e relato de conferência não bastam para promover dado a fato oficial. Não executar links externos/macros para extrair informações.

**Saída:** pedidos atualizados e importações catalogadas. Ausência de H02–H06 não bloqueia automaticamente o núcleo com fontes públicas.

### E4 — extração financeira e conciliações materiais

Ler dicionário e cabeçalhos reais dos ZIPs CVM antes do mapeamento. Identificar empresa, versão, documento, conta, valor, moeda/escala, início/fim do período, exercício e consolidado/individual. Nomes de contas auxiliares variam; não deduzir todo conceito por uma palavra-chave isolada.

Selecionar consolidado quando disponível e manter o escopo explícito. Não somar conta sintética com suas filhas. DFC acumulada não é fluxo trimestral: diferença entre acumulados só com mesmo perímetro e conceito. TTM de fluxo pode usar anual 2025 + acumulado 2026 − acumulado comparável 2025. Estoque de balanço não se anualiza. Não misturar ano corrente com comparativo reapresentado sem registrar versão.

Preservar extrações candidatas com `candidate_id`, fonte/localização, valor bruto, contexto, escopo e parser. Parser de PDF deve preservar página; tabelas deslocadas, sinais e unidades exigem conferência. Usar OCR apenas quando necessário e sempre sinalizar o resultado para revisão. Extração de texto não prova que a coluna correta foi lida.

Conciliações obrigatórias:

- Receita de serviço versus construção, custo de construção e remuneração de ativos financeiros; ponte do EBITDA reportado para ajustado. Atenção ao erro de sinal da Sabesp na planilha antiga.
- Dívida, caixa livre/restrito, leases, derivativos, outorgas, minoritários e demais direitos/obrigações, cada um com data. Registros são insumos para o ajuste econômico futuro, não preço estimado automático.
- Sanepar: nota 20, saldo circulante/não circulante do precatório, cronograma de desconto, investimento não oneroso e regra de remuneração. Examinar alterações até o corte. Evitar dupla contagem entre passivo, caixa e fluxos futuros.
- Capital: ações ON/PN, tesouraria, direitos, composição da unit e desdobramento. Confirmar fatores em documento vigente; unit não é novo capital somável às ações subjacentes.
- Último balanço versus preço de outubro: coletar movimentos/estimativas necessárias à ponte temporal. O caixa de janeiro a outubro não deve virar todo fluxo futuro de 2026. A implementação do stub e do DCF fica para o plano 05; a coleta precisa expor a lacuna e seus insumos.

**Saída:** histórico financeiro candidato, conciliações e lista de divergências com materialidade. Não preencher automaticamente passivo desconhecido com zero.

### E5 — extração operacional, regulatória e setorial

Usar `metric_dictionary.csv` como lista de perguntas, não como garantia de divulgação. Para cada indicador, registrar numerador/denominador, unidade, período e perímetro. Criar `definition_id` específico quando houver diferença metodológica. Não fabricar uma série contínua atravessando mudança de definição.

Pacotes mínimos por empresa:

1. Perdas com a definição disponível; cobertura/coleta/tratamento de esgoto separados; água; qualidade/resiliência quando divulgadas; tarifa social e capacidade de pagamento.
2. Metas, ligações/entregas e capex por período, com realizado versus anunciado e abertura expansão/manutenção quando disponível.
3. Regulação: autoridade competente para o contrato/data, revisão/reajuste, WACC em base real/nominal e pré/pós-impostos, remuneração de ativos, compartilhamento de ganhos, glosas e custos de execução.
4. Prazos e renovação/indenização das concessões materiais. Não aplicar a mesma data nacional ou uma perpetuidade a todos os contratos por conveniência.

Não confundir perdas físicas, aparentes, distribuição e faturamento; nem cobertura populacional com parcela do esgoto coletado tratada. Se a informação não permitir homogeneização, manter `incompatible` para ranking e uma descrição qualitativa com evidência. Falta de métrica não equivale a pior desempenho.

Para a ponte ESG, testar disponibilidade antes de prometer cálculo: volume e custo variável evitável para perda física; energia/preço/volume para intensidade energética; capex, entrega, receita e reconhecimento para expansão. Ganho bruto não é ganho retido pelo acionista. Se faltar insumo, selecionar alternativa e registrar a decisão.

No setor: um indicador nacional validado do [SINISA](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/resultados-sinisa/resultados-sinisa-2025), metas do [Marco Legal](https://www.gov.br/cidades/pt-br/assuntos/saneamento/marco-legal-do-saneamento) com ressalvas contratuais, um caso de competição/entrada/expansão e um de tecnologia com canal econômico. Não confundir concorrência pelo contrato com competição irrestrita na mesma rede, nem anúncio com execução.

Calendário de resultados e eventos deve ter publicação/ocorrência e fonte; emergência temporária não é automaticamente situação vigente. Ratings/índices, quando usados, precisam de provedor/vigência e ficam como evidência complementar.

**Saída:** indicadores com definições, termos contratuais, evidências qualitativas e diagnóstico de comparabilidade das três empresas.

### E6 — normalização, seleção e revisão

Manter todos os candidatos na camada intermediária; escolher explicitamente a observação preferida. Chave semântica para evitar duplicação: empresa/papel + métrica + período/data + escopo + definição + tipo de fato. Fonte/versão identificam candidatos; a base canônica não pode somar candidatos concorrentes.

Hierarquia contextual: documento oficial contábil/regulatório e nota explicativa para fatos; release oficial para ajuste operacional definido; Bloomberg para cotação/consenso identificado e checagem; planilha local como indicação a verificar. Não usar essa ordem para sobrescrever diferença legítima de conceito/perímetro. Duas fontes com valores distintos exigem explicar definição, escala, data, versão e arredondamento antes da escolha.

Separar verificação técnica de julgamento econômico. O agente verifica fonte, extração, conciliações e seleção; registrar IDs, responsável efetivo, data e justificativa em `data/catalog/review_decisions.csv`, a implementar. Encaminhar julgamentos materiais não resolvidos a H08 com alternativas e impacto. Não inventar assinatura humana nem exigir aprovação de toda célula. Pendências não críticas não devem parar tarefas independentes.

Atualizar `coverage.csv` por requisito, empresa e período: `not_started`, `downloaded`, `extracted_pending_review`, `verified`, `reconciled`, `not_disclosed`, `incompatible` ou `blocked`. Cobertura não se resume a contar células preenchidas. `not_disclosed` e limitação aceita exigem tentativas/fonte e efeito na análise registrados.

**Saída:** tabelas normalizadas com seleção rastreável, conflitos tratados e fila de lacunas prioritárias.

### E7 — QA e critérios de prontidão

Implementar testes para erros materiais, sem reproduzir apenas a implementação:

1. Duplicação de cadastro/classes não multiplica a DRE; unit não aumenta capital emitido.
2. Dinheiro em milhares/milhões, ações, razões percentuais e pontos percentuais convertem uma única vez; preservar sinais e fonte original.
3. Seleção de consolidado/período/versão, conta sintética e filha; acumulado versus trimestre; balanço não anualizado.
4. Publicação após corte, falta de localização/fonte e data de consulta insuficiente impedem promoção indevida. Corte `null` impede pacote final.
5. Definições incompatíveis de perdas/esgoto/tarifa social não entram em ranking; dado ausente não vira zero.
6. Arquivo de erro HTML, ZIP inválido, duplicação por hash, resposta de API vazia e metadados Bloomberg incompletos geram diagnóstico identificável.
7. B3 permanece manual. Modo offline não faz requisição nova. Reexecução com cache não altera a base arbitrariamente.
8. Conciliações relevantes do EBITDA, dívida/caixa, precatório e capital possuem evidência; tolerâncias seguem arredondamento/precisão da fonte, sem absorver diferença material.

Os relatórios implementados são `outputs/qa/relatorio_validacao.md`/`execution_validation.json`, além de auditorias de entradas, extração, pacote e recálculo da planilha. `validacao_coleta.md` era uma saída proposta, não um arquivo existente. Testes de cálculo já existem, mas aprovação estrutural ou matemática não certifica hipóteses econômicas.

**Portão para modelagem:** dados financeiros/mercado e ajustes críticos conciliados ou limites de impacto explicitamente aceitos no escopo; base operacional comparável/ressalvada para cinco fatores; pelo menos uma ponte com insumos suficientes ou reformulação documentada; recorte definido; rastreabilidade completa dos números que serão usados. A prontidão se refere aos dados, não à validação da recomendação. Se o precatório/classes/preço/contabilidade continuarem indeterminados em grau que possa inverter a escolha, emitir rascunho com bloqueios; não certificado final.

A tarefa D00/H07 de confirmar as orientações do Safra é P0 para a entrega da competição, mas sua pendência isolada não impede liberar uma base de dados que cumpra os critérios acima. Mantê-la no relatório como pendência operacional; não declarar conformidade com a competição. A fila deve distinguir os P0 aplicáveis à prontidão dos dados dos que bloqueiam a entrega audiovisual posterior.

### E8 — pacote de coleta e passagem para o plano 05

Gerar em `outputs/final/coleta/`, somente quando aprovado pelos critérios:

| Arquivo | Conteúdo |
| --- | --- |
| `LEIA_PRIMEIRO.md` | Versão, recorte, como abrir, limitações e próximos passos |
| `base_dados_coletados.xlsx` | Cadastros, fontes, financeiros, mercado/capital, ESG, definições, regulação, estimativas, ajustes e cobertura |
| `relatorio_cobertura.md` | O que existe por empresa/período, lacunas, comparabilidade e efeitos |
| `pendencias.csv` | Dado, impacto, responsável, tentativa, alternativa e prazo |
| `model_inputs.json` | Histórico e dados de referência com IDs/unidades; premissas propostas explicitamente separadas e sem validação implícita |
| `manifest.json` | Configuração/recorte, consultas, hashes, fontes/versões, decisões, testes e status de prontidão |

As tabelas em `data/processed/` continuam sendo a fonte de verdade; o XLSX é uma visão da base, não planilha preenchida manualmente em paralelo. Proteger a relação entre a base e seu manifesto. Em rascunho, gerar o mesmo formato em `outputs/draft/coleta/` com marcação visível de pendências.

Atualizar N01–N25 distinguindo `inputs_ready` de `analysis_completed`. DCF, cenários, waterfall, preço estimado, slides e fala seguem no plano 05 e não são declarados prontos pela entrega de dados.

## 5. Interface de execução atual

`scripts/run_esg.py` coordena os estágios. O coletor direto aceita `--offline` e `--keys`, não os antigos subcomandos inventory/fetch-public/import-manual/release. As rotas públicas estão implementadas; importação Bloomberg genérica e seleção por `--task Dxx` ainda não existem.

```powershell
python scripts/run_esg.py --stage collect --mode draft --offline
python scripts/collect_data.py --keys cvm_cadastro
python scripts/extract_data.py --cvm
python scripts/run_esg.py --stage model --mode draft --offline
python scripts/run_esg.py --stage validate --mode draft --offline
python scripts/run_esg.py --stage package --mode draft --offline
python scripts/run_esg.py --stage docs
python scripts/sync_project_docs.py --check
```

`run_esg.py --stage all --offline` refaz os estágios com cache; `--refresh` reextrai CVM/SINISA. `--stage collect` sem offline consulta fontes. O empacotamento não adquire arquivos novos. O modo final é recusado incondicionalmente: implementar/testar liberação por critérios é pendência A11. Atualizar o estado central e verificar a documentação ao encerrar mudanças.

## 6. Sequência, prazo e decisões de corte

1. **0–1 h útil:** inventário, schemas e pedidos humanos; começar público sem esperar Bloomberg.
2. **1–3 h:** agente implementa cliente/cache, consulta CVM/BCB e pesquisa documentos/regulação/ESG em frentes independentes; operador prepara H01 e grupo reúne H07.
3. **3–6 h:** extração, importação humana e conciliações, começando por capital/dívida/precatório e insumos da ponte.
4. **6–8 h:** normalização, cobertura, revisão cruzada e primeiro pacote para modelagem; manter pendências visíveis.

Estimativa para o núcleo com ajuda dos quatro e reaproveitamento dos materiais; não promessa de oito horas para pesquisa exaustiva. Ao surgir um problema material, priorizá-lo e avisar impacto no calendário. Entregar um rascunho cedo permite iniciar a modelagem sem confundir o que está revisado com o que está pendente.

Limites de tentativa: API Bloomberg 15 min; fonte indisponível 20 min de tentativas úteis antes de caminho alternativo; resposta 403 não recebe loop. Cortar P1/P2 antes de tirar conciliação crítica. Se não houver custo físico/definição confiável, mudar a ponte em vez de fabricar o input. Não ampliar a pesquisa para dezenas de empresas ou montar infraestrutura de serviço.

## 7. Auditoria deste plano e cuidados já incorporados

| Gap identificado | Solução |
| --- | --- |
| Organização quebrar os caminhos e perder versões | Mapa de dez movimentos, hashes e referências atualizadas; cartas preservadas no lugar |
| Três papéis Sanepar duplicarem seus financeiros | Cadastro de empresas separado de instrumentos |
| Lista de URLs parecer coleta pronta | `source_registry` separado de `sources` adquirido e de `observations` |
| Entrada local “conferida” virar fato sem documento | Extração candidata com aba/célula; promoção exige procedência |
| Não haver campos para definições, contratos ou consenso | Tabelas específicas preparadas; evidência não numérica preservada |
| Planilha de coleta divergir dos CSVs | XLSX exportado da base canônica, sem edição paralela |
| Todo indicador do dicionário virar obrigação artificial | Prioridades condicionais e cobertura com limitações justificadas |
| Automatização ultrapassar acesso disponível | Exportação Bloomberg; B3 manual; fallback documentado |
| Corte desconhecido invalidar a retrospectiva | Permitir rascunho, bloquear pacote final até fixar o recorte |
| Base preenchida ser confundida com tese validada | Separar prontidão dos dados, modelagem, recomendação e produção |

Ao terminar a implementação, verificar novamente o inventário, vínculos entre arquivos/tabelas e todos os P0 aplicáveis à prontidão dos dados. Documentar desvios, executar QA e atualizar o plano humano com o estado efetivo, mantendo as pendências da competição separadamente identificadas. Não marcar a etapa de dados como concluída enquanto faltar dado crítico ou a revisão de sua limitação.

## 8. Exemplo de consulta Focus preservado

A construção abaixo funcionou no teste de 31/10/2026; adaptar anos e limite ao recorte efetivo. Retorno pode ser anterior ao último dia pedido. Não transformar a data retornada na data solicitada.

```python
from urllib.parse import urlencode, quote
import requests

endpoint = ('https://olinda.bcb.gov.br/olinda/servico/Expectativas/'
            'versao/v1/odata/ExpectativasMercadoAnuais')
params = {
    '$filter': "Indicador eq 'IPCA' and Data le '2026-10-30' "
               "and DataReferencia eq '2027' and baseCalculo eq 0",
    '$orderby': 'Data desc', '$top': '1', '$format': 'json',
}
url = endpoint + '?' + urlencode(params, quote_via=quote)
response = requests.get(url, timeout=30)
response.raise_for_status()
rows = response.json()['value']
```
