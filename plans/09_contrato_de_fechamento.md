# Contrato de fechamento — dados, correções e entregáveis

<!-- PROJECT_STATUS:START -->
> [Estado central do projeto](../ESTADO_DO_PROJETO.md) · Revisão documental: 01/11/2026. Plano de método e critérios; conclusão de cada fase depende de evidência.
<!-- PROJECT_STATUS:END -->

Revisado em **01/11/2026**. Este é o detalhe executável do [estado central](../ESTADO_DO_PROJETO.md). O método geral permanece nos planos05–08. O [catálogo de requisitos](../data/catalog/completion_requirements.json) é a origem única das tarefas abaixo: contém evidência existente, onde buscar, ação, dependências, saídas, aceite e alternativa. Não criar outra lista concorrente.

## Resultado da auditoria documental

A documentação anterior cobria frentes gerais, mas não encerrava a especificação necessária. Foram identificados e documentados estes pontos concretos:

- **64 células históricas abertas**, antes agregadas como55 sem mapeamento e nove diferenças. Agora cada célula aponta para um requisito específico; diferença de conceito não foi declarada erro automaticamente.
- `corporate_actions.csv` está vazio e os campos de vigência dos termos regulatórios usados estão incompletos. Isso não confirma ausência de eventos ou vigência indefinida.
- `claims.csv` contém cinco afirmações, todas em S5. Faltava exigir a trilha de cada afirmação dos demais slides, gráficos e falas, inclusive associações semânticas corretas entre claim e observação.
- A validade de preço-alvo/resíduo antes do piso não é exportada em todos os cenários e pontos de sensibilidade. Isso importa para Excel/gráficos e para os controles do futuro HTML; um zero numérico não basta.
- Faltava especificar a liberação final por estágio, a resolução das dependências do pacote, os testes após correções e a compatibilidade entre os perfis PPTX9/HTML10/vídeo.

Esta auditoria verifica **cobertura documental dos requisitos conhecidos e das lacunas observadas**. Não executa as conciliações, não certifica projeções e não conhece exigências privadas ainda não recebidas em H07. Novas exigências ou fatos materiais precisam entrar neste contrato antes de declarar o projeto finalizado.

No catálogo, R01–R06 representam conteúdo público/instruções da competição; R07–R09 são critérios do plano da equipe para qualidade e reprodução; R10 é a solicitação de planejar o HTML10. Isso não cria novos pesos ou obrigações oficiais do Safra.

## Como executar sem ampliar o escopo desnecessariamente

1. Trabalhar por impacto na recomendação, seguindo dependências do catálogo; H07 pode avançar em paralelo. Preservar preço/avaliação30/10 e corte31/10 já registrados.
2. Antes de buscar dado novo, ler a evidência local indicada. Obter somente o período/conceito que falta; as rotas oficiais estão em [source_registry.csv](../data/catalog/source_registry.csv) e os documentos adquiridos em [sources.csv](../data/processed/sources.csv). Notas/atos materiais têm precedência sobre resumos.
3. Cada observação selecionada precisa de valor, unidade/escala, período, publicação/captura, definição, escopo e localização. Conferir versão CVM elegível, consolidado/individual e acumulado/trimestre; não somar conta sintética com filhas. Se uma publicação no próprio dia do corte tiver hora desconhecida, não afirmar precisão intradiária sem evidência.
4. Fato, hipótese e inferência têm tratamentos distintos. Julgamento H08/H09 não transforma número sem fonte em fato; fonte correta não torna previsão verdadeira. Ausência não vira zero.
5. Fechar requisito só com evidência e disposição explícitas: **resolvido**, **não aplicável comprovado**, **retirado de todas as afirmações/modelos que dependiam dele**, ou **incerteza limitada com evidência e conclusão robusta**. Registrar responsável/data e arquivos. Uma incerteza material que pode inverter a tese mantém o estágio em rascunho.
6. Opcionais não viram coleta obrigatória: consenso, índices, regressões, VPL por ligação, EV/BRR e todos os anexos municipais só entram se tiverem função na decisão. C29 documenta substitutos/omissões. Não calibrar hipóteses para obter compra ou valorização desejada.

As dependências são de fechamento do trabalho completo, não proíbem protótipos/rascunhos em paralelo. A liberação de um pacote somente factual avalia seus critérios próprios; não exige vídeo ou decisão de recomendação que não estejam contidos nele. C25 deve implementar essa distinção, em vez de aplicar todos os requisitos da competição a todo arquivo.

## Correções históricas: vínculo célula a célula

O [mapa de células](../data/catalog/cell_issue_mapping.csv) é gerado da auditoria existente e vincula cada uma das64 ocorrências atuais a C02–C07. A referência completa permanece em [extended_input_audit.csv](../outputs/qa/extended_input_audit.csv); o mapa não altera as planilhas originais.

<!-- CELL_COVERAGE:START -->

| Requisito | Lacuna atual | Células abertas vinculadas |
|---|---|---:|
| C02 | Sabesp: receita e custo de construção | 10 |
| C03 | Sabesp: ponte de EBITDA | 5 |
| C04 | Sabesp: investimento e desembolso | 4 |
| C05 | Giro operacional das três empresas | 30 |
| C06 | Copasa: capex caixa e regulatório | 5 |
| C07 | Sanepar: construção e zeros históricos | 10 |

Total vinculado: **64**. Ocorrências sem regra de cobertura: **0**. Esse vínculo não resolve a ocorrência.

<!-- CELL_COVERAGE:END -->

Os anos históricos que não sustentarem mais base, premissa, comparação ou afirmação podem ser retirados da análise com justificativa; não precisam ser confirmados apenas para manter uma célula decorativa. A base efetivamente usada no valuation precisa estar definida integralmente.

A conciliação futura em `data/interim/financial_reconciliation.csv` deve identificar requisito/célula, empresa/período, conceito e valor originais, fonte/localização, escopo/unidade/escala/sinal, componentes da ponte, definição/valor escolhidos, disposição, motivo, impacto no modelo e responsável/data. O cronograma `obligation_schedule.csv` deve identificar obrigação, saldo de abertura, movimentos realizados, fluxos futuros datados, atualização/impostos, desconto, PV e linhas de caixa/tarifa/capex onde o efeito já esteja reconhecido. Campos desconhecidos ficam explícitos; não criar um calendário fictício para preencher a tabela.

## Requisitos de fechamento conhecidos

Status no catálogo é de **execução**, não de qualidade de documentação. A existência deste contrato não fecha os itens abertos. As colunas de evidência, fontes e procedimento estão no JSON para consulta operacional; a tabela resume o necessário para agir e verificar conclusão.

<!-- COMPLETION_REQUIREMENTS:START -->

| ID / responsável / prioridade | Trabalho | Critério de fechamento |
|---|---|---|
| C01 · grupo · P0 | **Instruções efetivas da etapa** — Mensagem de16/10, live20/10 e alterações: horário/fuso, canal, nome, formato, tamanho, acesso do destinatário e conteúdo efetivamente exigido. Confirmar se HTML será apenas apoio local. | Cada exigência aplicável tem origem e valor explícitos; divergências resolvidas pelo canal já usado pelo grupo. Conteúdo privado não fornecido permanece desconhecido; H07 não impede a análise pública, mas impede declarar conformidade da submissão. |
| C02 · agente · P0 | **Sabesp: receita e custo de construção** — Dez células não mapeadas: Dados_RI linhas7–8, 2021–25. Separar serviços, construção, margem, remuneração de ativo financeiro e itens não caixa; manter escopo individual/consolidado por ano. | Cada uma das dez células tem fonte e disposição explícita; a base2025 usada no motor é rastreável e não duplica construção ou ativo financeiro. Número não confirmado só permanece no original histórico, sem promoção a fato ou uso silencioso na recomendação. |
| C03 · agente · P0 | **Sabesp: ponte de EBITDA** — Cinco diferenças2021–25 entre EBITDA da planilha e EBIT+D&A CVM; distinguir reportado, ajustado, recorrente e consolidação. | As cinco diferenças estão explicadas por componentes verificáveis; nenhuma é absorvida apenas por tolerância. A margem projetada se apoia numa definição recorrente identificada, sem perpetuar ajuste extraordinário. |
| C04 · agente · P0 | **Sabesp: investimento e desembolso** — Quatro diferenças de capex2021–24; distinguir investimento físico/competência, aquisição, pagamento, juros capitalizados e itens sem caixa.2025 também exige interpretação do conceito, mesmo com coincidência numérica. | Cada diferença tem ponte ou disposição fundamentada; capex FCFF é desembolso coerente com D&A, leases e receitas. Histórico descartado não sustenta mais premissas, gráficos ou falas. |
| C05 · agente · P0 | **Giro operacional das três empresas** — Trinta células2021–25 de outros ativos/passivos operacionais, linhas14/16. Definir clientes, estoques, fornecedores, impostos, folha, provisões e exclusões financeiras/regulatórias. | As trinta células têm mapeamento ou descarte explícito; os saldos efetivamente usados na projeção estão integralmente definidos. Mudanças de giro não duplicam precatório, financiamento, tributos sobre lucro ou caixa vinculado. |
| C06 · agente · P0 | **Copasa: capex caixa e regulatório** — Cinco células históricas de capex não mapeadas e plano futuro: desembolso, adições físicas, outorgas e reconhecimento anual na tarifa. | As cinco células estão explicadas ou substituídas; capex e receita regulatória futura usam o mesmo perímetro/calendário. O resíduo negativo atual foi investigado sem calibrar hipóteses para produzir alvo positivo. |
| C07 · agente · P0 | **Sanepar: construção e zeros históricos** — Dez zeros nas linhas7–8 de2021–25 ainda sem confirmação semântica; ausência de linha no extrator não prova inexistência econômica. | Cada zero usado tem justificativa contábil; não aplicável é uma disposição documentada, não dado faltante preenchido. A receita-base e a comparação com Sabesp/Copasa são semanticamente coerentes. |
| C08 · agente · P0 | **Sanepar: recorrência, imposto e plano de investimentos** — Efeitos do precatório/provisões na DRE, imposto efetivo extraordinário e plano2026–30 com doações, parcerias e capitalizações; separar lucro, benefício fiscal, investimento não oneroso e desembolso FCFF. | Base recorrente identificada e ponte reportado→normalizado; imposto e investimento têm trajetória e justificativa explícitas. Recebimento do precatório, passivo, tarifa e investimento aparecem uma única vez nos componentes econômicos pertinentes. |
| C09 · agente · P0 | **Preço, capital, classes e eventos** — Confirmar instrumento/fechamento30/10, precisão/fonte e eventos entre junho e avaliação: ações emitidas/tesouraria, desdobramentos, proventos, recompras, emissões e controle. corporate_actions.csv está vazio, não prova ausência de eventos. | Preço e denominador reconciliados na mesma convenção de data/ajustes; escala Copasa, golden share/minoritários Sabesp e classes Sanepar tratados. Evento ausente só é declarado após busca datada; confirmação Bloomberg é condicional à insuficiência das fontes públicas, não bloqueio automático. |
| C10 · agente · P0 | **Dívida, caixa e outros direitos de terceiros** — Conciliar dívida líquida reportada versus definição do modelo, arrendamentos, PPP, derivativos, outorgas, caixa restrito, participações, ativos não operacionais e aquisições relevantes. A tabela atual tem três deduções contábeis diagnósticas, não ajustes econômicos fechados. | Cada ajuste tem valor econômico ou faixa fundamentada, data, fonte e teste de sobreposição com fluxos. Saldos nominais não são tratados como PV automaticamente; nenhuma classe de obrigação material é omitida silenciosamente. |
| C11 · agente · P0 | **Precatório: cronograma e efeito incremental** — Converter o passivo regulatório de junho e a regra50/50 em fluxo econômico: descontos efetivos, investimentos não onerosos, atualização, impostos, execução e situação regulatória/judicial até o corte. | Ponte recebimento/tributos/passivo/consumo/saldo e fluxos futuros documentada, com ou sem faixa justificável. Dedução incremental concilia tarifa, capex e caixa; intervalo zero–saldo nominal não é apresentado como faixa de valor justo validada. |
| C12 · agente · P0 | **Ponte temporal e fluxo remanescente2026** — Balanço/capital de junho versus avaliação30/10; fluxo passado versus futuro, dividendos/financiamento/investimento e sazonalidade. O stub62/365 já existe, mas o rateio uniforme e a ponte não foram fundamentados integralmente. | Estoque inicial, datas de desconto e fluxos restantes são compatíveis; realizado pré-avaliação não entra novamente no FCFF futuro. Sensibilidade de dívida/sazonalidade tem justificativa e efeito; não equivale a balanço observado em outubro. |
| C13 · agente · P0 | **Trajetórias operacionais e macroeconômicas** — Justificar receita/volume, reajustes reais, margem, D&A, capex caixa, giro e imposto operacional2026–35; definir como investimento elegível vira remuneração por regulador/contrato. Não basta preservar as hipóteses verdes herdadas. | Premissas usadas têm evidência, unidade, período e justificativa; mudanças relevantes são explicadas e não ajustadas para uma cotação desejada. Os cinco julgamentos materiais chegam a H08 com alternativas calculadas; H08 não substitui prova de fatos. |
| C14 · agente · P0 | **Taxa de desconto e bases real/nominal** — Fundamentar WACC/estrutura de capital ou a faixa de comparação; distinguir custo de mercado, WACC regulatório, taxa real soberana e XTIR da firma. | FCFF e desconto têm moeda/base/tributação compatíveis; faixa proposta é defensável e cobre riscos relevantes. WACC regulatório8,08% real pós-impostos não é usado automaticamente como nominal de mercado ou retorno esperado da ação. |
| C15 · agente · P0 | **Terminal, reinvestimento e concessões materiais** — Prazos, renovação onerosa, ativos elegíveis, indenização contratual e calendário por perímetro material; g/ROIC e capex de manutenção compatíveis. Corte uniforme2048 e perpetuidade são sensibilidades, não fatos de todos os contratos. | g, desconto e retorno/reinvestimento terminal são coerentes; WACC>g nos casos aplicáveis. Metas nacionais são separadas das datas contratuais; a conclusão sobrevive aos tratamentos de continuidade adotados ou fica limitada. |
| C16 · agente · P0 | **Base comparativa ESG e lacunas materiais** — Cinco fatores nas três empresas: perdas; expansão/qualidade de esgoto; resiliência; acesso/capacidade de pagamento; governança/regulação. Completar séries2022–25/2026 somente onde suportem comparação/afirmação; fonte nacional SINISA2025 é base2024. | Cada célula material tem KPI/evidência ou lacuna e consequência delimitadas; nenhum ranking compara conceitos incompatíveis. Perdas físicas/aparentes/faturamento, população/domicílio/área e tratamento do coletado/gerado permanecem distintos; ausência não vira zero ou pior desempenho. |
| C17 · agente · P0 | **Ponte ESG: energia, caixa e valor** — Confirmar escopo municipal água2024 GFI2004, municípios e custo base; justificar atualização, evitabilidade, horizonte, imposto, investimento e retenção. A economia1% é sensibilidade e não um resultado físico ou projeto comprovado. | KPI/hipótese→benefício evitável→custo→FCFF→PV é reproduzível, com calendário e retenção identificados. Sem projeto/custo operacional observado, apresentar apenas sensibilidade/teto condicionado; não chamar gasto absoluto de eficiência ou custo marginal de perdas. |
| C18 · agente · P0 | **SWOT, médio prazo e eventos** — Verificar argumentos da SWOT, tecnologia, novos participantes, competição por concessões/capital e mudanças regulatórias; calendários e fatos materiais de todos os emissores relevantes à tese. | SWOT e médio prazo cobrem os itens pedidos com implicação na tese; não há causalidade/benchmark inventados. Eventos de capital e eventos operacionais têm tipos próprios; datas não confirmadas são omitidas ou sinalizadas, não copiadas de outro emissor. |
| C19 · agente+grupo · P0 | **Recomendação, cenários e gatilhos** — Fechar comparação entre três empresas, instrumento, preço/data, faixa economicamente defensável/condição de entrada, quatro cenários, três riscos e gatilhos mensuráveis. A preferência relativa atual não prova compra atrativa. | Conclusão compatível com valor/preço e limitações; objeção principal e condições de invalidação explícitas. H08/H09 têm decisão datada, responsável e justificativa reais; aprovação de hipótese não valida um fato sem fonte. |
| C20 · agente · P0 | **Rastreabilidade de cada afirmação e fala** — Mapear todos os fatos, inferências, hipóteses e números da apresentação final (12 slides), incluindo falas, figuras, notas e respostas; o mapeamento original cobria os nove slides e as dez páginas HTML. | Toda afirmação material das peças tem tipo, período, definição e trilha completa; associação entre claim e observação foi revisada semanticamente. Não há resultado prometido e ausente, consenso/índice não medido ou preço/empresa divergente entre fala e figura. |
| C21 · agente · P0 | **Exportações canônicas e estados do modelo** — Completar contratos JSON/CSV/XLSX e model_inputs: fluxos, premissas, ajustes, datas, classes e estado por cenário/grid. Hoje paper_value pode ser zero pelo piso de responsabilidade limitada sem flag por ponto, embora o caso-base tenha resíduo bruto. | Unidade, escala, perímetro, período, papel e estado são explícitos nos valores derivados e nas alternativas interativas. N/D não vira preço-alvo zero/negativo; os arquivos do pacote e suas referências/hashes podem ser resolvidos sem depender de cache opaco. |
| C22 · agente · P0 | **Validação dos dados e da análise final** — Ampliar a validação de13 testes e comparações existentes para os pontos corrigidos: semântica, ajustes/dupla contagem, datas, classes, recálculo, cenários e linhagem completa. Testes atuais não provam toda hipótese. | Nenhuma diferença material usada continua sem disposição; testes/inspeções cobrem os riscos alterados e identificam versão e escopo. Os relatórios e o recálculo correspondem aos hashes efetivos; execução anterior não é apresentada como validação da revisão atual. |
| C23 · agente · P0 | **Figuras, PPTX/PDF, roteiro e falas finais** — Regenerar figuras e tabelas, a apresentação final de 12 slides (HTML, PDF e PPTX), apoio de sete, narrativa, script dos quatro, teleprompters e respostas; alinhar ao fechamento. | Empresa, preço/data, números e conclusão coincidem entre peças; gráficos têm definição/período/fonte e não extrapolam o cálculo. Notas/fontes não são fala pronunciada; número de páginas e revisão visual são próprios do perfil e do hash produzido. |
| C24 · agente+grupo · P0 | **Ensaios, clipes e vídeo real** — Dois ensaios observados e clipes reais dos quatro, ainda inexistentes, no perfil deck12 (12 segmentos, um por slide). | Tempos reais e dois ensaios registrados; todos os ativos participam; duração final atende H07 e teto público. Vídeo real foi assistido por inteiro; fixture sintética/arquivo existente não comprova participação ou aprovação. H12 só se faltar ferramenta/acesso de fato. |
| C25 · agente · P0 | **Liberação e pacote final por estágio** — O modo final é recusado incondicionalmente. Implementar liberação verificável para dados/análise/apresentação, vídeo e HTML quando aplicável, com condições distintas de submissão. | Finalização não consiste em renomear draft ou desativar um erro; portões do estágio funcionam com testes negativos e positivos. Índice e arquivos referenciados existem; bases licenciadas não são embutidas indiscriminadamente no material de apresentação; envio continua pendente até prova humana. |
| C26 · grupo · P0 | **Envio e comprovante** — Responsável nominal, revisão final do vídeo e dos arquivos, canal/formato/tamanho/nome corretos, acesso do destinatário e comprovante. O HTML não substitui o vídeo oficial sem instrução expressa. | Há evidência real de entrega da versão revisada e acesso conforme exigido; status enviado só muda após isso. Se houver HTML de apoio, sua inclusão foi permitida/solicitada; não se presume que substitua o vídeo. |
| C27 · agente · P0 | **Documentação, inventário e estados mantidos** — Manter contrato de fechamento e estado central, preservar originais/decisões e distinguir dado coletado, reconciliado, hipótese, rascunho, final e enviado. A presente tarefa documenta critérios; não resolve as pendências financeiras. | Fases, pendências e próximos passos refletem evidência; todos os requisitos conhecidos têm responsável, método, saída, critério e alternativa. Novas instruções H07 ou descobertas materiais criam/ajustam requisitos antes de declarar cobertura completa; os originais ativos do inventário seguem preservados. |
| C28 · agente · P0 · HTML futuro | **Apresentação final em HTML de 12 slides planos, design asset.dev e exportações PDF/PPTX** — Manter a apresentação final de 12 slides planos (sem botões ou painéis), offline, no design de marcadev.html com nome asset.dev; exportar PDF e PPTX fiéis ao HTML e verificar cortes, sobreposição e colisão de rótulos. | O mapa define as 12 páginas, voz, tempo, dados e critérios; o deck segue a sequência do PPT reorganizado do grupo com os ajustes do plano 14. Doze seções/páginas de impressão, sem controles clicáveis, execução local sem rede, números iguais aos do pacote e estados N/D preservados. Design do manual com asset.dev, fontes incorporadas, autoteste sem sobreposição/transbordo/colisão em 1920 e 1366 e PDF/PPTX com 12 páginas; PPTX feito de imagens (sem edição de layout) com a fala nas notas. |
| C29 · agente · P1/P2 · condicional | **Complementos opcionais e omissões** — Consenso, analistas, ESG Bloomberg, título de apoio, índices/financiamento verde, EV/BRR, regressões, VPL por ligação e causalidade pós-privatização só quando forem efetivamente usados. Exportações públicas/permitidas têm metadata; importador Bloomberg genérico ainda não existe. | Nenhuma peça promete resultados omitidos ou chama premissa própria de consenso/medição causal. A ausência de complemento não bloqueia o núcleo quando houver alternativa suficiente; qualquer número opcional usado recebe a mesma rastreabilidade/validação dos demais. |

<!-- COMPLETION_REQUIREMENTS:END -->

## Portões de entrega

Estas famílias explicitam **o que gerar/regenerar a partir dos dados**. Caminhos finais são destinos, não arquivos declarados existentes; enquanto houver bloqueio, usar os equivalentes de rascunho. O nome/formato do vídeo depende de H07 e o HTML é uma extensão planejada.

<!-- COMPLETION_DELIVERABLES:START -->

| Família | Destino / escopo | Artefatos a gerar ou regenerar | Requisitos responsáveis |
|---|---|---|---|
| G01 — Pacote de dados | outputs/final/coleta/ | base_dados_coletados.xlsx; model_inputs.json; relatorio_cobertura.md; pendencias.csv; LEIA_PRIMEIRO.md; manifest.json | C21, C25 |
| G02 — Base e resultados canônicos | data/processed/ | observations.csv e definitions.csv; assumptions.csv; adjustments.csv e regulatory_terms.csv; corporate_actions.csv; claims.csv; valuation.json e scenarios.json; esg_matrix.json e esg_bridge.json; presentation_facts.json | C09, C10, C13, C15, C16, C17, C19, C20, C21 |
| G03 — Modelo e material visual | outputs/final/ | base_modelo_auditavel.xlsx; apresentacao_esg.pptx e .pdf (perfil escolhido); apoio_tecnico.pptx e .pdf; figuras/ com PNG, SVG e CSV-fonte | C21, C23, C25 |
| G04 — Narrativa e produção | outputs/final/ | roteiro_narrativo.md; script_apresentacao.md; teleprompter/ dos quatro; perguntas_banca.md (doze respostas); guia_gravacao.md | C20, C23, C24, C25 |
| G05 — Vídeo e prova de envio | versão exata referenciada no manifesto + data/raw/orientacoes/ | vídeo real no nome/formato de H07; registro de ensaios/revisão integral; hash do arquivo enviado, responsável, horário/fuso e comprovante | C01, C24, C25, C26 |
| G06 — Apresentação final deck12 (antes: extensão HTML10) | outputs/draft/html/ e outputs/qa/html/ | apresentacao_esg.html independente (12 slides planos); apresentacao_esg.pdf e apresentacao_esg.pptx de 12 páginas; manifest.json; capturas e html_validation.json | C28, C25 |
| G07 — Índice e liberação final | outputs/final/ | LEIA_PRIMEIRO.md; manifest.json por pacote/estágio; pendencias.md com disposições e limitações aceitas; release_validation.json em outputs/qa/ | C25, C27 |
| G08 — Evidências de qualidade | outputs/qa/ | relatorio_validacao.md e execution_validation.json; auditoria de entradas/linhagem; workbook_recalculation.json; package_validation.json; rendering.json e visual_review.json; documentation_validation.json e completion_documentation_validation.json | C20, C22, C23, C25, C27 |

<!-- COMPLETION_DELIVERABLES:END -->

| Estágio | Necessário para encerrar | O que não deve bloquear por si só |
|---|---|---|
| Base de dados | Conceitos usados, versão/período/unidades, capital, ajustes materiais e limites reconciliados; cobertura e referências resolvíveis. | Clipes e comprovante de envio; Bloomberg se o substituto público for suficiente. |
| Análise/recomendação | Projeções e tratamentos fundamentados, comparação robusta, cenários/gatilhos e decisões H08/H09 reais para a mensagem do grupo. | Todos os estudos P1/P2 ou uma falsa obrigação de provar cada anexo municipal. |
| Material visual | C20–C23 atendidos, versões consistentes e revisão de cada artefato. O HTML segue seu próprio perfil de dez páginas. | Filmagem para produzir um rascunho visual ou uma análise identificada como pronta sem vídeo. |
| Vídeo da competição | H07, ensaios, participação real dos quatro, montagem e revisão integral da versão exata, duração e requisitos técnicos atendidos. | Comprovante de envio anterior à geração do arquivo a enviar. |
| HTML local | Plano10 implementado/testado; dados e controles delimitados. Versão de rascunho pode usar a fotografia atual com suas limitações. | Publicação/hosting ou aceitação de HTML como substituto do vídeo — nenhum deles foi solicitado ou presumido. |
| Submissão | Pacote correto e comprovante real de envio pelo grupo conforme H07. | Decurso de tempo ou mera existência de arquivo nunca comprovam envio. |

O bloqueio atual de `--mode final` ainda é incondicional. C25 exige implementar portões por estágio e testar tanto recusa quanto sucesso com evidência. Esta tarefa documental não alterou esse bloqueio nem promoveu saídas a final.

## Como comprovar a completude deste contrato

Executar, após atualizar o catálogo e os documentos:

```powershell
& '.\.venv\Scripts\python.exe' scripts/validate_completion_docs.py --sync
& '.\.venv\Scripts\python.exe' scripts/sync_project_docs.py
& '.\.venv\Scripts\python.exe' scripts/validate_completion_docs.py
& '.\.venv\Scripts\python.exe' scripts/sync_project_docs.py --check
```

O verificador deve conferir: cobertura de A01–A11, D00–D32, H01–H13, N01–N25 e R01–R10; famílias G01–G08 de saídas; dados mínimos por requisito; rotas/evidências existentes; grafo sem ciclos; todas as células abertas vinculadas; dez páginas HTML planejadas cobrindo os nove slides atuais; tempos iguais ao orçamento registrado do roteiro, atualmente560 segundos; documentos gerados em sincronia. O resultado é uma validação de documentação, não um selo de conclusão financeira ou audiovisual.

O relatório fica em [completion_documentation_validation.json](../outputs/qa/completion_documentation_validation.json). As [simulações negativas](../outputs/qa/completion_documentation_negative_checks.json) conferem que omissões, ciclos, fechamento sem evidência e inconsistências do mapa HTML são rejeitados, usando cópias em memória sem alterar dados ou decisões reais.

O [plano HTML10](10_plano_html_interativo.md) trata a nova apresentação. A implementação HTML não foi solicitada nesta tarefa e ainda não existe; o plano e seus critérios ficam documentados para execução futura.
