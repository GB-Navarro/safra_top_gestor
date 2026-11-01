# Plano 14 — Apresentação final a partir do PPT do grupo

<!-- PROJECT_STATUS:START -->
> [Estado central do projeto](../ESTADO_DO_PROJETO.md) · Revisão documental: 01/11/2026. Plano de método e critérios; conclusão de cada fase depende de evidência.
<!-- PROJECT_STATUS:END -->

Data: 01/11/2026 (America/Sao_Paulo). Pedido do usuário: transformar `outputs/ppt_reorganizado.pptx`, a última versão feita pelo grupo, na apresentação final, com estes ajustes:

- storytelling novo nos primeiros slides;
- narrativa revisada e ancorada nos dados;
- texto no estilo das cartas;
- layout sério, limpo e plano (sem botões);
- validação final dos dados.

Entregar slides em HTML, PPTX e PDF e o script de fala ajustado. Ao final, apagar o PPT do grupo.

Recortes inalterados: preços e avaliação em 30/10/2026; corte informacional em 31/10/2026 18:25:27.

## 1. O que o pedido exige

| Exigência | Como será atendida | Aceite |
|---|---|---|
| Igual ao PPT do grupo, com ajustes | Mesma sequência de 12 slides e mesmo sistema visual (preto e ouro, asset.dev); conteúdo revisado slide a slide | 12 páginas na ordem do grupo, com os ajustes documentados abaixo |
| Abertura: o modelo da 2ª carta comprou Sabesp | Slide 2 com a carteira de ações da 2ª carta e o motivo dado na carta. Números vindos do pacote analítico, com a carta como fonte | Valores conferidos na tabela da seção 9 da 2ª carta |
| Por isso escolhemos o setor e o olhar fundamentalista | Slide 3 com a pergunta e o método, sem citar o modelo | Nenhuma menção ao modelo depois do slide 2 (lint) |
| Análise independente do modelo | Slides 4 a 12 e falas sem "modelo", "Black-Litterman" ou "sinal". "Nosso cálculo" e "caso-base" substituem "modelo" | Busca automática por termos proibidos nas páginas 3–12 e nas falas 3–12 |
| Narrativa sólida e ancorada nos dados | Cada slide afirma uma coisa, sustentada por números do pacote; frases do grupo sem fonte removidas ou reescritas | Revisão de fatos registrada; nenhum número literal fora de tokens |
| Texto no estilo das cartas | Frases diretas na primeira pessoa do plural, termo técnico explicado na primeira vez, números precisos, sem setas, símbolos ou títulos de efeito | Checklist de estilo + lint de padrões proibidos + leitura completa |
| Layout sério e limpo, sem botões | HTML estático (slides planos), navegação só por teclado/clique, sem barra de ferramentas, abas, botões, dicas ou painéis | Autoteste: nenhum `button` visível; geometria sem estouro em todas as páginas |
| HTML, PPTX e PDF | HTML-fonte → PDF pelo navegador → PPTX por imagens de alta resolução, com o script de cada slide nas notas | 12 páginas nos três formatos; números iguais entre formatos |
| Script ajustado | Script por slide (falante, tempo, texto), teleprompters por pessoa, perguntas da banca | Tempo planejado ≤ 9:20; estimativa a 140 palavras/min dentro do plano |
| Validação final dos dados | Ancoragem automática de cada valor observado no texto da fonte + revisão manual de toda frase literal | `outputs/qa/fact_check_final.json` sem pendência |
| Apagar o PPT do grupo | Último passo, depois de entregar e validar; antes, registrar hash e extração de texto | Arquivo removido; extração em `data/interim/production/reference/` |

## 2. Levantamento (feito)

**PPT do grupo:** 12 slides.

1. Capa.
2. 2ª carta.
3. Pergunta.
4. Setor e listadas.
5. SWOT.
6. Médio prazo.
7. Matriz ESG.
8. Do ESG ao valor.
9. Cálculo.
10. TIR.
11. Valor contra preço.
12. Conclusão.

Notas de fala com falante e tempo: soma de cerca de 9:45. Problemas encontrados:

- **Títulos de duas linhas sobre o subtítulo** (slides 3, 4, 5 e 10).
- **Frase sem fonte:** "medindo performance passada" (slide 2). A carta só diz "escolha do modelo (prêmio de risco)".
- **Afirmação sem dado:** "Execução forte" para a Sabesp (slide 12).
- **TIR das planilhas originais** (14,7% e 5,7%) nas notas do slide 10. O ramo legado não remunera o capex e foi superado; esses números saem.
- **Modelo citado depois da abertura:** capa, slide 3 e slide 11 ("a escolha do nosso modelo").
- **Símbolos e fórmulas de efeito:** setas, "≠" e "Canal no valor".

**2ª carta (seção 9):**

- Petrobras, Vale, WEG e Suzano com 5% cada;
- Bradesco com 3% e Sabesp com 2%, ambas com o motivo "Escolha do modelo (prêmio de risco)";
- método descrito na seção 8.

**3ª carta:** a carteira não tem ações. A Sabesp aparece só na 2ª.

**Pipeline anterior:** HTML10 interativo (deck.js), PPTX10 por imagens e PPTX9 editável separado. Validadores, integrador, falas, vídeo e testes presumiam os perfis 9 e 10 (substituídos pelo deck12 nesta execução).

## 3. Narrativa proposta

Fio: **viemos pela Sabesp; os fundamentos mostram que o valor do setor está na Sanepar, com preço-limite e gatilhos.** A Sabesp volta no fim como resposta à pergunta do slide 3, sem citar o modelo.

| # | Slide | Mensagem (título informativo) | Dados |
|---|---|---|---|
| 1 | Capa | Saneamento listado: onde está o valor | — |
| 2 | Ponto de partida | Na 2ª carta, o modelo de alocação comprou Sabesp sem uma tese nossa | Pesos da 2ª carta; motivo da carta |
| 3 | Pergunta e método | Fomos ao setor com um olhar fundamentalista: há valor nas três listadas ao preço de hoje? | Etapas do trabalho; perguntas-guia |
| 4 | Setor | 62,3% da população tem coleta de esgoto; a meta é 90% em 2033 | SINISA 2024, metas; três listadas (preço, EBITDA, contrato) |
| 5 | SWOT | Demanda estável e contratos longos; o retorno depende da regulação e dos juros | Prazos, perdas, capex, NTN-B, precatório, reajuste |
| 6 | Médio prazo | Regulação, competição e tecnologia definem quem ganha até 2030 | WACC regulatórios, Pará, desestatização da Copasa, perdas, energia |
| 7 | Matriz ESG | Os indicadores ESG chegam ao caixa por caminhos diferentes em cada empresa | Matriz 5 × 3 |
| 8 | Do ESG ao valor | Medimos uma alavanca: 1% a menos na conta de energia | Cadeia + sensibilidade de energia |
| 9 | Cálculo | Quanto vale R$ 1 investido e como sai o valor do acionista | R$ 1 investido; ponte da Sanepar |
| 10 | TIR | Ao preço de 30/10, só a Sanepar rende acima de 13,25% | TIR implícita no preço contra WACC |
| 11 | Valor contra preço | A Sanepar vale R$ 42,82 por unit; o mercado paga R$ 30,85 | Valor × preço; grade; pior ponto; semana do segundo turno (acrescentada na F6) |
| 12 | Conclusão | Compramos Sanepar até R$ 34,26; Sabesp e Copasa já estão no preço | Régua; cenários; gatilhos; fecho das três |

A narrativa se sustenta nos dados do pacote vigente:

- **Sanepar:** acima do preço em toda a grade; o cenário adverso (R$ 12,53) mostra o risco.
- **Sabesp:** só alcança o preço no cenário favorável.
- **Copasa:** fica abaixo do preço mesmo no favorável.

Falantes conforme o grupo:

- **Rodrigo:** slides 1–3 e 9–11;
- **Lorenzo:** slides 4–5;
- **Navarro:** slides 6 e 12;
- **Michel:** slides 7–8.

## 4. Etapas

| Etapa | O que fazer | Aceite |
|---|---|---|
| F0 — Referência | Gravar hash e extração (texto, notas, geometria) do PPT do grupo e folhas de contato em `data/interim/production/reference/` | Extração completa antes de apagar o original |
| F1 — Dados da 2ª carta (Parte 1) | Fotografia derivada que inclui a 2ª carta (original preservado). Ler a tabela da seção 9 e registrar pesos e motivos como observações (fonte: a carta); criar a afirmação de origem no slot `lead`; testes | Novo pacote com QA e contrato aprovados; casos-base inalterados |
| F2 — Modelo de 12 páginas (Parte 2) | `content.py` (páginas, textos de tela, falas, perguntas) e `deck_model.py` (dados de cada slide com `value_refs`, afirmações e fontes) | Todo número por token; afirmações dos slots posicionadas |
| F3 — HTML plano | HTML gerado em Python (marcação + SVG), CSS do sistema visual e JS mínimo (navegação por teclado, ajuste à janela, autoteste); sem botões ou controles | Autoteste no navegador aprovado em 1920 e 1366; impressão de 12 páginas |
| F4 — PPTX, PDF, script e vídeo | PDF pelo navegador; PPTX por imagens com script nas notas; `script_apresentacao.md`, teleprompters, perguntas e guia; perfil de vídeo do deck de 12 páginas, com o slide reduzido ao lado da câmera | Três formatos com 12 páginas; tempo ≤ 9:20 |
| F5 — Integração | QA, integrador, portões, sincronizador e validadores para o perfil único `deck12`; `html_slide_plan.json` e bloco do plano 10; testes de produção | Todas as suítes verdes; validadores verdes |
| F6 — Validação de fatos e estilo | Ancoragem automática dos valores observados no texto da fonte; revisão manual de cada frase literal (telas, falas, perguntas); lint de estilo e do modelo | `fact_check_final.json` sem pendência; lints vazios |
| F7 — Revisão visual e publicação | Revisar as 12 páginas em HTML/PDF/PPTX; corrigir e repetir até ficar limpo; registrar a revisão e publicar | Revisão vinculada aos hashes; publicação com suítes verdes |
| F8 — Fecho | Apagar o PPT do grupo; atualizar estado, contexto, README, AGENTS e catálogos; sincronizar e validar | Documentos coerentes; o PPT não existe mais |

## 5. Regras de estilo (cartas)

- **Voz:** primeira pessoa do plural ("medimos", "compramos"), frases curtas, verbo no início quando possível.
- **Termos técnicos:** explicados na primeira ocorrência ("WACC, o custo médio do capital").
- **Títulos:** afirmam um fato com número; nada de aforismo ("A demanda não é o risco…").
- **Proibido:** setas (→), "≠", travessões em série, "Canal no valor", "vale destacar", "crucial", "robusto", "em suma", "não é X, é Y" repetido, pontos de exclamação.
- **Falas:** escritas para dizer em voz alta. Números arredondados quando a precisão não muda a mensagem, sempre vindos dos tokens.
- **Fecho:** uma frase objetiva, como nas cartas.

## 6. Revisão crítica do plano

A primeira versão foi conferida contra o código e o pedido. Correções incorporadas às etapas:

1. **Câmera cobrindo conteúdo.** Os slides planos ocupam a tela inteira, mas o montador de vídeo sobrepõe a câmera no canto inferior direito, em cima do conteúdo. Na F4, a composição do vídeo passa a reduzir o slide (escala 0,84, à esquerda) e pôr a câmera ao lado. Sem isso, o slide 12 perderia os gatilhos no vídeo.
2. **A 2ª carta fica fora da fotografia.** O modo `derive:` só atualiza `data/raw/analysis`. A F1 precisa de uma lista explícita de insumos extras (a 2ª carta), copiada com hash e conferida contra o manifesto de originais.
3. **Exportação PPTX.** O PPTX por imagens não tem texto pesquisável fora das notas e do texto alternativo. O teste de números entre formatos (F5) passa a ler o texto alternativo de cada slide (texto da página do PDF) e as notas (script).
4. **Validador do mapa HTML.** `validate_completion_docs.py` exige P01–P10 e um PPTX-fonte de 9 slides. Na F5, o mapa (`html_slide_plan.json`) e o validador passam a descrever o deck de 12 páginas, com falantes e tempos conferidos contra o script.
5. **Formato de `script_word_counts.json`.** Os validadores leem `blocks` com bloco, falante e tempo. O integrador grava esse formato para o perfil `deck12` (bloco = slide).
6. **Resíduos do modelo.** Termos como "modelo" podem sobrar nas peças auxiliares (apoio técnico, perguntas, guia, documentos). O lint da F6 cobre telas, falas e perguntas; nos documentos de decisão, "modelo" só aparece no sentido de "modelo de valuation", e o texto será trocado por "nosso cálculo" quando ambíguo.
7. **UI escondida.** Barra de progresso, contador "Fontes e afirmações", tema claro e painéis também são interface e saem. A navegação por teclado fica. O modo gravação (tecla G, sem botão) fica como opção para gravar o HTML com câmera.
8. **Apoio técnico e documentos.** Eles dependem da estrutura antiga de páginas (P05, figuras). A F2/F5 adapta `build_support`, `figures.py` e `docs.py` ao novo modelo, para não quebrar peças que continuam publicadas.
9. **Duas cópias do deck.** Hoje existem `outputs/draft/apresentacao_esg.*` (PPTX9) e `outputs/draft/html/apresentacao_esg.*` (HTML10). Para não sobrar versão antiga contraditória, os dois caminhos recebem o mesmo deck final de 12 páginas.
10. **GitHub.** O repositório remoto tem a versão anterior (commit `76ef1f3`). Esta tarefa não faz push sem pedido; o manifesto de publicação no Git fica como registro histórico.
11. **Tempo.** O grupo somava cerca de 9:45. O script novo mira 9:20 ou menos, com margem para o teto de 10 minutos.
12. **Apagar o PPT.** O arquivo está fora do Git (`outputs/**` ignorado): a remoção é irreversível. Antes, F0 grava hash e extração completa. A remoção é o último passo, depois da entrega validada.

## 7. Registro de execução

Executado em 01/11/2026. Todas as etapas F0–F8 foram cumpridas; nada foi enviado ao Safra nem ao Git.

| Etapa | Resultado |
|---|---|
| F0 | Hash `ba65ba99…` e extração dos 12 slides (texto, notas, geometria, dados dos gráficos) em `data/interim/production/reference/`, com duas folhas de contato. |
| F1 | `analysis/origin.py` e fotografia `snap_20261031_a54d10bd24` (carta copiada com hash igual ao manifesto de originais); pacote `an_20261101T193707_e8a63bb3`. |
| F2 | `content.py` e `deck_model.py` reescritos para 12 páginas; `guards()` confere 16 relações afirmadas nos títulos e falas. |
| F3 | `slides.py` gera marcação e SVG; `deck.css`/`deck.js` novos, sem controles; autoteste com 73 verificações (sobreposição, transbordo, colisão de rótulos, navegação). |
| F4 | PDF e PPTX de 12 páginas com a fala nas notas; script único, teleprompters, 13 perguntas; vídeo com o slide a 0,84 ao lado da câmera (item 1 da revisão crítica, implementado na F8 depois de notado na conferência). |
| F5 | QA (19 verificações), integrador, portões, validadores documentais, catálogos e testes (`test_plan14.py`) para o perfil único `deck12`. |
| F6 | `data/interim/production/fact_check/`: 118 valores exibidos ou falados; 39 observados, 36 achados no texto da fonte e 3 conferidos à mão; 21 afirmações qualitativas com trecho na fonte; cotações de 30/10 confirmadas em segunda fonte pública. |
| F7 | Builds revisados até `pr_20261101T203705_e29905ab` (48 capturas; publicado em `pub_20261101T203832`, suítes 42 + 58 + 13). |
| F8 | PPT do grupo excluído; AGENTS, estado central, contexto, README, plano 10 (marcado como histórico) e catálogos atualizados sob trava. |

**O que a conferência mudou:**

1. **Semana do segundo turno.** A segunda fonte de preços mostrou queda de 20% a 24% no setor em 26/10. As tabelas de cotação já guardadas confirmam: SAPR11 fechou a R$ 41,92 em 23/10, perto do valor-base, e a R$ 30,85 em 30/10; a NTN-B 2035 foi de 6,76% para 7,88%. Os fechamentos de 23/10, a variação e a NTN-B entraram no pacote (`analysis/market_week.py`, `CL.result.election_week`, pacote `an_20261101T202028_e29905ab`), com uma reportagem de 26/10 como fonte datada. Slide 11, falas e perguntas passaram a dizer que a margem surgiu nessa semana; a tese deixou de afirmar que o desconto remunera o risco regulatório estadual.
2. **Frases sem base:** "Evasão e tarifa social pesam no cenário adverso" virou o choque de custo de 2% da receita, que é o que o cenário usa; "compromisso de R$ 15,0 bi" da Aegea virou "mais de"; "a base oficial ainda está em fiscalização" virou "estava, na nota técnica da revisão".
3. **Fontes:** rótulos corrigidos (a NT 006/2025 aparecia como "Agepar — portal") e rodapé agrupado por emissor.
4. **Carta:** a frase "Vale, WEG e Suzano pelo real mais fraco" foi conferida no parágrafo das exportadoras; `origin.py` passou a exigir esse parágrafo e o da Petrobras.

**Limitações:** o PPTX é feito de imagens (o layout se edita no HTML); preços de provedor público, sem confirmação Bloomberg/B3; premissas continuam proposta do agente até H08/H09; a revisão visual e a conferência são do agente; o GitHub ainda tem a versão anterior.
