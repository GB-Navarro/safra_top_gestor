# Seu plano de trabalho — o que fazer, como e por quê

<!-- PROJECT_STATUS:START -->
> [Estado central do projeto](../ESTADO_DO_PROJETO.md) · Revisão documental: 01/11/2026. Plano de método e critérios; conclusão de cada fase depende de evidência.
<!-- PROJECT_STATUS:END -->

Versão consolidada de 31/10/2026. Este é o plano principal para você coordenar a participação do grupo. O [plano do agente](05_plano_implementacao_agente_esg.md) cobre a execução técnica completa. O [anexo de exportações](08_plano_coleta_dados_humano.md) detalha a operação da Bloomberg.

A execução produziu dados, modelos de diagnóstico, gráficos, nove slides/PDF, apoio e falas. Comece por [PROXIMOS_PASSOS.md](../outputs/draft/PROXIMOS_PASSOS.md) e pelo [pacote](../outputs/draft/LEIA_PRIMEIRO.md). A conclusão econômica permanece em revisão; vídeo, ensaio e envio ainda não ocorreram. Ver [contexto de execução](../EXECUTION_CONTEXT.md).

## 1. O que você receberá do agente

O agente deve pesquisar fontes públicas, importar seus arquivos, organizar os dados, verificar definições/unidades, conciliar os pontos materiais, recalcular os três modelos e propor a recomendação. Também deve produzir matriz ESG, ponte financeira, cenários/gatilhos, gráficos, nove slides editáveis, apoio técnico, roteiro, fala exata dos quatro, teleprompter e perguntas de banca.

Sua participação concentra acesso à Bloomberg e orientações do Safra, revisão dos julgamentos que o grupo assumirá, ensaio, gravação real e envio. Se uma ferramenta de conversão/edição faltar ao agente, haverá uma tarefa manual específica. Ele deve levar propostas prontas para discussão, com evidência e alternativas.

Ainda há conciliação e fundamentação pública a cargo do agente antes do fechamento de H08/H09. Você não precisa resolver sozinho contabilidade, regulação ou programação. H07 pode avançar em paralelo; os procedimentos abaixo descrevem o que fazer quando os insumos estiverem preparados. Consulte o [estado central](../ESTADO_DO_PROJETO.md) para acompanhar as duas frentes.

O objetivo é uma escolha defensável entre Sabesp, Copasa e Sanepar, com preço/condição, efeito econômico de ESG e risco que a invalida. Não sabemos as notas dos concorrentes para calcular a recuperação necessária; o plano melhora cobertura e qualidade, sem garantir classificação.

## 2. Ordem prática

O [contrato de fechamento09](09_contrato_de_fechamento.md) separa a pesquisa/correção que falta ao agente dos registros humanos H07–H13. O [plano HTML10](10_plano_html_interativo.md) divide S7 em duas páginas e preserva9:20 planejados; se adotado para vídeo, o agente deverá atualizar roteiro/segmentos antes de pedir as tomadas. Hoje o perfil de gravação continua sendo o atual, de nove páginas.

Comece por **H07, instruções privadas, e H08/H09, revisão das propostas prontas**. H01 agora serve à confirmação de preços públicos e capital/eventos posteriores a junho. H02–H06 são complementos opcionais, substituídos por fontes públicas ou omitidos explicitamente.

Depois, responda H08/H09 com base no material que o agente produzirá. Quando os slides estiverem revisados, faça H10/H11. H12 só será acionado se faltar uma rota técnica ao agente. H13 conclui a entrega ao Safra.

A tabela `data/catalog/manual_export_requests.csv` mantém o nome antigo, mas passa a listar as 13 ações humanas. Os IDs abaixo são os mesmos usados no plano do agente. “P0” indica prioridade da tarefa quando sua condição se aplica; P1 é complemento. Não é necessário interromper toda a pesquisa enquanto uma ação está pendente.

## 3. Acesso e informações que você deve fornecer

### H07 — conferir a instrução efetiva da etapa — P0

**Por quê:** o PDF2026 já foi verificado via ferramenta web e confirma conteúdo, teto de dez minutos, participação ativa e prazo02/11. Horário, canal, formato/tamanho e alterações na comunicação privada precisam ser conferidos pelo grupo.

**Como:** reúna regulamento, mensagem/e-mail e orientações posteriores que o grupo recebeu. Salve os arquivos originais ou exportações legíveis em `data/raw/orientacoes/`. Registre em `resumo_orientacoes.md`: prazo com horário/fuso, canal, limite/formato/tamanho do vídeo, participação exigida e documentos que serão enviados. Para cada regra, indique arquivo/página ou mensagem/data; marque o que ainda não está informado.

**Entregar:** originais e resumo para o agente adaptar o pacote. Se não houver horário claro, buscar a confirmação pelo canal que vocês já usam; o agente não enviará mensagens em seu nome.

O prazo02/11 também consta do regulamento2026,p12. Nove slides, alvo9:20, limite interno9:45 e MP4/1080p são escolhas de produção até conferência das instruções. A pesquisa e os rascunhos já avançaram; H07 continua necessário para a submissão.

### H01 — confirmar preços/capital na Bloomberg — recomendado após a coleta pública

**Por quê:** preço, classe, ações e data errados podem inverter a recomendação, especialmente com o desdobramento da Sabesp e a unit da Sanepar.

**Como:** no Terminal, confirme os instrumentos SBSP3, CSMG3, SAPR3, SAPR4 e SAPR11; use o assistente do Excel para obter fechamento histórico de 30/10/2026, moeda e ajustes. Confirme ações por classe, tesouraria/quantidade usada no market cap, data efetiva e eventos de capital. Use busca de campos/ajuda do Terminal em caso de dúvida; não trate free float como total de ações.

Salve valores estáticos que abram sem add-in e mantenha a exportação original. Inclua aba `metadados`: operador, captura, data efetiva, consulta/campo, unidade, moeda, ajustes e eventuais indisponibilidades. Consulta atual não comprova valor histórico.

**Entregar:** `data/raw/bloomberg/01_mercado_20261030.xlsx`. O agente confere capital/eventos com RI/CVM e faz as contas. Se não conseguir Bloomberg, a alternativa é arquivo de preços B3 obtido manualmente conforme os termos aplicáveis, para importação local; informe a origem. Não preencher campos desconhecidos com zero.

### H02–H06 — complementos da Bloomberg — P1

**Por quê:** ajudam a comparar hipóteses e conferir evidências; a coleta pública pode suprir grande parte deles. Você não precisa encontrar sozinho todos os dados contábeis e ESG.

**Como e onde salvar:** exporte com unidades, período, escopo e aba de metadados. Use a data real do consenso; uma fotografia atual não vira consenso histórico ao trocar o título.

| ID | Arquivo em `data/raw/bloomberg/` | Conteúdo e finalidade |
| --- | --- | --- |
| H02 | `02_financeiros.xlsx` | DRE, balanço e DFC 2021–2025 e 1S25/1S26, EBITDA/ajustes; referência de apoio à CVM/RI |
| H03 | `03_consenso.xlsx` | Receita, EBITDA e capex 2026–2030; mediana, dispersão, contribuidores e data; confrontar premissas |
| H04 | `04_analistas.xlsx` | Preço-alvo, instituição, data e horizonte; comparação secundária |
| H05 | `05_esg.xlsx` | KPIs com definição, período e fonte original; acelerar localização de evidências |
| H06 | `06_titulos.xlsx` | Título IPCA, vencimento, tipo de taxa, data/horário e fonte; contexto de custo de oportunidade |

Se um pacote não estiver disponível, registre isso no catálogo ou informe ao agente. Ele segue com fontes públicas, hipótese própria identificada ou omissão do complemento. API Desktop é opcional; não gastar a janela de produção configurando integração. Não compartilhar senha.

## 4. Julgamentos que o grupo deve assumir

### H08 — revisar as premissas decisivas — P0 para a versão que vocês apresentarão

**Por quê:** o agente calcula as consequências, mas o grupo precisa compreender os julgamentos econômicos que defenderá. As hipóteses originais foram propostas com apoio de IA e não estão validadas apenas por existir uma planilha.

**Como:** peça ao agente `outputs/draft/decisao_proposta.md` e a tabela das cinco premissas que mais alteram a conclusão, com histórico, referência, base proposta e alternativas. Para cada uma, responda: concordamos; preferimos outra hipótese por determinado motivo; ou precisamos esclarecer uma questão específica. Não é necessário inventar números sem referência.

A discussão deve cobrir o que for material: margem/tarifa/volume; capex e reconhecimento; WACC/inflação/impostos; crescimento/reinvestimento terminal; concessões e obrigações. Exijam explicação do precatório, das classes/unit e do fluxo remanescente de 2026. O agente já deve ter feito a pesquisa e a conciliação; vocês revisam os julgamentos restantes.

**Entregar:** seção H08 em `data/interim/decisoes_equipe.md`, com decisão, justificativa, responsável/data e pontos em aberto. O agente recalcula e apresenta o impacto. Uma questão pendente mantém a conclusão afetada provisória, sem travar os demais rascunhos.

### H09 — decidir a recomendação a defender — P0 para a mensagem final

**Por quê:** a equipe deve conseguir explicar por que prefere uma empresa às outras e o que faria mudar de ideia. A maior TIR inicial não é critério suficiente.

**Como:** leia a proposta do agente e verifique cinco respostas: empresa/ticker escolhido; preço/data e condição de entrada; mecanismo ESG que altera o caixa; razão para preterir as outras duas; risco/gatilho que invalida a tese. Peça a melhor objeção contra a recomendação e sua resposta com evidência.

Se todas parecerem caras, preservem o resultado e discutam condição de entrada, conferindo com H07 se esse formato atende à exigência de recomendação. Não forcem premissas para produzir desconto.

**Entregar:** seção H09 no mesmo `decisoes_equipe.md`, com escolha, condições, objeções e responsáveis. O agente atualiza gráficos, títulos e falas. Cada integrante deve conseguir explicar a tese com suas próprias palavras.

## 5. Participação na apresentação

### H10 — fazer dois ensaios e devolver o tempo real — P0

**Por quê:** contagem de palavras não garante duração, e um texto correto pode soar confuso na fala. O ensaio testa compreensão, transições e participação.

**Como:** o agente entrega slides, script e teleprompter. No primeiro ensaio, cronometrem cada bloco e marquem trechos difíceis ou repetidos. No segundo, usem a versão corrigida e a ordem final. Gravem uma amostra curta para conferir áudio e legibilidade. Enviem os tempos e comentários ao agente em `data/interim/feedback_ensaio.md`.

| Slide | Voz proposta | Intervalo planejado |
| --- | --- | --- |
| S1 — recomendação | Rodrigo | 0:00–0:50 |
| S2 — contexto | Lorenzo | 0:50–1:40 |
| S3 — SWOT | Lorenzo | 1:40–2:55 |
| S4 — médio prazo | Navarro | 2:55–3:55 |
| S5 — matriz ESG | Michel | 3:55–5:25 |
| S6 — ponte financeira | Michel | 5:25–6:30 |
| S7 — valuation | Rodrigo | 6:30–7:55 |
| S8 — riscos/gatilhos | Navarro | 7:55–8:55 |
| S9 — conclusão | Todos | 8:55–9:20 |

O roteiro produzido soma cerca de1.150 palavras, contando marcadores de voz no fechamento, com janelas planejadas de9:20. A duração real depende do ensaio. Se ultrapassar9:45, cortar repetição/detalhes do apoio; não acelerar artificialmente a fala. O teto público é dez minutos e H07 pode acrescentar condições.

Distribuição de vozes é proposta; vocês podem alterá-la, avisando o agente para sincronizar script e teleprompter.

### H11 — gravar a participação real dos quatro — P0 para o vídeo

**Por quê:** a participação ativa é do grupo; slides e voz sintética não substituem a apresentação dos integrantes.

**Como:** sigam o `guia_gravacao.md` do agente para enquadramento, tela/câmera, áudio e ordem. Gravem em ambiente silencioso, com configuração consistente; mantenham breve pausa no início/fim de cada bloco para cortes. Confiram cada gravação antes de encerrar a sessão.

**Entregar:** preservar as tomadas originais e identificar a preferida. O montador espera as cópias selecionadas com os nomes de `config/video_segments.json`: `B1.mp4` a `B8.mp4` e os cinco trechos de B9. Não confundir nomes livres das tomadas com os arquivos esperados pelo programa. Se gravarem tudo de uma vez, entregar o original e os pontos de corte; o agente pode separar/montar os trechos com as ferramentas já preparadas, sem apagar os originais.

### H12 — executar operação técnica que o agente não conseguiu concluir — condicional

**Por quê:** criação de PPTX, exportação para PDF e edição de vídeo exigem ferramentas diferentes. A capacidade deve ser verificada, não presumida.

**Como:** só executar após o agente identificar a limitação e preparar os arquivos. Para PDF, abrir o PPTX fornecido no PowerPoint ou ferramenta compatível e usar Salvar como/Exportar PDF, com os nove slides. Salvar `outputs/draft/apresentacao_esg.pdf` para o agente conferir as páginas.

Se o bloqueio for um documento que apenas seu acesso consegue salvar, o agente deve indicar URL, documento/período e destino em `data/raw/`. Você salva o original; a extração e conferência continuam com o agente. Isso é uma tarefa pontual, sem transferir a pesquisa inteira.

Para eventual edição manual, seguir a ordem de clipes e instruções; o montador atual gera `outputs/draft/video_esg_rascunho.mp4`. H12 não requer ação manual no estado registrado: PDF e encoder foram preparados. Reavaliar apenas se houver falha real posterior; isso não bloqueia a pesquisa inicial.

As ocorrências são independentes: documento na coleta, PDF antes do ensaio e edição depois da gravação. O agente fornece o destino de cada pedido; não é preciso aguardar a gravação para resolver a exportação dos slides.

### H13 — assistir ao resultado inteiro, enviar e guardar comprovante — P0

**Por quê:** a última verificação confirma que a apresentação real atende ao canal, ao tempo e ao conteúdo. O envio não deve ser presumido por existir um arquivo local.

**Como:** assistir ao vídeo inteiro, confirmar áudio, transições, legibilidade, participação dos quatro, empresa/números corretos e duração. Verificar nome/formato/tamanho e canal de H07. Enviar somente os artefatos pedidos; testar o arquivo/link com o acesso exigido pelo destinatário, sem tornar bases licenciadas públicas.

Reservar ao menos duas horas antes do horário confirmado para exportação, upload e correção. Guardar protocolo/tela/mensagem de confirmação em `data/raw/orientacoes/` e informar ao agente o que foi efetivamente enviado e quando. Nenhum comprovante deve ser criado antes da submissão real.

## 6. Como coordenar sem duplicar o trabalho

Você pode distribuir H01–H07 a quem tiver acesso; H08/H09 são discussão do grupo; H10/H11 envolvem os quatro; H13 fica com um responsável nominal. Rodrigo pode revisar os julgamentos financeiros; Michel, os regulatórios/ESG; Lorenzo, definições/fontes; Navarro, coerência e operação. São revisões do material preparado pelo agente, com foco nas questões que alteram a conclusão.

O agente deve reportar: concluído com evidência; proposta que aguarda julgamento; dado inacessível com alternativa; operação técnica que precisa de ajuda. Para cada pendência, indicar a consequência e o que continua avançando. Não é necessário exigir uma aprovação a cada arquivo ou cálculo.

O recorte informacional operacional pode ser registrado pelo agente no início da execução, se não houver regra prescrita. Vocês devem avisar caso H07 imponha outra data. O preço planejado continua 30/10, e fontes posteriores precisam ser corretamente identificadas.

## 7. O que conferir ao receber o pacote

Em `outputs/final/coleta/`: base_dados_coletados.xlsx, cobertura, pendências, model_inputs.json e manifesto. Em `outputs/final/`: base_modelo_auditavel.xlsx; apresentacao_esg.pptx/.pdf; apoio_tecnico.pptx/.pdf; roteiro_narrativo.md; script_apresentacao.md; teleprompter; perguntas_banca.md; guia_gravacao.md; figuras e índice.

O vídeo só estará pronto após H11/A10 e revisão. O envio só estará concluído após H13. Dados, análise, slides, vídeo e submissão terão estados separados; um rascunho não deve ser confundido com entrega final.

A versão analítica precisa mostrar fontes e hipóteses, comparação coerente, ajustes materiais tratados, ponte ESG calculada ou limitação explicitada, riscos e gatilhos. Você deve conseguir localizar a evidência de um número sem reconstruir a pesquisa inteira.

## 8. Validação desta divisão

O plano foi revisto para transferir ao agente o trabalho técnico que ele pode executar, limitar pedidos humanos ao necessário e evitar espera global por um complemento. Os IDs H01–H13, destinos, prioridades e dependências devem corresponder ao catálogo e ao plano 05. Os nove tempos foram mantidos iguais entre os dois documentos.

Continuam pendentes conciliações/evidência pública material, fundamentação das projeções, recomendação definitiva, instruções privadas, ensaios, clipes e envio. Renderização PDF e teste técnico do encoder foram concluídos na execução registrada; isso não cria vídeo real. A revisão documental atual não reexecuta finanças e não completa fases. A liberação do modo final também exige implementação e teste pelo agente.
