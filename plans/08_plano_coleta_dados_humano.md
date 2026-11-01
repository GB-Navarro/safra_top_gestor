# Anexo humano — exportações e orientações H01–H07

<!-- PROJECT_STATUS:START -->
> [Estado central do projeto](../ESTADO_DO_PROJETO.md) · Revisão documental: 01/11/2026. Plano de método e critérios; conclusão de cada fase depende de evidência.
<!-- PROJECT_STATUS:END -->

Atualizado em 31/10/2026. O seu roteiro completo é o [plano humano 06](06_plano_executivo_grupo_esg.md), com H01–H13. Este anexo detalha a aquisição manual. O [plano 05](05_plano_implementacao_agente_esg.md) instrui o agente; o [plano 07](07_plano_coleta_dados_agente.md), os coletores.

## 1. Começar por mercado e orientações

O [contrato09](09_contrato_de_fechamento.md) documenta também os dados/correções públicos a cargo do agente; não transformar essa lista em novas exportações obrigatórias para você. O [plano10](10_plano_html_interativo.md) é uma extensão visual planejada, sem mudança automática do formato de envio da competição.

Cinco referências públicas de fechamento foram obtidas e CVM/RI/SINISA/BCB/Tesouro abasteceram a pesquisa. H01 serve agora à confirmação e a eventos de capital posteriores a junho; H02–H06 são opcionais. H07 precisa das instruções privadas, pois o regulamento público2026 já foi verificado. Ações imediatas em [PROXIMOS_PASSOS.md](../outputs/draft/PROXIMOS_PASSOS.md).

## 2. Operar a Bloomberg

1. Confirme o instrumento no Terminal. Pontos de partida: `SBSP3 BZ Equity`, `CSMG3 BZ Equity`, `SAPR3 BZ Equity`, `SAPR4 BZ Equity`, `SAPR11 BZ Equity`. Nome, classe, bolsa e moeda precisam corresponder ao papel.
2. Localize dados com busca/ajuda e funções disponíveis: DES, FA, EE, ANR, ESG e FLDS são pontos de partida. Confirme campos no próprio Terminal; não copie um identificador que devolve conceito diferente.
3. Use o assistente do Excel para gerar a consulta. Para fechamento de 30/10, use consulta histórica; uma consulta pontual corrente não comprova valor naquela data.
4. Exporte valores estáticos que abram sem o add-in e preserve a exportação original. Campos indisponíveis ficam identificados, sem zeros artificiais.
5. Salve na pasta e nome abaixo, com aba de metadados. Avise ao agente o que ficou faltando para ele aplicar a alternativa.

| ID | Arquivo em `data/raw/bloomberg/` | Pedido |
| --- | --- | --- |
| H01 | `01_mercado_20261030.xlsx` | Fechamento histórico dos cinco papéis, moeda/ajustes, capital por classe com data, tesouraria/market cap e eventos |
| H02 | `02_financeiros.xlsx` | DRE/BP/DFC 2021–2025 e 1S25/1S26, EBITDA e ajustes, unidade e escopo |
| H03 | `03_consenso.xlsx` | Receita/EBITDA/capex 2026–2030, mediana, dispersão, número de contribuidores, data e período previsto |
| H04 | `04_analistas.xlsx` | Instituição, preço-alvo, data e horizonte; identificar relatório atualizado |
| H05 | `05_esg.xlsx` | KPI, definição, unidade, período/perímetro e fonte original; rating separado de indicador operacional |
| H06 | `06_titulos.xlsx` | Título IPCA, identificação/vencimento, tipo de taxa, data/horário e fonte |

A aba `metadados` deve trazer operador, captura com fuso, data efetiva do dado, função/consulta/campo, moeda, escala, período, ajustes de eventos/proventos e observações de indisponibilidade. Dados de balanço não viram valores de outubro apenas porque a exportação ocorreu em outubro. Quantidade emitida, fora de tesouraria e free float não são iguais.

Para consenso, preservar a fotografia realmente disponível. Se a consulta trouxer estimativa atual, registrar como atual, sem rotular como histórico. Instituição/data/horizonte evitam comparar ou contar preços-alvo incompatíveis.

API Desktop é opção técnica, dependente de sessão/permissão; não compartilhar senha nem dedicar a janela de ensaio à integração. Referência: [biblioteca oficial Bloomberg](https://professional.bloomberg.com/support/api-library/).

No teste registrado, o SDK e a pasta DAPI existiam, mas o endpoint local8194 estava inativo. Após abrir/autenticar o Terminal, o agente pode testar a sessão. A importação genérica das exportações também precisa de implementação quando essa rota for usada. Coleta pública e fechamento contábil do agente seguem independentes desse complemento; ver [estado central](../ESTADO_DO_PROJETO.md).

## 3. Se faltar preço na Bloomberg

A alternativa é o operador obter manualmente arquivo permitido da [B3](https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/mercado-a-vista/cotacoes-historicas/) e salvá-lo em `data/raw/b3_manual/` com origem/data. A página restringe coleta automatizada; o agente importa a cópia local pelo layout, sem automatizar a aquisição.

O histórico não está ajustado por proventos. O agente tratará fechamento/eventos conforme o uso; não apresentar esse arquivo como retorno total ajustado.

## 4. H07 — salvar regras e instruções

Reunir regulamento e comunicações efetivas em `data/raw/orientacoes/`. Preparar `resumo_orientacoes.md` com prazo/horário/fuso, canal, vídeo/formato/tamanho, participação, conteúdo e artefatos pedidos. Citar documento/página ou mensagem/data em cada regra e marcar campos não informados.

O agente extrai e confere o material; o grupo esclarece o que depender do canal privado. O prazo 02/11 vem dos planos internos e precisa de confirmação. Não é necessário aguardar H07 para iniciar coleta/modelos; conformidade e envio dependem da orientação atual.

## 5. Depois das exportações

Seguir H08/H09 para revisar premissas e recomendação, H10/H11 para ensaio/gravação, H12 somente para operação técnica indisponível e H13 para revisão/envio. Essas ações e seus arquivos estão no plano 06. Os gráficos, slides, roteiro e falas são preparados pelo agente.
