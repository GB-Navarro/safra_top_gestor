# Estado do projeto — Safra Top Gestor 2026 / asset.dev

Revisão documental: **01/11/2026**. Responsável pela manutenção: agente que realizar cada próxima tarefa, conforme [AGENTS.md](AGENTS.md).

**Retomada por outro agente:** ler o [guia operacional de continuidade](EXECUTION_CONTEXT.md), com ponto de retomada, ambiente, mapa de código, comandos, recuperação dos arquivos locais e decisões que não podem ser perdidas. Os dois documentos devem ser atualizados em toda tarefa material; este descreve o andamento, o guia permite continuar sem o histórico do chat.

## O que é o projeto

Preparar a análise setorial ESG de saneamento da equipe asset.dev no Desafio Safra Top Gestor 2026. O grupo tem quatro integrantes e informou estar em 13º, com meta de alcançar pelo menos o 3º; não há notas dos concorrentes para calcular a recuperação necessária. A análise compara Sabesp, Copasa e Sanepar para produzir uma recomendação defensável, ligando fatores ESG a operação, caixa, risco, valuation e preço.

O resultado pretendido é uma base auditável, análise reconciliada, gráficos, a apresentação final de doze slides (HTML, PDF e PPTX), apoio técnico, roteiro/falas dos quatro e vídeo revisado para o grupo enviar. Doze slides e duração planejada de 9:30 são escolhas de produção. As regras públicas verificadas na pesquisa de 31/10 incluem vídeo de até dez minutos, participação ativa, SWOT, médio prazo/tecnologia/competição, recomendação e matriz ESG; o cronograma indica 02/11/2026. Horário/canal e alterações privadas continuam dependentes de H07. Ver [regras e origem da verificação](outputs/draft/regras_2026_verificadas.md).

**Apresentação final (plano 14, 01/11):** a pedido do usuário, a apresentação passou a seguir o PPT reorganizado pelo grupo, com 12 slides planos (sem botões, painéis ou elementos clicáveis), em [HTML](outputs/draft/html/apresentacao_esg.html), [PDF](outputs/draft/apresentacao_esg.pdf) e [PPTX](outputs/draft/apresentacao_esg.pptx), com o [script](outputs/draft/script_apresentacao.md) ajustado. A história começa na 2ª carta: o modelo de alocação pôs 2% do patrimônio em Sabesp, por escolha do modelo (prêmio de risco), sem tese nossa; por isso fomos ao setor com um olhar fundamentalista, e o modelo não volta a ser citado. O texto segue o estilo das cartas. O design é o de [marcadev.html](resources/design_system/marcadev.html) com o nome asset.dev. O PPTX é feito das páginas renderizadas (sem edição de layout), com a fala nas notas. Os perfis anteriores (PPTX9 editável e HTML10 interativo) foram aposentados e o PPT do grupo foi excluído depois da montagem, como autorizado; a extração está em `data/interim/production/reference/`. Não se presume que o HTML possa ser usado na gravação ou como anexo sem H07; o PDF e o PPTX têm os mesmos slides.

**Apresentações no Git:** sete arquivos enviados para `main` em [GB-Navarro/safra_top_gestor](https://github.com/GB-Navarro/safra_top_gestor), no [commit `76ef1f3`](https://github.com/GB-Navarro/safra_top_gestor/commit/76ef1f30ae9811448de152c8502feb22e93ae8e3). Inclui HTML/PDF/PPTX10, PPTX/PDF9 e apoio técnico PPTX/PDF7. Os blobs do commit conferem com os hashes da publicação; [índice das versões](data/catalog/presentations_git_manifest.json). São os rascunhos anteriores ao plano 14 (HTML10/PPTX9); a apresentação final de 12 slides **não foi enviada ao Git** (não houve pedido).

## Estado real

**Parte 1 (dados e análise) e Parte 2 (apresentação e engenharia) executadas em 01/11/2026. As peças são rascunhos canônicos de uma proposta: decisões humanas (H08/H09), instruções privadas (H07), ensaios, clipes, vídeo e envio continuam pendentes. O projeto inteiro não está concluído.**

O pacote analítico 1.0 vigente é [`an_20261101T202028_e29905ab`](outputs/draft/analysis_bundle/an_20261101T202028_e29905ab/LEIA_PRIMEIRO.md) (ponteiro em [latest.json](outputs/draft/analysis_bundle/latest.json)), da fotografia derivada `snap_20261031_b126c2edf0`: os mesmos insumos de 31/10, as fontes primárias do plano 13 e, no plano 14, a 2ª carta (original preservado), as tabelas de cotação e a série do Tesouro já usadas (agora lidas também em 23/10) e uma reportagem de 26/10. Contém:

- as 64 células históricas e C08 com disposição e fonte;
- capital e eventos;
- obrigações por natureza e cronograma datado do precatório;
- premissas com alternativas;
- FCFF revisado com vínculo capex→base remunerada e 68 casos com validade por caso;
- matriz e ponte ESG;
- decisão proposta por regra;
- 34 afirmações (33 nos 10 slots e uma verificação da base), incluindo a origem na 2ª carta e a semana do segundo turno;
- duas planilhas.

Estado `analysis_proposed`; QA e contrato aprovados. As versões anteriores (`an_..083333`, `an_..132455`, `an_..193707`) continuam preservadas. Nenhum valor de caso-base mudou no plano 14.

A Parte 2 consumiu esse pacote no build `pr_20261101T203705_e29905ab` (publicação `pub_20261101T203832`, [manifesto](outputs/draft/production/published.json)):

- **Apresentação final (deck12):** 12 slides planos gerados em Python (marcação e gráficos SVG) a partir do pacote; o script só navega (setas, espaço, clique), ajusta à janela e liga o modo gravação (tecla G, que reduz o slide e libera a área da câmera). Impressão de 12 páginas e PPTX das mesmas páginas com a fala nas notas.
- **Apoio técnico de 7 páginas** e **figuras** (PNG/SVG/CSV).
- **Textos:** script único, quatro teleprompters, 13 perguntas da banca, guia de gravação, [checklist de envio](outputs/draft/checklist_envio.md) e documentos de decisão.
- **Dados:** `data/processed` reflete o contrato 1.0 ([CANONICAL_SOURCE.json](data/processed/CANONICAL_SOURCE.json)).

QA das peças: **19/19 verificações**, autoteste com 73 verificações em 1920×1080 e 1366×768 (sem sobreposição, transbordo ou colisão de rótulos; sem controles), números iguais entre HTML, PPTX e script, e 16 relações afirmadas nos títulos e falas conferidas contra o pacote. Revisão visual do agente sobre 48 capturas. No estado publicado: **42 + 58 + 13 testes, código 0; 15 originais preservados**. [Conferência de fatos](data/interim/production/fact_check/fact_check_final.json): 39 valores observados exibidos ou falados ancorados no texto da fonte (3 conferidos à mão), 21 afirmações qualitativas com trecho na fonte e as três cotações de 30/10 confirmadas em segunda fonte pública. Não há ensaios, clipes, vídeo ou submissão; outputs/final continua vazio, porque o portão `group_material` recusa por falta de H08/H09.

**Achado do plano 14:** os preços de 30/10 são posteriores à semana do segundo turno. Em 23/10, a SAPR11 fechou a R$ 41,92, perto do valor-base (R$ 42,82); em 30/10, a R$ 30,85 (−26,4%). SBSP3 e CSMG3 caíram 22,8% e 25,5%, e a NTN-B 2035 subiu de 6,76% para 7,88%, taxa já usada no custo de capital. A margem de compra da Sanepar surgiu nessa semana; o slide 11, as falas e as perguntas dizem isso, e a tese deixou de afirmar que o desconto remunera o risco regulatório estadual.

Correções factuais do plano 13 (fontes primárias):

- **Copasa:** foi **desestatizada em junho/2026**, com a Equatorial como investidora de referência (30,08%). A oferta foi secundária, sem mudança no número de ações. A versão anterior dizia "em andamento".
- **Prazo das concessões da Copasa:** o prazo médio ponderado é de ~29 anos.
- **Capex da Copasa:** a companhia descontinuou as projeções em 03/2026, então o plano usado passa a ser premissa do analista.
- **WACC regulatório da Sabesp:** 7,86%, agora com fonte primária. O Anexo VIII do contrato URAE-1 o fixa até 2029.
- **Base da Sanepar:** a base implícita fica 9,9% abaixo da BRR oficial da 3ª RTP atualizada, ou seja, no lado conservador.

Nenhum valor de caso-base mudou.

Proposta do caso-base revisado (30/10/2026, WACC 13,25%): Sanepar R$ 42,82/unit vs R$ 30,85, a única acima do preço em toda a grade WACC×g; Sabesp R$ 15,94 vs R$ 24,70; Copasa R$ 20,53 vs R$ 48,11. O cenário adverso de regulação/execução leva a Sanepar a R$ 12,53, por isso a proposta é **compra condicionada** (entrada até R$ 34,26), com três gatilhos. É proposta do agente: H08/H09 não registrados. O precatório entra pelo PV de R$ 4.577,8 mi; como o saldo é atualizado a ~WACC, o PV fica próximo do saldo atualizado, e a dedução integral não é mais tratada como "ponta inferior". A ponte de energia segue como sensibilidade, não economia realizada.

## Onde está tudo o que falta

O [contrato de fechamento09](plans/09_contrato_de_fechamento.md) detalha os dados a obter, correções, dependências, critérios de aceite e entregáveis. Sua origem única é [completion_requirements.json](data/catalog/completion_requirements.json), com fontes/rotas, evidência existente, responsável, método, saída e alternativa por requisito. O [mapa de células](data/catalog/cell_issue_mapping.csv) vincula individualmente os problemas históricos aos requisitos; o [plano 14](plans/14_plano_apresentacao_final.md) especifica a apresentação final de 12 slides (o [plano 10](plans/10_plano_html_interativo.md) do HTML10 ficou como histórico).

A auditoria documental cobre os requisitos conhecidos dos planos, conteúdo público registrado e lacunas observadas nos arquivos. O [relatório de completude](outputs/qa/completion_documentation_validation.json) confere cobertura, dependências e rastreabilidade da lista, sem declarar os trabalhos executados. H07 pode acrescentar exigências ainda desconhecidas; novas descobertas materiais precisam ser incorporadas antes do encerramento.

Para distribuir a execução, usar os dois planos: **[parte1 — dados e análise](plans/11_plano_agente_analise_dados.md)** e **[parte2 — apresentação e engenharia](plans/12_plano_agente_engenharia_entrega.md)**. Cada parte inicia e testa sua entrega autônoma com insumos atuais, contrato1.0 e áreas de escrita próprias. A integração definitiva continua condicionada a dados revisados e registros humanos reais. O [catálogo da divisão](data/catalog/two_part_execution.json) e seu [relatório de validação](outputs/qa/two_part_plan_validation.json) verificam a cobertura dos29 requisitos, autoria, dependências e interface. **Parte 1 executada** (AN01–AN12; progresso em [parallel_progress/analysis.json](data/catalog/parallel_progress/analysis.json)); **Parte 2 executada** (EN01–EN12; progresso em [parallel_progress/production.json](data/catalog/parallel_progress/production.json)). O status por requisito está em completion_requirements.json (`status`, `status_note`). Com o [plano 13](plans/13_plano_fechamento_residual_agente.md), C20, C21, C22 e C28 estão fechados com evidência; o plano 14 atualizou C20, C23, C24 e C28 para o deck12 e registrou o pedido como regra R11. Os requisitos restantes ficam em dois grupos:

- dependem de ação humana: C01, C13, C14, C19, C23–C26;
- seguem com limitação declarada: C06, C09–C12, C15, C16, C18, C29, além de C27 (documentação), que é contínuo.

## Recorte e evidências registradas

Preços e avaliação: **30/10/2026**. Corte informacional: **31/10/2026, 18:25:27, America/Sao_Paulo**. Balanço usado nos casos principais: junho/2026. A atualização desta documentação em 01/11 não altera esses recortes e não representa atualização das cotações. A configuração efetiva está em [collection.json](config/collection.json).

<!-- PROJECT_EVIDENCE:START -->

Trecho automático. Números extraídos dos arquivos atuais e das verificações **já registradas**; esta sincronização não executa nova validação econômica.

| Indicador | Registro |
|---|---|
| Última execução da análise/QA central registrada | 01/11/2026 20:39:07 (-03:00) |
| Estado do relatório | controles técnicos aprovados; revisão econômica pendente |
| Fontes adquiridas / observações / contas CVM | 58 / 1.298 / 10.675 |
| Registros municipais SINISA (última extração registrada) | 271.856 |
| Originais preservados na execução registrada | 15 |
| Testes centrais na última execução | 113; código de saída 0 |
| Recálculo independente Excel/Python | 82 comparações; passed; hash da planilha atual coincide |
| Pacote — verificações registradas | 18; passed (não certifica premissas) |
| Auditoria de entradas históricas | 195 células: 131 coincidências dentro do arredondamento, 9 diferenças a conciliar e 55 sem mapeamento suficiente |
| PDFs na última renderização | apresentacao_esg: 12 páginas, html/apresentacao_esg: 12 páginas, apoio_tecnico: 7 páginas |
| Script / duração planejada | 1108 palavras, incluindo marcadores; 570 segundos planejados; ensaio real não inferido |
| Fila / ações humanas cadastradas | 33 tarefas de dados / 13 ações |
| Clipes indicados presentes | 0 de 12; presença de arquivo não comprova qualidade/revisão |
| Arquivos em outputs/final (exceto .gitkeep) | 0; quantidade não equivale a submissão |
| Pacote analítico 1.0 (Parte 1) | an_20261101T202028_e29905ab; estado analysis_proposed; QA analítica passed |
| Peças publicadas (Parte 2) | build pr_20261101T203705_e29905ab (pub_20261101T203832); validação passed_technical_checks_with_economic_review_pending; revisão visual reviewed_no_material_layout_defect (agente) |
| Apresentação de 12 slides — autoteste/offline/impressão | 1920: 73 verificações passed; 1366: passed; sem controles passed; offline passed; PDF 12 e PPTX 12 páginas |
| Portões de liberação (evidência real) | data_factual: liberado; analysis_proposal: liberado; group_material: bloqueado; video_submission: bloqueado; sent: bloqueado |
| Contrato de fechamento — documentação | 29 requisitos; 64 células vinculadas; fontes correspondem à revisão; não é conclusão financeira |
| Apresentação final — mapa de páginas | 12 páginas / 570 segundos; artefato presente, consultar validação HTML própria |

Evidências: [relatório técnico](outputs/qa/relatorio_validacao.md), [recálculo da planilha](outputs/qa/workbook_recalculation.json), [auditoria de células](outputs/qa/extended_input_audit.csv), [cobertura](data/processed/coverage.csv) e [ações humanas](data/catalog/manual_export_requests.csv).

<!-- PROJECT_SNAPSHOT_SHA256:17f020ea9937b772bdad5b19d0806fa0b38218321f658d5a2709f365b17fa09a -->
<!-- PROJECT_EVIDENCE:END -->

## O que já foi feito

- Repositório organizado, originais inventariados e preservados, ambiente Python e ferramentas de geração/renderização preparados. PowerPoint/LibreOffice foram encontrados fora do PATH; o encoder de vídeo foi instalado.
- Coletados cadastro/DFP/ITR da CVM, releases/notas/estatuto, SINISA, BCB/Focus, Tesouro e referências públicas dos cinco papéis. Arquivos brutos, hashes, localização e recortes estão registrados. Não houve confirmação pela Bloomberg.
- Extraídas contas e observações com definições/unidades. Corrigida a conversão indevida de lucro por ação; tratados capital, classes e unit. Cobertura histórica/contratual permanece parcial onde indicado nos catálogos.
- Reproduzidos os três DCFs originais em Python. Confirmado que o rateio de2026 já existia; XTIR baseada em firma/FCFF não foi rotulada como retorno acionário. Gerados experimentos de terminal, custos de capital, dívida e obrigações, com limites explícitos.
- Produzidos matriz ESG de cinco fatores, sensibilidade financeira de energia, quatro figuras PNG/SVG/CSV, base/modelo XLSX, apresentação de nove slides, apoio de sete páginas, script, teleprompters, doze perguntas e guia de gravação.
- Executados testes e verificações técnicas no escopo dos relatórios abaixo; PDFs inspecionados. O teste do montador utilizou uma amostra sintética temporária e não gerou vídeo do grupo.
- Auditada a especificação de fechamento, vinculadas as células históricas abertas e documentado o plano de dez páginas HTML. Esta revisão foi documental: não corrigiu dados financeiros, não aprovou premissas e não gerou o HTML.
- **Parte 1 (plano11) implementada em `analysis/`**:
  - Fotografia congelada (`snap_20261031_2cf3206ead`).
  - Conciliação das 64 células e C08: C02/C04 confirmadas; C03 2023–24 retiradas da base; giro canônico; Copasa em capex caixa; zeros da Sanepar fundamentados.
  - Base remunerada implícita, ligada ao WACC regulatório (Sanepar 8,08%, Copasa 9,79%, Sabesp 7,86%; a fonte primária da Sabesp foi obtida no plano 13).
  - WACC de mercado por CAPM local (NTN-B 2035 7,88%).
  - Cronograma do precatório; ponte junho→outubro.
  - Pacote 1.0 com recálculo independente no LibreOffice (82 comparações, erro relativo máx. 4e-15) e legado reproduzido.
  - 32 testes em tests/analysis.
  - Corrigidos os acentos corrompidos do contrato em two_part_execution.json.
- **Parte 2 (plano12) implementada em `production/` e `presentation_web/`**:
  - **Consumidor 1.0.** Rejeita versão major, kind, hash, escape de caminho, colunas, fontes e claims ausentes, formato numérico e alvo sem validade. Adaptador `baseline_unreconciled` separado.
  - **Modelo de páginas e HTML10.** Dados embutidos com `value_ref`; 31 verificações de interação no Edge headless.
  - **Formatos e falas.** Figuras, PPTX9/apoio7 com títulos e eixos em pt-BR, falas sem números literais fora de tokens, perfis de vídeo 13/14 e montagem testada com fixture sintética.
  - **Portões por estágio** (dados, análise, visual, vídeo e envio), `--mode final` condicionado aos portões e integrador sob trava com reversão.
  - **Testes:** 50 em tests/production, com fixtures isoladas e duas versões trocando números sem mudar código.
  - **Sincronizador.** Passou a usar a trava documental, ignora builds imutáveis e mostra evidências das duas partes.
- **Plano 13 (fechamento residual do agente)** executado em [plans/13](plans/13_plano_fechamento_residual_agente.md):
  - **Levantamento e revisão crítica.** Inventário de tudo o que faltava, separando o que é do agente e o que é humano; a revisão crítica corrigiu 10 erros ou lacunas do próprio plano.
  - **Fontes primárias novas:** Anexo VIII URAE-1, NT Agepar 006/2025, fato relevante da Copasa de 11/06/2026 e fato relevante da Sanepar de 28/10/2026.
  - **Fotografia derivada.** O modo `--baseline derive:` evita capturar `data/processed` publicado como insumo.
  - **Nova versão do pacote e das peças** com as correções factuais; 7 testes novos na Parte 1.
  - **Revisão semântica e fechamentos.** Revisão das 32 afirmações registrada; C20 e C22 fechados; fila de coleta, números N e mapa HTML atualizados.
- **Plano 14 (apresentação final)** executado em [plans/14](plans/14_plano_apresentacao_final.md):
  - **Narrativa:** 12 slides na sequência do PPT do grupo, com origem na 2ª carta e análise independente do modelo depois do slide 2; títulos afirmam fatos com número; texto no estilo das cartas, verificado por lint.
  - **Dados:** pesos e motivos da 2ª carta e semana do segundo turno entraram no pacote com fonte; rótulos de fonte corrigidos.
  - **Peças:** HTML plano, PDF e PPTX de 12 páginas, script e teleprompters; vídeo com o slide reduzido ao lado da câmera.
  - **Conferência:** valores e afirmações ancorados nas fontes; relações dos títulos conferidas a cada build.

## Cumprimento das fases do plano

| Fase | Estado | O que falta para encerrar |
|---|---|---|
| A01 — ambiente e inventário | Inventário ativo atualizado:15 originais; áudio removido a pedido do usuário | Registrar eventual mudança real de capacidade/acesso; H07 segue como dependência da submissão. |
| A02 — aquisição | Executada na Parte 1 e completada no plano 13 (fontes primárias do WACC Sabesp, BRR Sanepar, desestatização da Copasa, eventos de outubro) | Residual sem fonte primária extraível: BRR líquida de Sabesp e Copasa, plano de capex vigente da Copasa (projeções descontinuadas) e preço da EMAE; H01 opcional. Não bloqueiam a proposta. |
| A03 — normalização/conciliação | Concluída para a proposta (64 células + C08) | Revisar se H07 ou novos fatos exigirem; IR/CS em tributos a recuperar não separável. |
| A04 — valuation | Ramo revisado implementado; premissas propostas; caso finito das três empresas calculado; base implícita verificada contra a BRR oficial da Sanepar | H08 sobre cinco julgamentos (WACC, WACC regulatório Sabesp, defasagem/captura, precatório, terminal); nova versão do pacote se mudarem. |
| A05 — ESG e efeito no valor | Matriz com value_refs e ponte (base remunerada + energia); governança da Copasa corrigida | Indicador de acesso da Copasa ausente; energia permanece sensibilidade. |
| A06 — recomendação | Decisão proposta por regra (Sanepar, compra condicionada) | Adoção real H09; Parte 2 representar fielmente proposta/condições/gatilhos. |
| A07 — visualizações | Deck12 no design asset.dev: gráficos SVG com ouro para a medida principal e cinza para comparação; autoteste geométrico em duas resoluções e revisão de 48 capturas | Regenerar automaticamente se H08/H09 mudarem premissas (nova versão do pacote → `production.run`). |
| A08 — slides e falas | Apresentação final de 12 slides em HTML/PDF/PPTX (plano 14), script único no estilo das cartas, quatro teleprompters e apoio7 | Ajustar falas com os tempos reais dos ensaios (H10); versão definitiva após H08/H09. |
| A09 — validação | QA 19/19 e validação integral 42+58+13 aprovadas; 15 originais conferidos; conferência de fatos do plano 14 registrada | Revalidar a cada nova versão; premissas econômicas seguem sem certificação por testes. |
| A10 — ensaio/vídeo | Perfil deck12 (12 segmentos) e montador testados com fixture sintética | Receber dois ensaios e clipes reais; montar (`production.video.assemble`), medir e o grupo revisar o vídeo inteiro. |
| A11 — pacote final | Rascunhos canônicos publicados (apresentação final de 12 slides); Git ainda com a versão anterior; portões mantidos | Portões liberarem com H08/H09, H07, H10, H11 e revisão integral; então `--mode final` promove; grupo envia (H13) e guarda comprovante. |

O `--mode final` avalia os portões de liberação. Hoje recusa com motivos, porque H08/H09 não estão registrados. Ele só copia para outputs/final com evidência real e nunca envia nada.

As rotas públicas existem. Um importador genérico das exportações Bloomberg e a seleção por `--task Dxx` não existem na interface atual. Implementar o importador se essa rota for usada; o complemento não é pré-requisito de toda a pesquisa pública. Os comandos antigos de coleta apresentados como proposta foram substituídos pelos comandos reais nos planos05/07.

## O que falta ao agente — ordem de execução

| Prioridade / referências | Trabalho e motivo | Resultado que comprova conclusão |
|---|---|---|
| 1 — A04/A06/A07/A08 após H08/H09 | Se o grupo alterar algum dos cinco julgamentos ou a recomendação: `python -m analysis.run --baseline derive:data/interim/analysis/baseline/snap_20261031_b126c2edf0` (`new` é recusado depois da publicação 1.0); depois `python -m production.run --input-bundle latest`, revisar capturas, `--record-visual-review` e `--publish`. | Nova versão `group_adopted` só com registros reais H08/H09; peças regeneradas e republicadas. |
| 2 — A10 com clipes reais | Conferir clipes (`--release-report`), montar o rascunho do vídeo (deck12, 12 segmentos) e medir duração/áudio. | Vídeo de rascunho para revisão integral do grupo; nada enviado. |
| 3 — A11 | Após os portões liberarem: `scripts/run_esg.py --mode final` (ou `--final-stage video_submission`). | outputs/final com manifesto; submissão continua humana (H13). |
| 4 — residual público (opcional) | BRR líquida de Sabesp/Copasa em fonte primária extraível; plano de capex vigente da Copasa (se o novo controlador divulgar); preço/participação da EMAE; datas de eventos de Sabesp/Copasa. Uma tentativa por fonte no plano 13 não bastou. | Limitação mantida ou substituída; nova versão do pacote se mudar número. |

Pesquisa pública, conciliação contábil e programação seguem como responsabilidade do agente. Só declarar dependência humana quando faltar acesso pessoal, julgamento que o grupo assumirá, atuação em ensaio/vídeo ou envio. Não condicionar toda a análise às exportações Bloomberg.

## O que falta ao grupo

| Ação | Como e por quê | Registro esperado |
|---|---|---|
| H07 — instruções privadas | Reunir mensagem/orientações e confirmar hora/fuso, canal, formato/tamanho, alterações e se o HTML pode ser usado na gravação. Seguir o [checklist de envio](outputs/draft/checklist_envio.md). | Originais e resumo em data/raw/orientacoes. |
| H08/H09 — decisões | **Proposta pronta.** Usar o checklist de cinco julgamentos e a decisão em [LEIA_PRIMEIRO do pacote](outputs/draft/analysis_bundle/an_20261101T202028_e29905ab/LEIA_PRIMEIRO.md); assumir ou rejeitar hipóteses, recomendação, condições e objeção. Não refazer a pesquisa nem aceitar projeções só porque existem. | [decisoes_equipe.md](data/interim/decisoes_equipe.md), com responsável, data e justificativa reais. |
| H10 — ensaios | Fazer dois passes cronometrados com os quatro, usando o [HTML](outputs/draft/html/apresentacao_esg.html) (ou o PDF/PPTX) e os [teleprompters](outputs/draft/teleprompter/). Os 9:30 são planejamento, não duração medida. Revisar slides e falas antes. | [feedback_ensaio.md](data/interim/feedback_ensaio.md). |
| H11 — gravação | Gravar participação real conforme o script e o [manifesto de segmentos](config/video_segments.json): 12 clipes, um por slide (S01–S12); o HTML tem modo gravação (tecla G). | Clipes em data/raw/gravacao e indicação das tomadas preferidas. |
| H13 — revisão/envio | Assistir ao arquivo inteiro, conferir requisitos e enviar pelo canal confirmado. | Comprovante e arquivo/link efetivamente enviados. |
| H01 — confirmação útil | Abrir/autenticar o Terminal para tentativa de API ou exportar preços/capital/eventos. SDK foi encontrado, mas o endpoint estava inativo no teste anterior. | Exportação local ou captura autorizada com metadados; não compartilhar credenciais. |

H02–H06 são complementos opcionais, substituídos por fontes públicas ou omitidos no pacote atual. H12 não exige ação técnica manual no estado registrado: PDF e encoder foram preparados. Reavaliar apenas se houver falha real posterior.

## O que foi adiado ou omitido deliberadamente

Consenso e alvos de analistas não adquiridos; índices/financiamento verde sem prova específica; regressões de privatização/juros; VPL por ligação e EV/BRR como extensões. Não apresentar resultados desses estudos. EV/BRR é P2: obter todos os anexos de todos os contratos não é condição universal para terminar, mas os contratos/regulações materiais usados na tese precisam de fundamento.

## Arquivos para trabalhar

| Finalidade | Arquivo |
|---|---|
| Método e responsabilidade do agente | [Plano05](plans/05_plano_implementacao_agente_esg.md) e [anexo07](plans/07_plano_coleta_dados_agente.md) |
| Duas partes de execução autônoma | [Plano11: dados/análise](plans/11_plano_agente_analise_dados.md) e [plano12: apresentação/engenharia](plans/12_plano_agente_engenharia_entrega.md), com contrato de integração e escrita separada |
| Fechamento residual do agente | [Plano 13](plans/13_plano_fechamento_residual_agente.md): inventário, revisão crítica e registro de execução |
| Pacote analítico 1.0 (Parte 1) | [latest.json](outputs/draft/analysis_bundle/latest.json) → recomendação, casos, conciliação, cronograma e planilhas; QA em outputs/qa/analysis; código em analysis/ |
| Peças e integração (Parte 2) | [Apresentação HTML](outputs/draft/html/apresentacao_esg.html), [conferência de fatos](data/interim/production/fact_check/fact_check_final.json), [publicação](outputs/draft/production/published.json), [relatório de validação](outputs/qa/relatorio_validacao.md), [portões](outputs/qa/release_validation.json), [revisão visual](outputs/qa/visual_review.json); código em production/ e presentation_web/ |
| Procedimento humano | [Plano06](plans/06_plano_executivo_grupo_esg.md), [anexo08](plans/08_plano_coleta_dados_humano.md) e [próximos passos](outputs/draft/PROXIMOS_PASSOS.md) |
| Auditoria e limitações | [Conciliação](outputs/draft/conciliacao_financeira.md), [auditoria](outputs/draft/auditoria_modelos.md), [pendências](outputs/draft/pendencias.md) |
| Modelos e apresentação | [XLSX](outputs/draft/base_modelo_auditavel.xlsx), [base de coleta](outputs/draft/coleta/base_dados_coletados.xlsx), [PPTX](outputs/draft/apresentacao_esg.pptx), [PDF](outputs/draft/apresentacao_esg.pdf) |
| Falas e produção | [Script](outputs/draft/script_apresentacao.md), [teleprompters](outputs/draft/teleprompter/), [roteiro](outputs/draft/roteiro_narrativo.md), [perguntas](outputs/draft/perguntas_banca.md), [guia](outputs/draft/guia_gravacao.md), [checklist de envio](outputs/draft/checklist_envio.md) |
| Fechamento executável e apresentação | [Contrato09](plans/09_contrato_de_fechamento.md), [plano 14](plans/14_plano_apresentacao_final.md), [plano10 (histórico)](plans/10_plano_html_interativo.md), [requisitos](data/catalog/completion_requirements.json), [mapa HTML](data/catalog/html_slide_plan.json) |
| Registro detalhado | [Contexto técnico](EXECUTION_CONTEXT.md), [contexto do desafio](SAFRA_TOP_GESTOR_2026_CONTEXT.md), [fila de dados](data/catalog/collection_backlog.csv), [ações humanas](data/catalog/manual_export_requests.csv) |

Os HTMLs01–03, as cartas, o áudio e os modelos originais são insumos históricos preservados. Não representam o estado atual. Planos e checklists são critérios de trabalho; arquivos em outputs/draft são rascunhos; relatórios QA têm escopo e data próprios.

## Como manter este documento atualizado

Depois de cada mudança material: revisar as fases, responsáveis, critérios e próxima ação acima; atualizar catálogos quando houver evidência; corrigir o gerador de qualquer texto gerado; registrar no histórico o que realmente mudou. Então executar:

Atualizar também a data de revisão, o ponto de retomada e o registro da última tarefa em EXECUTION_CONTEXT.md. O empacotador preserva esse contexto manual; o sincronizador confere os campos de continuidade e a coerência da data, sem inventar seu conteúdo.

```powershell
& '.\.venv\Scripts\python.exe' scripts/sync_project_docs.py
& '.\.venv\Scripts\python.exe' scripts/sync_project_docs.py --check
& '.\.venv\Scripts\python.exe' scripts/validate_completion_docs.py
& '.\.venv\Scripts\python.exe' scripts/validate_two_part_plans.py
```

O sincronizador também será chamado ao fim dos estágios do pipeline. Ele atualiza indicadores e referências documentais, sem recalcular finanças ou declarar validação humana. Os trechos fora dos marcadores automáticos exigem revisão responsável do agente. Para verificar uma nova análise, executar os testes/cálculos próprios da mudança e só depois atualizar seu status.

## Integridade do workspace

Por solicitação do usuário em01/11/2026, a pasta do áudio de Rodrigo foi removida. O áudio saiu do inventário ativo, dos catálogos de entrada e do mapa de reorganização. As verificações conferem os15 originais restantes; nenhuma depende do áudio. Fotografias, builds e relatórios antigos mantêm seus registros históricos. Ver [validação desta alteração](outputs/qa/audio_removal_validation.json).

## Próxima ação

**Grupo, agora:**

- **H07:** instruções, canal, horário e se o HTML pode ser usado (o PDF e o PPTX têm os mesmos 12 slides).
- **H08/H09:** pelo checklist do pacote, registrando em [decisoes_equipe.md](data/interim/decisoes_equipe.md).
- **H10:** revisar os 12 slides e o script e ensaiar com os teleprompters.

**Agente, depois disso:**

- se H08/H09 mudarem premissas: `analysis.run` → `production.run` → revisão visual → `--publish`;
- com clipes reais: montar o vídeo de rascunho;
- com os portões liberados: `--mode final`.

Nenhum passo do agente envia nada. Respeitar a trava para alterações globais.

## Histórico de mudanças

- **31/10/2026:** organização, coleta/extração, modelos de diagnóstico, rascunhos de apresentação e validações técnicas produzidos. Fechamento econômico e etapas humanas permaneceram pendentes.
- **01/11/2026:** documentação revisada após a constatação de execução parcial; criado este documento central; responsabilidades e pendências autônomas/humanas separadas; manutenção contínua registrada em AGENTS.md e sincronização documental integrada ao pipeline. Esta revisão não executa nova análise financeira nem conclui fases por existência de arquivos.
- **01/11/2026 — auditoria de completude:** criado contrato de fechamento por requisito com cobertura dos planos e lacunas atuais, mapa individual das células históricas abertas e plano de conversão PPTX9→HTML10. Integrada verificação de cobertura/dependências à sincronização; dados, modelos e entregáveis financeiros anteriores permanecem na fotografia original.
- **01/11/2026 — passagem entre agentes:** ampliado EXECUTION_CONTEXT.md com ordem de leitura, escopo, retomada C02, ambiente/dependências, mapa de implementação, comandos e reconstrução do workspace; manutenção dos dois documentos tornou-se obrigatória. Removida a sobrescrita do contexto pelo gerador de status, para preservar registros futuros. Esta revisão não implementou conciliações ou HTML.
- **01/11/2026 — execução em duas partes:** criados planos11/12, catálogo de24 tarefas e contrato1.0 de dados; separadas autoria, entrega autônoma, integração e ações humanas. Acrescentado validador de cobertura/dependências/escrita/interface à sincronização. Validação estrutural e revisão de lacunas são documentais; nenhum dado financeiro foi corrigido, HTML implementado ou vídeo produzido nesta tarefa.
- **01/11/2026 — Parte 1 executada:** implementado `analysis/` (AN01–AN12) e publicado o pacote `an_20261101T083333_e758f3af` (`analysis_proposed`). Versões anteriores do mesmo dia foram preservadas como histórico:
  - `an_20261101T082913_dfe39899` e `an_20261101T083008_5fb05fc7`: `analysis_incomplete`, porque o recálculo do LibreOffice não rodou ou não recalculou fórmulas;
  - `an_20261101T083109_37c60ff6`: substituído após revisão de textos (afirmação sobre a Sabesp, gatilho de juros, unidades).

  Catálogos atualizados sob trava: status por requisito, H08/H09 com proposta pronta e acentos do contrato. O sincronizador documental passou a ignorar `outputs/draft/analysis_bundle/`: ele inseria banners nos pacotes publicados e quebrava seus hashes. Arquivos restaurados e teste de regressão criado. Decisões humanas, peças de apresentação e vídeo não foram produzidos.
- **01/11/2026 — Parte 2 executada:** implementados `production/` e `presentation_web/` (EN01–EN12).
  - **Build e publicação.** Build `pr_20261101T124209_e758f3af` com 15 de 15 verificações de QA e revisão visual do agente vinculada aos hashes. Publicado pelo integrador (`pub_20261101T124305`, 82 arquivos, reversão em data/interim/production/rollback). As suítes rodaram no estado publicado: 32 + 49 + 13 testes, código 0; 16 originais preservados.
  - **Revisão visual.** Antes do registro, foram corrigidos:
    - impressão do HTML com 11 páginas;
    - palco deslocado em janelas menores e refluxo no modo gravação;
    - contraste do painel no tema escuro;
    - sobreposição de rótulos na régua de compra;
    - títulos longos sobre o subtítulo no PPTX;
    - eixos com separadores em inglês;
    - códigos em inglês no apoio técnico.
  - **Ajustes em código legado não atribuído:**
    - `tests/test_core.py` lê `esg_bridge` legado da fotografia quando a fonte canônica é o contrato 1.0;
    - `validate_completion_docs.py` aceita os dois esquemas;
    - o sincronizador passou a usar a trava, ignora `outputs/draft/production/` e mostra as duas partes.
  - **Incidente.** Um teste de fumaça de `run_esg.py --stage model`, feito antes da primeira publicação (quando a guarda ainda não se aplicava), executou o modelo legado.
    - As saídas legadas foram regeneradas byte a byte iguais às fotografias. A única diferença, o `retrieved_at` de `sources.csv`, foi restaurada; os JSON de `data/interim/acquisitions` ficaram com o horário dessa releitura local. Não houve download nem mudança de corte.
    - O `sync()` acionado nessa execução inseriu banners em três builds de desenvolvimento; os arquivos foram restaurados byte a byte contra os manifestos.
  - **Fora do escopo do agente:** H07–H13, ensaios, clipes, vídeo e envio não foram realizados.
- **01/11/2026 — plano 13 (fechamento residual do agente):**
  - **Plano.** Levantados todos os requisitos abertos. Foi escrito o [plano 13](plans/13_plano_fechamento_residual_agente.md), cuja revisão crítica corrigiu 10 erros ou lacunas do próprio plano (por exemplo, `--baseline new` capturaria saídas publicadas como insumo).
  - **Erro factual corrigido:** a Copasa já estava desestatizada (jun/2026), e o release 2T26 da fotografia já trazia isso.
  - **Fontes primárias:**
    - prazo médio de 29 anos das concessões da Copasa;
    - WACC da Sabesp no Anexo VIII;
    - BRR da Sanepar na NT Agepar;
    - fato relevante da Copasa;
    - licitação SAINP da Sanepar;
    - descontinuação das projeções de capex da Copasa (fonte de imprensa).
  - **Versões novas.** Fotografia derivada `snap_20261031_7c31b5560e`, pacote `an_20261101T132455_ac536175`, build `pr_20261101T132746_ac536175` e publicação `pub_20261101T132847`. Nenhum valor de caso-base mudou.
  - **Fechamentos.** C20 (revisão semântica) e C22 fechados.
  - **Erros encontrados e corrigidos na própria execução:**
    - textos literais da produção ainda diziam "fonte secundária" e "em andamento";
    - a pergunta da banca sobre a BRR estava desatualizada;
    - o integrador não guardava reversão das escritas diretas;
    - o validador documental quebrava com o esquema 1.0;
    - `script_word_counts.json` perdeu o formato legado.
  - **Fora do alcance:** H07–H13 continuam pendentes.

- **01/11/2026 — design asset.dev:** novo build `pr_20261101T151834_ac536175`, publicação `pub_20261101T152159`. HTML/PDF10 com o design de marcadev.html e PPTX10 fiel às páginas do HTML; fontes locais, testes de117 estados em duas resoluções e tema claro, revisão das20 páginas PDF/PPTX. Corrigidos espaçamentos, legendas e tabela longa. A comparação dos formatos passou; análise financeira não foi regenerada. A primeira tentativa identificou áudio original ausente e falhou por esse motivo; a revalidação está registrada a seguir, sem alteração dos critérios ou dos hashes esperados.

- **01/11/2026 — revalidação da revisão visual:** áudio novamente disponível com o hash original; publicação `pub_20261101T153001` do mesmo build, com39+50+13 testes aprovados e16 originais conferidos. A falha da primeira tentativa foi resolvida sem dispensa de teste ou alteração de inventário.

- **01/11/2026 — remoção solicitada do áudio:** pasta resources/audio excluída; inventário, catálogos, mapa, teste e gerador de status ajustados para os15 originais ativos. Testes desta tarefa: 102, status passed. Slides e pacotes versionados preservados.

- **01/11/2026 — apresentações no Git:** sete arquivos publicados em `origin/main`, commit `76ef1f3`. Exceções específicas no .gitignore e atributo -text preservam o HTML byte a byte; índice com hashes registrado. Nenhuma regeneração, atualização financeira ou envio à competição nesta tarefa. Verificações desta tarefa: hashes dos sete blobs, referência remota e documentação; testes de análise/layout são de execuções anteriores.

- **01/11/2026 — plano 14 (apresentação final):** a pedido do usuário, a apresentação passou a seguir o PPT reorganizado do grupo, com 12 slides planos e a história iniciada na 2ª carta. Fotografias `a54d10bd24` e `b126c2edf0`; pacotes `an_20261101T193707_e8a63bb3` e `an_20261101T202028_e29905ab` (vigente); builds até `pr_20261101T203705_e29905ab`, publicações `pub_20261101T202934` e `pub_20261101T203832` (vigente). Perfis pptx9/html10 aposentados; PPT do grupo excluído após a montagem.
  - **Erros encontrados e corrigidos na execução:** "Evasão e tarifa social pesam no cenário adverso" não tinha base (o adverso usa choque de custo de 2% da receita); "compromisso de R$ 15,0 bi" da Aegea virou "mais de"; a resposta sobre a BRR deixou de afirmar o estado atual; a NT 006/2025 aparecia como "Agepar — portal"; linha tracejada cortando rótulos nos slides 9 e 10 e colisão na régua do slide 12; o montador de vídeo punha a câmera sobre o conteúdo; a QA comparava números sem tratar o espaço não separável.
  - **Achado de dados:** a margem de compra da Sanepar surgiu na semana do segundo turno (fechamentos de 23/10 e 30/10 das mesmas fontes); incorporado ao pacote, ao slide 11, às falas e às perguntas.
  - **Verificações desta tarefa:** 42 testes da Parte 1, 58 da Parte 2 e 13 legados no estado publicado; QA 19/19; revisão visual de 48 capturas; conferência de fatos registrada; validadores documentais e sincronização ao fim. H07–H13 continuam pendentes; nada foi enviado ao Safra nem ao Git.
