# Plano de implementação — apresentação HTML interativa de dez páginas

<!-- PROJECT_STATUS:START -->
> [Estado central do projeto](../ESTADO_DO_PROJETO.md) · Revisão documental: 01/11/2026. Plano de método e critérios; conclusão de cada fase depende de evidência.
<!-- PROJECT_STATUS:END -->

Revisado em **01/11/2026**. Escopo desta tarefa: **plano**, ainda sem construir o HTML. O [estado central](../ESTADO_DO_PROJETO.md) descreve o projeto e o [contrato09](09_contrato_de_fechamento.md) cobre dados/correções/entregáveis. Este plano é a especificação de C28.

## Resultado esperado

Produzir `outputs/draft/html/apresentacao_esg.html`: um arquivo local independente, em português, com **exatamente dez slides**, navegação por teclado/botões, gráficos e painéis interativos, fontes consultáveis e impressão/PDF de dez páginas. Abrir por duplo clique deve bastar; não depender de CDN, servidor, conta, API ou conexão de rede.

Usar o conteúdo do [PPTX atual](../outputs/draft/apresentacao_esg.pptx), seu [PDF](../outputs/draft/apresentacao_esg.pdf) e os dados canônicos como insumos. A saída não será apenas nove imagens num carrossel: texto, matriz e gráficos precisam ser elementos HTML/SVG acessíveis e interativos. O PPTX/PDF de nove páginas e os originais permanecem preservados como versão anterior.

O HTML serve à apresentação, ensaio e análise. **Não substitui o vídeo solicitado pela competição** sem orientação expressa em H07. Não publicar um site nem adicionar infraestrutura de hospedagem. Entregar somente as informações e fontes necessárias à apresentação, sem copiar arquivos brutos ou exportações Bloomberg inteiras para o HTML.

## Transformação de nove para dez slides

Dividir o **S7 atual** em duas páginas: método/premissas/ponte de valor e resultado versus preço/sensibilidade. S8 e S9 passam a P09 e P10. Isso dá espaço à questão econômica mais importante sem criar uma capa ou página de créditos apenas para completar dez.

O [mapa canônico](../data/catalog/html_slide_plan.json) define origem, conteúdo, dados, interação e aceite de cada página. Não manter outro mapa manual divergente.

<!-- HTML_SLIDE_MAP:START -->

| Página / origem | Conteúdo e voz | Janela planejada | Interação |
|---|---|---|---|
| P01 ← S1 (B1) | **Tese e condição de investimento** · Rodrigo | 0:00–0:50 | Abrir fonte/data do preço e condições da recomendação em painel; manter a conclusão principal visível. |
| P02 ← S2 (B2) | **O déficit de saneamento e a expansão** · Lorenzo | 0:50–1:40 | Selecionar água/coleta para destacar a série; tooltip e painel explicam denominador, ano-base e meta, sem somar coleta/tratamento. |
| P03 ← S3 (B3) | **SWOT: crescimento precisa remunerar capital** · Lorenzo | 1:40–2:55 | Selecionar quadrante para revelar evidência e implicação econômica; estado inicial mostra a matriz inteira. |
| P04 ← S4 (B4) | **Regulação, competição e tecnologia** · Navarro | 2:55–3:55 | Três cartões com abas de fato, prazo e canal econômico; detalhes da Aegea e da Copasa abrem fontes. |
| P05 ← S5 (B5) | **Matriz ESG comparativa** · Michel | 3:55–5:25 | Clicar em célula/fator abre definição, período, fonte e linha de caixa; destacar empresa sem eliminar as outras da comparação inicial. |
| P06 ← S6 (B6) | **Eficiência energética: teto condicionado de investimento** · Michel | 5:25–6:30 | Alternar retenção de50%/100% sobre redução hipotética fixa de1%; mostrar fluxos/horizonte e premissas em painel, usando valores já calculados. |
| P07 ← S7 (B7.a) | **Como o modelo transforma caixa em valor** · Rodrigo | 6:30–7:10 | Selecionar empresa para inspecionar PV explícito, terminal e ponte EV→patrimônio→papel; diferenciar método original de experimento proposto. |
| P08 ← S7 (B7.b) | **Valor versus preço e sensibilidade** · Rodrigo | 7:10–7:55 | Selecionar empresa e ponto da grade WACC×g pré-calculada; marcar a referência de mercado e permitir restaurar a configuração inicial. |
| P09 ← S8 (B8) | **Cenários, riscos e gatilhos** · Navarro | 7:55–8:55 | Selecionar um dos quatro cenários e revelar choques/duração; cartões mostram métrica, limiar, data/frequência e ação de cada gatilho. |
| P10 ← S9 (B9) | **Decisão e condições para manter a tese** · Todos | 8:55–9:20 | Resumo fixo da decisão aprovada/proposta e botão de fontes; encerrar ou reiniciar a apresentação sem adicionar página de créditos. |

<!-- HTML_SLIDE_MAP:END -->

Total planejado: **560 segundos /9:20**, preservando a margem de quarenta segundos até o teto público de dez minutos. São janelas de produção, não tempos humanos medidos. Repartir a fala B7 em B7.a/B7.b, sem acrescentar conteúdo/tempo automaticamente; redistribuir as palavras e confirmar a divisão nos ensaios. O script atual tem cerca de1.150 palavras contando marcadores, que não são pronunciados.

## Aparência e comportamento

- Preservar a linguagem visual atual: fundo claro, azul-marinho/teal, alto contraste, tipografia sem serifa e uma mensagem principal por página. Usar SVG para barras, pontos e fluxos; tabela como alternativa textual. Evitar animação decorativa e navegação automática.
- Tela16:9 com área principal legível e área de câmera reservada à direita quando usada em gravação. Conferir1920×1080 e1366×768; em tela menor, manter navegação e leitura por ajuste de escala/rolagem de detalhes, sem cortar conteúdo ou transformar10 slides em páginas adicionais.
- Mostrar contador `n/10`, barra de progresso, anterior/próximo, índice de páginas e botão de tela cheia. Teclas: setas/PageUp/PageDown e Home/End; não capturar setas quando o foco estiver em campo/controle. Manter foco visível e ativação por teclado.
- Usar `#slide-01` a `#slide-10` para voltar/reabrir a página; validar/clamp de índice inválido. Estado inicial e botão Restaurar voltam à configuração canônica. Não deixar preferências antigas do navegador mudarem silenciosamente o caso mostrado no ensaio ou gravação.
- Painéis de fonte/definição/premissa podem abrir sobre o slide e **não contam como novas páginas**. Fechar por botão/Escape, devolver foco ao acionador e impedir navegação atrás do modal. Texto crítico e conclusão continuam visíveis sem abrir o painel. Seguir o [padrão de diálogo da W3C](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/).
- Solicitar tela cheia somente por ação explícita no botão; tratar falha e continuar no navegador normal. Não depender de bloqueio especial de teclado ou fullscreen para funcionar. A [documentação da Fullscreen API](https://developer.mozilla.org/en-US/docs/Web/API/Fullscreen_API/Guide) exige ativação do usuário.
- Respeitar `prefers-reduced-motion`, usar rótulos acessíveis e não transmitir distinções somente por cor. No modo gravação, fechar painéis, restaurar estado canônico e esconder controles/notas; os conteúdos e a identificação de hipóteses permanecem. Entrada nesse modo é uma ação de produção, não aprovação econômica.
- Manter IDs técnicos, hashes e detalhes de arquivos no manifesto/apoio; a tela principal mostra mensagem, unidade, período e limitações relevantes. Painéis de fonte explicam a evidência em linguagem legível, sem despejar metadados brutos na apresentação.

## Dados e controles: contrato de fidelidade

O gerador Python prepara um pacote mínimo `data/processed/html_presentation_data.json`. Cada valor precisa de identificador, número/tipo de ausência, unidade/escala, empresa/papel, período, definição, fonte/localização ou premissa/cálculo, status e limitações. Cada afirmação da narrativa aponta para claim_id. Incluir decisão/condições, quatro cenários, pontos disponíveis de sensibilidade e metadados de versão/corte; nunca tratar a data de geração HTML como data do dado.

Fontes já existentes: `presentation_facts.json`, `valuation.json`, `scenarios.json`, `esg_matrix.json`, `esg_bridge.json`, `observations.csv`, `definitions.csv`, `claims.csv`, `assumptions.csv`, `adjustments.csv`, `market_reference.json` e `capital_reference.json`. As informações da decisão em Markdown devem ganhar uma representação estruturada para não extrair recomendações por busca textual frágil. C20/C21 cobrem essas adaptações, ainda pendentes.

| Controle | Implementação prevista | Restrição econômica |
|---|---|---|
| Empresa/célula ESG | Selecionar entre os três emissores e abrir a definição/fonte exata. | Não calcular score ESG ou ordenar desempenho de métricas incompatíveis. |
| Retenção de eficiência | Alternar50%/100% na sensibilidade de economia hipotética1%, usando os valores do Python. | Mostrar teto condicionado de investimento, escopo água municipal2024 e horizonte2027–35. Não inserir ganho extra na margem nem inventar projeto realizado. |
| Método/ponte do valor | Selecionar empresa e revelar PV explícito/terminal, dívida/outros ajustes e classe. | A dedução nominal integral de obrigações continua diagnóstico enquanto não conciliada; não é faixa aprovada de preço-alvo. |
| WACC×g | Selecionar apenas pontos exportados pelo motor. A grade atual tem cinco WACCs e três g; opções e caso inicial devem vir dos dados, sem limites/defaults duplicados no JavaScript. | Exigir valor bruto do patrimônio, flag do piso e validade do alvo em **cada ponto**. Sem isso, controle indisponível ou N/D; zero do piso não é preço-alvo. Não interpolar nem extrapolar silenciosamente. |
| Quatro cenários | Selecionar o cenário exportado e mostrar os choques/duração e gatilhos. | Nenhuma probabilidade, retorno observado, causalidade ou movimento de mercado é criado pelo front-end. |

O navegador não implementa outro DCF: renderiza resultados do Python e alterna estados pré-calculados. Se futuramente houver cálculo numérico no cliente, ele exige especificação e equivalência adicional, não simples cópia de fórmulas. Valores ausentes/indeterminados permanecem distintos de zero. Formatação monetária é uma visão, sem arredondar os números antes do cálculo.

Na versão inicial de layout, a matriz de dados disponível pode ser usada com marcação de rascunho e controles sem metadados completos desabilitados. Aprovar o layout não aprova a recomendação. A versão definitiva precisa de C19–C23 e dos portões aplicáveis.

## Arquitetura simples e independente

Estrutura **proposta**, ainda inexistente:

```text
presentation_web/
  template.html             Estrutura semântica e dez seções
  styles.css                Tema, escala, foco e impressão
  app.js                    Navegação, painéis e seleção de estados
scripts/build_html_deck.py  Exportação mínima, validação e montagem do arquivo único
data/processed/html_presentation_data.json
outputs/draft/html/
  apresentacao_esg.html     CSS, JavaScript e dados embutidos
  apresentacao_esg.pdf      Exportação própria de dez páginas
  manifest.json            Entradas, hashes, versão, corte e limitações
outputs/qa/html/
  slide_01.png ... slide_10.png
outputs/qa/html_validation.json
```

Usar HTML/CSS/JavaScript nativos e o ambiente Python existente. Os arquivos-fonte separados facilitam manutenção; o distribuidor os incorpora no HTML. Dados entram em `<script type="application/json">`, com escape seguro para conteúdo HTML/fechamento de script, sem inserir texto de fonte via `innerHTML`. Gráficos SVG e metadados são incorporados. Nenhuma leitura `fetch()` de arquivos vizinhos é necessária: origens `file:` podem sofrer restrições de CORS, conforme [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS/Errors/CORSRequestNotHttp).

O manifesto registra hashes dos dados/gerador/HTML, perfil `html10`, limites e estado de revisão, sem concluir etapas humanas. Não incluir datas voláteis nos valores de análise. Não criar serviço web, banco de dados, login ou novo projeto de aplicação.

## Etapas de implementação

| Etapa | Pode começar agora? | Trabalho / dependência | Resultado verificável |
|---|---|---|---|
| W01 — inventário e contrato | Sim | Confirmar os nove slides/notas atuais; usar o mapa P01–P10 e definir schema mínimo de claims/valores/estados. C20/C21 têm pendências reais, não campos fictícios. | Mapa, schema e exportador que recusam incoerência de tipo/unidade e preservam ausências. |
| W02 — casca e navegação | Sim | Montar dez seções, tema16:9, contador, índice, foco, hash, fullscreen e modo gravação com dados de rascunho. | Arquivo único aberto por duplo clique; dez páginas navegáveis sem rede. |
| W03 — conteúdo e fontes | Sim, como rascunho | Converter texto e matriz para HTML/SVG; criar painéis e tabelas acessíveis; separar notas de fala. | Todas as dez páginas possuem mensagem, evidência ou pendência explícita; nenhuma é só uma captura do PPTX. |
| W04 — controles financeiros | Parcial | Integrar alternâncias somente com dados completos; depender de C17/C20/C21 para fidelidade e flags. | Cada seleção bate com o JSON/Python; controle indisponível não fabrica resultado. |
| W05 — narrativa e produção | Após decisão/feedback para fechar | Repartir B7; gerar roteiro/teleprompters do perfil HTML10 e, se for usado no vídeo, nova configuração de segmentos. | Dez blocos planejados, quatro vozes,560s de orçamento e mapeamento correto para gravação. |
| W06 — impressão e verificação visual | Após conteúdo de cada versão | CSS de impressão, PDF de dez páginas, capturas de todos os estados relevantes e inspeção. | Páginas sem cortes, fonte legível, estado inicial reproduzível e fontes disponíveis no impresso. |
| W07 — testes e pacote | Depois de cada mudança material | Testar o checklist abaixo; corrigir falhas, registrar hashes e atualizar estado/documentação. | Relatório HTML e manifesto; saída permanece draft enquanto faltarem portões econômicos/humanos aplicáveis. |

Comandos **propostos para implementar**, não disponíveis hoje:

```powershell
python scripts/build_html_deck.py --mode draft
python scripts/validate_html_deck.py
```

Ao implementá-los, documentar suas opções reais; não acrescentar no README um comando de exportação/liberação ainda inexistente. Um navegador automatizado, como Playwright quando disponível, pode gerar capturas/testes; a escolha e a instalação ficam para a implementação, com fallback de inspeção explícita se a ferramenta faltar.

## PDF, PPTX e vídeo: compatibilidade de perfis

Para impressão, aplicar CSS `@media print`/`@page`, revelar as dez seções e ocultar controles, notas/painéis transitórios. Cada seção ocupa uma página, inclusive as que estavam inativas. PDF usa a configuração canônica dos controles, com hipóteses/limites e fontes legíveis; não captura um cenário aleatório deixado por interação. A [referência de impressão MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Media_queries/Printing) descreve essa separação de estilos. No navegador escolhido, verificar dimensões16:9 e dez páginas efetivas, sem confiar apenas na contagem de seções HTML.

O renderizador/validador atuais exigem nove slides para o PPTX, e o montador atual lê `apresentacao_esg.pdf` com o mapa de nove páginas. **Não mudar esses testes globalmente para dez.** Introduzir um perfil explícito `html10` para o novo PDF e sua validação, mantendo `pptx9` para os artefatos atuais.

Se o grupo usar o HTML10 como base visual do vídeo, criar `config/video_segments_html10.json` com o caminho do novo PDF, dez páginas e B7 dividido em B7.a/B7.b. Isso passa de treze para **quatorze segmentos** quando mantidos os cinco trechos de encerramento. Gravar tomadas separadas ou cortar em pausa real identificada; não dividir o clipe por porcentagem arbitrária nem acelerar a fala. C24 exige ensaios e revisão reais. O perfil original só é substituído por decisão explícita de produção, nunca como efeito de gerar o HTML.

## Checklist de aceite da implementação futura

- Exatamente dez seções principais P01–P10 e PDF de dez páginas; índice, hash e contador consistentes. Os nove slides de origem estão cobertos e só S7 foi dividido.
- Duplo clique e execução offline funcionam sem requisições de recursos externos, erros de console ou dependência de porta local. Links de fonte só abrem rede por ação do usuário.
- Teclado, foco, botões, painéis e retorno de foco funcionam; campos não disparam troca de slide indevida. A apresentação continua operável sem fullscreen e com movimento reduzido.
- Para todas as empresas, cenários e combinações exportadas: número, unidade, data, estado e flags coincidem com o motor. Ausente/N/D/piso não é confundido com preço zero; nenhum controle usa valor de outra classe/empresa.
- Comparações mantêm definições e períodos. Fontes e premissas são consultáveis por teclado e no material estático. O caso inicial e Restaurar são determinísticos.
- Textos, símbolos, rótulos e gráficos foram inspecionados nas dez páginas e nos estados abertos/selecionados em1920×1080 e1366×768, além de uma tela menor. Sem sobreposição na área de câmera, cortes ou tipografia ilegível.
- Impressão oculta UI/notas e mostra as dez páginas no estado canônico. Nenhuma animação ou painel aberto muda inadvertidamente o PDF.
- P01/P08/P10, narração e artefatos estáticos compartilham a mesma conclusão/versão. O orçamento de560s foi preservado no plano; a duração real só é aceita após H10/C24.
- Testes negativos incluem JSON/valor ausente, NaN/infinito, WACC/g não suportado, índice de página inválido e resíduo negativo. Testes de interface e de conteúdo econômico são relatados separadamente.
- Manifesto e documentação mostram o que foi gerado, testado e aprovado de fato. Gerar HTML ou passar testes de navegação não fecha as conciliações econômicas nem significa envio ao Safra.
