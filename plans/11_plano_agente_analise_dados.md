# Parte 1 — execução autônoma de dados e análise econômica

<!-- PROJECT_STATUS:START -->
> [Estado central do projeto](../ESTADO_DO_PROJETO.md) · Revisão documental: 01/11/2026. Plano de método e critérios; conclusão de cada fase depende de evidência.
<!-- PROJECT_STATUS:END -->

Plano de implementação; **a criação deste arquivo não executou as tarefas abaixo**. Especificação revista em 01/11/2026. Esta parte entrega a pesquisa, os cálculos e a proposta que sustentam a apresentação ESG da asset.dev sobre Sabesp, Copasa e Sanepar.

Validação da revisão: [cobertura e estrutura](../outputs/qa/two_part_plan_validation.json) e [revisão com casos de falha](../outputs/qa/two_part_plan_review.json). Os dois planos cobrem os29 requisitos conhecidos, oito famílias de entregáveis e13 condições humanas. A checagem não certifica projeções futuras nem elimina a possibilidade de H07 acrescentar instruções ainda desconhecidas.

## Resultado e independência

Entregar um pacote analítico reproduzível: dados conciliados, definições, premissas fundamentadas, DCF revisado, cenários, matriz/ponte ESG, proposta de recomendação, duas planilhas e evidências de qualidade. O resultado deve permitir comparar as empresas, defender as conclusões e atualizar os materiais sem digitar números nos slides.

**Esta parte começa e entrega sua proposta sem qualquer saída nova da outra parte.** Usa os arquivos atuais, pesquisa pública e o contrato abaixo. Não modifica a apresentação nem espera sua implementação. A revisão H08/H09 é necessária para registrar a adoção pelo grupo; sua ausência não impede entregar uma proposta fundamentada. Pesquisa pública material ainda não feita não pode ser disfarçada como dependência humana.

A independência é de execução e teste. A apresentação definitiva continuará dependendo do conteúdo revisado deste pacote e dos registros humanos aplicáveis. Não se promete independência entre a conclusão financeira e a mensagem final que a utiliza.

## Antes de executar

1. Ler [AGENTS](../AGENTS.md), [estado](../ESTADO_DO_PROJETO.md) e [continuidade](../EXECUTION_CONTEXT.md). Consultar o [contrato09](09_contrato_de_fechamento.md) e os requisitos selecionados em [completion_requirements.json](../data/catalog/completion_requirements.json). Fontes, alternativas e aceite por requisito estão nesse catálogo; não substituí-los por outra lista informal.
2. Validar o plano com o comando existente `.venv/Scripts/python.exe scripts/validate_two_part_plans.py`. Conferir ambiente/recuperação no contexto operacional: há arquivos locais ignorados, não há Git neste workspace e uma cópia nova pode não conter dados brutos ou outputs.
3. Fixar identidade/hash dos insumos em `data/interim/analysis/baseline/`. Copiar os arquivos necessários, inclusive os dados canônicos atuais e módulos legados utilizados. Fazer a cópia antes de qualquer publicação global; registrar nomes, hashes, versão do Python/dependências e configurações. Depois trabalhar com essa cópia, não com arquivos canônicos que outro processo possa atualizar.
4. Preservar avaliação/preços de **30/10/2026** e corte informacional de **31/10/2026 18:25:27 -03:00**. O balanço de junho exige ponte temporal; não passa a ser balanço de outubro. Fonte publicada depois do corte não serve de evidência ex ante: guardar separadamente, ou abrir nova versão com novo recorte explicitamente aprovado pelo objetivo vigente.

O ramo legado reproduz os originais; o ramo revisado deve consumir entradas escolhidas e rastreáveis. Não editar caches ou originais para fazer um teste coincidir.

## Autoria e escrita

<!-- TWO_PART_PATHS:START -->

Escrita exclusiva de trabalho:

- `analysis/`
- `tests/analysis/`
- `data/raw/analysis/`
- `data/interim/analysis/`
- `data/processed/analysis/`
- `outputs/draft/analysis_bundle/`
- `outputs/qa/analysis/`
- `data/catalog/parallel_progress/analysis.json`

Insumos existentes para iniciar, somente leitura:

- `data/catalog/completion_requirements.json`
- `data/catalog/cell_issue_mapping.csv`
- `config/collection.json`
- `data/processed`
- `data/interim/acquisitions`
- `data/interim/pdf_text`
- `resources/modelos_originais`
- `outputs/qa/extended_input_audit.csv`

<!-- TWO_PART_PATHS:END -->

Os15 originais ativos inventariados permanecem intactos; o áudio foi retirado do escopo por solicitação do usuário. Os módulos financeiros legados listados no catálogo desta divisão são somente leitura. Desenvolver em `analysis/`, com caminhos de entrada/saída explícitos; não alterar `common.ROOT` globalmente e não importar módulos em edição pela parte de produção. Se aproveitar uma rotina antiga, fixar sua versão ou portar a função para o namespace próprio, com a origem registrada.

Registrar progresso em `data/catalog/parallel_progress/analysis.json`. Atualizações de catálogos, README, estado, continuidade e qualquer sincronização/globalização exigem exclusão de escrita por **`data/interim/coordination/documentation.lock`**, criado atomicamente com dono, início e operação. Essa trava é um protocolo a implementar com biblioteca padrão, não uma ferramenta já instalada. Liberar em `finally`; não apagar trava ativa de outro processo. Enquanto estiver ocupada, continuar trabalho local. Conferir os módulos de documentação antes de chamar o sincronizador, pois a outra parte pode estar editando-os. Toda escrita global derivada do sincronizador também fica dentro da trava. Nunca substituir decisões humanas ou fechar sozinho uma fatia compartilhada.

## Sequência de execução e aceite

As dependências AN são internas. AN03, AN04, AN05 e AN11 podem avançar depois do inventário; a ordem numérica não impõe espera desnecessária. AN11 fecha por aquisição efetiva **ou omissão justificada** do complemento. Não esperar Bloomberg para fazer o núcleo público.

<!-- TWO_PART_TASKS:START -->

| Tarefa / depende de | O que fazer e por quê / cobertura | Aceite |
|---|---|---|
| **AN01 — Fixar fotografia e entradas** / início | Ler contexto e contrato1.0, verificar originais/fontes/cache e congelar cópia/hash dos insumos usados no namespace da análise; não depender de arquivos canônicos que a integração poderá substituir. (C27) | Inventário de entradas verificável, recortes preservados, nenhuma escrita em cache/original compartilhado e runner local com raízes explícitas. |
| **AN02 — Resolver histórico e definições** / AN01 | Tratar as64 células abertas e base efetivamente usada: construção, EBITDA, capex caixa, giro, zeros Sanepar, precatório/recorrência/imposto e doações. Usar notas/contas e registrar disposição por célula. (C02, C03, C04, C05, C06, C07, C08) | Nenhum fato material usado fica sem definição/fonte; diferenças são conciliadas ou retiradas/limitadas com motivo e efeito demonstrados, sem alterar originais. |
| **AN03 — Conferir mercado, capital e direitos** / AN01 | Reconciliar cinco referências30/10, capital emitido/tesouraria, eventos, classes/unit, precisão e perímetro. Buscar fontes públicas antes de depender de H01. (C09) | Preço e denominador compatíveis; eventos/ausência de eventos têm busca datada e classes têm alocação justificada, não free float ou preço médio indevido. |
| **AN04 — Fechar saldos e obrigações identificadas** / AN01 | Conciliar dívida/caixa, caixa vinculado, leases, PPP, derivativos, outorgas, minoritários e ativos/obrigações não operacionais; preparar cronogramas por natureza e explicar diferenças para o release. (C10) | Saldos e definições rastreáveis, componentes sem duplicação e calendário/evidência disponíveis para o tratamento econômico posterior. |
| **AN05 — Completar contratos, ESG e setor** / AN01 | Obter regras contratuais materiais/vigências, KPIs dos cinco fatores, metas, resiliência/acesso, SWOT, tecnologia, participantes e eventos; separar anúncio, execução e futuro. (C15, C16, C18) | Afirmações têm definição/período/perímetro e consequência; lacunas são delimitadas sem inventar comparação ou exigir todos os anexos municipais. |
| **AN06 — Fundamentar operações e desconto** / AN02, AN03, AN04, AN05 | Construir trajetória2026–35 e faixas de volume/tarifa/margem, D&A, capex/giro/imposto, macro e custo de capital; separar WACC regulatório, econômico e taxa soberana. (C13, C14) | Cada driver tem base/evidência, escolha e alternativa; não há calibração para atingir cotação desejada nem alíquota extraordinária perpetuada. |
| **AN07 — Datar precatório e ponte até avaliação** / AN04, AN06 | Modelar descontos/investimentos/atualização/impostos e consumo do precatório, ponte junho→outubro e fluxo remanescente2026; testar calendário e sazonalidade sem fabricar realizado. (C11, C12) | Ajuste incremental/fluxos não duplicam caixa, tarifa, giro ou capex; último balanço e estimativa de outubro não são confundidos. |
| **AN08 — Revisar DCF, terminal e ponte ESG** / AN05, AN06, AN07 | Implementar ramo revisado com entradas selecionadas, preservar reprodução legada, tratar reinvestimento/concessões/indenizações e calcular energia→FCFF→PV com custos/retenção e sobreposição explícitos. (C15, C17) | Taxas/fluxos/terminal coerentes, peso do terminal explicado e alavanca ESG apresentada apenas no grau de evidência disponível. |
| **AN09 — Propor decisão e conteúdo econômico** / AN03, AN05, AN08 | Preparar empresa/papel, faixa ou condição de entrada, quatro cenários, três riscos/gatilhos com métrica/limite/data/ação, objeção e cinco julgamentos. Exportar claims semânticos e os dez slots narrativos, sem decidir layout. (C19, C20) | Proposta defensável com fontes e alternativas; inferência, hipótese e fato separados; nenhuma aprovação do grupo ou probabilidade inventada. |
| **AN10 — Exportar e validar pacote analítico** / AN09 | Gerar todos os arquivos mínimos1.0 e duas planilhas; incluir resíduo/validade por cenário e ponto, testar matemática/dados/linhagem e publicar pacote completo com hashes e qualidade. (C21, C22, C23) | Pacote autoconsistente, referências resolvíveis e casos sem alvo tratados; XLSX/Python reconciliados conforme ferramentas disponíveis; o ramo legado continua reproduzível. |
| **AN11 — Tratar complementos somente se aplicáveis** / AN01 | Importar dados Bloomberg autorizados se fornecidos/necessários, com campos/unidades/data confirmados; manter substitutos públicos e omitir estudos não selecionados. Se complemento mudar a tese, repetir as etapas afetadas. (C29) | Nenhum consenso, índice, beta, causalidade ou dado verde não adquirido é prometido; dependência opcional não paralisa o núcleo. |
| **AN12 — Entregar proposta e incorporar decisões reais** / AN10, AN11 | Entregar checklist curto H08/H09 e evidências; atualizar progresso/contexto. Se decisões reais chegarem, recalcular e publicar nova versão1.0 com a deliberação referenciada, preservando a anterior. (C19, C27) | Entrega autônoma utilizável para revisão e integração; ausência humana fica registrada, sem concluir análise pública que ainda não foi executada nem marcar julgamento ausente como aprovado. |

<!-- TWO_PART_TASKS:END -->

## Como executar a pesquisa e a conciliação

Começar pelo cache: [fontes](../data/processed/sources.csv), [documentos CVM](../data/processed/cvm_documents.csv), [contas](../data/processed/cvm_accounts.csv), metadados em `data/interim/acquisitions/` e textos em `data/interim/pdf_text/`. Os endereços/rotas concretos estão nos campos de fontes de cada C02–C18 e no [plano07](07_plano_coleta_dados_agente.md). Em novos acessos, preferir CVM, RI das empresas, ARSESP, ARSAE-MG, AGEPAR, SINISA/SNIS, BCB/Focus e Tesouro. Buscar/verificar na fonte primária antes de incorporar um fato novo. Registrar URL, arquivo original, hash, publicação, período e página/conta. HTTP403 não prova ausência; tentar a rota pública alternativa permitida, sem inventar acesso.

Para cada uma das **64 células abertas** do [mapa](../data/catalog/cell_issue_mapping.csv), formar uma linha de conciliação; não recontar as 131 coincidências como 131 revisões econômicas. C02 tem dez células Sabesp construção; C03 cinco de EBITDA; C04 quatro de capex Sabesp; C05 trinta de ativos/passivos operacionais; C06 cinco de capex Copasa; C07 dez zeros de construção Sanepar. C08 cobre recorrência e tributos além dessa contagem. Diferença contra a CVM não é automaticamente erro da planilha.

Usar o esquema de `financial_reconciliation.csv` do contrato09, no diretório próprio: empresa, período, célula/conceito, valor original e selecionado, fonte/localizador, escopo, sinal, unidade/escala, componentes, transformação, disposição, justificativa e efeito no cálculo. Para cada item, escolher entre confirmado, corrigido, reclassificado, exclusão fundamentada ou limitação com alternativas quantificadas. Ausência de divulgação não autoriza zero. Só marcar resolução quando a definição econômica e o efeito estiverem demonstrados.

- **Sabesp:** separar serviço, construção, margem de construção, remuneração do ativo financeiro, itens de EBITDA e investimento efetivamente pago. Reconstruir pontes reportado→ajustado→recorrente; não somar remuneração regulatória duas vezes.
- **Copasa:** distinguir investimento contábil, adições, caixa e eventuais outorgas; conciliar empréstimos, debêntures, leases, derivativos, caixa restrito e passivos de concessão antes de definir dívida líquida.
- **Sanepar:** verificar se zeros de construção significam inexistência, apresentação líquida ou falta de mapeamento; separar efeito de precatório, impostos e receitas não recorrentes. O plano2026–30 de R$13.077 milhões inclui redes doadas de R$212,8 milhões; não transformar todo investimento econômico em desembolso da empresa.
- **Unidades e escopo:** CVM `MIL` monetário exige escala; lucro por ação não é milhão de reais. Sabesp2021–22 individual não é automaticamente comparável ao consolidado posterior; Sanepar individual não implica dados de consolidação. Participação não controladora zero só com fundamento no escopo. Usar conceito/período/entidade da conta, não apenas número parecido.

### Capital, obrigações e tempo

AN03 verifica preços da mesma sessão, ações emitidas/em tesouraria, classes, eventos e data efetiva. Os fechamentos públicos atuais são referências ainda sem confirmação Bloomberg/B3. Exportação recebida deve conter identificador, campo, moeda, unidade, data e origem; divergência exige conciliação, não substituição silenciosa. No cadastro CVM, conferir escala de capital empresa a empresa. Unit SAPR11 contém 1ON+4PN e não acrescenta ações ao capital; não precificar ON/PN por uma regra de igualdade não declarada. A preferência de dividendo não garante razão fixa de preços. Tratar explicitamente a ação especial da Sabesp e o denominador de ações econômicas.

AN04 identifica dívida financeira, outros direitos/obrigações, caixa e tratamento no FCFF ou na ponte EV→acionista. AN07 constrói `obligation_schedule.csv`: obrigação, data, indexador, componente tarifa/capex/financeiro, valor, unidade, hipótese/fonte e convenção de desconto. Primeiro identificar os fluxos; depois descontá-los com a taxa coerente definida em AN06.

O passivo regulatório do precatório Sanepar de R$4.407,957 milhões **não é seu VPL**. Modelar desconto tarifário e investimentos não onerosos, atualização por taxa real/IPCA e calendário verificável. Sem calendário divulgado, usar alternativas limitadas e identificadas; não inventar distribuição anual. Uma mesma obrigação entra uma vez: no fluxo, na tarifa/capex ou na ponte de valor. Dedução nominal integral é diagnóstico, não faixa de valor justo.

Conciliar junho→outubro com geração de caixa, dividendos/JCP, dívida, capex, eventos de ações e mudança de data. Separar saldo observado e rollforward estimado. O rateio remanescente de2026 **já existe** nos originais (62/365); auditar convenções e evitar acrescentar outro stub sobre o mesmo período.

### Projeção, desconto e terminal

Construir trajetórias com volumes/ligações, tarifas e revisões, perdas, custos de energia/pessoal, margem recorrente, D&A, capex, giro e impostos. DRE isolada não determina investimento, dívida ou FCFF. Separar projeção divulgada, hipótese da equipe e extrapolação. Registrar justificativa, fontes, unidade, intervalo e sensibilidade de cada premissa material; não ajustar premissas só para obter um preço desejado.

Explicitar FCFF = EBIT após imposto + D&A − capex − variação do giro, reconciliando com a contabilidade e com exclusões regulatórias. Custo de capital exige coerência de moeda, inflação, horizonte, taxa real/nominal, antes/depois de imposto, alavancagem e data. A curva Focus adquirida termina em2030; os anos seguintes são hipóteses próprias. Taxa soberana não é automaticamente WACC. Sem beta/estrutura defensáveis, usar faixas justificadas e declarar o alcance, sem alegar estimação inexistente.

Para cada caso, testar `WACC > g`, tributação e reinvestimento que sustente crescimento (ROIC/margem/rotação coerentes). Não aplicar perpetuidade uniforme até2048 às três empresas. Selecionar fluxo até vencimento/reversão, renovação explicitamente assumida ou continuidade com reinvestimento; reconhecer incerteza contratual. Projetar crescimento perpetuamente sem o reinvestimento necessário superestima valor.

Manter EV, dívida/caixa/outros ajustes, participação e quantidade de ações auditáveis. Resíduo acionário não positivo significa **ausência de alvo significativo nesse cenário**, não preço justo zero/negativo, falência ou retorno de−100%. Todos os cenários e pontos da grade precisam guardar resíduo bruto e validade; isso hoje falta em57 pontos. A XTIR baseada em EV/FCFF mede fluxos da firma, não retorno esperado do acionista; não usar como ranking de retorno acionário sem reconstrução apropriada.

### ESG, comparação e recomendação

Preservar os cinco fatores materiais já mapeados, completando apenas lacunas que possam mudar a tese. Para cada KPI, registrar população/base, abrangência, período, definição e qualidade. Perdas em litros/ligação/dia de2024 e LTMjunho/2026 não viram uma série uniforme. Coleta/tratamento e denominadores populacionais distintos não sustentam ranking direto. Valor municipal SINISA não equivale automaticamente à operação consolidada; conferir companhia/UF e homônimos.

A ponte exige KPI→efeito operacional→receita/custo/capex/tributo→caixa→valor. A sensibilidade atual de1% de despesa de energia, retenção50/100%, não é economia realizada nem projeto identificado. Separar ganho bruto, repasse tarifário, custo de implantação, calendário e risco; não somar o ganho a uma margem que já o incorpora. Custo de energia por município não é custo marginal de água perdida. Se só houver sensibilidade, denominá-la assim e mostrar capex de equilíbrio, sem inventar causalidade.

Produzir SWOT, médio prazo, tecnologia, competição/regulação e eventos relevantes com fatos e inferências separados. Comparar mesmo preço/data e casos coerentes; não privilegiar Sanepar porque o rascunho a propôs. É aceitável recomendar condição de entrada/monitoramento se o preço não sustentar compra. Criar gatilhos com métrica, limite, data/frequência e ação; probabilidades exigem fundamento ou ficam ausentes.

AN09 escreve argumentos e as dez posições narrativas do contrato, sem definir layout: mensagem principal, setor, SWOT, médio prazo, ESG, ponte, método, resultado, riscos e conclusão. Cada afirmação numérica ou factual recebe ID e evidência; a narrativa não deve conter número novo sem referência. Propor premissas e recomendação para H08/H09 com alternativas e consequências, em vez de pedir ao grupo que descubra o modelo.

## Interface de entrega — contrato comum 1.0

Esta interface está repetida nos dois planos e deriva do mesmo [catálogo de execução](../data/catalog/two_part_execution.json). A implementação deve transformá-la em esquema/testes antes de calcular os resultados. A parte de apresentação não precisa importar código analítico.

<!-- TWO_PART_CONTRACT:START -->

Versão: **1.0**. Produtor `analysis`; consumidor `production`. Diretório `outputs/draft/analysis_bundle/<bundle_id>/`.

Arquivos mínimos (incluem arquivos de auditoria, não só dados de renderização):

- `manifest.json`
- `metadata.json`
- `model_inputs.json`
- `relatorio_cobertura.md`
- `tables/entities.csv`
- `tables/instruments.csv`
- `tables/sources.csv`
- `tables/observations.csv`
- `tables/definitions.csv`
- `tables/assumptions.csv`
- `tables/adjustments.csv`
- `tables/regulatory_terms.csv`
- `tables/corporate_actions.csv`
- `tables/financial_reconciliation.csv`
- `tables/obligation_schedule.csv`
- `tables/claims.csv`
- `results/valuation.json`
- `results/scenarios.json`
- `results/esg_matrix.json`
- `results/esg_bridge.json`
- `results/presentation_facts.json`
- `results/narrative.json`
- `results/recommendation.json`
- `workbooks/base_dados_coletados.xlsx`
- `workbooks/base_modelo_auditavel.xlsx`
- `qa/analysis_validation.json`
- `LEIA_PRIMEIRO.md`
- `pendencias.csv`

| Objeto | Campos/estados normativos |
|---|---|
| Manifesto | `schema_version`, `bundle_id`, `kind`, `state`, `market_asof`, `valuation_date`, `information_cutoff`, `built_at`, `files`, `external_evidence`, `requirement_dispositions`, `human_records`, `limitations` |
| Estados analíticos publicados | `analysis_incomplete`, `analysis_proposed`, `group_adopted` |
| Observação/valor | `value_id`, `entity_id`, `instrument_id`, `metric_id`, `value`, `value_state`, `unit`, `scale`, `period_start`, `period_end`, `observed_at`, `scope`, `definition_id`, `fact_type`, `source_refs`, `assumption_refs`, `calculation_ref` |
| Estado do valor | `observed`, `derived`, `assumed`, `missing`, `not_applicable` |
| Cada case, inclusive grade | `case_id`, `entity_id`, `instrument_id`, `scenario_id`, `dimensions`, `value_refs`, `wacc`, `g`, `terminal_method`, `equity_residual_before_floor`, `equity_floor_applied`, `paper_value`, `target_validity`, `assumption_refs`, `limitations` |
| Validade do alvo | `conditional_value`, `no_meaningful_target`, `unresolved` |
| Afirmação | `claim_id`, `claim_type`, `text_template`, `value_refs`, `source_refs`, `assumption_refs`, `calculation_refs`, `status`, `limitations` |
| Slots narrativos | `lead`, `sector`, `swot`, `medium_term`, `esg`, `bridge`, `valuation_method`, `valuation_result`, `risks`, `conclusion` |

Cabeçalhos mínimos das tabelas de identidade e evidência; campos adicionais compatíveis são permitidos:

| Tabela | Campos |
|---|---|
| `entities.csv` | `entity_id`, `legal_name`, `cvm_code`, `cnpj`, `currency`, `identity_status` |
| `instruments.csv` | `instrument_id`, `entity_id`, `ticker`, `security_class`, `currency`, `bloomberg_security`, `unit_components`, `identity_status` |
| `sources.csv` | `source_id`, `issuer`, `title`, `url`, `local_path`, `published_at`, `retrieved_at`, `sha256`, `access_method`, `reference_date`, `version`, `access_status` |
| `definitions.csv` | `definition_id`, `entity_id`, `metric_id`, `numerator`, `denominator`, `unit`, `scope`, `methodology`, `methodology_valid_from`, `source_ids`, `comparability_status` |
| `assumptions.csv` | `assumption_id`, `entity_id`, `driver`, `year`, `base`, `adverse`, `favorable`, `unit`, `rationale`, `supporting_obs_ids`, `owner`, `reviewer`, `approval_status`, `source_id`, `source_location`, `value_refs` |

UTF-8; JSON estrito sem NaN/Infinity; CSV com cabeçalho, vírgula e decimal ponto, escape RFC4180. Listas/objetos nas células são JSON. Datas ISO8601; timestamps com fuso. Valor ausente é null no JSON e célula vazia no CSV, sempre acompanhado de value_state; zero só é observação/resultado fundamentado. value é número finito ou null; scale é multiplicador numérico para a unidade declarada; taxas usam fração, scale1 (12,5% = 0.125). Campos textuais de contexto ficam em definições/claims. fact_type distingue fact/assumption/inference/derived. missing/not_applicable exigem null e motivo, nunca número de substituição.

schema_version é a string 1.0. kind é analysis para pacote real publicado, baseline para adaptação provisória e fixture para teste; os dois últimos são recusados no carregador de pesquisa/release. files é lista de objetos path/bytes/sha256 relativos ao bundle, únicos e sem escape da raiz. external_evidence e human_records são listas com ID/caminho/hash/localizador/data, sem credenciais. requirement_dispositions é lista requirement_id/slice/status/evidence_refs/limitations. Estado group_adopted exige decision.status=adopted e referências reais H08/H09, além de análise elegível. Baseline e fixture só em execução explícita de rascunho/QA. supporting_obs_ids legados e obs_id, se mantidos, referenciam os mesmos IDs de value_id; não geram uma segunda série de valores. Campos que não se aplicam a uma linha ficam vazios com justificativa no registro associado.

Todo results/*.json contém schema_version, bundle_id e value_ids/referências resolvíveis em observations.csv. valuation/scenarios usam cases; esg_matrix usa rows; esg_bridge usa cases; presentation_facts usa views; narrative usa slots; recommendation usa objeto decision. Cada item tem ID único e referências, sem números duplicados em texto livre.

Cada view tem view_id, slot, view_type (table/bar/line/matrix/scatter/heatmap/bridge), title, series e claim_refs. Cada série tem series_id, label, points; cada ponto tem point_id, x_value_ref opcional, y_value_ref, case_ref opcional e claim_refs. Labels são texto, métricas/unidades/datas vêm dos value_refs. Grids referenciam cases completos, nunca preços sem validade. Cada ponto também tem label e point_role (ordinary/start/delta/end); no bridge, start/delta/end são declarados pelo produtor, não inferidos somando barras pela interface. case_ref liga cada opção/grade às dimensions do case.

Os dez slots são listas ordenadas de claim_ids; claims contêm text_template com tokens {{value:value_id}} e referências. decision contém status (proposed/adopted/unresolved), entity_id/instrument_id opcionais, rationale_claim_refs, alternative_claim_refs, trigger_claim_refs, human_record_refs. adopted exige registros reais H08/H09.

Cada fonte externa tem source_id, localização original, hash e localizador (página/conta/trecho/data). O manifesto inclui hash/bytes/path de cada arquivo exceto ele próprio; evidência externa deve ser copiada ou ter caminho resolvível com hash e licença/limitação declarada. QA identifica hashes das entradas/resultados excluindo o próprio QA e manifesto; o manifesto inclui o hash do QA. O consumidor registra separadamente o hash do manifesto validado.

value_refs mapeia os campos numéricos do case a value_ids com valores coincidentes; dimensions é mapa de eixos selecionáveis com IDs/tipos/unidades declarados (cenário, retenção, WACC, g etc.). Todos os pontos de grade são cases completos. paper_value exige número finito >=0 apenas com conditional_value e resíduo positivo; nos outros estados é null, nunca zero de piso. equity_floor_applied é booleano, resíduo bruto pode ser negativo/null; dado desconhecido não permite inferir validade. g pode ser null quando o método finito não o usa, com justificativa. Cada entrada de dimensions é axis_id -> {option_id, label, value_ref}; value_ref pode ser null em opção categórica, e a unidade/tipo numéricos vêm da observação referenciada. scenario_id identifica a alternativa econômica e não substitui case_id único.

Publicar diretório novo e completo, com arquivos/hashes e estado reais; só depois atualizar ponteiro de versão de forma atômica. O consumidor nunca lê a área de trabalho mutável da análise.

A engenharia adapta os arquivos atuais para este contrato com estado baseline_unreconciled fora da publicação analítica; faltas permanecem desconhecidas e controles correspondentes indisponíveis. Fixtures sintéticas só em QA, nunca no pacote de pesquisa.

Versão major desconhecida é rejeitada; campo adicional compatível não altera significado existente. Mudança material do contrato exige atualizar as duas especificações antes de integrar.

Cada parte grava part_id, task_id/status, requirement_slices, evidence_paths/hashes, unresolved, human_needed, next_action, updated_at no seu parallel_progress/<part_id>.json. Fechamento global de C compartilhado exige ambas as fatias e evidência humana aplicável.

<!-- TWO_PART_CONTRACT:END -->

Cabeçalhos existentes de entidades, instrumentos, fontes, definições e tabelas auxiliares devem ser preservados no adaptador legado; os campos normativos acima são a interface nova. IDs são únicos e estáveis. `instrument_id` pode ficar vazio em métricas corporativas; período ou localizador não aplicável deve vir com justificativa. Observação derivada exige cálculo e referências de entrada; premissa exige hipótese identificada; fato exige fonte. Campos CSV que contêm listas usam JSON, não separação ambígua por ponto e vírgula.

Tabelas regulatórias/ajustes/cronogramas seguem os esquemas analíticos do contrato09 e ficam disponíveis para auditoria; o consumidor não depende de suas fórmulas internas. `model_inputs.json` contém exatamente as entradas selecionadas do ramo revisado, com IDs de observações/premissas, configuração e origem; a análise deve poder ser refeita dele. `metadata.json` repete recortes/identidade e explicita escopo, método e limitações. `pendencias.csv` contém requisito, disposição, justificativa, bloqueio por estágio e evidência. `relatorio_cobertura.md` explica faltas e substitutos.

Casos de ESG e cenários ligam os mesmos valores e cases aos gráficos; sem nova matemática financeira na interface. `qa/analysis_validation.json` referencia hashes das entradas/resultados, excluindo ele próprio e o manifesto; o manifesto registra os hashes do QA e demais arquivos, excluindo o próprio manifesto. Isso evita autorreferência. O consumidor calcula o hash do manifesto ao registrar a integração.

Publicar primeiro em diretório temporário próprio, validar, renomear para um `bundle_id` novo e só então atualizar atomicamente `outputs/draft/analysis_bundle/latest.json` com ID/caminho/hash do manifesto. Não sobrescrever versão publicada. Fonte grande pode ficar externa somente com caminho resolvível/hash e limitação de transporte declarada. Arquivo vazio só é permitido para tabela legitimamente sem registros, com cabeçalho e disposição explícita; não usar vazio para fingir entrega completa.

## Implementação e testes

Criar CLI própria, por exemplo **futura** `.venv/Scripts/python.exe -m analysis.run --baseline <snapshot> --config <arquivo> --output <raiz>`. Esse comando ainda precisa ser implementado, com `--help` e erros acionáveis. Reutilizar o cache; downloads devem ser idempotentes, com timeout, controle de falhas e hashes. Testar uma empresa/conceito antes de ampliar. Não executar `run_esg --stage all/model` enquanto o runner legado escrever nos caminhos globais.

Verificações obrigatórias, proporcionais às mudanças:

- Todas as64 ocorrências com disposição/evidência, ou limitação fundamentada que impeça o uso indevido; nenhuma unidade, data ou escopo inferidos apenas para coincidir. Conciliar receita/resultado/balanço/DFC/capex no alcance disponível e explicar diferenças restantes.
- Casos numéricos independentes de FCFF, desconto com datas/stub, ponte EV→equity, classes/unit, terminal/ROIC e precatório sem dupla contagem; incluir resíduo não positivo, dado ausente, `WACC<=g` e dívida com fluxo já tratado.
- Recalcular as duas planilhas em cópia própria com LibreOffice/Excel quando disponível e comparar entradas, fórmulas e saídas com Python, usando tolerâncias declaradas por unidade. Erro ou indisponibilidade real é registrado; teste de recálculo não comprova a premissa econômica. A rotina local não depende de script mutável pertencente à produção.
- Validar contrato, hashes, referências e todos os cases, inclusive grade/sensibilidade. Nenhum NaN/Infinity ou zero de substituição. Claims e dez slots devem cobrir setor, SWOT, médio prazo, matriz, valuation, riscos e recomendação/condições.
- Preservar os15 originais ativos e a reprodução legada. Gerar QA própria em `outputs/qa/analysis/`, com snapshot, comandos, resultado, limites e próxima ação. Não atribuir a esta execução os13 testes/141 comparações/102 verificações de uma execução anterior.

## Fechamento, grupo e continuidade

O trabalho autônomo termina quando a pesquisa material foi executada, a proposta e suas alternativas são utilizáveis, o pacote pode ser reproduzido/consumido e os testes adequados passaram. Incerteza irredutível pode permanecer com evidência de busca, impacto e limite; não confundi-la com trabalho analítico adiado. H08/H09 ausentes mantêm estado de proposta, não bloqueiam o pacote autônomo. Decisão real posterior gera nova versão e revalida os resultados afetados.

H01–H06 são complementos quando selecionados e sem substituto suficiente; H12 só aparece por falha real de ferramenta/acesso. H07 fornece instruções privadas que o agente não pode adivinhar; verificar documentos fornecidos e requisitos públicos é trabalho do agente. H08/H09 exigem julgamento real do grupo. H10/H11/H13 — ensaios, clipes, revisão/envio — não são executáveis por esta análise. Registrar responsáveis e próximos passos sem inventar participação, aprovação ou comprovante.

As famílias G01/G02 e a planilha de G03 são produzidas aqui; suas cópias finais são publicadas pelo integrador. Os relatórios financeiros compõem a fatia analítica G08. A cobertura e as fatias compartilhadas estão abaixo. **Não fechar C19/C20/C21/C22/C23/C27/C29 globalmente só por terminar esta fatia.**

<!-- TWO_PART_SHARED:START -->

| Requisito compartilhado | Responsabilidade desta parte |
|---|---|
| C19 | Escolha econômica e alternativas propostas; tratamento das decisões reais do grupo. |
| C20 | Claims, fatos, premissas e referências semanticamente corretos. |
| C21 | Produzir arquivos e valores1.0, inclusive flags por caso e planilhas. |
| C22 | Qualidade dos dados, matemática, tratamento econômico e igualdade Excel/Python. |
| C23 | Conteúdo econômico e planilhas auditáveis. |
| C27 | Progresso/evidência do próprio trabalho e atualização documental serializada. |
| C29 | Obter/importar complementos somente se escolhidos e manter omissões justificadas. |

<!-- TWO_PART_SHARED:END -->

Ao terminar cada tarefa, atualizar o progresso próprio, as evidências do requisito e ambos os documentos centrais sob a trava. Executar os validadores documentais existentes e conferir suas saídas: `scripts/validate_completion_docs.py`, `scripts/validate_two_part_plans.py`, `scripts/sync_project_docs.py` e `scripts/sync_project_docs.py --check`, sempre com o Python da venv. Entregar ID/hash do pacote, testes reais, limitações, questões H08/H09 e próximo comando executável. Não declarar implementação concluída apenas porque este plano passou na validação documental.
