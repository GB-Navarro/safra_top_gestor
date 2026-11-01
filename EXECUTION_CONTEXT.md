# Continuidade operacional para agentes de IA

<!-- PROJECT_STATUS:START -->
> [Estado central do projeto](ESTADO_DO_PROJETO.md) · Revisão documental: 01/11/2026. Guia de leitura e continuidade; consultar o andamento na fonte central.
<!-- PROJECT_STATUS:END -->

Revisão de continuidade: **01/11/2026**, America/Sao_Paulo. Este documento deve permitir retomar o projeto sem acesso ao chat. É mantido pelo agente responsável por cada tarefa; o empacotador não pode substituí-lo por um texto fixo.

O [estado central](ESTADO_DO_PROJETO.md) é a fonte do andamento. Este arquivo explica como operar, onde continuar e quais decisões/contextos não perder. As listas detalhadas de requisitos continuam no contrato09, sem duplicá-las aqui.

## Ordem de leitura

1. [AGENTS.md](AGENTS.md): instruções permanentes, autorização/limites e manutenção documental.
2. [ESTADO_DO_PROJETO.md](ESTADO_DO_PROJETO.md): objetivo, estado real, fases e dependências atuais.
3. Este documento: ambiente, ponto de retomada, arquivos, comandos e riscos já identificados.
4. [Contrato09](plans/09_contrato_de_fechamento.md) e [catálogo C01–C29](data/catalog/completion_requirements.json): selecionar os requisitos da tarefa, suas fontes, dependências e aceite. Não é preciso reler todas as planilhas para começar.
5. [Plano05](plans/05_plano_implementacao_agente_esg.md)/[anexo07](plans/07_plano_coleta_dados_agente.md) para método; [planos06](plans/06_plano_executivo_grupo_esg.md)/[08](plans/08_plano_coleta_dados_humano.md) para ações humanas. Ler o [plano10](plans/10_plano_html_interativo.md) quando trabalhar na extensão HTML.
6. Escolher uma das duas partes de execução: [plano11 — análise/dados](plans/11_plano_agente_analise_dados.md) ou [plano12 — apresentação/engenharia](plans/12_plano_agente_engenharia_entrega.md). Ambas iniciam com a fotografia existente; a segunda não precisa esperar dados futuros para implementar/testar seu sistema. Contrato e autoria em [two_part_execution.json](data/catalog/two_part_execution.json); critérios de fechamento continuam no contrato09.

Se houver conflito: instrução atual do usuário prevalece; o andamento vem do estado central apoiado em evidência; o catálogo de fechamento especifica o trabalho; relatórios descrevem suas próprias versões/escopos. HTMLs01–03, cartas e modelos originais são insumos históricos, não o status corrente.

## Escopo e instruções do usuário

- A equipe asset.dev informou quatro integrantes, posição13º e meta de pelo menos3º. Não forneceu notas/distâncias dos concorrentes. Não prometer classificação ou inferir a nota necessária.
- O usuário autorizou a execução autônoma do trabalho técnico local/público do agente: coleta permitida, extração, conciliação, programação, testes, materiais e documentação. Avançar sem pedir confirmação a cada ação reversível, respeitando o pedido vigente. Pesquisa pública pendente não é dependência humana de autorização.
- O grupo oferece acesso à Bloomberg, mas isso não comprova API/sessão disponível. Login/acesso pessoal, instruções privadas, julgamentos a defender, ensaios, participação real e envio continuam ações humanas quando aplicáveis. Não solicitar credenciais nem enviar mensagens/arquivos ao Safra pelo usuário.
- O usuário pede precisão, crítica e evidência. Distinguir dado, hipótese, inferência e resultado condicional; registrar o que faltar e continuar o trabalho independente. Não declarar tudo correto porque os testes passaram.
- A terceira carta indicada é [Carta_ao_Investidor_3a_Entrega_B_Lula.docx](cartas/Carta_ao_Investidor_3a_Entrega_B_Lula.docx). Seu horizonte curto não deve virar premissa de dez anos automaticamente. O relato de Rodrigo sobre entradas vermelhas conferidas e hipóteses ajustadas está resumido no [contexto do desafio](SAFRA_TOP_GESTOR_2026_CONTEXT.md), seção9; esse relato não substitui conferência primária.
- A solicitação de HTML feita em 01/11 foi primeiro de um **plano**. Depois, ao pedir a Parte 2, o usuário pediu **slides bonitos, fáceis de entender e interativos em HTML**: o HTML10 foi implementado e publicado como rascunho. Não confundir implementação, revisão econômica e envio.
- Em uma etapa anterior o usuário pediu **planos** em duas partes independentes. Planos11/12 e validador foram criados. A independência é da entrega autônoma de análise e de software; o conteúdo definitivo integrado depende de análise revisada/H08/H09 e dos demais registros humanos aplicáveis.
- Em 01/11 o usuário pediu para **seguir o plano como está**, sem cortes por prazo, e implementar a **Parte 1** (plano11), revisando a implementação. A Parte 1 foi executada (AN01–AN12). Em seguida pediu para conferir a documentação e implementar a **Parte 2**, que também foi executada (EN01–EN12). O prazo público de envio é 02/11/2026; horário e canal dependem de H07.
- Depois, o usuário pediu para **investigar tudo o que falta, mapear o que o agente pode fazer, planejar, revisar criticamente o plano e implementar**. Isso virou o [plano 13](plans/13_plano_fechamento_residual_agente.md), executado em 01/11.

- Pedido anterior: aplicar todo o design de `resources/design_system/marcadev.html` ao HTML/PDF de dez páginas, mantendo asset.dev, validar posicionamento e gerar PPTX do HTML. Implementado em01/11; PPTX10 renderizado para fidelidade visual, com texto nas notas. Não altera a análise nem registra decisões humanas.
- **Pedido mais recente (plano 14, 01/11):** tornar a apresentação final igual ao PPT reorganizado do grupo (12 slides), com a história começando na 2ª carta (o modelo pôs 2% em Sabesp, escolha do modelo pelo prêmio de risco) e seguindo pelos fundamentos sem citar o modelo; texto no estilo das cartas; layout sério e limpo; slides planos, sem botões; validação final de dados, fontes e narrativa; script ajustado; entregar HTML, PPTX e PDF e depois excluir o PPT do grupo. Executado; detalhes no [plano 14](plans/14_plano_apresentacao_final.md).

## Ponto de retomada

**Partes 1 e 2, o plano 13 e o plano 14 concluídos como proposta; o próximo passo é humano (H07, H08/H09, H10).**

- **Pacote vigente:** `an_20261101T202028_e29905ab` (ponteiro `outputs/draft/analysis_bundle/latest.json`, estado `analysis_proposed`), gerado da fotografia derivada `snap_20261031_b126c2edf0` (mãe `snap_20261031_2cf3206ead` → plano 13 `7c31b5560e` → plano 14 `a54d10bd24` → `b126c2edf0`).
- **Peças:** build `pr_20261101T203705_e29905ab`, publicado em `pub_20261101T203832` (`outputs/draft/production/published.json`). Perfil único **deck12**: 12 slides planos em HTML (`outputs/draft/html/apresentacao_esg.html`), PDF e PPTX (`outputs/draft/apresentacao_esg.{pdf,pptx}`, cópias idênticas em `outputs/draft/html/`), script `outputs/draft/script_apresentacao.md` e quatro teleprompters.
- **Onde estão:** peças em `outputs/draft`; tabelas de `data/processed` (marcador `CANONICAL_SOURCE.json`) refletem o pacote vigente.
- **Versões anteriores** (`an_..083333`, `an_..132455`, `an_..193707`; `pr_..124209`, `pr_..151834`, `pr_..202800`) seguem preservadas. O PPT do grupo foi excluído a pedido do usuário; a extração (texto, notas, geometria) e as folhas de contato estão em `data/interim/production/reference/`.

Tudo continua como proposta (selo "H09 pendente").

**Inventário atual:**15 originais ativos. O usuário solicitou remover resources/audio e a dependência do áudio nos testes; não restaurar nem exigir esse arquivo. Registros antigos com16 originais são históricos.

O agente retoma quando houver fato novo:

- **Decisão H08/H09 que mude premissa:** nova versão do pacote com `python -m analysis.run --baseline derive:data/interim/analysis/baseline/snap_20261031_b126c2edf0`. A opção `new` é recusada, porque `data/processed` agora tem saídas publicadas. Para registrar uma fonte nova da Parte 1, coloque-a em `data/raw/analysis/<emissor>/` (e em `EXTRA_PDFS` se for PDF a extrair, ou em `DERIVE_EXTRA` se estiver fora de `data/raw/analysis`), e derive de novo. Depois, novo build (`production.run`), revisão das capturas, `--record-visual-review` e `--publish`.
- **Clipes reais:** `--release-report` e montagem do perfil deck12 (`config/video_segments.json`, 12 segmentos S01–S12).
- **Portões liberados:** `run_esg.py --mode final`.

Como a Parte 2 foi implementada (para manter ou reexecutar):

1. **EN01** `production/snapshot.py`: fotografia `data/interim/production/baseline/legacy_7dbbf9cfea` dos insumos e peças legados antes da primeira publicação (base do adaptador e da reversão).
2. **EN02** `consumer.py` e `adapter.py`:
   - o consumidor 1.0 rejeita versão major ≠ 1, kind fora do modo, hash/bytes, escape de caminho, arquivo ou colunas ausentes, fontes e claims inexistentes, número inválido, ausente com número, valor exibível sem validade e adoção sem registro humano;
   - `format_value` formata em pt-BR;
   - `Bundle.render` resolve os tokens `{{value:ID|estilo}}`;
   - o adaptador gera `kind=baseline` / `baseline_unreconciled` com todos os casos `unresolved`.
3. **EN03** `deck_model.py` + `content.py` + `labels.py` (plano 14):
   - 12 páginas S01–S12 com números `{ref,num,fmt}`, fontes por página e rodapé de fontes agrupado por emissor;
   - `guards()` confere as relações afirmadas nos títulos e falas (quem rende acima do custo de capital, quem fica acima do preço etc.) e recusa o deck (`IncompatibleState`) se o pacote deixar de sustentá-las;
   - `IncompatibleState` também quando não há decisão proposta/adotada ou o caso-base decidido não tem alvo;
   - `claim_placements.csv` do perfil deck12.
4. **EN04** `slides.py` + `html_deck.py` + `presentation_web/deck.css` + `deck.js` (HTML único, offline, plano):
   - marcação e gráficos SVG gerados em Python; nenhum botão, painel, dica ou barra de progresso;
   - `deck.js` só navega (setas, espaço, clique, Home/End, `#pN`), ajusta à janela, liga o modo gravação (G ou `?rec=1`: slide a 0,84 e área da câmera 1644, 540, 252×448 livre) e roda o autoteste `?selftest=1` (73 verificações: sobreposição de título/subtítulo/corpo/rodapé, transbordo, colisão de rótulos, ausência de controles, navegação, fontes);
   - impressão de 12 páginas.
5. **EN05** `html_pptx.py`, `figures.py` e `pptx_deck.py`: PPTX das 12 páginas renderizadas a 3840 px, com o texto do slide no texto alternativo e a fala nas notas; figuras PNG/SVG/CSV do modelo novo; apoio técnico de 7 páginas (o PPTX9 editável foi aposentado).
6. **EN06** `narrative.py`: script único (12 falas), quatro teleprompters, perguntas, guia; lints de números literais, de estilo das cartas (sem travessão, seta, exclamação e chavões) e do modelo citado depois do slide 2.
7. **EN07** `video.py`:
   - perfil único deck12 (12 segmentos) em `config/video_segments.json`;
   - `overlay` reduz o slide inteiro a 0,84 à esquerda e põe a câmera ao lado, sem cobrir conteúdo;
   - `assemble` só com clipes reais; autoteste sintético com x264 limitado a 2 threads.
8. **EN08** `run.py`: CLI e perfis. `scripts/run_esg.py` delega às duas partes e recusa etapas legadas que reescreveriam a fonte canônica sem `--legacy`.
9. **EN09** `qa.py`: 19 verificações por build (autoteste em 1920 e 1366, offline, slides sem controles, PDF e PPTX de 12 páginas, falas nas notas, apoio 7, números entre formatos, relações dos títulos, claims, lints, orçamento de fala, vídeo), capturas e folhas de contato.
10. **EN10** `release.py`:
    - portões `data_factual` → `sent`, com revisão visual vinculada aos hashes;
    - `checklist_envio.md` gerado por `docs.py`.
11. **EN11** `publish.py`:
    - integrador sob trava, com reversão das cópias e das escritas diretas;
    - executa as três suítes e grava `execution_validation.json`, `relatorio_validacao.md`, `release_validation.json` e `visual_review.json`;
    - `promote_final` só promove com o portão liberado (testado em sandbox).
12. **EN12**: progresso em `data/catalog/parallel_progress/production.json`; evidências das duas partes no bloco automático do sincronizador.

Como a Parte 1 foi implementada (para manter ou reexecutar):

0. **Plano 13:** fotografia derivada `snap_20261031_7c31b5560e` (`derive_snapshot`), com quatro fontes primárias novas, e pacote `an_20261101T132455_ac536175`. Detalhe no [plano 13](plans/13_plano_fechamento_residual_agente.md).
0. **Plano 14:** `origin.py` lê a 2ª carta (pesos, motivos, método e teses) e cria `CL.lead.origin`; `market_week.py` registra os fechamentos de 23/10 (mesmas tabelas de cotação), a variação até 30/10, a NTN-B de 23/10 (mesma série do Tesouro) e a reportagem do Poder360 de 26/10, com `CL.result.election_week`; `DERIVE_EXTRA` copia a carta, as tabelas de cotação e a série do Tesouro na fotografia. Tese sem a frase sobre o risco estadual. Pacote `an_20261101T202028_e29905ab`; 3 testes em `tests/analysis/test_plan14.py`.
1. **AN01** `analysis/snapshot.py`: copia insumos para `data/interim/analysis/baseline/<snapshot_id>/files`, com hashes, extrações novas (release 4T25 e plano de capex da Sanepar, apresentação Sabesp, composição de capital CVM, Tesouro 30/10) e verificação dos 16 originais. Fotografia em uso: `snap_20261031_2cf3206ead`.
2. **AN02** `reconciliation.py`, 64 células + C08 com disposição:
   - C02: DVA 7.01.03 e notas de custos por natureza.
   - C03: definição Sabesp `EBIT + D&A − outras operacionais − margem de construção − ativo financeiro líquido`.
   - C04: DFC 6.02.01 + 6.02.02.
   - C05: giro canônico.
   - C06: capex caixa da DFC.
   - C07: apresentação líquida.
   - C08: EBITDA ajustado do release (3.101,5).
3. **AN03/AN04/AN07**, nos módulos `capital.py` e `obligations.py`:
   - capital CVM de 30/06/2026; desdobramento 1:5 e bonificação conferidos;
   - componentes de dívida e obrigações por natureza, com tratamento;
   - cronograma mensal do precatório (50% descontos até mai/2029; 50% investimento não oneroso até dez/2030), atualizado por 8,08% real + IPCA;
   - rolagem jun→out pelo FCFF.
4. **AN06/AN08**, nos módulos `assumptions.py`, `dcf.py` e `valuation.py`:
   - WACC de 13,25% por CAPM local;
   - base remunerada implícita B0 = EBIT2025 / r_pre;
   - capex entra na base com defasagem de 2 anos;
   - quatro cenários, grade 5×3, caso finito, sazonalidade e classes Sanepar;
   - WACC implícito no preço.
5. **AN05/AN09**, nos módulos `sector.py` e `recommendation.py`: matriz ESG com value_refs, ponte de energia, termos regulatórios, decisão por regra (margem 20% e grade inteira acima do preço), 31 claims e 10 slots. Se a regra escolher outra empresa, o código para com erro em vez de gerar texto incoerente.
6. **AN10–AN12**, nos módulos `bundle.py`, `contract.py`, `workbooks.py` e `progress.py`:
   - exportação 1.0;
   - planilha com fórmulas, recalculada no LibreOffice com perfil próprio (`OOXMLRecalcMode=0`);
   - QA e manifesto;
   - publicação atômica;
   - progresso em `data/catalog/parallel_progress/analysis.json`.

Reexecutar a Parte 1 só por fato novo: decisão real H08/H09, fonte primária do WACC regulatório Sabesp, BRR ou DF 2025 da Copasa. Cada execução publica uma versão nova sem sobrescrever as anteriores. O grupo pode reunir H07 e revisar H08/H09 já.

## Ambiente e dependências

Ambiente observado em01/11: Windows/PowerShell, Python **3.11.9**, `.venv` existente com `include-system-site-packages=true`. As13 versões declaradas em [requirements.txt](requirements.txt) foram encontradas. Isso é inventário de pacotes, não uma instalação portátil nem teste de todas as bibliotecas nativas em outra máquina.

- Usar `.venv/Scripts/python.exe` neste workspace. Em outro ambiente, criar uma venv nova e instalar requirements; não copiar a venv como se fosse independente do host. Uma venv nova pode ser criada com `python -m venv .venv` e abastecida com `python -m pip install -r requirements.txt` usando o Python dessa venv. Não sobrescrever a venv existente apenas para repetir preparação.
- LibreOffice observado em `C:/Program Files/LibreOffice/program/soffice.exe`; PowerPoint em `C:/Program Files/Microsoft Office/Root/Office16/POWERPNT.EXE`. Renderização/recálculo usam o primeiro caminho, atualmente específico desta máquina. Em outra máquina, localizar/configurar a ferramenta ou pedir H12 pontual; pesquisa e rascunhos independentes continuam.
- Encoder via pacote `imageio-ffmpeg`; não depender de `ffmpeg`/`ffprobe` no PATH. O teste existente usa fixture sintética temporária, sem participação humana.
- SDK `blpapi`/pasta DAPI foram encontrados, mas localhost8194 estava inativo no teste registrado. É complemento opcional, não dependência obrigatória dos coletores públicos. Conferir a disponibilidade real antes de prometer captura Bloomberg.
- JSON/CSV/Markdown são UTF-8; preservar códigos CVM como texto, sinais, unidade e escala. Na shell Windows, preferir scripts salvos em UTF-8 para código com acentos, em vez de interpolar texto/aspas/comandos de forma frágil.
- Nesta máquina a memória comprometida livre fica baixa (cerca de 0,9 GB livre de commit com vários aplicativos abertos), embora haja RAM física livre. Importar o numpy (via openpyxl) pode falhar com "OpenBLAS error: Memory allocation still failed", e o x264 já falhou com `malloc` (corrigido com `-threads 2`). Rodar as duas partes com `OPENBLAS_NUM_THREADS=1` e `PYTHONIOENCODING=utf-8`. O LibreOffice da Parte 1 usa perfil próprio em `outputs/qa/analysis/lo_profile` com recálculo forçado; a primeira conversão com perfil novo pode falhar (erro de E/S 16) e é repetida uma vez, com registro no QA.

## Arquivos, autoria e reconstrução

| Fonte de verdade / camada | Como usar |
|---|---|
| `config/collection.json` | Recorte comum de preço/avaliação/corte. Mudança exige versão explícita; atualizar documentação não altera o mercado. |
| `config/extra_sources.json` / `verified_evidence.json` | Rotas adicionais e anotações com fonte/localização. Anotação não é prova autossuficiente; conferir o documento usado. |
| `data/catalog/source_registry.csv` / `data/processed/sources.csv` | Rotas descobertas versus arquivos adquiridos e seus hashes. Não confundir as duas camadas. |
| `data/raw/` + `data/interim/acquisitions/` | Bytes e metadados de aquisição necessários para reproduzir esta fotografia. Manter os pares juntos. |
| `data/interim/original_models.json` / `pdf_text/` | Cache de leitura dos originais e extrações; não substitui o PDF/XLSX para validar semântica. |
| `data/processed/` | Tabelas canônicas e resultados calculados. Desde `pub_20261101T124305` vêm do pacote 1.0 ([CANONICAL_SOURCE.json](data/processed/CANONICAL_SOURCE.json)). Ficam fora do pacote `cvm_accounts.csv` e `sinisa_municipal.csv`. Rodar o modelo legado exige `--legacy` e reescreve o esquema. |
| `outputs/draft/production/<build>` / `outputs/qa/production/<build>` | Builds imutáveis da Parte 2 (manifesto e hashes) e seu QA/capturas. O sincronizador não toca neles. Publicar só via `--publish`. |
| `completion_requirements.json` / `html_slide_plan.json` | Especificação e estado dos requisitos; mapas/tabelas dos planos09/10 são derivados. |
| `outputs/draft/` | Artefatos de revisão gerados; corrigir também seu gerador. Nenhum arquivo existente comprova aprovação. |
| `outputs/qa/` | Resultados com versão/data/escopo. Origem dos testes registrados, não promessa de validade futura. |

O diretório atual tem Git, branch `main`, remoto `origin` em https://github.com/GB-Navarro/safra_top_gestor. As sete apresentações publicadas têm exceções explícitas no .gitignore; o HTML usa -text em .gitattributes para conservar os hashes. O commit das peças é `76ef1f30ae9811448de152c8502feb22e93ae8e3`; hashes em `data/catalog/presentations_git_manifest.json`. Dados brutos, interim, demais outputs e várias tabelas continuam locais/ignorados. Uma cópia só do Git contém as apresentações, mas não toda a fotografia de análise. Não publicar bases licenciadas ou credenciais.

Se faltarem arquivos: primeiro restaurar cópia/arquivo da fotografia original. Coleta pública seletiva é alternativa, mas downloads posteriores podem ter versões/conteúdo diferentes; manter captura real, filtrar publicações elegíveis e verificar hashes/escopo. Não fabricar data antiga nem supor que uma nova URL reproduz os bytes de31/10. Orientações privadas e exportações pessoais ausentes continuam dependências identificadas, não arquivos reconstruíveis pelo agente.

## Mapa de implementação

| Módulo | Responsabilidade / atenção |
|---|---|
| [common.py](scripts/common.py) | I/O, cache de aquisição, SHA256, fontes e ROOT relativo ao repositório. |
| [collect_data.py](scripts/collect_data.py) | Rotas CVM/BCB/RI e extras; `--keys`/`--offline`. Não possui antigos subcomandos inventory/import-manual/release. |
| [extract_data.py](scripts/extract_data.py) | Versão/período/escopo CVM, modelos e PDFs; `--cvm`, `--models`, `--pdf`. EPS3.99 fica bruto. |
| [normalize_data.py](scripts/normalize_data.py) | Observações/definições e snapshots. IDs OBS são sequenciais: uma reextração pode renumerá-los; atualizar e conferir claims/consumidores. |
| [sinisa_data.py](scripts/sinisa_data.py) | Municípios/prestadores, homônimos, energia água; sem médias simples de razões. |
| [prepare_analysis.py](scripts/prepare_analysis.py) | Mercado público datado, capital/CNPJ e confrontos básicos. Conferir a fonte para mudar unidade ou direitos. |
| [financial_audit.py](scripts/financial_audit.py) | Auditoria195 células, pontes/termos e conciliação parcial. Coincidência numérica não encerra semântica. |
| [model.py](scripts/model.py) | FCFF, terminal, classes, cenários e ponte ESG. Tratamento econômico e flags por ponto ainda têm pendências C13–C21. |
| [analysis_outputs.py](scripts/analysis_outputs.py) | Premissas, matriz, claims, decisão e auditorias. Há textos/hipóteses literais a alinhar; decisões humanas não são importadas automaticamente. |
| [presentation.py](scripts/presentation.py) | Gerador **legado** de figuras, PPTX9, apoio7 e falas (texto literal). As peças vigentes vêm de `production/` com números por token; usar só com `--legacy`. |
| [render_slides.py](scripts/render_slides.py) / [recalculate_workbook_qa.py](scripts/recalculate_workbook_qa.py) | LibreOffice isolado, PDF/capturas e segunda verificação da planilha. Nova versão/hash invalida revisão anterior pertinente. |
| [validate.py](scripts/validate.py) | Testes, fontes, recortes, referências, artefatos e pacote; escopo limitado ao que está declarado no relatório. |
| [package_outputs.py](scripts/package_outputs.py) | XLSX, guias e manifestos. Regera documentos; não presumir incorporação de H08/H09 ou entrega final. |
| [assemble_video.py](scripts/assemble_video.py) | Montador **legado**; lê `config/video_segments.json` e o PDF publicado. A montagem vigente (deck12, 12 segmentos, slide a 0,84 ao lado da câmera), medição e autoteste sintético estão em `production/video.py`. |
| [execution_status.py](scripts/execution_status.py) | Inicializa estados sem reiniciar registros posteriores; deve preservar este documento manual. |
| [sync_project_docs.py](scripts/sync_project_docs.py) / [validate_completion_docs.py](scripts/validate_completion_docs.py) | Referências/indicadores/tabelas, cobertura, células e dependências; não validam economia por conta própria. |
| [run_esg.py](scripts/run_esg.py) | Coordena estágios por subprocesso. Os estágios `analysis`, `production`, `publish` e `release` delegam às duas partes, e `--mode final` avalia portões via `production.run --promote-final`. Os estágios legados `model`/`slides`/`render`/`validate`/`package` exigem `--legacy` quando a fonte canônica é o contrato 1.0. |
| [production/](production/) + [presentation_web/](presentation_web/) — Parte 2 | Consome só o pacote publicado (`consumer.resolve('latest')`); não importa `analysis/`. Fluxo: `snapshot` → `consumer` → `deck_model` → `slides`/`html_deck`/`figures`/`narrative`/`pptx_deck`(apoio)/`docs` → `qa` (com `html_pptx`) → `release`, com `publish` como integrador. Escrita limitada a `production.common.writable` (o integrador usa `publishing=True` sob trava). Testes em `tests/production/` com fixtures `kind=fixture` em diretório temporário. |
| [analysis/](analysis/) — Parte 1 | Namespace próprio (não importa `scripts/`; ramo legado portado em `analysis/legacy.py`). Fluxo: `snapshot` → `origin` → `reconciliation` → `capital` → `obligations` → `assumptions` → `market_week` → `valuation`/`dcf` → `sector` → `recommendation` → `bundle` (com `workbooks` e `contract`) → `progress`. Escreve só nas raízes exclusivas (`analysis.common.assert_writable`). Atualizações globais pela trava `analysis/lock.py`. Testes em `tests/analysis/`. |

## Comandos de retomada

Começar pela verificação documental, que não pesquisa ou recalcula finanças:

```powershell
& '.\.venv\Scripts\python.exe' scripts/validate_completion_docs.py
& '.\.venv\Scripts\python.exe' scripts/run_esg.py --stage docs
& '.\.venv\Scripts\python.exe' scripts/sync_project_docs.py --check
```

Pipeline legado: só deliberadamente. Ele reescreve `data/processed` com o esquema antigo e exige `--legacy` depois da publicação 1.0:

```powershell
& '.\.venv\Scripts\python.exe' scripts/run_esg.py --stage model --offline --legacy
```

Parte 2 (peças a partir do pacote publicado; build e QA nas raízes próprias, publicação só pelo integrador):

```powershell
$env:OPENBLAS_NUM_THREADS = '1'; $env:PYTHONIOENCODING = 'utf-8'
& '.\.venv\Scripts\python.exe' -m production.run --input-bundle latest --check
& '.\.venv\Scripts\python.exe' -m production.run --input-bundle latest            # build + QA (perfil deck12)
# revisar outputs/qa/production/<build>/{html,pdf,pptx,support7}_contact_sheet.png, html/rec_p*.png e html/p*_1366x768.png
& '.\.venv\Scripts\python.exe' -m production.run --record-visual-review outputs/draft/production/<build> --notes "..."
& '.\.venv\Scripts\python.exe' -m production.run --publish outputs/draft/production/<build>
& '.\.venv\Scripts\python.exe' -m production.run --release-report
& '.\.venv\Scripts\python.exe' -m production.run --baseline default               # rascunho do legado (kind=baseline), só relatório
& '.\.venv\Scripts\python.exe' scripts/run_esg.py --mode final                     # recusa com motivos até os portões liberarem
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests/production -p "test_*.py"
```

Abrir o HTML: `outputs/draft/html/apresentacao_esg.html` no navegador, em tela cheia (F11). Avança com →, espaço ou clique; volta com ←; Home/End; G liga o modo gravação e Esc desliga. `?selftest=1` roda o autoteste. Não há botões na tela.

Parte 1 (pacote analítico 1.0; não toca nos caminhos globais do pipeline legado):

```powershell
$env:OPENBLAS_NUM_THREADS = '1'
& '.\.venv\Scripts\python.exe' -m analysis.run --baseline derive:data/interim/analysis/baseline/snap_20261031_b126c2edf0
& '.\.venv\Scripts\python.exe' -m analysis.run --check outputs/draft/analysis_bundle/an_20261101T202028_e29905ab
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests/analysis -p "test_*.py"
```

Opções de `--baseline`:

- **`derive:<fotografia-mãe>`:** copia os insumos da mãe e acrescenta só a coleta própria (`data/raw/analysis/*/*` e `EXTRA_PDFS`), com ID novo se o conteúdo mudar.
- **`new`:** recusado enquanto existir `data/processed/CANONICAL_SOURCE.json`, porque capturaria saídas publicadas como insumo.
- **Caminho de uma fotografia existente:** reexecuta sobre ela.

Não rodar o pipeline legado (`--legacy`) em paralelo com as Partes 1 ou 2.

`--stage all --offline` encadeia os estágios; `--refresh` reextrai CVM/SINISA. Não começar por reprocessar tudo se a correção é localizada. O estágio model e os geradores podem substituir hipóteses/resultados/guias: aplicar decisões no código/base correta e atualizar consumidores. Após novos XLSX, rodar `scripts/recalculate_workbook_qa.py`; após novo PDF, inspecionar as páginas e registrar a revisão por hash. Os scripts não incorporam automaticamente decisões escritas em Markdown.

Para coletar, o coletor permite seleção por chave de `jobs()`/extra_sources; verificar a chave antes de usar. O download direto do regulamento Safra retornou403; não repetir esse erro em loop. Não automatizar a aquisição B3 restringida. Coleta offline usa os arquivos já disponíveis, não recupera magicamente um snapshot ausente.

A apresentação final (deck12, plano 14) usa `production/brand.py` (fontes/símbolo do manual), `production/content.py` (textos e falas com tokens), `deck_model.py`, `slides.py`, `html_deck.py`, `presentation_web/deck.css` e `deck.js`; `html_pptx.py` gera o PPTX das páginas do PDF do HTML. A QA compara números entre HTML, PPTX (texto alternativo e notas) e script, e renderiza o PPTX pelo LibreOffice. Os perfis pptx9/html10 foram aposentados; não recriá-los. Para mudar texto, editar `content.py` (números só por `{{value:ID}}`) e rodar o build; os lints e `guards()` recusam números digitados, chavões e títulos que o pacote não sustenta. A conferência de fatos do plano 14 está em `data/interim/production/fact_check/` (scripts reexecutáveis e `fact_check_final.json`).

## Registro de continuidade

| Campo | Registro desta revisão |
|---|---|
| Última tarefa | Plano 14: apresentação final igual ao PPT reorganizado do grupo (12 slides planos), origem na 2ª carta, narrativa no estilo das cartas, conferência final de dados/fontes e script; HTML, PDF e PPTX publicados (`pub_20261101T203832`); PPT do grupo excluído após a montagem. |
| Alterações do plano 14 | **Parte 1:** `analysis/origin.py` e `analysis/market_week.py` (novos), `snapshot.py` (`DERIVE_EXTRA`), `bundle.py`, `recommendation.py` (origem no slot lead, semana do segundo turno no slot de resultado, tese revista); `tests/analysis/test_plan14.py`; fonte nova `data/raw/analysis/mercado/poder360_queda_acoes_pos_eleicao.html`; fotografias `a54d10bd24` e `b126c2edf0`; pacotes `an_20261101T193707_e8a63bb3` e `an_20261101T202028_e29905ab` (vigente).<br>**Parte 2:** `content.py`, `deck_model.py`, `slides.py` (novo), `html_deck.py`, `html_pptx.py`, `narrative.py`, `qa.py`, `publish.py` (perfil único, PDF/PPTX finais também em `outputs/draft/apresentacao_esg.*`, remoção de obsoletos com reversão), `run.py`, `release.py`, `video.py`, `figures.py`, `pptx_deck.py` (só apoio), `docs.py`, `labels.py`, `consumer.py` (estilo `pct2`), `brand.py`, `common.py`; `presentation_web/deck.css` e `deck.js` reescritos; testes `test_plan14.py`, `test_versions.py` e `test_narrative_video.py`. Builds `pr_..202413` (QA reprovada, verificação corrigida), `pr_..202541`, `pr_..202800` (publicado em `pub_..202934`) e `pr_..203705` (publicado em `pub_..203832`, vigente).<br>**Sob trava:** `completion_requirements.json` (C20, C23, C24, C28, G06, regra R11), `two_part_execution.json` (`config/video_segments.json` passa a ser escrita da Parte 2), `html_slide_plan.json` (mapa S01–S12), `manual_export_requests.csv` (H08–H11), `scripts/validate_completion_docs.py`, `scripts/sync_project_docs.py`, AGENTS.md (regra de perfil), plano 10 (marcado como substituído), plano 14, estado central, este guia e README.<br>**Removidos:** `outputs/ppt_reorganizado.pptx` (a pedido), `outputs/draft/script_apresentacao_html10.md`, `config/video_segments_html10.json` e capturas antigas (cópias na reversão `pub_..202934`). |
| Verificações | **Nesta tarefa:** `analysis.run` (QA e contrato aprovados, 42 testes); 58 testes da Parte 2; QA do build 19/19 (autoteste 73/73 em 1920×1080 e 1366×768); revisão visual das 48 capturas (HTML, PDF, PPTX reconvertido, modo gravação, 1366, apoio) com o build final idêntico pixel a pixel ao revisado; publicação com 42 + 58 + 13 testes, código 0, 15 originais preservados; conferência de fatos: 118 valores, 39 observados (36 no texto da fonte, 3 à mão), 21 afirmações qualitativas com trecho na fonte, cotações de 30/10 conferidas em segunda fonte pública; quadro do vídeo sintético conferido; validadores documentais e sincronização ao fim. Testes não certificam premissas econômicas. |
| Verificações históricas — Git | Envio das sete apresentações anteriores ao GitHub (commit `76ef1f3`): SHA256 dos blobs conferidos com o manifesto de publicação. O GitHub continua com essa versão anterior (HTML10/PPTX9); a apresentação do plano 14 não foi enviada (sem pedido). |
| Alterações da revisão visual (HTML10, histórico) | Fontes incorporadas em presentation_web/fonts; brand.py; CSS/JS; html_deck.py; html_pptx.py; QA de geometria, exportação e hashes; publish.py inclui PPTX10. Substituído pelo deck12 no plano 14. |
| Tarefa anterior — plano13 | Fechamento residual da análise e correções factuais; detalhes históricos nas linhas seguintes. |
| Alterações do plano 13 | **Fontes:** 4 PDFs primários em `data/raw/analysis/{urae1,agepar,copasa,sanepar}/`.<br>**Fotografia:** modo `derive:` em `analysis/snapshot.py`/`run.py`, com `new` recusado após a publicação 1.0; fotografia `snap_20261031_7c31b5560e`.<br>**Análise:** `assumptions.py`, `capital.py`, `sector.py`, `valuation.py` (`brr_check`), `recommendation.py`, `bundle.py` e `progress.py`; 7 testes em `tests/analysis/test_plan13.py`.<br>**Pacote:** `an_20261101T132455_ac536175`.<br>**Produção:**<br>• `content.py` (P04, B4 e três perguntas);<br>• `pptx_deck.py` (A01 com a verificação da BRR);<br>• `docs.py` (auditoria, próximos passos e conciliação);<br>• `publish.py` (reversão das escritas diretas, formato legado de `script_word_counts.json`, tolerância ao banner em `promote_final`);<br>• `release.py`/`qa.py`/`run.py` (portão visual, `--profile`, `--baseline`, `--record-visual-review`, `--promote-final`).<br>**Builds e publicação:** `pr_20261101T132746_ac536175`, publicação `pub_20261101T132847`.<br>**Scripts:**<br>• `sync_project_docs.py` (builds imutáveis, evidências);<br>• `validate_completion_docs.py` (esquema 1.0, verificação HTML real).<br>**Sob trava:**<br>• `outputs/qa/claims_semantic_review.json`;<br>• completion_requirements.json (C20 e C22 fechados; notas de C06, C09, C13–C16, C18);<br>• `collection_backlog.csv` (D09, D16, D19, D21, D31);<br>• `n_status.csv` (N10);<br>• `html_slide_plan.json` (só o status);<br>• estado central, este guia e README. O AGENTS.md não mudou nesta tarefa; as regras de builds e de liberação final são da Parte 2. |
| Alterações da Parte 2 (tarefa anterior) | **Código novo da Parte 2:**<br>• `production/`: 18 módulos, incluindo o CLI `run.py`;<br>• `presentation_web/` (`deck.css`, `deck.js`);<br>• `tests/production/` com 50 testes e fixtures em temporário;<br>• `config/video_segments_html10.json`;<br>• progresso em `data/catalog/parallel_progress/production.json`.<br>**Fotografia e builds:**<br>• fotografia `data/interim/production/baseline/legacy_7dbbf9cfea`;<br>• builds em `outputs/draft/production/` (publicado: `pr_20261101T124209_e758f3af`) e QA em `outputs/qa/production/`;<br>• os builds sem manifesto `pr_..121244` e `pr_..124103` foram interrompidos e não são publicáveis.<br>**Publicação `pub_20261101T124305`:** 82 arquivos em outputs/draft (peças, figuras, teleprompters, html, coleta), outputs/qa/html, `data/processed` (contrato 1.0) e `data/interim` (conciliação/cronograma), mais relatórios de integração. Reversão em `data/interim/production/rollback/pub_20261101T124305`; ela não cobre as escritas diretas dessa primeira publicação, lacuna já corrigida no código.<br>**Arquivos da Parte 2 alterados:** `scripts/run_esg.py` (delegação, guarda `--legacy`, final por portões); `scripts/sync_project_docs.py` (trava, builds imutáveis, evidências das duas partes); `scripts/validate_completion_docs.py` (esquema 1.0, verificação HTML real).<br>**Sob trava:**<br>• `tests/test_core.py`: ajuste mínimo, pois o teste de `esg_bridge` lê a cópia legada quando a fonte canônica é 1.0;<br>• completion_requirements.json (C19–C29; C21 e C28 fechados);<br>• manual_export_requests.csv (H07/H10/H11/H13);<br>• este guia, o estado central e o README.<br>**Incidente:** `run_esg.py --stage model` foi executado sem querer antes da primeira publicação. A regeneração legada saiu idêntica às fotografias; o `sources.csv` foi restaurado e os três builds de desenvolvimento com banner foram restaurados byte a byte (detalhes no histórico do estado central). Nenhum original foi alterado. |
| Verificações | Nesta tarefa: referência remota conferida, SHA256 dos sete arquivos idênticos aos blobs do commit e ao manifesto de publicação, diff staged sem problemas e sincronização documental/check executados ao fim. Atributo -text impede conversão de finais de linha do HTML. Testes102 e revisão visual são das tarefas anteriores; não houve novo build ou análise. |
| Verificações históricas — plano13 | **Executadas na tarefa anterior (plano13):**<br>• `require_text` confere, na página citada, cada trecho usado das fontes novas;<br>• ensaio do build da análise em diretório temporário, comparando com o pacote anterior (só o prazo da Copasa mudou entre valores existentes; casos-base iguais);<br>• `analysis.run` com QA e contrato aprovados e 39 testes;<br>• `production.run` com QA 15/15;<br>• revisão visual das folhas completas e das páginas alteradas;<br>• publicação com 39 + 50 + 13 testes, código 0, 16 originais preservados e portões recalculados;<br>• revisão semântica das 32 afirmações sem defeito;<br>• validadores documentais, sincronização e `--check` ao fim.<br>Testes não certificam premissas econômicas. |
| Verificações da Parte 2 (tarefa anterior) | **Executadas na Parte 2:**<br>• build `pr_20261101T124209_e758f3af` com QA 15/15 (autoteste HTML com 31 verificações em 1920 e 1366, offline, PDF de 10 páginas, PPTX 9 e apoio 7, números entre formatos, value_refs, ponte, claims por perfil, lint, orçamento de fala, encoder sintético, prontidão de vídeo);<br>• revisão visual de 31 capturas registrada com os hashes;<br>• no estado publicado: 32 testes da Parte 1, 49 da Parte 2 e 13 legados, todos com código 0; 16 originais preservados;<br>• consumidor `--check` válido; `--baseline default` válido como baseline e recusado no modo padrão; `--mode final` recusado com motivo H08/H09; guarda legada recusando `--stage model`;<br>• `validate_completion_docs.py` e `validate_two_part_plans.py` aprovados; sincronização e `--check` ao fim.<br>**De execuções anteriores (Parte 1):** QA analítica do pacote e recálculo LibreOffice.<br>Testes não certificam premissas econômicas. |
| Próxima ação | **Grupo:**<br>• H07, seguindo `outputs/draft/checklist_envio.md`;<br>• H08/H09, registrando em `data/interim/decisoes_equipe.md` (a narrativa e a semana do segundo turno estão no slide 11 e nas perguntas);<br>• H10, ensaiando com o HTML (ou PDF/PPTX) e os teleprompters; revisar as falas e os slides (`data/interim/production/fact_check/fact_check_final.json` lista o que foi conferido).<br>**Agente:** reexecutar Parte 1 → Parte 2 → publicar se H08/H09 mudarem premissas; montar o vídeo com clipes reais; `--mode final` quando os portões liberarem. |
| Dependências humanas | H07 (instruções privadas, canal, horário, uso do HTML); H08/H09 sobre a proposta pronta; H10/H11 com ensaios e clipes reais (12 segmentos, um por slide); revisão integral do vídeo; H13 envio. H01 é complemento opcional. |
| Trabalho não iniciado aqui | Decisões humanas, ensaios, clipes, vídeo, promoção a outputs/final e envio. A revisão visual e a semântica registradas são do agente; as do grupo não foram feitas. Residual público sem fonte primária extraível (uma tentativa cada): BRR líquida de Sabesp/Copasa, plano de capex vigente da Copasa, preço da EMAE e datas de eventos de Sabesp/Copasa. |
| Em caso de interrupção | Conferir:<br>• `outputs/draft/analysis_bundle/latest.json` e `outputs/draft/production/published.json`;<br>• `outputs/qa/execution_validation.json`;<br>• a trava `data/interim/coordination/documentation.lock` (não apagar trava ativa de outro dono).<br>Builds e pacotes são imutáveis: uma reexecução gera versão nova. Nada foi deixado rodando em background. |

**Ao encerrar cada tarefa material:** atualizar este registro, o ponto de retomada, decisões/limites alterados e o estado central. Manter detalhes de cada pendência no catálogo, sem copiar aqui a lista inteira. O sincronizador só mantém blocos automáticos; não substitui a revisão do contexto. Não modificar a data para simular execução ou preencher aprovação ausente.

## Memória técnica da execução original

As seções restantes preservam o registro da primeira execução, em31/10/2026. Para andamento e próximo trabalho, usar as seções operacionais acima e o estado central; não interpretar um status histórico como confirmação da situação futura.

O fechamento executável está no [contrato09](plans/09_contrato_de_fechamento.md), em completion_requirements.json e no mapa de células derivado. O [plano10](plans/10_plano_html_interativo.md) especificava o HTML10 (substituído pelo deck12 do [plano 14](plans/14_plano_apresentacao_final.md) em 01/11). A auditoria documental de01/11 cobre requisitos conhecidos e não executa suas correções; H07 ainda pode adicionar exigências. Rodar validate_completion_docs.py e sync_project_docs.py após mudanças.

Execução em 31/10/2026. Corte informacional: 31/10 às 18:25:27 de São Paulo; preços de 30/10. Não existe Git neste diretório. Originais imutáveis: 16, preservados por SHA256. Não sobrescrever modelos/cartas/documentos originais.

## Resultado local

`outputs/draft/` contém a base XLSX, modelo auditável, nove slides editáveis e PDF, apoio de sete páginas, quatro figuras PNG/SVG/CSV, roteiro, script por quatro integrantes, teleprompters, doze perguntas e guia de gravação. Pacote de coleta e manifestos também disponíveis. Estado: rascunho técnico, revisão econômica pendente. Não há vídeo real, ensaio ou envio concluído. Ler `outputs/qa/execution_validation.json` para as contagens atuais e escopo dos testes.

## Correções verificadas

- Regulamento 2026 lido via ferramenta web no PDF oficial: conteúdo p9, peso/classificação p10, cronograma p12. Original HTTP 403, portanto o JSON de regras é uma anotação da verificação, não o PDF original baixado. Público: até dez minutos, todos ativos, SWOT/médio prazo/recomendação/matriz ESG, entrega 02/11; peso setorial 25%, cinco finalistas padrão, até dez discricionários. Mensagem/live privada com hora/canal continua H07.
- Os três modelos já fazem stub 62/365. A XTIR é da firma/FCFF, não retorno da ação. A reprodução matemática confere, as premissas não foram certificadas.
- Copasa: quantidade em milhares no release, capital líquido 379,181 milhões arredondado. Sabesp: capital líquido de junho 3.506,830477 milhões inclui uma PN especial. Sanepar 1.511,205519 milhões ON+PN; unit1ON+4PN não adiciona capital.
- Adicional de dividendos PN 10% não fixa preço PN/ON; rateio usado é hipótese de risco/distribuição. Conta Sanepar é individual; zero NCI é específico desse perímetro.
- CINCO referências públicas de fechamento 30/10 foram coletadas; não afirmar confirmação Bloomberg/B3. Capital/balanço de junho não é observação de outubro.
- CVM: EPS na subárvore 3.99 permanece bruto, fora de valor_brl_million. Arquivo contém níveis hierárquicos não aditivos e DRE trimestral/acumulada; usar início/fim/conta para filtrar.
- SINISA: 271.856 observações municipais, sigla+nome+UF para excluir homônimo Sanepar no PA. Energia GFI2004 é água municipal 2024, não consolidado/marginal. Sem média simples de perdas. Nacional: água84,1%/coleta62,3% da população total.
- Ponte ESG usa redução HIPOTÉTICA de 1% da despesa de energia, retenção50–100%,2027–35,IR34%,WACC12,5%,sem terminal. Não adicionar a margem-base sem retirar sobreposição.
- Sanepar: passivo precatório R$4.407,957mi; nominal não é PV. 50% modicidade/50% investimentos não onerosos, atualização real8,08%+IPCA. Dedução integral é diagnóstico, não preço-alvo validado.
- Capex Sanepar anunciado13.077mi inclui doações212,8mi; não igualar total com caixa. EBITDA e imposto Sanepar2025 têm não recorrentes; Sabesp requer ponte de EBITDA/construção/ativo financeiro; Copasa requer receita regulatória compatível com capex.
- Caso experimental comum: WACC12,5%,g3,5%,ROICterminal12,5%,Focusaté2030,prorrogação3,5%própria. Operações herdadas só propostas. Copasa resíduo negativo = N/D, não alvo zero/insolvência. Sanepar29,14 versus30,85 não sustenta compra a mercado; faixa com dedução nominal não é faixa de valor justo certificada.

## Dependências e continuação

H07: instruções privadas/hora/canal. H08: revisão pelo grupo das cinco decisões econômicas propostas, com evidências/alternativas em `decisao_proposta.md` e auditorias. H09: grupo assumir a recomendação. H10: dois ensaios reais. H11: clipes reais. H13: revisão completa, envio e comprovante. H01 útil para confirmar preço/capital/eventos; SDK Bloomberg instalado, mas localhost8194 inativo no teste (`outputs/qa/bloomberg_capability.json`); abrir/autenticar Terminal ou exportar é ação humana, sem pedido de credenciais. H02–H06 opcionais substituídos por fontes públicas. H12 PDF resolvido por LibreOffice instalado fora do PATH; encoder de vídeo também instalado e testado com fixture temporária. Nunca marcar revisão/ensaio/gravação/envio como concluídos por decurso de tempo.

Pesquisa econômica pública ainda parcial é trabalho pendente do agente, não dependência humana de acesso: ver `outputs/draft/pendencias.md`. Conciliar a base regulatória anual, recorrência, capex caixa e cronograma/duplicidade das obrigações antes de chamar os valores de alvos. Não calibrar hipóteses para obter valorização desejada. Respeitar o escopo/tempo da apresentação; extras N04/N21–N23 foram adiados.

## Comandos reais

`.venv/Scripts/python.exe scripts/run_esg.py --stage all --offline` reproduz a base atual, cálculos, apresentações, PDFs, QA e pacotes. `--refresh` reextrai CVM/SINISA. `--stage collect` sem offline consulta fontes públicas; originais imutáveis por hash. O snapshot de datas é congelado; comando recusa migração silenciosa. `--mode final` atualmente é recusado incondicionalmente: implementar e testar uma liberação baseada em evidências é pendência técnica A11. Regeneração dos PDFs invalida a revisão visual anterior quando o hash mudar.

Documentação: `scripts/run_esg.py --stage docs` ou `scripts/sync_project_docs.py`, seguido de `scripts/sync_project_docs.py --check`. O sincronizador não recalcula finanças nem presume decisões humanas. Atualizar também o texto de fases/pendências e histórico no documento central antes de encerrar cada trabalho material.

PowerPoint e LibreOffice estão instalados em Program Files. Python local `.venv` usa system-site-packages; bibliotecas adicionais/versões estão em requirements.txt. Não usar automação B3; exportações manuais podem ser importadas. Não enviar mensagens nem arquivos ao Safra pelo usuário. Não criar classificação, pesos adicionais, consenso ou ratings não observados.
