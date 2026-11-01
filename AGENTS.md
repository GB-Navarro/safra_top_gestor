# Instruções permanentes do projeto

## Estado e documentação

A pedido do usuário, **manter [ESTADO_DO_PROJETO.md](ESTADO_DO_PROJETO.md) e [EXECUTION_CONTEXT.md](EXECUTION_CONTEXT.md) atualizados em toda tarefa que altere dados, análise, código, decisões, entregáveis ou pendências**. O primeiro é a fonte do andamento; o segundo é o guia operacional para outro agente retomar sem o chat. Ler ambos e o README ao iniciar trabalho.

Antes de encerrar uma tarefa:

1. Atualizar no documento central as fases A01–A11, pendências, próxima ação e histórico. Atualizar também no contexto operacional o ponto de retomada, última tarefa, arquivos/decisões alterados, verificações reais, limitações e próximo passo executável. Usar a data do cliente em America/Sao_Paulo. Atualização documental não altera o corte dos dados nem significa nova execução analítica.
2. Atualizar os catálogos de tarefas e ações humanas quando houver evidência de mudança. Preservar decisões, notas e estados registrados; não retornar uma tarefa concluída ao padrão inicial durante o empacotamento.
3. Se mudar um documento gerado, corrigir também seu gerador. Não permitir que a próxima execução restaure texto desatualizado. Planos descrevem o método e critérios de conclusão; o documento central descreve o andamento.
4. Executar `.venv/Scripts/python.exe scripts/sync_project_docs.py` e depois `.venv/Scripts/python.exe scripts/sync_project_docs.py --check`. O comando sincroniza indicadores/avisos, confere links locais e preservação dos originais e atualiza manifestos de rascunhos; não faz pesquisa ou validação financeira.
5. Informar quais verificações foram executadas nesta tarefa e quais pertencem a uma execução anterior. Registrar limitação/falha real sem prometer correção de previsões futuras.

O sincronizador atualiza trechos automáticos. **O agente continua responsável por revisar o texto de andamento, os critérios e a próxima ação.** Não basta trocar a data. Se somente responder uma pergunta sem alterar o estado, não inventar progresso ou novos testes.

Não recriar EXECUTION_CONTEXT.md com um snapshot fixo no empacotador/gerador de status. Preservar a memória manual; o sincronizador só mantém seus blocos automáticos. Em outra máquina ou cópia, seguir a seção de reconstrução: Git/arquivos versionáveis podem não incluir raw, interim, outputs e vários processed ignorados. Não presumir que a venv ou um novo download reproduzam o ambiente/snapshot original.

O detalhe executável de tudo que falta está em `data/catalog/completion_requirements.json`, renderizado no plano09; a conversão HTML está no plano10 e em `html_slide_plan.json`. Atualizar esses catálogos quando surgir ou fechar requisito material, incluindo instruções novas de H07. `scripts/validate_completion_docs.py` verifica cobertura e dependências; o sincronizador também o chama. Os critérios e o mapa de células documentam trabalho ainda aberto, não aprovação econômica. Não editar manualmente os blocos gerados dos planos09/10.

## Regras de evidência e escopo

- O projeto está parcialmente executado, com materiais em outputs/draft e fechamento econômico pendente. Existência de XLSX/PPTX/PDF não comprova conclusão da fase.
- Separar tarefa pública/analítica do agente, julgamento econômico do grupo e acesso/ação pessoal. Conciliação contábil e pesquisa pública não devem ser transferidas ao humano como dependência de autorização.
- Não presumir H08/H09, ensaios, gravação, revisão de vídeo ou envio. Exigir registro real para marcar esses itens concluídos. Não enviar mensagens ou arquivos ao Safra pelo usuário.
- Testes, hashes e coincidência de fórmulas verificam o escopo declarado; não certificam automaticamente a qualidade econômica das premissas.
- Preservar bytes dos15 originais ativos definidos em data/catalog/original_files_manifest.json. Por solicitação explícita do usuário em01/11/2026, resources/audio foi removida e o áudio está fora das verificações de integridade; não recriar a pasta nem exigir/restaurar o arquivo. HTMLs01–03, cartas e modelos originais são insumos/histórico, não documentos correntes para reescrever. O mapa de reorganização não deve ser executado novamente.
- Pacotes em `outputs/draft/analysis_bundle/<bundle_id>/` são versões imutáveis com manifesto e hashes (contrato 1.0). Não editar nem reformatar; mudança gera nova versão via `python -m analysis.run` e atualização atômica de `latest.json`. O sincronizador documental não gerencia essa pasta.
- Builds de peças em `outputs/draft/production/<build_id>/` também são imutáveis (manifesto/hashes, QA em `outputs/qa/production/<build_id>/`). Publicar nos destinos canônicos só via `python -m production.run --publish`, que exige QA aprovado e revisão visual vinculada aos hashes do build.
- Não promover rascunho a final ou desbloquear o modo final apenas para melhorar a aparência do status. A liberação final (`--mode final` / `--promote-final`) é decidida pelos portões de `production/release.py`. Nunca injetar evidência humana fora da sandbox de testes nem afrouxar um portão para liberar.
- Não atualizar silenciosamente preços/avaliação30/10/2026 ou corte31/10/2026. Nova fotografia exige versão e justificativa explícitas.
- O perfil PPTX9/PDF9 usa nove slides; o HTML interativo de dez páginas está implementado como perfil próprio (html10), com PDF10 e exportação PPTX10 fiel por imagens de alta resolução e texto nas notas. O design vem de resources/design_system/marcadev.html, preservando o nome asset.dev; fontes locais ficam em presentation_web/fonts. O gerador é production/brand.py + html_deck.py + html_pptx.py, e deve ser alterado junto das peças. Manter perfis separados e não trocar globalmente o teste de nove por dez. O vídeo segue o perfil pptx9 (13 segmentos) salvo instrução H07 para usar o html10 (14 segmentos).

## Onde continuar

Para execução em duas partes, seguir [plano11](plans/11_plano_agente_analise_dados.md) (dados/análise) ou [plano12](plans/12_plano_agente_engenharia_entrega.md) (apresentação/engenharia). A divisão é declarada em `data/catalog/two_part_execution.json` e validada por `scripts/validate_two_part_plans.py`, também chamado pelo sincronizador. Não há dependência de saída futura da outra parte para implementar/testar/entregar o pacote autônomo; há dependência real de conteúdo revisado para a integração definitiva.

Antes de executar em paralelo, fixar snapshots próprios e implementar o protocolo de exclusão de escrita em `data/interim/coordination/documentation.lock`. Respeitar as raízes exclusivas e os módulos legados somente leitura do catálogo. Atualizações globais, edição/chamada de sincronizadores e publicação canônica são serializadas; não apagar trava ativa nem perder decisões. Cada parte mantém progresso próprio; requisito compartilhado só fecha com ambas as fatias e evidência humana aplicável. Planos11/12 não substituem os critérios do contrato09 ou o mapa HTML10; distribuem sua implementação. A tarefa que os criou não executou suas24 etapas.

O fechamento econômico autônomo precede a gravação definitiva: entradas históricas, recorrência, receita regulatória/capex, obrigações datadas, balanço/capital, hipóteses e recomendação. O grupo pode reunir H07 em paralelo. Detalhes, responsáveis e critérios em ESTADO_DO_PROJETO.md e nos planos05–08.
