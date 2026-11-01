"""EN08 — documentos de rascunho para o grupo, gerados do pacote 1.0 (substituem os textos da análise anterior)."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from .common import write_text
from .consumer import Bundle


def build(b: Bundle, model: dict, out: Path, html_rel: str = "html/apresentacao_esg.html") -> list[Path]:
    f = b.fmt
    dec = b.decision
    made = []
    lead = [
        f"# Leia primeiro — pacote de apresentação (rascunho)", "",
        f"Gerado do pacote analítico `{b.bundle_id}` ({b.manifest['state']}). Preços/avaliação 30/10/2026; corte 31/10/2026 18:25:27 −03:00.", "",
        "**Proposta do agente; decisão do grupo (H08/H09) pendente.** Nada aqui foi enviado ao Safra.", "",
        "## O que abrir",
        f"- `{html_rel}` — apresentação interativa de 10 páginas (offline, duplo clique; teclas ← →, G = modo gravação).",
        "- `html/apresentacao_esg.pdf` — as mesmas 10 páginas em PDF (estado padrão).",
        "- `apresentacao_esg.pptx` / `.pdf` — versão de 9 slides editável com notas do orador.",
        "- `apoio_tecnico.pptx` / `.pdf` — 7 páginas de método, conciliação, premissas, precatório, sensibilidade e limitações.",
        "- `script_apresentacao.md` (pptx9) e `script_apresentacao_html10.md` — falas exatas; `teleprompter/` por integrante.",
        "- `perguntas_banca.md`, `guia_gravacao.md`, `decisao_proposta.md`, `PROXIMOS_PASSOS.md`.",
        "- `base_modelo_auditavel.xlsx` (fórmulas do caso-base) e `coleta/base_dados_coletados.xlsx`.", "",
        "Cada número vem de um `value_id` do pacote, com fonte, período e unidade. Testes verificam contas e rastreabilidade, não as premissas.", ""]
    made.append(write_text(out / "LEIA_PRIMEIRO.md", "\n".join(lead)))
    nxt = [
        "# O que o grupo precisa fazer agora", "",
        f"A análise da Parte 1 foi concluída como **proposta** (pacote `{b.bundle_id}`) e as peças foram regeneradas a partir dela. "
        "Faltam decisões e ações que só o grupo pode fazer:", "",
        "1. **Navarro — H07 (hoje, prioridade máxima).** Confirmar horário, canal, formato e tamanho do envio de 02/11/2026 (mensagem de 16/10 e live de 20/10) "
        "e salvar o original em `data/raw/orientacoes/`. Sem isso não se declara conformidade da submissão.",
        f"2. **Grupo — H08 (premissas).** Revisar os cinco julgamentos do checklist (`LEIA_PRIMEIRO.md` do pacote): WACC {f('A.wacc_nominal.base')}, "
        f"WACC regulatório da Sabesp {f('A.sabesp_wacc_reg.base')} (contrato, fixo até 2029; alternativas valem para o 2º ciclo), defasagem {f('A.recognition_lag.base')}, precatório 100% "
        f"(PV {f('V.sanepar.obligation_pv.base', 'precise')}) e terminal. Registrar em `data/interim/decisoes_equipe.md`.",
        f"3. **Grupo — H09 (recomendação).** Adotar ou rejeitar: {b.entity_name(dec['entity_id'])} ({dec['instrument_id']}) compra condicionada abaixo de "
        f"{f('V.sanepar.max_entry_price')}; valor-base {f('V.case.sanepar.base.paper_value')} contra {f('V.SAPR11.close.2026-10-30')}. "
        "Se mudarem premissas, o agente reexecuta `python -m analysis.run` e `python -m production.run` (nova versão; a anterior fica preservada).",
        "4. **Os quatro — H10 (dois ensaios cronometrados).** Usar o HTML (ou PDF) e o teleprompter; registrar tempos por bloco em `data/interim/feedback_ensaio.md`.",
        "5. **Os quatro — H11 (gravação).** Seguir `guia_gravacao.md`; clipes em `data/raw/gravacao/` (perfil pptx9) ou `data/raw/gravacao/html10/` (perfil html10).",
        "6. **Responsável pelo envio — H13.** Assistir ao vídeo inteiro, conferir requisitos de H07 e enviar pelo canal confirmado; guardar comprovante.", "",
        "O agente não envia mensagens nem arquivos ao Safra.", ""]
    made.append(write_text(out / "PROXIMOS_PASSOS.md", "\n".join(nxt)))
    from .narrative import segments
    n9, n10 = len(segments("pptx9")), len(segments("html10"))
    chk = ["# Checklist de envio (H07 → H13)", "",
           "Preencher só com evidência real. O agente não envia nada e não marca item por inferência ou por existência de arquivo.", "",
           "## H07 — instruções privadas (Navarro)", "",
           "- [ ] Horário-limite do envio de 02/11/2026 (mensagem de 16/10 ou live de 20/10)",
           "- [ ] Canal (e-mail, plataforma ou link) e destinatário",
           "- [ ] Formato e tamanho máximo do arquivo; duração máxima do vídeo",
           "- [ ] Nome do arquivo e identificação da equipe exigidos",
           "- [ ] Se o HTML interativo pode ser usado na gravação ou como anexo (sem instrução, o vídeo segue o perfil pptx9)",
           "- Registro: salvar o original em `data/raw/orientacoes/` (além do regulamento público já verificado).", "",
           "## H08/H09 — premissas e recomendação (grupo)", "",
           "- [ ] Cinco julgamentos H08 decididos em `data/interim/decisoes_equipe.md`",
           "- [ ] Recomendação H09 adotada ou substituída; se mudar premissa, reexecutar `analysis.run` e `production.run`", "",
           "## H10/H11 — ensaios e gravação (os quatro)", "",
           "- [ ] Dois ensaios cronometrados por bloco em `data/interim/feedback_ensaio.md`",
           f"- [ ] Clipes reais em `data/raw/gravacao/` (pptx9, {n9} segmentos) ou `data/raw/gravacao/html10/` (html10, {n10} segmentos)",
           "- [ ] `python -m production.run --release-report` sem motivo de bloqueio em H10/H11", "",
           "## H13 — revisão integral e envio (responsável)", "",
           "- [ ] Vídeo assistido inteiro pelo grupo; registrar `data/raw/orientacoes/video_review.json` (quem, quando, hash do vídeo)",
           "- [ ] Requisitos de H07 conferidos item a item",
           "- [ ] Envio feito por um membro pelo canal confirmado",
           "- [ ] Comprovante em `data/raw/orientacoes/comprovante_envio.json` (data/hora, canal, hash do arquivo enviado)", ""]
    made.append(write_text(out / "checklist_envio.md", "\n".join(chk)))
    pend = ["# Pendências e limites", "", f"Disposições do pacote `{b.bundle_id}` (ver `pendencias.csv` do pacote).", "",
            "| Requisito | Status | Limitação |", "|---|---|---|"]
    pend += [f"| {d['requirement_id']} | {d['status']} | {d['limitations']} |" for d in b.manifest["requirement_dispositions"]]
    pend += ["", "Limitações gerais: " + "; ".join(b.metadata["limitations"]) + ".", "",
             "Pendências humanas: H07 (instruções privadas), H08/H09 (premissas e recomendação), H10 (dois ensaios), H11 (clipes reais), H13 (revisão integral e envio).", ""]
    made.append(write_text(out / "pendencias.md", "\n".join(pend)))
    sc = lambda e, s: b.case(f"{e}.{s}")["paper_value"]
    dp = [f"# Proposta para discussão — {b.entity_name(dec['entity_id'])} sob condições", "",
          b.claim_text("CL.lead.decision"), "", b.claim_text("CL.lead.thesis"), "",
          "| Papel | Preço 30/10 | Valor caso-base | Potencial | WACC implícito no preço |", "|---|---:|---:|---:|---:|"]
    for e, t in (("sanepar", "SAPR11"), ("sabesp", "SBSP3"), ("copasa", "CSMG3")):
        c = b.case(f"{e}.base")
        dp.append(f"| {t} | {f(c['value_refs']['price'])} | {f(c['value_refs']['paper_value']) if c['paper_value'] is not None else 'N/D'} | "
                  f"{f(c['value_refs']['upside'], 'signed1') if 'upside' in c['value_refs'] else 'N/D'} | {f(b.extras['implied_wacc'][e])} |")
    dp += ["", "## Cenários (Sanepar)", "", b.claim_text("CL.risk.scenarios"), "", "## Gatilhos", ""] + \
          [f"- {b.claim_text(c)}" for c in dec["trigger_claim_refs"]] + ["", "## Melhor objeção", "", b.claim_text("CL.risk.objection"), "",
          "## Cinco julgamentos para H08", ""] + [f"- **{j['topic']}**: proposta `{j['proposal_ref']}` ({f(j['proposal_ref']) if j['proposal_ref'] in b.obs else 'caso'})"
                                                 for j in dec.get("h08_judgments", [])] + \
          ["", "Valores condicionais às premissas propostas; não são preços-alvo aprovados.", ""]
    made.append(write_text(out / "decisao_proposta.md", "\n".join(dp)))
    cnt = Counter((r["requirement_id"], r["disposition"]) for r in b.reconciliation)
    cf = ["# Conciliação financeira — resumo", "", f"64 células históricas e a recorrência da Sanepar (C08) com disposição e fonte em `tables/financial_reconciliation.csv` do pacote `{b.bundle_id}`.", "",
          "| Requisito | Disposição | Linhas |", "|---|---|---:|"] + [f"| {k[0]} | {k[1]} | {v} |" for k, v in sorted(cnt.items())] + [
          "", "- **C02/C04 (Sabesp):** construção e capex da planilha confirmados nas demonstrações (DVA 7.01.03, notas de custos, DFC 6.02.01+02).",
          f"- **C03 (Sabesp):** EBITDA recorrente 2025 {f('V.sabesp.ebitda_recurring.2025', 'precise')} por componentes; 2023–24 com resíduos não itemizados ficaram fora da base.",
          "- **C05:** giro com definição única nas três empresas (sem dividendos, PPP, derivativos, passivo regulatório e provisões).",
          "- **C06 (Copasa):** capex em caixa da DFC; plano 2026–30 da DF 2025 (projeções descontinuadas pela companhia em 03/2026; premissa do analista).",
          f"- **C07/C08 (Sanepar):** zeros de construção fundamentados (margem nula); EBITDA recorrente {f('V.sanepar.ebitda_recurring.2025', 'precise')}; IR 34% normalizado; "
          "plano de investimento sem doações e parcerias; precatório em tratamento único.", ""]
    made.append(write_text(out / "conciliacao_financeira.md", "\n".join(cf)))
    leg = b.extras.get("legacy", [])
    am = ["# Auditoria dos modelos", "", "## Ramo legado (planilhas originais)", "",
          "| Planilha | Valor calculado | Valor em cache | Reproduz? |", "|---|---:|---:|---|"] + \
         [f"| {r['workbook']} | {r['calculated_share']:.4f} | {r['cached_share']:.4f} | {'sim' if r['passed'] else 'não'} |" for r in leg] + [
         "", "Reproduzir fórmula não valida premissa: o ramo legado trata capex só como saída de caixa, sem remuneração regulatória.", "",
         "## Ramo revisado", "", b.claim_text("CL.method.fcff"), "", b.claim_text("CL.bridge.rab"), "",
         *([b.claim_text("CL.method.brr_check"), ""] if "CL.method.brr_check" in b.claims else []),
         f"QA do pacote: {b.qa.get('status')} — recálculo independente no LibreOffice, conciliação das 64 células e identidade do FCFF.", ""]
    made.append(write_text(out / "auditoria_modelos.md", "\n".join(am)))
    return made
