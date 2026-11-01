# Safra Top Gestor 2026 — asset.dev

<!-- PROJECT_STATUS:START -->
> [Estado central do projeto](ESTADO_DO_PROJETO.md) · Revisão documental: 01/11/2026. Guia de leitura e continuidade; consultar o andamento na fonte central.
<!-- PROJECT_STATUS:END -->

Projeto de análise setorial ESG de saneamento da equipe asset.dev. **Execução parcial.** As duas partes do agente foram executadas em 01/11/2026:

- **Parte 1** (dados, conciliação e análise econômica) publicou um pacote analítico 1.0 como proposta.
- **Parte 2** (apresentação e engenharia) regenerou dele gráficos, slides, falas e um **HTML interativo de dez páginas**, com portões de liberação e integrador.
- **Plano 13** ([fechamento residual](plans/13_plano_fechamento_residual_agente.md)) corrigiu fatos com fontes primárias (desestatização da Copasa, prazos, WACC regulatório da Sabesp, verificação da BRR da Sanepar) e republicou pacote e peças.

Faltam:
- decisões do grupo (H08/H09) e instruções privadas (H07);
- ensaios, vídeo e envio.

**Comece por [ESTADO_DO_PROJETO.md](ESTADO_DO_PROJETO.md)**: o que é o projeto, o que foi feito, cumprimento de A01–A11, pendências do agente/grupo, próxima ação e histórico. A documentação foi revisada em01/11/2026. Os dados/modelos permanecem no recorte de30–31/10/2026, registrado em `config/collection.json`.

Para executar o restante, usar o **[contrato de fechamento09](plans/09_contrato_de_fechamento.md)**: dados/correções/entregáveis com responsáveis, fontes, dependências, aceite e alternativa, incluindo vínculo célula a célula. O **[plano10](plans/10_plano_html_interativo.md)** especifica a conversão dos nove slides para dez páginas HTML interativas. A conversão está implementada em [outputs/draft/html/apresentacao_esg.html](outputs/draft/html/apresentacao_esg.html): um arquivo local, sem rede. Teclas: ←/→, G para gravação, T para tema e ? para ajuda.

Execução distribuída em dois planos: **[parte1 — dados e análise econômica](plans/11_plano_agente_analise_dados.md)** e **[parte2 — apresentação e engenharia de entrega](plans/12_plano_agente_engenharia_entrega.md)**. Cada parte pode começar, testar e entregar seu pacote autônomo com os arquivos atuais. A versão definitiva integrada exige os dados revisados e as evidências humanas aplicáveis. Contrato, autoria e24 tarefas estão em [two_part_execution.json](data/catalog/two_part_execution.json). **Parte 1 implementada** em `analysis/`; pacote vigente em [latest.json](outputs/draft/analysis_bundle/latest.json); reexecução com `python -m analysis.run --baseline <fotografia>`. **Parte 2 implementada** em `production/` e `presentation_web/`: `python -m production.run --input-bundle latest` gera e verifica as peças, e `--publish` as publica sob trava ([manifesto](outputs/draft/production/published.json)).

As **sete apresentações mais recentes estão versionadas em `main`**, no [commit `76ef1f3`](https://github.com/GB-Navarro/safra_top_gestor/commit/76ef1f30ae9811448de152c8502feb22e93ae8e3). O [índice com SHA256](data/catalog/presentations_git_manifest.json) identifica exatamente os arquivos publicados. O clone inclui essas peças; os dados brutos e os demais produtos locais continuam fora do Git.

- [**Apresentação interativa (HTML,10 páginas)**](outputs/draft/html/apresentacao_esg.html), [PDF10](outputs/draft/html/apresentacao_esg.pdf) e [PPTX10 fiel ao HTML](outputs/draft/html/apresentacao_esg.pptx): design preto/ouro do manual, com a marca asset.dev. O PPTX10 usa imagens de alta resolução e notas; o perfil PPTX9 editável permanece separado.
- [Apresentação PDF](outputs/draft/apresentacao_esg.pdf) e [PPTX com notas](outputs/draft/apresentacao_esg.pptx): nove slides.
- [Modelo auditável](outputs/draft/base_modelo_auditavel.xlsx), [base de coleta](outputs/draft/coleta/base_dados_coletados.xlsx) e [apoio técnico](outputs/draft/apoio_tecnico.pdf).
- [Próximos passos do grupo](outputs/draft/PROXIMOS_PASSOS.md), [decisão proposta](outputs/draft/decisao_proposta.md), [conciliação financeira](outputs/draft/conciliacao_financeira.md) e [auditoria](outputs/draft/auditoria_modelos.md).
- [Script dos quatro](outputs/draft/script_apresentacao.md) (e [versão HTML10](outputs/draft/script_apresentacao_html10.md)), [teleprompters](outputs/draft/teleprompter/), [perguntas de banca](outputs/draft/perguntas_banca.md), [guia de gravação](outputs/draft/guia_gravacao.md), [checklist de envio](outputs/draft/checklist_envio.md) e [validação executada](outputs/qa/relatorio_validacao.md).
- [Contexto de execução para continuidade](EXECUTION_CONTEXT.md) e [pendências](outputs/draft/pendencias.md).

O regulamento público2026 foi verificado via ferramenta web apesar do HTTP direto403: teto de dez minutos, participação ativa, SWOT/médio prazo/recomendação/matriz ESG, prazo02/11 e peso25% na classificação. Horário/canal e orientações privadas ainda pendentes. Fontes e páginas em [regras verificadas](outputs/draft/regras_2026_verificadas.md). A proposta atual do pacote é **Sanepar (SAPR11), compra condicionada**: comprar só até o limite de entrada, com o precatório deduzido e três gatilhos de revisão. Os números estão nas peças e no [LEIA_PRIMEIRO do pacote](outputs/draft/analysis_bundle/an_20261101T132455_ac536175/LEIA_PRIMEIRO.md). É proposta do agente, pendente de H08/H09; não usar os valores como alvos certificados.

## Por onde começar

| Documento | Função |
|---|---|
| [Estado central](ESTADO_DO_PROJETO.md) | Fonte principal do andamento real; atualizar em cada mudança material. |
| [Instruções permanentes](AGENTS.md) | Obriga próximos agentes a revisar o estado, preservar evidências e sincronizar documentos. |
| [Contexto de execução](EXECUTION_CONTEXT.md) | Memória técnica, decisões metodológicas e limites dos resultados anteriores. |
| [Contexto do desafio](SAFRA_TOP_GESTOR_2026_CONTEXT.md) | Pesquisa, regras verificadas e histórico; não substitui instruções privadas. |
| Planos04–08 abaixo | Método, responsabilidades e critérios; não são prova de que as fases terminaram. |
| [Contrato09](plans/09_contrato_de_fechamento.md) e [plano10](plans/10_plano_html_interativo.md) | Fechamento executável de dados/análise/produção e especificação do HTML10 (implementado em production/ e presentation_web/). |
| [Plano11](plans/11_plano_agente_analise_dados.md) e [plano12](plans/12_plano_agente_engenharia_entrega.md) | Duas partes autônomas, contrato de integração, caminhos exclusivos e critérios de entrega. |
| outputs/draft e outputs/qa | Artefatos de revisão e verificações com data/escopo próprios. |

- **Para o agente executar toda a etapa:** [plano principal do agente](plans/05_plano_implementacao_agente_esg.md), com tarefas A01–A11, método, motivo e critérios de conclusão.
- **Para você e o grupo:** [plano humano](plans/06_plano_executivo_grupo_esg.md), com ações H01–H13, procedimento e arquivo esperado.
- **Apoio:** [contratos técnicos da coleta](plans/07_plano_coleta_dados_agente.md) e [exportações Bloomberg/orientações](plans/08_plano_coleta_dados_humano.md).
- **Contexto e diagnóstico:** [contexto consolidado](SAFRA_TOP_GESTOR_2026_CONTEXT.md) e [checklist de fechamento](plans/04_checklist_de_fechamento_esg.md).

## Estrutura atual

```text
cartas/                         Cartas originais, mantidas no mesmo lugar
plans/                          Planos históricos e planos atuais 04–08
resources/
  modelos_originais/{sabesp,copasa,sanepar}/
  documentos_financeiros/sabesp/
  roteiros/
config/
  collection.json               Configuração da coleta
  repository_layout.json        Mapa dos arquivos movidos e pastas
data/
  catalog/                      Inventário, fontes, métricas e tarefas
  raw/                          Fontes adquiridas preservadas; exportações pessoais quando fornecidas
  interim/                      Extrações candidatas e conciliações em trabalho
  processed/                    Cadastros e tabelas normalizadas
scripts/                        Pipeline legado, coordenador run_esg e sincronizador documental
analysis/                       Parte 1: análise e pacote 1.0
production/, presentation_web/  Parte 2: peças, HTML interativo, QA, portões e integrador
tests/                          Regressões legadas, tests/analysis e tests/production
outputs/{draft,final,qa}/         Pacotes de trabalho, versões finais e verificações
```

Os dez arquivos antes soltos em `resources/` foram movidos, sem modificar o conteúdo. Os nomes foram preservados; os caminhos antigos e os hashes estão no [inventário original](data/catalog/original_files_manifest.json) e no [catálogo de materiais](data/catalog/local_assets.csv). O relatório `data/catalog/reorganization_audit.csv` registra a conferência da reorganização. Os documentos Markdown de contexto/planos tiveram suas referências atualizadas.

## O que já está preparado

- [Configuração da coleta](config/collection.json), com recortes, unidades e rotas públicas.
- [Catálogo de fontes](data/catalog/source_registry.csv): rotas com o estado efetivo; [fontes adquiridas](data/processed/sources.csv) registram arquivos e hashes.
- [Fila de implementação/coleta](data/catalog/collection_backlog.csv), com responsáveis propostos, prioridades e dependências.
- [Ações humanas H01–H13](data/catalog/manual_export_requests.csv), incluindo acesso, revisão econômica, ensaio, gravação e envio; o catálogo mantém o nome legado.
- [Dicionário de métricas](data/catalog/metric_dictionary.csv), observações, definições, contas CVM, modelos e dados SINISA em `data/processed/`.

Três identidades conferidas na CVM, cinco instrumentos, fontes adquiridas e observações preenchidas. O pacote contém auditoria ampliada de195 células históricas com diferenças e lacunas explícitas. Aquisição, coincidência numérica e hipótese econômica são estados distintos; nenhum dado foi aprovado apenas pela cor da célula original.

## Regras de trabalho

Preservar originais e downloads; trabalhar com cópias/extrações nas camadas seguintes. Distinguir fonte descoberta, arquivo adquirido, dado extraído e dado revisado. Cada número deve apontar para documento, página/tabela ou consulta, período e definição. Ausência não é zero.

Novos dados entram em `data/raw/`, conforme a origem. Modelos revisados e saídas vão para `outputs/`; não sobrescrever as planilhas de `resources/modelos_originais/`. Exportações Bloomberg ficam locais. A obtenção de arquivos B3 é manual conforme a rota prevista, seguida de importação local.

## Reprodução

Em PowerShell, com `requirements.txt` instalado:

```powershell
$env:OPENBLAS_NUM_THREADS = '1'; $env:PYTHONIOENCODING = 'utf-8'
& '.\.venv\Scripts\python.exe' -m analysis.run --check outputs/draft/analysis_bundle/an_20261101T132455_ac536175
& '.\.venv\Scripts\python.exe' -m production.run --input-bundle latest      # peças + QA num build novo
& '.\.venv\Scripts\python.exe' -m production.run --release-report
& '.\.venv\Scripts\python.exe' scripts/run_esg.py --stage docs
& '.\.venv\Scripts\python.exe' scripts/sync_project_docs.py --check
& '.\.venv\Scripts\python.exe' scripts/validate_completion_docs.py
```

Desde a publicação do contrato 1.0, `scripts/run_esg.py` delega às duas partes (`--stage analysis|production|publish|release`). Os estágios legados que reescreveriam `data/processed` exigem `--legacy`. `--mode final` avalia os portões de liberação e hoje recusa com motivos (H08/H09 sem registro). As datas do snapshot são congeladas. Um build novo exige nova revisão visual vinculada aos hashes antes de `--publish`. Nenhum comando presume julgamento econômico, envia mensagem ou submete arquivos.

A montagem de vídeo (`production/video.py`) espera clipes reais em `data/raw/gravacao/`: 13 segmentos no perfil pptx9 ([config](config/video_segments.json)) ou 14 em `data/raw/gravacao/html10/` no perfil html10. O autoteste usa apenas fixture sintética temporária, sem produzir vídeo do grupo. `outputs/final/` só recebe arquivos pela promoção condicionada aos portões. As ações humanas estão em `PROXIMOS_PASSOS.md` e no `checklist_envio.md`.

## Manutenção da documentação

**Para outro agente retomar sem o chat:** seguir [EXECUTION_CONTEXT.md](EXECUTION_CONTEXT.md). Ele contém ordem de leitura, autorização/limites já registrados, ponto de retomada C02, ambiente, mapa do código, comandos e recuperação dos arquivos locais. Não reiniciar o projeto nem presumir que só os arquivos versionáveis contenham os dados/cache; há camadas ignoradas pelo Git e a venv atual depende desta máquina.

Ao alterar dados, análise, código, decisões ou entregáveis, o agente deve atualizar ESTADO_DO_PROJETO.md, o registro/ponto de retomada de EXECUTION_CONTEXT.md e os catálogos afetados. `scripts/sync_project_docs.py` sincroniza indicadores, referências e manifestos; `--check` confere consistência, campos/data do contexto operacional, links e preservação dos originais. Os estágios chamam a sincronização, que não reexecuta finanças nem comprova aprovação humana. O contexto manual é preservado pelo gerador de status; a revisão de conteúdo continua obrigatória conforme AGENTS.md.

`completion_requirements.json` e `html_slide_plan.json` alimentam automaticamente as tabelas dos planos09/10. `validate_completion_docs.py` confere cobertura de fases/tarefas/ações/indicadores, células abertas, dependências e dez páginas/tempos; também é chamado pelo sincronizador. Requisito documentado não equivale a requisito concluído, nem cobre instruções privadas ainda não recebidas.

Os HTMLs01–03 e demais originais são mantidos como histórico sem reescrita. Relatórios antigos de validação de planos/reorganização descrevem suas próprias execuções e não comprovam conclusão atual do projeto.
