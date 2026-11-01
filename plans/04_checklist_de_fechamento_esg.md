# Fechamento da análise setorial ESG — asset.dev

<!-- PROJECT_STATUS:START -->
> [Estado central do projeto](../ESTADO_DO_PROJETO.md) · Revisão documental: 01/11/2026. Plano de método e critérios; conclusão de cada fase depende de evidência.
<!-- PROJECT_STATUS:END -->

Diagnóstico inicial de31/10/2026, atualizado documentalmente em01/11/2026 após a execução parcial. A explicação de Rodrigo e os materiais originais continuam insumos; o [estado central](../ESTADO_DO_PROJETO.md) registra o andamento efetivo.

Este checklist contém critérios de fechamento. A presença de um arquivo ou uma fórmula reproduzida não comprova que o critério econômico foi atendido.

## Situação dos critérios

- [x] Ambiente, inventário e preservação dos originais preparados.
- [x] Coleta/extração e base de trabalho produzidas, com cobertura parcial documentada.
- [x] Reconstrução matemática dos três DCFs, matriz, sensibilidade ESG, gráficos e rascunhos de slides/falas produzidos.
- [x] Controles técnicos, exportação PDF e inspeção visual registrados para os artefatos da execução anterior.
- [ ] Encerrar conciliações contábeis e regulatórias, recorrência, obrigações e ponte de datas/capital — trabalho do agente.
- [ ] Fundamentar premissas, fechar recomendação e atualizar os materiais com H08/H09.
- [ ] Confirmar instruções privadas H07; realizar ensaios H10, gravação H11, revisão/envio H13.
- [ ] Implementar/testar a liberação final baseada em evidências e gerar o pacote definitivo.

## 1. Entrega a concluir

A estrutura de nove slides e nove blocos já foi produzida como rascunho. A matriz e a sensibilidade ESG existem; falta completar a evidência material, fechar o valuation e fazer a recomendação sobreviver às conciliações. Só então consolidar a versão para gravação.

O conteúdo de referência é: SWOT setorial; médio prazo com tecnologia e novos participantes; recomendação de empresa; matriz ESG ligada à avaliação; vídeo de até dez minutos com os membros ativos. Esses requisitos foram confirmados no regulamento2026 via ferramenta web, apesar de o HTTP direto devolver403. Horário/canal/formato e alterações das orientações privadas continuam H07. Ver [regras verificadas](../outputs/draft/regras_2026_verificadas.md).

O prazo02/11/2026 também consta do cronograma2026 verificado. MP4,1080p, nove slides, duração-alvo9:20 e limite interno9:45 são escolhas de produção, sujeitas às instruções privadas. O texto seguinte descreve o método e os critérios, não declara conclusão das tarefas.

## 2. Fixar o escopo antes de finalizar os cálculos

Proposta de fechamento:

- Usar o DCF já implementado como método principal, após revisão de dados e hipóteses. Atualizar os planos que ainda prometem fluxo de consenso até 2030 e saída por BRR; as planilhas projetam até 2035 e usam perpetuidade.
- Apresentar preço estimado, intervalo de sensibilidade, preço de referência e riscos. A XTIR atual usa EV e FCFF: se mantida, precisa ser identificada como TIR da firma no modelo. Retorno do acionista exige fluxos e financiamento correspondentes.
- Mostrar ao menos uma alavanca ESG quantitativa bem fundamentada; buscar duas se os dados permitirem. Essa quantidade é uma recomendação de qualidade, não uma exigência numérica comprovada do regulamento.
- Deixar θ (N21) e regressão de juros (N22) para material de reserva. A sensibilidade do DCF ao WACC pode ser usada com seu nome correto.
- Usar valor por ligação (N23) e EV/BRR (N04) somente se houver insumos e cálculo completos. A demonstração de vínculo entre ESG e valor pode ser feita por outra ponte quantitativa documentada.
- Manter versão única dos modelos e o recorte de preços30/10/2026. Referências públicas de fechamento já substituíram os preços antigos/intradiários; confirmação Bloomberg e eventos de capital posteriores a junho continuam úteis. Não atualizar o recorte por mudar a data da documentação.

## 3. Quatro peças que precisam ficar prontas

### A. Base comparativa e registro de fontes

Produzir uma tabela de trabalho com as três empresas e os seguintes campos:

| Dado | O que é necessário conferir | Uso |
| --- | --- | --- |
| Preço, ticker e data | Mesma data de fechamento; ON, PN, unit e desdobramentos tratados corretamente | S1, S7, S9 |
| Ações, dívida, caixa e demais ajustes | Base contábil recente identificada; caixa livre versus vinculado; passivos relevantes | S7 |
| Perdas de água | Definição, unidade, período, perímetro e componente físico/aparente | S5, S6 |
| Coleta, tratamento e qualidade | Denominadores separados: cobertura, volume coletado tratado e conformidade do efluente | S5 |
| Metas contratuais e investimentos | Prazo de universalização de cada contrato; expansão versus manutenção quando disponível | S2, S4, S6 |
| Regulação | WACC regulatório, base real/nominal e pré/pós-impostos; reconhecimento de investimentos; compartilhamento de eficiência | S4, S6 |
| Acesso e tarifa social | Beneficiários, subsídio, compensação tarifária e inadimplência | S5 |
| Resiliência hídrica e governança | Eventos datados, controles, obrigações ambientais e consequências econômicas | S5, S8 |

Para cada entrada, registrar: `ID | empresa | indicador | valor | unidade | período/data-base | definição/perímetro | documento e página | link | realizado/estimativa | status`.

Começar pelos releases e ITRs do 2T26, com dados históricos já disponíveis nas planilhas e relatórios anuais. Se a fonte mais recente de determinado KPI for anual, indicar seu período; não tratá-lo como dado trimestral. Não atribuir desempenho pior a uma empresa apenas por faltar dado comparável.

Correções já identificadas: perdas no faturamento não são automaticamente perdas físicas; cobertura de esgoto não equivale à fração do esgoto coletado que é tratada; o roteiro não pode dizer que apenas a Sanepar divulga perdas.

### B. Premissas e valuation reconciliados

Usar as abas existentes `Dados_RI`, `Premissas`, `Projecao_FCFF`, `TIR`, `Sensibilidade` e `Estresse`.

1. Designar a versão válida da Sabesp. `TIR_Sabesp.xlsx` tem erro de sinal na receita de construção; `Modelo_TIR_Sabesp.xlsx` é a base a revisar.
2. Conferir dados de balanço, receitas de construção, receitas financeiras/não caixa, EBITDA e capital de giro. Registrar a conciliação entre EBITDA reportado e ajustado.
3. Na Sanepar, reconciliar caixa, obrigação do precatório, descontos futuros, investimentos não onerosos e eventual exclusão da remuneração regulatória. Explicar os efeitos em EV e nos fluxos e evitar dupla contagem. Somar todo o passivo nominal ao EV é uma aproximação que precisa de justificativa econômica.
4. Para cada hipótese de margem, tarifa, volume, capex, D&A, capital de giro, imposto, WACC e g, registrar: `valor base | referência histórica/contratual | justificativa | faixa adversa/favorável | fonte ou estimativa do grupo`.
5. Usar hipóteses macro comuns quando apropriado, preservando diferenças operacionais, tributárias e regulatórias justificadas entre as empresas.
6. Verificar se reinvestimento, crescimento terminal e duração contratual são coerentes. Verificar também que aquisições, arrendamentos e obrigações foram tratados de modo compatível com os fluxos projetados.
7. Produzir a ponte EV operacional → ajustes de caixa, dívida e outros direitos/obrigações → patrimônio → valor por ação, explicitando o tratamento das classes de ações.
8. Exportar uma tabela final com `preço de referência | preço estimado no base | intervalo de sensibilidade | potencial relativo ao preço | WACC | g | percentual do EV vindo do terminal` para cada empresa.

Critério de conclusão: a empresa recomendada deve ter uma justificativa de investimento que sobreviva às correções. Se todas parecerem caras, rever a evidência e apresentar a condição de preço de entrada, verificando sua compatibilidade com a orientação da etapa. A melhor colocada entre três alternativas não se torna automaticamente uma boa compra no preço atual.

### C. Matriz ESG e ponte para o valor

Tabela de trabalho completa:

`fator material | KPI/definição | Sabesp | Copasa | Sanepar | efeito econômico | premissa/linha do modelo afetada | evidência | risco e responsável por absorvê-lo`.

Cinco linhas sugeridas:

1. Eficiência hídrica: perdas físicas e aparentes separadas quando possível.
2. Expansão e qualidade do esgotamento: cobertura, tratamento, metas e conformidade ambiental.
3. Resiliência hídrica: fontes de abastecimento, estiagem e investimentos de segurança.
4. Acesso: tarifa social, compensação, capacidade de pagamento e inadimplência.
5. Governança e regulação: controle, incentivos, retenção dos ganhos e obrigações como o precatório.

Para o slide S5, condensar em cinco colunas: `fator | Sabesp | Copasa | Sanepar | consequência financeira`. Definições, períodos e fontes ficam em notas legíveis. Ler na fala apenas os contrastes que alteram a escolha.

Como quantificar a eficiência hídrica (L1/N12):

- Fixar volume entregue ao consumidor C e uma taxa de perdas físicas p. A água a produzir é C/(1−p).
- Comparar p0 e p1: `volume evitado = C/(1−p0) − C/(1−p1)`.
- Multiplicar pelo custo variável evitável de tratamento e bombeamento; considerar investimento necessário, impostos, capital de giro e a regra de compartilhamento regulatório.
- Recalcular os fluxos e o valor por ação. Apresentar alteração em R$/ação ou intervalo, identificada como estimativa.
- Perdas aparentes exigem uma conta de faturamento recuperável e arrecadação; não geram necessariamente a mesma economia física. Evitar contar o mesmo volume como economia e receita adicional.
- Se não houver separação física/aparente nem custos suficientes, mostrar uma sensibilidade financeira identificada como tal ou usar outra alavanca documentada. Não apresentar a economia física como calculada.

Como quantificar expansão/universalização (L2):

- Obter o investimento incremental e seu calendário, a meta operacional correspondente e quando o regulador reconhece/remunera o ativo.
- Construir trajetórias de receita, custos e caixa com execução base e com atraso/ineficiência, incluindo eventual glosa ou parcela não remunerada.
- Recalcular o valor nas duas trajetórias. Se os ganhos já estiverem na margem, no volume ou na tarifa-base, não adicioná-los novamente.
- Usar VPL por ligação apenas com investimento de expansão e ligações incrementais do mesmo perímetro e período. A fórmula simplificada do plano depende de hipóteses de remuneração, depreciação e continuidade; preferir explicitar seus limites.

Saída para S6: uma ponte que mostre `mudança operacional → fluxo incremental → parcela retida → efeito no valor`. Mostrar ao menos uma relação com números e fonte/premissa rastreável. O caso do precatório pode complementar a demonstração de quem retém o valor, desde que reconciliado no modelo.

### D. Cenários e gatilhos

Montar uma tabela com quatro casos adaptados ao horizonte do valuation: base; abertura de juros/custo de capital; adverso operacional/regulatório; favorável de execução/ambiente econômico. Não chamar esses casos de reprodução exata dos eventos de catorze pregões da carta.

Para cada cenário, fixar a alteração das variáveis relevantes — WACC, custos de energia, reajuste tarifário, volume, margem e capex —, justificar a duração e recalcular o valor por ação. Um teste de WACC de +1 p.p. deve ser chamado de sensibilidade do valuation; não significa que a ação perde o mesmo percentual quando a NTN-B sobe 1 p.p.

Reportar `hipóteses | preço estimado | diferença para o preço de referência | principal causa da alteração`. Esses são valores condicionais do modelo, não perdas efetivamente realizadas nem preços futuros garantidos.

Definir três gatilhos com métrica, limite, data/período e decisão. Derivar os limites das premissas que sustentam a recomendação: perda acima da trajetória adotada, investimento entregue com atraso ou tarifa/remuneração abaixo do necessário para preservar a margem de segurança, por exemplo. Não inventar probabilidades para calcular um retorno médio.

## 4. O que precisa existir para cada slide

| Slide e tempo | Critério a conferir antes da versão definitiva | Como apresentar | Condição para finalizar |
| --- | --- | --- | --- |
| S1 — 0:00–0:50 | Empresa, ticker, preço/data, tese e conclusão econômica | Recomendação e uma frase com mecanismo ESG e condição de valor | Deriva de S5–S8; título escrito por último |
| S2 — 0:50–1:40 | Indicador nacional validado, metas legais e contexto do setor | Um indicador nacional e uma linha do tempo curta | Ano da publicação e ano-base identificados; meta nacional separada do prazo contratual |
| S3 — 1:40–2:55 | SWOT revisada e ancorada em fatos | Matriz 2×2 com dois itens por quadrante; fala desenvolve as relações | Cada item tem evidência ou justificativa e consequência na análise |
| S4 — 2:55–3:55 | Uma mudança regulatória, um exemplo de concorrência e uma tecnologia concreta | Três frentes para 2027–2030, cada uma com implicação para o setor | Documento, data e mecanismo econômico para cada exemplo |
| S5 — 3:55–5:25 | Matriz comparativa preenchida | Cinco fatores, três empresas e consequência financeira | Indicadores comparáveis ou limitações explícitas; empresa recomendada incluída |
| S6 — 5:25–6:30 | Ponte quantitativa de ESG para o valor | Uma alavanca calculada em destaque e segunda relação se houver suporte | Cálculo reproduzível; custos e compartilhamento tratados; sem dupla contagem |
| S7 — 6:30–7:55 | Valuation validado das três e escolha da empresa | Preço de referência versus faixa de valor; WACC/g e ajustes principais em notas | Uma única metodologia declarada; recomendação compatível com os resultados |
| S8 — 7:55–8:55 | Cenários recalculados e três gatilhos | Tabela curta e gatilhos com data | Resultado reproduzível e explicação do que faria a equipe mudar de ideia |
| S9 — 8:55–9:20 | Conclusão coerente com os slides anteriores | Ticker, tese e principal condição/risco | Mesma empresa, preço de referência e argumento do S1 e S7 |

Os nove slides já foram montados como rascunho. Os números/títulos definitivos, especialmente S1/S6–S9, dependem do fechamento analítico; os critérios da tabela não significam que cada evidência esteja pronta.

## 5. Ajustes do roteiro existente

Preservar `resources/roteiros/sugestao_roteiro_rodrigo.txt` como insumo original. O script gerado atual é `outputs/draft/script_apresentacao.md`, com teleprompters e roteiro narrativo; atualizar o gerador e esses materiais a partir da conclusão reconciliada.

- B1/B7/B9: definir recomendação depois da revisão. Substituir a descrição de XTIR da firma como retorno da ação. Se o gráfico principal passar a ser preço versus valor, reescrever a fala de modo correspondente.
- B2: conferir o indicador nacional no SINISA 2025 (ano-base 2024). Explicar a meta nacional sem supor que todos os contratos têm o mesmo prazo.
- B3: manter a SWOT do setor. Qualificar estabilidade da demanda, considerando seca, consumo por cliente e capacidade de pagamento.
- B4: trocar afirmações genéricas sobre tecnologia por exemplo verificável. Um investimento anunciado não prova, por si só, que uma técnica é sempre mais barata que renovar tubulações.
- B5: incluir a comparação entre as três empresas, corrigir definições de perdas e esgoto e remover o argumento de indisponibilidade geral de dados das concorrentes.
- B6: explicar o que foi efetivamente calculado. Comparar retorno regulatório com custo de capital econômico em bases compatíveis. Remover VPL por ligação ou outras métricas que não forem executadas.
- B8: declarar que os cenários são adaptações para o horizonte setorial; mostrar gatilhos específicos em vez de afirmações vagas como “perdas em queda”.
- Remover de títulos, etiquetas, falas e checklists todas as referências a θ, beta ou outros resultados que não forem incluídos.

Na fala, usar um número principal por argumento e deixar tabelas completas no apoio. O script produzido tem cerca de1.150 palavras contando marcadores; o tempo planejado é9:20. Duração real e ajustes dependem dos dois ensaios, ainda não registrados.

## 6. Divisão sugerida entre quatro integrantes

O agente pesquisa, concilia, calcula, prepara a proposta e escreve os materiais. A divisão abaixo é de fala/revisão humana dos resultados; não transfere a execução técnica aos integrantes.

| Pessoa | Entrega principal | Revisão cruzada |
| --- | --- | --- |
| Rodrigo | Revisar julgamentos financeiros propostos; falar S1/S7 e fechamento | Michel revisa os julgamentos regulatórios materiais |
| Lorenzo | Revisar indicadores/definições e SWOT preparados; falar S2/S3 | Navarro revisa coerência das datas e implicações |
| Michel | Revisar matriz, hipóteses da ponte ESG e obrigações; falar S5/S6 | Rodrigo revisa o entendimento econômico da tese |
| Navarro | Reunir H07; revisar cenários/gatilhos e falar S4/S8 | Lorenzo revisa clareza da narrativa |

## 7. Sequência até a entrega indicada no plano

Sequência para a janela restante, sujeita ao horário/canal real de H07. As metas antigas de31/10 não representam tarefas concluídas nem duração garantida:

1. **Agente, prioridade imediata:** concluir conciliações e fundamentação econômica que podem alterar a recomendação. **Grupo, em paralelo:** reunir H07. Preços/corte permanecem na fotografia registrada; os rascunhos já existem.
2. **Depois da análise:** revisar H08/H09 com a proposta fundamentada; consolidar títulos, números, figuras e falas em uma única versão e revalidar.
3. **Depois do fechamento:** realizar dois ensaios, incorporar feedback, gravar os quatro, montar e assistir ao vídeo inteiro.
4. **Antes do horário de envio confirmado:** conferir duração, participação, legibilidade, áudio, formato e acesso ao arquivo/link; enviar pelo canal oficial e guardar comprovante. O cronograma público registrado indica02/11, mas a hora não foi fornecida.

Se houver corte de escopo, priorizar análise setorial, matriz ESG, recomendação sustentada e entrega do vídeo. θ, regressão de juros e VPL por ligação podem ficar fora. Retirar uma análise exige atualizar todas as falas e os slides que prometem seus resultados.

## 8. Evidência mínima para autorizar internamente a gravação

- Instruções operacionais conferidas e prazo/canal registrados.
- Matriz ESG preenchida e suas definições verificadas por outro integrante.
- Valuation conciliado, fontes e premissas disponíveis e empresa escolhida a partir dele.
- Pelo menos uma ponte quantitativa de ESG para valor revisada, ou escopo analítico reformulado com transparência se os insumos forem insuficientes.
- SWOT, médio prazo, inovação e entrada de participantes efetivamente cobertos.
- Cenários e gatilhos compatíveis com a tese e com o horizonte da análise.
- S1, S7 e S9 consistentes; demais slides e roteiro sem resultados prometidos e ausentes.
- Os quatro integrantes conseguem explicar a tese, os ajustes, a principal sensibilidade e o que a invalida.

## 9. Fontes públicas que já ajudam a executar

- [Regulamento Safra2026](https://www.safra.com.br/data/files/76/64/7B/85/0ABCE910FDA2D4E9E3ADF9C2/Regulamento_Safra_Top_Gestor_2026.pdf), verificado via ferramenta web: conteúdo p9, classificação p10 e cronograma p12. Conferir as instruções privadas e eventuais alterações; a revisão documental não foi nova consulta ao Safra.
- [Resultados SINISA 2025](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/resultados-sinisa/resultados-sinisa-2025): localizar relatório e indicadores, preservando o ano-base.
- [Marco Legal, Ministério das Cidades](https://www.gov.br/cidades/pt-br/assuntos/saneamento/marco-legal-do-saneamento): referência para metas nacionais.
- [Aegea, concessão no Pará](https://www.aegea.com.br/2025/04/14/aegea-conquista-concessao-para-operar-servicos-de-agua-e-esgoto-no-para/): exemplo documentado de entrada/expansão de operador; distinguir investimento ao longo de 40 anos de investimento anual.
- [Copasa, release 2T26](https://www.rad.cvm.gov.br/ENETCONSULTA/frmDownloadDocumento.aspx?CodigoInstituicao=1&Tela=99&descTipo=IPE&numProtocolo=1556698&numSequencia=1081404&numVersao=1): indicadores de perdas, cobertura e iniciativas de medição/eficiência.
- [Sabesp, release 2T26](https://www.rad.cvm.gov.br/ENETCONSULTA/frmDownloadDocumento.aspx?CodigoInstituicao=1&Tela=99&descTipo=IPE&numProtocolo=1556532&numSequencia=1081238&numVersao=1): atualização de balanço e resultados para revisar o modelo.
- [Sanepar, release 2T26](https://ri.sanepar.com.br/docs/Sanepar-2026-06-30-LhNKMDPD.pdf): definições operacionais, tarifa social e concessões.
- [Sanepar, ITR 2T26](https://ri.sanepar.com.br/docs/ITR-Sanepar-2026-06-30-kcDdgkwC.pdf): conferir caixa e passivo regulatório na nota 20; saldo do passivo de R$ 4,407957 bilhões em junho.
- [Sanepar, fato relevante de 23/06/2026](https://ri.sanepar.com.br/docs/Fato-Relevante-Sanepar-2026-06-23-HKd9Bg6R.pdf): destinação do precatório e WACC regulatório real líquido de impostos de 8,08%.
- [Sanepar, emergência hídrica comunicada em abril](https://ri.sanepar.com.br/docs/Comunicado-ao-Mercado-Sanepar-2026-04-30-NTphdJrk.pdf) e [acordo ambiental divulgado em outubro](https://ri.sanepar.com.br/docs/Fato-Relevante-Sanepar-2026-10-26-HnB9fFkj.pdf): eventos específicos para examinar resiliência e obrigações; não presumir impacto financeiro sem avaliação.
- [Damodaran/NYU: valuation por FCFF e FCFE](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/lectures/val.html): referência metodológica para manter coerentes fluxos, valor e taxa de desconto.
