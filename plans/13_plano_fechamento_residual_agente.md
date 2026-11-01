# Plano 13 — Fechamento residual do agente

<!-- PROJECT_STATUS:START -->
> [Estado central do projeto](../ESTADO_DO_PROJETO.md) · Revisão documental: 01/11/2026. Plano de método e critérios; conclusão de cada fase depende de evidência.
<!-- PROJECT_STATUS:END -->

Data: 01/11/2026 (America/Sao_Paulo). Escopo: tudo o que ainda falta no projeto e pode ser feito pelo agente sem decisão, acesso ou atuação do grupo. Os recortes continuam: preços e avaliação em 30/10/2026, corte informacional em 31/10/2026 18:25:27. Fontes novas só entram se publicadas até o corte; a data de leitura (01/11) é registrada à parte.

Este plano complementa os planos 11/12 (já executados) e não substitui o contrato 09: os requisitos C01–C29 continuam sendo a referência de conclusão.

## 1. Como o levantamento foi feito

- Catálogo `completion_requirements.json`: 29 requisitos, 9 fechados antes desta tarefa.
- Progresso das duas partes, `pendencias.csv` do pacote, fila de coleta (`collection_backlog.csv`) e números N (`n_status.csv`).
- Leitura do código que gera os textos (análise e produção) e da fotografia `snap_20261031_2cf3206ead`.
- Sondagem de fontes públicas para cada limitação aberta: reguladores (Arsesp/URAE-1, Agepar, Arsae), RI das três empresas e anúncios de oferta.

## 2. Inventário do que falta

| Item | Requisito | Situação encontrada | Quem |
|---|---|---|---|
| Desestatização da Copasa | C16, C18, C20 | **Erro factual.** O pacote diz "desestatização em andamento". O release 2T26 da Copasa (já na fotografia, p. 25) lista o preço da oferta (12/06), o acordo de acionistas e a decisão do CADE (05/08). A oferta foi secundária: as ações em circulação seguem em 379.181 mil (p. 26). Textos literais da produção repetem o erro. | agente |
| Prazo das concessões da Copasa | C15, N10, D19 | O caso finito está "unresolved", mas o mesmo release informa prazo médio ponderado de cerca de 29 anos (p. 21–22), 43 contratos até 07/02/2073 (37,5% da receita) e 58 vencidos (5,2%). | agente |
| WACC regulatório da Sabesp | C14 | Marcado como fonte secundária. O Anexo VIII do contrato URAE-1 (item 10.7, Tabela 5) fixa 7,86% pós e 11,91% pré-impostos, constantes no 1º ciclo (até 31/12/2029). | agente |
| BRR oficial | C13–C15 | Não usada. Nota Técnica Agepar 006/2025 (3ª RTP da Sanepar, p. 81): BRR líquida 2024 de R$ 16.846,8 mi a preços de dez/2020, sob fiscalização; WACC 12,24%/8,08% (p. 25). Para a Sabesp, a NT Arsesp do 1º reajuste (nov/2025) só traz a BAR bruta em texto extraível; para a Copasa, nenhum valor encontrado. | agente (verificação) |
| Plano de capex da Copasa | C06 | Valores do pacote iguais aos divulgados pela companhia, mas transcritos da planilha. Fonte primária (DF 2025, item 6.2) não obtida. | agente (uma tentativa) |
| Eventos jul–out/2026 | C09, C18, D21 | Não pesquisados. Sondagem: nenhuma alteração de quantidade de ações (oferta da Copasa secundária; Sabesp só debêntures); Sanepar suspendeu os JCP do 1S26 pelo precatório e contesta a decisão da Agepar; fatos relevantes da Sanepar em 27/10 e 29/10. | agente |
| EMAE (Sabesp) | C10 | Sem valoração separada; sem preço público na fotografia. | limitação mantida |
| Ponte jun→out | C12 | 3T26 não publicado antes do corte. | limitação mantida |
| Indicador de acesso da Copasa | C16 | Ausente; o release não traz cobertura de tarifa social comparável. | limitação mantida |
| Revisão semântica das afirmações | C20 | Placement feito; falta revisão registrada claim a claim. | agente |
| Validação estendida | C22 | Ambas as fatias concluídas; fechar com a evidência da nova versão. | agente |
| Catálogos defasados | C27 | D31 ainda diz "peças pendentes"; `html_slide_plan.json` ainda diz "planned_not_implemented". | agente |
| Decisões, ensaios, vídeo, envio | C01, C19, C23–C26 | H07, H08/H09, H10, H11, revisão integral, H13. | grupo |
| Complementos opcionais | C29 | H01–H06 omitidos com justificativa. | grupo (opcional) |

## 3. Etapas

| Etapa | O que fazer | Aceite |
|---|---|---|
| E1 — Fontes | Salvar em `data/raw/analysis/<emissor>/` os PDFs novos (Anexo VIII URAE-1 e NT Agepar 006/2025) com sha256, URL, data de publicação e data de leitura. Uma tentativa para cada: fato relevante do investidor de referência da Copasa, DF 2025 da Copasa (item 6.2) e fatos relevantes da Sanepar de 27/10 e 29/10. | Toda fonte usada tem publicação ≤ corte e hash; o que não for obtido fica registrado como tentativa. |
| E2 — Fotografia derivada | Implementar em `analysis/snapshot.py` o modo `--baseline derive:<snapshot>`. Ele copia a fotografia anterior (insumos de 31/10) e acrescenta só as fontes novas de `data/raw/analysis`. | `data/processed` publicado (contrato 1.0) não entra na entrada da análise; ID novo; originais conferidos; teste. |
| E3 — Correções da análise | **Copasa:**<br>• governança e afirmações de médio prazo com a desestatização concluída (release 2T26, p. 25–26);<br>• `concession_end_year` *derivado* do prazo médio (2026 + 29), com limitação;<br>• oferta secundária registrada como evento sem mudança de ações.<br>**Sabesp:** WACC regulatório com fonte primária (Anexo VIII) e rótulo da alternativa H08.2 como sensibilidade além do contrato.<br>**Sanepar:** BRR oficial atualizada pelo IPCA de 2021–2024 × base implícita, como valores e uma afirmação fora dos slots.<br>**Eventos:** limitação substituída pela cobertura real.<br>**Geradores:** `bundle.py`, `progress.py`, `recommendation.py`, `sector.py` e `assumptions.py` sem texto antigo. | Nova versão do pacote com QA analítico aprovado; caso finito da Copasa calculado; a busca por "em andamento"/"fonte secundária"/"não pesquisados" no código e no pacote não encontra resquício indevido. |
| E4 — Testes da análise | Atualizar e ampliar `tests/analysis` para os comportamentos novos. | Suíte verde, sem afrouxar asserções antigas sem motivo. |
| E5 — Peças | Corrigir os textos literais de `production/content.py` sobre a Copasa (cartão P04, fala B4, pergunta da banca); mostrar a verificação da BRR no apoio A01 e em `decisao_proposta.md`; build; revisão visual; publicação. | QA 15/15; revisão visual nova; publicação com as três suítes verdes. |
| E6 — Fechamentos | Revisão semântica das afirmações (C20) com registro; fechar C20/C22 se a evidência permitir; atualizar D09/D19/D21/D31, N10/N20 e `html_slide_plan.json`. | Validadores verdes; nenhum requisito com fatia humana fechado. |
| E7 — Documentação | Estado central, contexto operacional, README, progresso das partes e este plano (registro de execução); sync e `--check`. | Documentos coerentes com a evidência. |

## 4. Fora do alcance do agente

H07 (instruções privadas), H08/H09 (adoção de premissas e da recomendação), H10 (ensaios), H11 (clipes), revisão integral do vídeo, H13 (envio) e H01–H06 (acessos e complementos opcionais). As ferramentas para cada uma já existem: checklist de envio, teleprompters, perfis de vídeo, portões e promoção.

## 5. Revisão crítica do plano

A primeira versão foi conferida contra o código (snapshot, registro de fontes, contrato, consumidor da Parte 2, testes) e contra as regras do AGENTS. Erros e lacunas encontrados, já corrigidos nas etapas:

1. **Fonte sem uso.** A NT Arsesp do 1º reajuste só tem a BAR *bruta* em texto extraível, que não é comparável à base líquida implícita. Ela sai da E1: não adquirir fonte que não será usada. A verificação BRR × base implícita fica restrita à Sanepar, empresa da decisão, com fonte primária e valor líquido.
2. **Afirmação nova quebraria a Parte 2.** Uma afirmação nova posta num dos 10 slots exigiria posicionamento em página, porque a verificação `claims_placed` falharia. A verificação da BRR entra como afirmação **fora dos slots**, exibida no apoio técnico (A01) e em `decisao_proposta.md`. A desestatização corrige afirmações já existentes, sem criar novas.
3. **Texto literal da produção sem lastro.** O texto do cartão "Competição" (P04) e da fala B4 não vem do pacote. A correção atualiza o literal **e** a afirmação de médio prazo da Parte 1 que o sustenta, para que a fonte do painel continue coerente.
4. **Inconsistência com o contrato.** O contrato fixa o WACC regulatório da Sabesp até 2029, mas as alternativas 7,5%/8,5% (H08.2) se aplicam ao horizonte inteiro. Não há mudança de mecânica nesta tarefa: o rótulo e a limitação passam a dizer que a alternativa é uma sensibilidade e que o contrato fixa 7,86% no 1º ciclo.
5. **Caso finito da Copasa.** Um horizonte único (2026 + 29 = 2055) aproxima um portfólio misto: 43 contratos até 2073, 58 vencidos (5,2% da receita) que seguem operados e o restante com prazos variados. O valor entra como *derivado* (prazo médio ponderado), com essa limitação explícita, e não como fato contratual.
6. **Geradores com o texto antigo.** Os textos "fonte secundária", "eventos não pesquisados", "prazo não obtido" e "em andamento" estão espalhados em `bundle.py` (disposições e LEIA_PRIMEIRO), `progress.py`, `recommendation.py`, `sector.py`, `assumptions.py` e `content.py`. Corrigir só o pacote faria a próxima execução restaurá-los, então todos os geradores entram na E3/E5, com uma busca final por resquícios.
7. **Trava.** Alterações em catálogos globais, documentos centrais e o sincronizador seguem serializadas na trava documental. Faltava dizer isso.
8. **Teste do snapshot derivado.** O teste precisa usar raiz temporária, para não criar fotografia real durante a suíte.
9. **Esforço de pesquisa.** Uma tentativa por fonte faltante. Se falhar, a limitação continua com o registro da tentativa e o trabalho segue.
10. **Responsáveis por documento.** `html_slide_plan.json` era insumo somente leitura da Parte 2 durante a execução paralela. Agora C28 está fechado, e o AGENTS manda atualizar o catálogo quando o requisito fecha. A alteração é mínima (só o `status`) e sob a trava.

Riscos aceitos: a decisão (Sanepar, compra condicionada) não deve mudar, porque o caso-base de nenhuma empresa é alterado (o WACC da Sabesp e a base implícita da Sanepar ficam iguais; muda só o caso finito da Copasa). Se a regra de decisão mudar mesmo assim, a geração das peças para com `IncompatibleState`, em vez de produzir texto incoerente.

## 6. Registro de execução

Executado em 01/11/2026.

| Etapa | Resultado |
|---|---|
| E1 | **Obtidos** (publicação ≤ corte):<br>• Anexo VIII URAE-1 (apostilado, fev/2025);<br>• NT Agepar 006/2025 (03/04/2025);<br>• fato relevante da Copasa de 11/06/2026 (preço R$ 49,03; 114.075.921 ações à Equatorial);<br>• fato relevante da Sanepar de 28/10/2026 (SAINP).<br>**Tentativas sem fonte primária:**<br>• DF 2025 da Copasa: a busca achou, em imprensa (Diário do Comércio, 13/03/2026), que a companhia **descontinuou as projeções em 12/03/2026**, fato incorporado como limitação;<br>• BAR líquida da Sabesp: a NT Arsesp tem tabela não extraível;<br>• fatos da Sanepar de 27 e 29/10: não constam como fatos relevantes no RI; existe uma resposta à CVM de 28/10, sem efeito no modelo. |
| E2 | `derive_snapshot` e `--baseline derive:` implementados; `new` é recusado com `CANONICAL_SOURCE.json`. Fotografia `snap_20261031_7c31b5560e`: 24 de 24 insumos de `data/processed` idênticos aos da mãe. |
| E3 | Pacote `an_20261101T132455_ac536175`: QA e contrato aprovados, decisão inalterada (Sanepar, compra condicionada).<br>**Valores alterados:** apenas `V.copasa.concession_end_year` (antes ausente, agora 2055). O caso finito da Copasa passa a valer R$ 21,11.<br>**Valores novos:**<br>• WACC regulatório da Sabesp como fato (7,86% / 11,91%);<br>• BRR da Sanepar de R$ 16.846,8 mi em dez/2020, igual a R$ 22,4 bi a preços de 2025, contra base implícita de R$ 20,2 bi (−9,9%);<br>• participação da Equatorial (30,08%);<br>• IPCA de 2021–2023. |
| E4 | `tests/analysis/test_plan13.py` com 7 testes: fotografia derivada, guarda do `new` e correções publicadas. Suíte da Parte 1 com 39 testes verdes. |
| E5 | Build `pr_20261101T132746_ac536175` com QA 15/15, revisão visual registrada e publicação `pub_20261101T132847` (39 + 50 + 13 testes, código 0). A revisão visual achou mais um literal "fonte secundária" no cartão P04/S4, corrigido antes da publicação. |
| E6 | `outputs/qa/claims_semantic_review.json`: 32 afirmações, sem defeito. C20 e C22 fechados com evidência; D09, D16, D19, D21 e D31, N10 e o status do `html_slide_plan.json` atualizados. |
| E7 | Estado central, contexto operacional, README e progresso das partes atualizados; sincronização e validadores ao fim. |

**Falhas encontradas na execução e corrigidas:**

- Textos literais da produção ainda diziam "fonte secundária" (P04) e "BRR oficial não está disponível" (pergunta da banca).
- O validador documental quebrava com o esquema 1.0 (`claims.csv` e `script_word_counts.json`).
- A reversão da primeira publicação da Parte 2 não guardava as escritas diretas. Corrigido no código; a lacuna daquela publicação fica registrada.

**Continua aberto:**

- **Humano:** H07, H08/H09, H10, H11, revisão integral e H13.
- **Residual público com limitação declarada:** BRR líquida de Sabesp/Copasa, plano de capex vigente da Copasa, EMAE, indicador de acesso da Copasa, ponte jun→out (3T26 só sai depois do corte) e datas de eventos de Sabesp/Copasa.
