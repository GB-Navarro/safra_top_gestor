# Parte 2 — execução autônoma de apresentação e engenharia de entrega

<!-- PROJECT_STATUS:START -->
> [Estado central do projeto](../ESTADO_DO_PROJETO.md) · Revisão documental: 01/11/2026. Plano de método e critérios; conclusão de cada fase depende de evidência.
<!-- PROJECT_STATUS:END -->

Plano de implementação; **a criação deste arquivo não executou as tarefas abaixo**. Especificação revista em 01/11/2026. Esta parte transforma dados identificados em material de apresentação e implementa o sistema de integração, verificação e liberação da etapa ESG.

Validação da revisão: [cobertura e estrutura](../outputs/qa/two_part_plan_validation.json) e [revisão com casos de falha](../outputs/qa/two_part_plan_review.json). Os dois planos cobrem os29 requisitos conhecidos, oito famílias de entregáveis e13 condições humanas. A checagem não certifica projeções futuras nem elimina a possibilidade de H07 acrescentar instruções ainda desconhecidas.

## Resultado e independência

Entregar um sistema funcional com consumidor de dados, visualizações, PPTX9/PDF9, apoio técnico7, HTML interativo/PDF10, roteiro e teleprompters por perfil, perguntas, ferramentas de vídeo e liberação por estágio. Demonstrar tudo com a fotografia atual explicitamente provisória e fixtures separadas para estados que ainda não existem. Uma estrutura vazia ou dez imagens estáticas não cumpre esse resultado.

**Esta parte começa, implementa, testa e entrega o sistema sem qualquer saída nova da parte analítica.** O adaptador usa a base atual; o contrato abaixo permite trocar depois para um pacote revisado sem mudar o código. Testes sintéticos comprovam comportamento do software, nunca resultados financeiros ou participação real do grupo.

A versão definitiva integrada precisa de análise revisada e dos registros humanos aplicáveis. Essa é uma condição de conteúdo e liberação, não uma justificativa para esperar antes de implementar/testar a engenharia. Não declarar a recomendação final aprovada porque o sistema aceita um pacote de teste.

## Antes de executar

1. Ler [AGENTS](../AGENTS.md), [estado](../ESTADO_DO_PROJETO.md) e [continuidade](../EXECUTION_CONTEXT.md). Consultar [contrato09](09_contrato_de_fechamento.md), [plano HTML10](10_plano_html_interativo.md), [requisitos](../data/catalog/completion_requirements.json) e [mapa das dez páginas](../data/catalog/html_slide_plan.json). Não depender da leitura do plano da outra parte.
2. Validar a especificação com o comando existente `.venv/Scripts/python.exe scripts/validate_two_part_plans.py`. Conferir as ferramentas reais no contexto: Python/venv, PowerPoint/LibreOffice e encoder; navegador/automação de navegador ainda precisam de verificação nesta execução. Falha de ferramenta deve gerar tentativa de alternativa e relato concreto.
3. Congelar os insumos próprios em `data/interim/production/baseline/`: dados canônicos atuais, slides/PDF, roteiro, figuras, configuração, scripts legados necessários e hashes. Há nove slides principais, sete páginas de apoio e13 segmentos; não renumerar os originais.
4. Manter os recortes: preços/avaliação30/10/2026; informação31/10/2026 18:25:27 -03:00. Não atualizar cotações para a data da execução da interface. Verificar as regras públicas e documentos recebidos, registrar alterações e H07 ausente. O prazo público registrado é02/11; hora/canal/formato privado não foram confirmados. Nova conformidade exige evidência atual, não inferência do rascunho.

## Autoria e escrita

<!-- TWO_PART_PATHS:START -->

Escrita exclusiva de trabalho:

- `production/`
- `presentation_web/`
- `tests/production/`
- `data/interim/production/`
- `outputs/draft/production/`
- `outputs/qa/production/`
- `data/catalog/parallel_progress/production.json`
- `scripts/run_esg.py`
- `scripts/presentation.py`
- `scripts/render_slides.py`
- `scripts/package_outputs.py`
- `scripts/assemble_video.py`
- `scripts/validate.py`
- `scripts/recalculate_workbook_qa.py`
- `scripts/execution_status.py`
- `scripts/sync_project_docs.py`
- `scripts/validate_completion_docs.py`
- `config/video_segments.json`
- `config/production_profile.json`

Publicação somente pelo integrador, com trava/manifesto:

- `data/processed/entities.csv`
- `data/processed/instruments.csv`
- `data/processed/sources.csv`
- `data/processed/observations.csv`
- `data/processed/definitions.csv`
- `data/processed/assumptions.csv`
- `data/processed/adjustments.csv`
- `data/processed/regulatory_terms.csv`
- `data/processed/corporate_actions.csv`
- `data/processed/claims.csv`
- `data/processed/valuation.json`
- `data/processed/scenarios.json`
- `data/processed/esg_matrix.json`
- `data/processed/esg_bridge.json`
- `data/processed/presentation_facts.json`
- `outputs/final/`
- `outputs/draft/html/`
- `outputs/qa/html/`
- `data/interim/financial_reconciliation.csv`
- `data/interim/obligation_schedule.csv`
- `outputs/qa/relatorio_validacao.md`
- `outputs/qa/execution_validation.json`
- `outputs/qa/workbook_recalculation.json`
- `outputs/qa/package_validation.json`
- `outputs/qa/rendering.json`
- `outputs/qa/visual_review.json`
- `outputs/qa/release_validation.json`

Insumos existentes para iniciar, somente leitura:

- `data/catalog/completion_requirements.json`
- `data/catalog/html_slide_plan.json`
- `config/collection.json`
- `data/processed`
- `outputs/draft/apresentacao_esg.pptx`
- `outputs/draft/apresentacao_esg.pdf`

<!-- TWO_PART_PATHS:END -->

Implementar em `production/`, `presentation_web/` e nos módulos de produção atribuídos. Módulos financeiros legados e os15 originais ativos são somente leitura. Não alterar o modelo econômico, ajustar premissas, completar observações ausentes ou importar o código novo da análise. Renderizar cálculos publicados; transformação de unidade/forma deve preservar definição e referência. Não criar outro DCF em JavaScript.

Registrar progresso em `data/catalog/parallel_progress/production.json`. Qualquer escrita global — catálogos, README/estado/continuidade, sincronização e publicação canônica — exige exclusão por **`data/interim/coordination/documentation.lock`**, criada atomicamente com dono/início/operação e liberada em `finally`. A trava é protocolo a implementar, não recurso já disponível. Não apagar trava ativa. Fazer edições de módulos compartilhados da documentação e suas chamadas sob a mesma trava; a análise pode estar utilizando o sincronizador. Continuar implementação/testes locais enquanto o controle estiver ocupado.

Os caminhos legados de rascunhos, HTML e QA serão publicados só no momento de integração, com manifesto e exclusão de escrita; os diretórios de trabalho/teste são os próprios. Não executar o runner legado global sem antes implementar raízes explícitas. Nunca alterar o ambiente global `common.ROOT` para redirecionar efeitos colaterais.

## Sequência de execução e aceite

As dependências EN são internas. HTML, slides, roteiro e empacotador podem avançar em paralelo após o consumidor comum. EN11 é implementação/demonstração do integrador; importar depois o pacote real não é pré-requisito da entrega autônoma do software.

<!-- TWO_PART_TASKS:START -->

| Tarefa / depende de | O que fazer e por quê / cobertura | Aceite |
|---|---|---|
| **EN01 — Fixar contrato, baseline e regras** / início | Verificar ambiente, fontes públicas da competição e contrato1.0; congelar insumos atuais próprios, registrar H07 desconhecido e preparar testes de inputs/humanos ausentes sem pedir nova autorização para cada operação local. (C01, C27) | A parte inicia sem pacote da análise; baseline tem identidade/hash e estado provisório, e regras privadas não recebidas continuam desconhecidas. |
| **EN02 — Implementar consumidor e adaptador** / EN01 | Implementar leitura/validação1.0, adaptador do baseline e fixtures isoladas; resolver unidades, papéis, referências e validade de cada ponto, sem recalcular DCF ou completar lacunas com zero. (C20, C21) | Pacote válido é consumido; versão/arquivo/hash/referência inválidos são rejeitados; dados incompletos só habilitam controles/peças compatíveis com seu estado. |
| **EN03 — Criar visões e posicionamento de claims** / EN02 | Vincular claims/valores aos slots de9 e10 páginas; gerar figuras PNG/SVG/CSV, tabelas e fontes a partir de dados canônicos, com formatação consistente e estado N/D. (C20, C23) | Não há número/empresa/definição literal independente da entrada; matriz/figuras preservam escopo e não criam ranking ou alvo sem suporte. |
| **EN04 — Implementar HTML interativo de dez páginas** / EN03 | Implementar o plano10: arquivo único offline, SVG/HTML acessível, navegação/foco/fontes, retenção/cenários/grade disponíveis e impressão de dez páginas, sem publicação de site. (C28) | P01–P10 funcionam por duplo clique, sem rede; S7 foi dividido,560s planejados preservados e controles sem metadados completos ficam indisponíveis. |
| **EN05 — Regenerar PPTX9, apoio7 e PDF** / EN03 | Gerar material editável e estático por perfil, com fontes/notas e espaço de câmera; inspecionar todas as páginas e registrar hash/revisão. (C23) | PPTX9/PDF9 e apoio7 continuam distintos de HTML10/PDF10; nenhuma mudança global do teste9 apenas para fazer o novo perfil passar. |
| **EN06 — Gerar roteiro, falas e preparação humana** / EN03 | Gerar narrativa, falas exatas, teleprompters dos quatro, doze perguntas e guia por perfil; dividir B7.a/B7.b para HTML, usando claims e valores recebidos, sem escolher outra tese por conta da interface. (C19, C20, C23) | Conteúdo coincide com os dados e a proposta/adopção recebida; notas não são fala, tempo é orçamento até ensaio real e nenhum resultado omitido é prometido. |
| **EN07 — Preparar e testar montagem de vídeo** / EN04, EN05, EN06 | Implementar perfis PDF9/13 segmentos e HTML10/14 segmentos, checagem de clipes e montagem; testar encoder com fixtures explicitamente sintéticas. Montar vídeo real somente se houver clipes fornecidos. (C24) | Sem clipes informa ausência sem vídeo fictício; com clipes mede duração/áudio/formato e entrega rascunho para revisão humana integral, sem aceleração artificial. |
| **EN08 — Implementar CLI e empacotamento** / EN02 | Criar execução com input/output/profile explícitos, empacotamento, índices, hashes e dependências; consumir as planilhas fornecidas pela análise em vez de gerar outro modelo econômico. (C21, C25) | Runner funciona sem importar código da análise; arquivos só são escritos nas raízes autorizadas, com erros acionáveis e nenhuma declaração automática de envio. |
| **EN09 — Verificar sistema e todos os formatos** / EN04, EN05, EN06, EN07, EN08 | Testar offline, teclado/foco, impressão10, renderização9/7, todas as seleções e estados, unidades, lineage, ausência e pacotes corrompidos; separar teste de software de validação econômica. (C22, C23, C28) | Sistema demonstrável com baseline/fixtures sem dados futuros da Parte1; relatórios identificam exatamente as entradas e os estados testados. |
| **EN10 — Implementar portões e preparar envio** / EN09 | Substituir recusa final incondicional por portões de dados/análise/visual/vídeo; testar sucesso e recusa com evidências de teste isoladas. Gerar checklist de H07/H13; não enviar ao Safra. (C25, C26) | Coleta factual não exige clipes; vídeo exige participação/revisão reais; resultado de navegação não aprova economia e arquivo existente não comprova envio. |
| **EN11 — Integrar versões sem acoplamento de código** / EN10 | Implementar importação de pacote1.0 publicado, validação de hashes/estado, seleção de versão e regeneração dos formatos; provar com fixtures de duas versões que a troca dispensa mudar código. Quando o pacote real e registros humanos chegarem, executar o mesmo fluxo. (C19, C23, C24, C25) | Não lê trabalho mutável da outra parte; pacote parcial não promove final. Ausência de pacote real não impede entregar o integrador e rascunhos honestos com baseline. |
| **EN12 — Consolidar progresso e continuidade** / EN11 | Registrar o próprio pacote técnico, consolidar estados por escopo sob exclusão de escrita, preservar decisões/limitações, atualizar ambos os documentos de contexto e revalidar o fechamento conhecido. (C27, C29) | O sistema e o próximo passo podem ser retomados sem o chat; complementos omitidos não reaparecem na interface e nenhuma condição humana é presumida cumprida. |

<!-- TWO_PART_TASKS:END -->

## Consumidor, baseline e afirmações

Implementar o consumidor1.0 antes de layouts. Validar major version, arquivos/hashes, IDs, recortes, tipos, unidades, referências, estados e relação entre claims/valores/cases. Rejeitar pacote corrompido, inválido ou que use caminhos fora da raiz autorizada. Não ler diretório de trabalho mutável da análise. Consumir apenas versão completa publicada ou cópia própria congelada.

O adaptador legado converte o snapshot atual para a interface com marcador **`baseline_unreconciled`**, exclusivo desse modo de rascunho. Não promove a base atual a `analysis_proposed`. Em especial, há57 pontos/cenários sem metadados suficientes de resíduo/validade; tratá-los como desconhecidos e bloquear seu uso como alvo, sem inferir validade pelo número exibido. Dados ausentes continuam ausentes; não colocar zero, reutilizar outro cenário ou inventar faixa.

Criar fixtures isoladas em testes para: dados completos/incompletos, alvo válido/resíduo não positivo, mudança de versão, fontes/claims ausentes, formatos incorretos e registros humanos ausentes/presentes. O carregador de pesquisa recusa `kind=fixture`. A simulação de registros humanos é permitida apenas na sandbox de testes; nunca entra nos registros reais, outputs finais ou indicadores de conclusão.

Criar `claim_placements.csv` na área de produção: artefato/perfil, página/bloco, claim_id, value_ids, source_ids e versão/hash da entrada. Toda afirmação numérica, factual ou causal exige referência; títulos e falas também. Hipóteses e inferências mantêm seus rótulos. Os cinco claims atuais restritos a S5 não bastam. Se faltar conteúdo semântico, registrar lacuna e apresentar estado honesto, sem inventar a afirmação para preencher slide.

## Interface de entrada — contrato comum 1.0

Esta interface deriva do [catálogo de execução](../data/catalog/two_part_execution.json), reproduzido nos dois planos. Implementar esquema e testes em `production/` sem importar o produtor financeiro. Não redefinir o contrato unilateralmente.

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

IDs são únicos e estáveis. CSV usa lista/objeto JSON quando necessário. Entidades/instrumentos/fontes/definições preservam as colunas legadas no adaptador; os campos normativos são os da interface nova. `instrument_id` vazio é permitido em dado corporativo. Observações, cases, claims e views são os dados de renderização; tabelas de conciliação, ajustes e cronogramas ficam disponíveis para auditoria, sem serem reinterpretadas pela interface.

O manifesto registra hashes dos arquivos, exceto ele próprio; QA analítica identifica hashes de entradas/resultados excluindo o próprio QA e manifesto. Assim não há ciclo de hashes. Exigir resolução das evidências externas ou impedir a afirmação/pacote correspondente. `model_inputs.json` é insumo de reprodução financeira, não autorização para recalcular outro modelo no navegador. `pendencias.csv` especifica disposição e bloqueio por estágio; evidência ausente não é aprovação.

## Visualizações e perfis

Criar figuras PNG/SVG e CSV-fonte do mesmo modelo de visão: comparação ESG com definições/períodos, ponte do efeito ESG, comparação preço/valor/condições e cenários/riscos. Recorrer a tabela ou faixas de disponibilidade quando o ranking não é comparável. Mostrar fonte, data, escala e hipótese junto da figura, com detalhes acessíveis. Resíduo não positivo aparece como N/D acompanhado de explicação; não como barra de preço justo zero.

Separar perfis para que um não quebre os testes do outro:

| Perfil | Estrutura | Produção |
|---|---|---|
| `pptx9` | Nove slides, apoio técnico separado de sete páginas | PPTX editável, notas/fontes, PDF9, roteiro/13 segmentos atuais |
| `html10` | Dez páginas, S7 dividido em método e resultado | HTML independente, PDF10, capturas10, roteiro/14 segmentos se adotado para gravação |

O HTML não substitui automaticamente o vídeo requerido pela competição. O grupo escolhe qual perfil grava depois de revisar conteúdo; ambos devem funcionar como material de revisão. Manter PPTX9 em vez de alterar globalmente a expectativa antiga para dez.

### HTML interativo de dez páginas

Seguir integralmente o plano10 e `html_slide_plan.json`: HTML/CSS/JS/SVG nativos, dados incorporados e arquivo único offline, navegável por duplo clique. Sem CDN, fetch obrigatório, fonte externa, servidor obrigatório ou publicação de site. Implementar áreas seguras, contador, progresso, teclado, foco, escape, detalhes/fontes, contraste, redução de movimento e impressão.

<!-- TWO_PART_PAGES:START -->

| Página / origem | Conteúdo | Voz / segundos planejados |
|---|---|---|
| S01 ← S1 | Saneamento: onde está o valor do setor listado | Rodrigo / 14 |
| S02 ← S2 | Na 2ª carta, o modelo comprou Sabesp sem uma tese nossa sobre a empresa | Rodrigo / 40 |
| S03 ← S3 | Fomos ao setor com um olhar fundamentalista | Rodrigo / 28 |
| S04 ← S4 | 62,3% da população tem coleta de esgoto; a meta é 90% até 2033 | Lorenzo / 50 |
| S05 ← S5 | Demanda estável e contratos longos; o risco está na regulação e nos juros | Lorenzo / 65 |
| S06 ← S6 | Até 2030, regulação, competição e tecnologia decidem quem ganha | Navarro / 55 |
| S07 ← S7 | Cada indicador ESG chega ao caixa por um caminho diferente | Michel / 70 |
| S08 ← S8 | Medimos uma alavanca: 1% a menos na conta de energia | Michel / 40 |
| S09 ← S9 | Do caixa da empresa ao valor do acionista | Rodrigo / 55 |
| S10 ← S10 | Ao preço de 30/10, só a Sanepar rende acima do nosso custo de capital | Rodrigo / 45 |
| S11 ← S11 | A Sanepar vale R$ 42,82 por unit; o mercado paga R$ 30,85 | Rodrigo / 50 |
| S12 ← S12 | Compramos Sanepar até R$ 34,26 por unit; Sabesp e Copasa já estão no preço | Navarro / 58 |

<!-- TWO_PART_PAGES:END -->

São560 segundos/9:20 planejados, não medidos. A divisão de B7.a/B7.b precisa aparecer no roteiro e no perfil de segmentos; não basta dividir visualmente o slide.

Implementar seleções de empresa/KPI/período/cenário/retenção e grade WACC×g somente quando os dados publicados suportarem a seleção completa, inclusive validade. Atualizar gráfico, tabela, notas e acessibilidade juntos. Seleção inexistente fica indisponível com motivo; não interpolar DCF nem projetar valor novo. Definir modo de gravação com defaults reproduzíveis. Impressão mostra exatamente dez páginas principais, com estado/default explícito, sem modal sobreposto. Inspecionar todas as dez capturas e o PDF10.

### PPTX, roteiro e preparação do grupo

Regenerar PPTX/PDF/apoio com conteúdo, figuras e notas do pacote selecionado. Conferir enquadramento, legibilidade, fonte, unidade e reserva de câmera. Renderizar por ferramenta disponível e inspecionar todas as páginas; presença de PDF não comprova ausência de cortes.

Gerar `roteiro_narrativo.md`, `script_apresentacao.md`, teleprompters dos quatro, doze perguntas/respostas e guia de gravação por perfil. O script contém as falas exatas; notas de fonte/limitação operacional ficam fora do texto a pronunciar. Proposta continua proposta até H08/H09 reais. Contagem de palavras estima plausibilidade, não substitui ensaio. Preparar formulário de dois ensaios cronometrados; incorporar feedback real quando fornecido. Todos precisam ter participação substantiva, não somente aparição no fechamento.

### Vídeo

Manter `config/video_segments.json` para9/13 e criar perfil separado `config/video_segments_html10.json` para10/14. Validar caminho, tomada, ordem, falante, associação ao roteiro, áudio, dimensões, duração e margens. Testar encoder com amostra sintética isolada e removível, claramente identificada como teste; não produzir vídeo fictício do grupo.

Com clipes reais, montar rascunho, medir duração total/transições/áudio e preparar arquivo de revisão. Se exceder dez minutos ou houver trecho faltante, apontar cortes de roteiro ou nova tomada; não acelerar artificialmente a fala. O arquivo definitivo exige revisão integral real do grupo e evidência correspondente. Exibir hash/nome exatos do arquivo revisado, evitando revisão de uma versão e envio de outra.

## CLI, publicação e liberação por estágio

Criar CLI própria, por exemplo **futura** `.venv/Scripts/python.exe -m production.run --input-bundle <pasta> --profile pptx9 --output <raiz> --stage <etapa>`. Implementar também `--baseline <snapshot>` para rascunho, `--help`, modo de checagem sem publicação, erros acionáveis e raízes explícitas. Esses argumentos ainda não existem no runner legado. Adaptar `scripts/run_esg.py` depois para delegar aos componentes sem recalcular finanças; manter compatibilidade dos comandos antigos.

O consumidor transporta as duas planilhas fornecidas pela análise e confere hash/referências; não recria premissas. O pacote G01 precisa dos seis arquivos do contrato09, incluindo `model_inputs.json` e relatório de cobertura. Gerar todos os artefatos G01–G08 aplicáveis; versões definitivas usam nome/canal/formato de H07 quando isso se aplicar. HTML/QA são desenvolvidos nas raízes próprias; no publish copiar para os destinos catalogados `outputs/draft/html/`, `outputs/qa/html/`, rascunhos legados e `outputs/final/` sob exclusão de escrita e manifesto. Não escrever nesses destinos durante testes.

Substituir a recusa final incondicional por portões específicos, com relatório de motivos e sucesso testável:

| Estágio | Evidência necessária | Condição que permanece externa |
|---|---|---|
| Dados factuais | Proveniência, unidades/recortes, qualidade, cobertura/limitações e hashes aprovados para o conteúdo incluído | Não exige ensaios nem adoção de recomendação que o pacote não contém |
| Proposta analítica | Pesquisa material executada, reconciliações/limites e QA econômica no alcance declarado | Sem H08/H09, só proposta identificada; não liberar como tese adotada |
| Material definitivo do grupo | Bundle revisado compatível, H08/H09 reais para premissas/recomendação, claims e revisão visual atuais | H07 necessário para declarar conformidade com instruções privadas aplicáveis |
| Vídeo definitivo para envio | Conteúdo adotado, H07, dois ensaios/clipes reais, duração/formato e revisão integral comprovados | Grupo realiza revisão e envio; o agente prepara o arquivo |
| Enviado | Arquivo/link exato, hash, responsável, data/fuso, canal e comprovante reais | Somente após H13 real; comprovante não é requisito para gerar o arquivo a enviar |

Limitação material pode impedir uma recomendação incondicional, mas permitir proposta/faixa/condição explicitamente delimitada. Não fechar gate econômico por simples status textual: exigir evidência e checagens dos critérios. Não exigir ausência de toda incerteza para liberar um pacote factual; nem tratar omissão de um estudo P2 como falha global.

Publicar resultados em diretório temporário, verificar integridade e promover uma versão nova; manter rollback por versão anterior. Antes de atualizar caminhos canônicos, conferir se o snapshot mudou e não sobrescrever intervenções humanas. A publicação tem um único escritor; nunca lê arquivo ainda em geração. Enviar ao Safra, e-mail ou terceiros não está autorizado nesta tarefa.

## Testes e entrega autônoma

- Consumidor: versão incompatível, hash/path inválidos, referências quebradas, unidades/recortes inconsistentes, dado ausente, resíduo não positivo e qualquer ponto de cenário sem validade. Rejeição deve ser explicável. Não usar contagem fixa57 como regra de produto.
- HTML: abertura offline com rede bloqueada, exatamente dez páginas, teclado/foco/escape, fontes, todos os controles habilitados e desabilitados, alterações coerentes de texto/gráfico/tabela, impressão10 e modo gravação. Testar ao menos uma implementação de navegador disponível e declarar a cobertura real; screenshots não substituem teste de interação.
- Artefatos: renderização9/7/10 nos perfis corretos, revisão de todas as páginas, falas/valores/claims consistentes e nenhum dado de fixture em pacote real. Conferir CSV-fonte das figuras e comparações de valores com bundle.
- Vídeo/portões: ausência de clipes/decisões não aprova final; input real incompleto retorna motivos; fixtures isoladas testam também o caminho de sucesso. Não falsificar registros reais para provar que o gate funciona.
- Integração: duas versões de bundle da mesma major mudam números/argumentos e regeneram todas as peças sem editar código. Baseline continua provisório. Nova major incompatível é recusada. Reexecução não altera originais ou decisões humanas nem mistura perfis.
- Guardar QA própria em `outputs/qa/production/`, com hashes/versões, comandos, páginas revisadas, casos testados e limites. QA de software não substitui QA financeira; os resultados antigos não são novos testes.

O pacote autônomo está completo quando o sistema e os materiais provisórios são demonstráveis, todas as famílias aplicáveis têm gerador/integrador funcional e os testes relevantes passaram. Não esperar clipes ou análise futura para entregar esse sistema. Quando os insumos reais chegarem, executar o fluxo já testado, revalidar conteúdos/resultados e liberar apenas o estágio elegível.

## Humanos, responsabilidade e continuidade

H01–H06 são complementos conforme necessidade e aquisição real; H12 só por falha concreta de acesso/ferramenta. H07 pode acrescentar exigências: pesquisar o público e processar documentos recebidos é do agente; obter instrução privada ausente é do grupo. H08/H09 exigem julgamento real, H10 dois ensaios, H11 clipes dos quatro e H13 revisão/envio/comprovante. Preparar, medir, montar e verificar são tarefas do agente; não inventar a ação humana.

Esta parte publica G01/G02 e a planilha de G03 a partir do produtor, produz a apresentação/figuras de G03, G04, ferramentas/integração de G05, G06, G07 e QA de software G08. Prova de envio em G05 é humana. A fatia econômica continua tendo outra autoria; **não fechar C19/C20/C21/C22/C23/C27/C29 globalmente só por terminar esta fatia**.

<!-- TWO_PART_SHARED:START -->

| Requisito compartilhado | Responsabilidade desta parte |
|---|---|
| C19 | Representação fiel da proposta/adoção e aplicação dos portões; não altera a escolha econômica. |
| C20 | Posicionamento em páginas/falas, formatação e cobertura de cada peça. |
| C21 | Validar/consumir a interface, adaptar baseline e resolver referências sem recalcular economia. |
| C22 | Ingestão, rastreabilidade nas peças, interface, formatos e integridade de pacotes. |
| C23 | Figuras, PPTX/PDF, HTML, texto falado, apoio e renderização. |
| C27 | Progresso próprio, consolidação por escopo e manutenção dos verificadores sem apagar a outra parte. |
| C29 | Não prometer/renderizar estudos omitidos; incorporar opcionais apenas pela mesma interface. |

<!-- TWO_PART_SHARED:END -->

Ao finalizar cada tarefa, registrar progresso próprio, preservar decisões e atualizar estado/continuidade sob a trava. Executar com a venv: `scripts/validate_completion_docs.py`, `scripts/validate_two_part_plans.py`, `scripts/sync_project_docs.py` e `scripts/sync_project_docs.py --check`. Acrescentar novos requisitos materiais ao catálogo antes de declarar fechamento. Entregar instrução de uso com comandos realmente implementados, ID/hash das entradas, testes executados, limites, registros humanos ainda necessários e o próximo comando. Validar planos não equivale a implementar este sistema ou certificar a conclusão econômica.
