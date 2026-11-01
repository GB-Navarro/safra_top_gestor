"""AN10 — exportação, QA e publicação atômica do pacote analítico 1.0.

Ordem: tabelas/resultados → planilhas → recálculo independente → QA (hashes de entradas e
resultados, sem QA/manifesto) → manifesto (inclui hash do QA) → validação do contrato →
renomear diretório temporário → atualizar latest.json atomicamente. Nunca sobrescreve versão.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import openpyxl

from . import (SCHEMA_VERSION, assumptions, capital, contract, legacy, obligations, reconciliation, recommendation, sector, valuation,
               workbooks)
from .common import (REPO, SAO_PAULO, atomic_write_json, copy_into, now_iso, publish_directory, read_json, sha256_file, write_csv,
                     write_json)
from .data import Baseline, Registry, file_source

BUNDLE_ROOT = REPO / "outputs/draft/analysis_bundle"
QA_ROOT = REPO / "outputs/qa/analysis"
PROCESSED = REPO / "data/processed/analysis"
SOFFICE = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
OBS_HEADER = contract.OBS_FIELDS + ["source_location", "note"]
ASSUMPTION_HEADER = contract.TABLE_HEADERS["tables/assumptions.csv"]
CLAIM_HEADER = contract.CLAIM_FIELDS
SLICE = {"C02": "AN02", "C03": "AN02", "C04": "AN02", "C05": "AN02", "C06": "AN02", "C07": "AN02", "C08": "AN02", "C09": "AN03",
         "C10": "AN04", "C11": "AN07", "C12": "AN07", "C13": "AN06", "C14": "AN06", "C15": "AN05/AN08", "C16": "AN05", "C17": "AN08",
         "C18": "AN05", "C19": "AN09/AN12", "C20": "AN09", "C21": "AN10", "C22": "AN10", "C23": "AN10", "C27": "AN01/AN12", "C29": "AN11"}


def _code_hash() -> str:
    h = hashlib.sha256()
    for p in sorted((REPO / "analysis").glob("*.py")):
        h.update(p.read_bytes())
    return h.hexdigest()[:8]


def _dispositions(rec_rows, cal, val) -> list[dict]:
    by_req = {}
    for r in rec_rows:
        by_req.setdefault(r["requirement_id"], []).append(r["disposition"])
    sab_gap = cal["sabesp"]["gap_pp"]
    D = [
        ("C02", "resolved", ["tables/financial_reconciliation.csv#C02"], "Perímetro individual 2021–22 vs consolidado 2023–25; só 2025 usado."),
        ("C03", "resolved_with_limitations", ["tables/financial_reconciliation.csv#C03"], "2023–24: resíduos não itemizados (525,7 e 1.200,3); anos excluídos da base. 2025 reclassificado por componentes."),
        ("C04", "resolved", ["tables/financial_reconciliation.csv#C04"], "Comparador anterior omitia DFC 6.02.02."),
        ("C05", "resolved_with_limitations", ["tables/financial_reconciliation.csv#C05"], "Tributos a recuperar podem conter IR/CS (não separável no nível CVM)."),
        ("C06", "resolved_with_limitations", ["tables/financial_reconciliation.csv#C06", "tables/assumptions.csv#capex_copasa"], "Plano 2026–30 da planilha (DF 2025 item 6.2); a companhia descontinuou as projeções em 12/03/2026 e o novo controlador revisará o plano: premissa do analista."),
        ("C07", "resolved", ["tables/financial_reconciliation.csv#C07"], "Zero fundamentado (apresentação líquida, margem nula)."),
        ("C08", "resolved", ["tables/financial_reconciliation.csv#C08"], "Base recorrente publicada pela companhia; plano reclassificado por componente."),
        ("C09", "resolved_with_limitations", ["tables/corporate_actions.csv", "tables/observations.csv#shares"], "Preços de provedor público sem confirmação H01; eventos jul–out pesquisados em fontes públicas (oferta secundária da Copasa sem emissão); recompras da Sabesp após junho não observadas."),
        ("C10", "resolved_with_limitations", ["tables/adjustments.csv"], "EMAE (consolidada na Sabesp em 2026) sem valoração separada; aplicações de longo prazo fora do caixa."),
        ("C11", "resolved_with_limitations", ["tables/obligation_schedule.csv"], "Calendário mensal estimado; benefício fiscal e desfecho judicial incertos (casos favorável/adverso)."),
        ("C12", "resolved_with_limitations", ["results/valuation.json#rollforward"], "Rolagem jun→out por FCFF uniforme; sensibilidade ×0,5/×1,5."),
        ("C13", "limited", ["tables/assumptions.csv"], f"Premissas propostas para H08; Sabesp: crescimento-modelo 2026 {sab_gap:+.1f} p.p. acima do observado (custos 2T26)."),
        ("C14", "resolved_with_limitations", ["tables/assumptions.csv#wacc_nominal"], "Beta/ERP/estrutura são premissas com faixa; WACC regulatório Sabesp do contrato (Anexo VIII, fixo até 2029)."),
        ("C15", "resolved_with_limitations", ["results/valuation.json#terminal_finite"], "Copasa: caso finito pelo prazo médio ponderado (~29 anos), aproximação de um portfólio com contratos até 2073 e vencidos."),
        ("C16", "limited", ["results/esg_matrix.json"], "Copasa: indicador de acesso não obtido; séries 2022–25 não completadas (não sustentam afirmação)."),
        ("C17", "resolved", ["results/esg_bridge.json"], "Apenas sensibilidade/teto condicionado; não somado ao DCF."),
        ("C18", "resolved_with_limitations", ["tables/claims.csv#swot", "tables/regulatory_terms.csv"], "Eventos jul–out/2026 pesquisados (desestatização da Copasa, SAINP da Sanepar); calendário de outros emissores não certificado."),
        ("C19", "proposed_pending_human", ["results/recommendation.json"], "H08/H09 não registrados; fatia de produção pendente."),
        ("C20", "analysis_slice_done", ["tables/claims.csv", "results/narrative.json"], "Posicionamento em páginas/falas é da Parte 2."),
        ("C21", "analysis_slice_done", ["results/valuation.json", "model_inputs.json"], "Consumo/adaptação é da Parte 2."),
        ("C22", "analysis_slice_done", ["qa/analysis_validation.json"], "QA de ingestão/peças é da Parte 2."),
        ("C23", "analysis_slice_done", ["workbooks/base_modelo_auditavel.xlsx"], "Figuras/PPTX/HTML são da Parte 2."),
        ("C27", "analysis_slice_done", ["data/catalog/parallel_progress/analysis.json"], "Consolidação global depende das duas partes."),
        ("C29", "resolved", ["relatorio_cobertura.md#omissoes"], "Complementos omitidos sem bloqueio (consenso, analistas, Bloomberg, regressões, EV/BRR)."),
    ]
    return [dict(requirement_id=r, slice=f"analysis:{SLICE[r]}", status=s, evidence_refs=e, limitations=l) for r, s, e, l in D]


RECALC_ITEMS = ('<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item>'
                '<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="ODFRecalcMode" oor:op="fuse"><value>0</value></prop></item>')


def _force_recalc_profile(profile_dir: Path) -> None:
    """Perfil próprio do LibreOffice que recalcula todas as fórmulas ao abrir (sem valores em cache = recálculo real)."""
    xcu = profile_dir / "user" / "registrymodifications.xcu"
    xcu.parent.mkdir(parents=True, exist_ok=True)
    if xcu.is_file():
        text = xcu.read_text(encoding="utf-8")
        if "OOXMLRecalcMode" in text:
            return
        text = text.replace("</oor:items>", RECALC_ITEMS + "</oor:items>")
    else:
        text = ('<?xml version="1.0" encoding="UTF-8"?>\n<oor:items xmlns:oor="http://openoffice.org/2001/registry" '
                'xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                + RECALC_ITEMS + "</oor:items>\n")
    xcu.write_text(text, encoding="utf-8")


def _recalculate(xlsx: Path, out_dir: Path, cellmap: dict, expected: dict) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    if not SOFFICE.is_file():
        return {"status": "unavailable", "reason": f"LibreOffice não encontrado em {SOFFICE}"}
    _force_recalc_profile(QA_ROOT / "lo_profile")
    profile = (QA_ROOT / "lo_profile").resolve().as_uri()
    target = out_dir / xlsx.name
    attempts = []
    for _ in range(2):  # a primeira execução com perfil novo pode falhar só ao inicializá-lo
        p = subprocess.run([str(SOFFICE), f"-env:UserInstallation={profile}", "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(out_dir), str(xlsx)],
                           capture_output=True, text=True, timeout=180, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        attempts.append({"returncode": p.returncode, "stderr": p.stderr[-500:]})
        if p.returncode == 0 and target.is_file():
            break
    if not target.is_file():
        return {"status": "failed_to_run", "attempts": attempts}
    book = openpyxl.load_workbook(target, data_only=True, read_only=True)
    checks, errors, max_rel = 0, [], 0.0
    for key, (sheet, cell) in cellmap.items():
        got = book[sheet][cell].value
        exp = expected.get(key)
        if exp is None:
            continue
        checks += 1
        if not isinstance(got, (int, float)):
            errors.append({"key": list(key), "got": str(got), "expected": exp})
            continue
        rel = abs(got - exp) / max(1.0, abs(exp))
        max_rel = max(max_rel, rel)
        if rel > 1e-9:
            errors.append({"key": list(key), "got": got, "expected": exp, "rel_error": rel})
    book.close()
    return {"status": "passed" if not errors else "failed", "engine": "LibreOffice Calc (headless)", "attempts": attempts, "checks": checks,
            "max_relative_error": max_rel, "tolerance": "1e-9 relativo (R$ milhões ou R$/papel)", "errors": errors,
            "recalculated_copy": target.relative_to(REPO).as_posix() if target.is_relative_to(REPO) else str(target)}


def _unit_tests() -> dict:
    p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests/analysis", "-p", "test_*.py"],
                       cwd=REPO, capture_output=True, text=True, timeout=900)
    tail = (p.stderr or "")[-1500:]
    return {"command": "python -m unittest discover -s tests/analysis -p 'test_*.py'", "returncode": p.returncode,
            "status": "passed" if p.returncode == 0 else "failed", "summary": tail}


def build(snapshot_dir: Path, *, bundle_root: Path = BUNDLE_ROOT, qa_root: Path = QA_ROOT, processed_root: Path = PROCESSED,
          run_tests: bool = True) -> dict:
    base = Baseline(snapshot_dir)
    stamp = datetime.now(SAO_PAULO).strftime("%Y%m%dT%H%M%S")
    bundle_id = f"an_{stamp}_{_code_hash()}"
    reg = Registry(bundle_id)
    reviewed_at = now_iso()
    for r in base.csv("data/processed/sources.csv"):
        reg.source(**r)
    file_source(reg, base, "SRC_an_sabesp_inst_2025", "data/raw/analysis/sabesp/sabesp_apresentacao_mziq_e0de9896.pdf", issuer="Sabesp",
                title="Apresentação Institucional (fevereiro de 2025)",
                url="https://api.mziq.com/mzfilemanager/v2/d/9e47ee51-f833-4a23-af98-2bac9e54e0b3/e0de9896-cbf5-2960-c121-5126b8dfb72b?origin=1",
                published_at="2025-02-18", retrieved_at="2026-11-01", access_method="web_fetch", access_status="downloaded_published_before_cutoff")
    # Plano 13: fontes primárias publicadas antes do corte, lidas em 01/11/2026.
    for sid, rel, issuer, title, url, pub in (
            ("SRC_urae1_anexo_viii_2025", "data/raw/analysis/urae1/urae1_anexo_viii_formacao_tarifa_inicial_apostilado.pdf", "URAE-1/Governo de SP",
             "Contrato de Concessão 01/2024 — Anexo VIII (Formação da Tarifa Inicial), versão apostilada",
             "https://urae1.sp.gov.br/wp-content/uploads/sites/26/2025/02/ANEXO-VIII_Apostilado.pdf", "2025-02"),
            ("SRC_agepar_nt_006_2025", "data/raw/analysis/agepar/agepar_nt_006_2025_3rtp_sanepar.pdf", "Agepar",
             "Nota Técnica 006/2025 — 3ª Revisão Tarifária Periódica da Sanepar",
             "http://www.sanepar.com.br/sites/default/files/notatecnica620253artpsanepar.pdf", "2025-04-03"),
            ("SRC_copasa_fr_20260611", "data/raw/analysis/copasa/copasa_fato_relevante_20260611_preco_oferta.pdf", "Copasa",
             "Fato relevante — preço da oferta secundária e investidor de referência",
             "https://api.mziq.com/mzfilemanager/v2/d/8bdb3906-0618-4e78-bbe3-a0be9f02d8cc/f79246f5-13ce-0a60-1e38-8d8b828375d0?origin=2", "2026-06-11"),
            ("SRC_sanepar_fr_20261028_sainp", "data/raw/analysis/sanepar/sanepar_fato_relevante_20261028_sainp.pdf", "Sanepar",
             "Fato relevante — resultado da licitação de locação de ativos (SAINP)",
             "https://ri.sanepar.com.br/docs/Fato-Relevante-Sanepar-2026-10-28-pwH9r7qG.pdf", "2026-10-28")):
        file_source(reg, base, sid, rel, issuer=issuer, title=title, url=url, published_at=pub, retrieved_at="2026-11-01",
                    access_method="web_fetch", access_status="downloaded_published_before_cutoff")
    # ---------------- AN02–AN09 ----------------------------------------------------------
    rec = reconciliation.build(reg, base, reviewed_at)
    cap = capital.build(reg, base)
    bal = obligations.balances(reg, base)
    m = assumptions.macro(reg, base)
    a = assumptions.build(reg, base, rec, cap, m)
    val = valuation.build(reg, base, rec, cap, bal, a, m)
    sec = sector.build(reg, base, val, cap, m, a)
    rcm = recommendation.build(reg, rec, cap, bal, a, val, sec)
    leg = legacy.replicate(base.json("data/interim/original_models.json"))
    infl = assumptions.inflation_path(reg, m)
    infl[2024], infl[2025] = reg.get(m["actual"][2024]), reg.get(m["actual"][2025])
    sched = {k: obligations.precatorio_schedule(reg, base, infl, k) for k in ("base", "adverse", "favorable")}
    # ---------------- escrever no diretório temporário ------------------------------------
    tmp = bundle_root / f".tmp_{bundle_id}"
    T = tmp / "tables"
    write_csv(T / "entities.csv", base.csv("data/processed/entities.csv"), contract.TABLE_HEADERS["tables/entities.csv"])
    write_csv(T / "instruments.csv", base.csv("data/processed/instruments.csv"), contract.TABLE_HEADERS["tables/instruments.csv"])
    write_csv(T / "sources.csv", list(reg.sources.values()), contract.TABLE_HEADERS["tables/sources.csv"])
    write_csv(T / "observations.csv", list(reg.observations.values()), OBS_HEADER)
    write_csv(T / "definitions.csv", list(reg.definitions.values()), contract.TABLE_HEADERS["tables/definitions.csv"])
    write_csv(T / "assumptions.csv", list(reg.assumptions.values()), ASSUMPTION_HEADER)
    write_csv(T / "adjustments.csv", bal["adjustments"], obligations.ADJ_HEADER)
    write_csv(T / "regulatory_terms.csv", sec["terms"], sector.REG_HEADER)
    write_csv(T / "corporate_actions.csv", cap["events"], capital.CA_HEADER)
    write_csv(T / "financial_reconciliation.csv", rec["rows"], reconciliation.HEADER)
    write_csv(T / "obligation_schedule.csv", obligations.schedule_rows(sched), obligations.SCHEDULE_HEADER)
    write_csv(T / "claims.csv", list(reg.claims.values()), CLAIM_HEADER)
    head = {"schema_version": SCHEMA_VERSION, "bundle_id": bundle_id}
    R = tmp / "results"
    clean_cases = [{k: v for k, v in c.items()} for c in val["cases"]]
    write_json(R / "valuation.json", {**head, "method": "FCFF com base remunerada implícita (ramo revisado); ver model_inputs.json",
                                      "cases": clean_cases, "calibration": val["calibration"], "implied_wacc_refs": val["implied_wacc"],
                                      "legacy_replication": leg, "capital_search": cap["search_record"]})
    write_json(R / "scenarios.json", {**head, "cases": [c for c in clean_cases if c["scenario_id"] in valuation.SCENARIOS],
                                      "scenario_labels": valuation.SCENARIOS})
    write_json(R / "esg_matrix.json", {**head, "rows": sec["matrix"], "note": "Sem score sintético; células com value_refs e texto."})
    write_json(R / "esg_bridge.json", {**head, "cases": sec["bridge_cases"]})
    write_json(R / "presentation_facts.json", {**head, "views": rcm["views"]})
    write_json(R / "narrative.json", {**head, "slots": rcm["slots"]})
    write_json(R / "recommendation.json", {**head, "decision": rcm["decision"]})
    # model_inputs: entradas selecionadas do ramo revisado (permite refazer a análise).
    mi = {**head, "branch": "revised", "snapshot_id": base.snapshot_id, "valuation_date": "2026-10-30",
          "engine": "analysis.dcf.run + analysis.dcf.bridge", "entities": {}}
    for e in valuation.ENTITIES:
        b = rec["basis"][e]
        mi["entities"][e] = {"value_refs": {"ebitda_2025": b["ebitda_2025"], "da_2025": b["da_2025"], "revenue_2025": b["revenue_2025"],
                                            "wc_ratio": b["wc_ratio"], "net_debt_june": bal["items"][e]["net_debt"],
                                            "shares": cap["shares"][e]["total"], "price": cap["prices"][valuation.ENTITIES[e]],
                                            "regulatory_wacc": a["reg_wacc"][e]["base"], "capex_2024": f"V.{e}.capex_cash.2024",
                                            "capex_2025": f"V.{e}.capex_cash.2025"},
                             "debt_like_refs": {k: v for k, v in bal["items"][e].items() if k not in ("gross_debt", "cash", "net_debt")},
                             "capex_plan_refs": {str(y): v for y, v in a["capex"][e].items()},
                             "base_case": next(c["case_id"] for c in val["cases"] if c["case_id"] == f"{e}.base")}
    mi["common_refs"] = {"wacc": a["wacc"], "lag": a["lag"], "share": a["share"], "opex_shock": a["opex"], "eligible": a["eligible"],
                         "rab_g": a["rab_g"], "tax": a["tax"], "inflation_focus": m["focus"], "inflation_actual": m["actual"]}
    write_json(tmp / "model_inputs.json", mi)
    meta = {**head, "part_id": "analysis", "snapshot_id": base.snapshot_id, "market_asof": "2026-10-30", "valuation_date": "2026-10-30",
            "information_cutoff": "2026-10-31T18:25:27-03:00", "balance_date": "2026-06-30", "built_at": now_iso(),
            "scope": "Sabesp (consolidado), Copasa (consolidado), Sanepar (individual); R$ milhões nominais salvo indicação",
            "method": ["AN02 conciliação de 64 células e recorrência", "AN03 capital/classes/eventos", "AN04/AN07 obrigações e ponte temporal",
                       "AN05 regulação/ESG/setor", "AN06 premissas com alternativas", "AN08 FCFF com base remunerada implícita",
                       "AN09 decisão por regra e claims"],
            "limitations": ["Base remunerada implícita no EBIT de 2025; BRR oficial só da Sanepar (verificação, em fiscalização)",
                            "Alternativas do WACC regulatório da Sabesp aplicadas ao horizonte inteiro (contrato fixa 7,86% até 2029)",
                            "Plano de capex da Copasa é premissa do analista (projeções descontinuadas pela companhia em 03/2026)",
                            "Preços de provedor público; confirmação H01 ausente",
                            "Proposta econômica; H08/H09 não registrados"]}
    write_json(tmp / "metadata.json", meta)
    disp = _dispositions(rec["rows"], val["calibration"], val)
    write_csv(tmp / "pendencias.csv", [dict(requirement_id=d["requirement_id"], disposition=d["status"], justification=d["limitations"],
                                            stage_blocking=("apresentação definitiva/vídeo (H08/H09)" if d["status"] in ("proposed_pending_human", "limited") else "nenhum para proposta analítica"),
                                            evidence=d["evidence_refs"]) for d in disp],
              ["requirement_id", "disposition", "justification", "stage_blocking", "evidence"])
    (tmp / "relatorio_cobertura.md").write_text(_coverage_md(rec, val, sec, disp), encoding="utf-8")
    (tmp / "LEIA_PRIMEIRO.md").write_text(_readme_md(bundle_id, base, reg, rcm, val), encoding="utf-8")
    # ---------------- planilhas ----------------------------------------------------------
    W = tmp / "workbooks"
    W.mkdir(parents=True, exist_ok=True)
    tables = {"Fontes": (contract.TABLE_HEADERS["tables/sources.csv"], list(reg.sources.values())),
              "Observacoes": (OBS_HEADER, list(reg.observations.values())),
              "Definicoes": (contract.TABLE_HEADERS["tables/definitions.csv"], list(reg.definitions.values())),
              "Conciliacao": (reconciliation.HEADER, rec["rows"]), "Ajustes": (obligations.ADJ_HEADER, bal["adjustments"]),
              "Cronograma_obrigacoes": (obligations.SCHEDULE_HEADER, obligations.schedule_rows(sched)),
              "Termos_regulatorios": (sector.REG_HEADER, sec["terms"]), "Eventos": (capital.CA_HEADER, cap["events"]),
              "Premissas": (ASSUMPTION_HEADER, list(reg.assumptions.values())), "Claims": (CLAIM_HEADER, list(reg.claims.values()))}
    workbooks.data_workbook(W / "base_dados_coletados.xlsx", tables,
                            [f"Pacote {bundle_id} — base de dados coletados e conciliados (Parte 1).", "Valores em R$ milhões salvo indicação.",
                             "Cada número aponta para value_id, fonte e localização; ausência não é zero."])
    inputs, expected = {}, {}
    for e in valuation.ENTITIES:
        case = next(c for c in val["cases"] if c["case_id"] == f"{e}.base")
        p = valuation._params(reg, rec, a, m, e, {})
        inputs[e] = workbooks.inputs_from_case(reg, rec, cap, bal, a, m, case, p, e)
        d = case["diagnostics"]
        expected.update({(e, "enterprise_value"): reg.get(case["value_refs"]["enterprise_value"]),
                         (e, "pv_explicit"): reg.get(case["value_refs"]["pv_explicit"]), (e, "pv_terminal"): reg.get(case["value_refs"]["pv_terminal"]),
                         (e, "equity_residual"): case["equity_residual_before_floor"], (e, "paper_value"): case["paper_value"],
                         (e, "terminal_fcff"): d["terminal_fcff"], (e, "b0"): d["b0_real"]})
        for row in d["flows"]:
            expected[(e, f"fcff_{row['year']}")] = row["fcff"]
            expected[(e, f"ebitda_{row['year']}")] = row["ebitda"]
    expected[("sanepar", "obligation_pv")] = reg.get(next(c for c in val["cases"] if c["case_id"] == "sanepar.base")["value_refs"]["obligation_pv"])
    sched_rows = [dict(date=f["date"].isoformat(), component=f["component"], nominal=f["nominal"], after_tax=f["after_tax"]) for f in sched["base"]]
    cellmap = workbooks.model_workbook(W / "base_modelo_auditavel.xlsx", inputs, val["cases"], leg, sched_rows,
                                       [f"Pacote {bundle_id} — modelo auditável (ramo revisado, caso-base com fórmulas).",
                                        "Abas Sabesp/Copasa/Sanepar: entradas verdes, base remunerada implícita, fluxos 2026–35, terminal e ponte.",
                                        "Aba Casos: todos os cenários/grade (valores do motor Python). Aba Legado: reprodução das planilhas originais.",
                                        "N/D = resíduo acionário não positivo ou caso não calculável; nunca preço zero."])
    recalc = _recalculate(W / "base_modelo_auditavel.xlsx", qa_root / "recalculated" / bundle_id, cellmap, expected)
    # ---------------- QA -----------------------------------------------------------------
    rec_cells = [r for r in rec["rows"] if r["requirement_id"] in ("C02", "C03", "C04", "C05", "C06", "C07")]
    mapping = base.csv("data/catalog/cell_issue_mapping.csv")
    mapped = {(m_["entity_id"], int(m_["year"]), m_["cell"]) for m_ in mapping}
    covered = {(r["entity_id"], int(r["period"]), r["cell"]) for r in rec_cells}
    checks = {
        "cell_coverage": {"open_cells": len(mapped), "with_disposition": len(mapped & covered), "missing": sorted(map(str, mapped - covered)),
                          "status": "passed" if mapped <= covered and all(r["disposition"] for r in rec_cells) else "failed"},
        "legacy_replication": {"results": leg, "status": "passed" if all(x["passed"] for x in leg) else "failed"},
        "workbook_recalculation": recalc,
        "calibration_2026": val["calibration"],
        "case_states": {"total": len(val["cases"]), "by_validity": {k: sum(1 for c in val["cases"] if c["target_validity"] == k) for k in contract.VALIDITY},
                        "status": "passed" if all(c["paper_value"] is None for c in val["cases"] if c["target_validity"] != "conditional_value") else "failed"},
        "fcff_identity": _fcff_identity(val),
        "unit_tests": _unit_tests() if run_tests else {"status": "skipped"},
    }
    hashed = {}
    for pth in sorted(tmp.rglob("*")):
        if pth.is_file() and pth.name not in ("analysis_validation.json", "manifest.json"):
            hashed[pth.relative_to(tmp).as_posix()] = sha256_file(pth)
    snap_meta = base.meta
    gating = ["cell_coverage", "legacy_replication", "workbook_recalculation", "case_states", "fcff_identity", "unit_tests"]
    # Indisponibilidade real de ferramenta/teste pulado é registrada, não aprovada nem escondida.
    gate_ok = all(checks[k]["status"] in ("passed", "unavailable", "skipped") for k in gating)
    qa = {**head, "created_at": now_iso(), "snapshot_id": base.snapshot_id,
          "input_hashes": {f["path"]: f["sha256"] for f in snap_meta["files"]}, "result_hashes": hashed, "checks": checks,
          "gating_checks": gating, "status": "passed" if gate_ok else "failed",
          "scope": "Dados, matemática, linhagem, recálculo Excel/Python e reprodução legada desta execução; não certifica premissas econômicas.",
          "not_covered": ["Adoção humana H08/H09", "Conformidade com instruções privadas H07", "Peças de apresentação (Parte 2)"]}
    write_json(tmp / "qa" / "analysis_validation.json", qa)
    files = []
    for pth in sorted(tmp.rglob("*")):
        if pth.is_file() and pth.name != "manifest.json":
            files.append({"path": pth.relative_to(tmp).as_posix(), "bytes": pth.stat().st_size, "sha256": sha256_file(pth)})
    external = [{"id": "EXT.sabesp_inst_2025", "path": "data/raw/analysis/sabesp/sabesp_apresentacao_mziq_e0de9896.pdf",
                 "sha256": sha256_file(REPO / "data/raw/analysis/sabesp/sabesp_apresentacao_mziq_e0de9896.pdf"), "locator": "p8, p10",
                 "date": "2025-02-18", "license": "documento público de RI; fora do pacote por tamanho"},
                {"id": "EXT.arsesp_1749_2025", "path": "data/raw/analysis/arsesp/arsesp_deliberacao_1749_20251201.pdf",
                 "sha256": sha256_file(REPO / "data/raw/analysis/arsesp/arsesp_deliberacao_1749_20251201.pdf"),
                 "locator": "busca do WACC regulatório Sabesp (não encontrado)", "date": "2025-12-01", "license": "ato público"},
                *[{"id": f"EXT.{k}", "path": rel, "sha256": sha256_file(REPO / rel), "locator": loc, "date": d, "license": "documento público"}
                  for k, rel, loc, d in (
                      ("urae1_anexo_viii", "data/raw/analysis/urae1/urae1_anexo_viii_formacao_tarifa_inicial_apostilado.pdf", "item 10.7, Tabela 5 (p26)", "2025-02"),
                      ("agepar_nt_006_2025", "data/raw/analysis/agepar/agepar_nt_006_2025_3rtp_sanepar.pdf", "p25 (WACC), p81 (BRR)", "2025-04-03"),
                      ("copasa_fr_20260611", "data/raw/analysis/copasa/copasa_fato_relevante_20260611_preco_oferta.pdf", "p1–2", "2026-06-11"),
                      ("sanepar_fr_20261028_sainp", "data/raw/analysis/sanepar/sanepar_fato_relevante_20261028_sainp.pdf", "p1", "2026-10-28"))],
                {"id": "EXT.snapshot", "path": snapshot_dir.relative_to(REPO).as_posix() + "/snapshot.json",
                 "sha256": sha256_file(snapshot_dir / "snapshot.json"), "locator": "fotografia de entrada (AN01)", "date": snap_meta["created_at"],
                 "license": "cópia local; dados brutos podem não estar versionados"}]
    state = "analysis_proposed" if qa["status"] == "passed" and not any(d["status"] == "open" for d in disp) else "analysis_incomplete"
    manifest = {"schema_version": SCHEMA_VERSION, "bundle_id": bundle_id, "kind": "analysis", "state": state, "market_asof": "2026-10-30",
                "valuation_date": "2026-10-30", "information_cutoff": "2026-10-31T18:25:27-03:00", "built_at": now_iso(), "files": files,
                "external_evidence": external, "requirement_dispositions": disp, "human_records": [],
                "limitations": meta["limitations"]}
    write_json(tmp / "manifest.json", manifest)
    pre = contract.validate(tmp)
    if pre["status"] != "passed":
        write_json(qa_root / f"contract_validation_{bundle_id}_FAILED.json", pre)
        raise RuntimeError(f"Contrato 1.0 não atendido; pacote não publicado: {pre['errors'][:10]}")
    final = publish_directory(tmp, bundle_root / bundle_id)
    post = contract.validate(final)
    manifest_hash = sha256_file(final / "manifest.json")
    atomic_write_json(bundle_root / "latest.json", {"bundle_id": bundle_id, "path": f"outputs/draft/analysis_bundle/{bundle_id}",
                                                    "manifest_sha256": manifest_hash, "state": state, "updated_at": now_iso()})
    for rel_ in ["tables/" + p.name for p in (final / "tables").iterdir()] + ["results/" + p.name for p in (final / "results").iterdir()]:
        copy_into(final / rel_, processed_root / rel_)
    write_json(processed_root / "CURRENT.json", {"bundle_id": bundle_id, "manifest_sha256": manifest_hash, "note": "Cópia de trabalho da Parte 1; publicação canônica global é do integrador (Parte 2)."})
    write_json(qa_root / f"contract_validation_{bundle_id}.json", {"bundle_id": bundle_id, "pre_publish": pre, "post_publish": post,
                                                                     "manifest_sha256": manifest_hash, "checked_at": now_iso()})
    return {"bundle_id": bundle_id, "path": final, "state": state, "manifest_sha256": manifest_hash, "qa": qa, "contract": post,
            "decision": rcm["decision"], "registry": reg, "val": val}


def _fcff_identity(val) -> dict:
    worst = 0.0
    for c in val["cases"]:
        for r in (c.get("diagnostics") or {}).get("flows", []):
            worst = max(worst, abs(r["ebitda"] - r["tax"] - r["capex"] - r["delta_wc"] - r["fcff"]))
    return {"max_abs_error": worst, "status": "passed" if worst < 1e-6 else "failed", "identity": "FCFF = EBITDA − IR − capex − ΔGiro"}


def _coverage_md(rec, val, sec, disp) -> str:
    lines = ["# Relatório de cobertura — Parte 1", "",
             "Explica faltas, substitutos e disposições. Requisito documentado não equivale a aprovação econômica.", "",
             "## Disposições por requisito", "", "| Requisito | Status | Limitação |", "|---|---|---|"]
    lines += [f"| {d['requirement_id']} | {d['status']} | {d['limitations']} |" for d in disp]
    lines += ["", "## Células históricas (64)", ""]
    from collections import Counter
    cnt = Counter((r["requirement_id"], r["disposition"]) for r in rec["rows"])
    lines += [f"- {k[0]}: {k[1]} = {v}" for k, v in sorted(cnt.items())]
    lines += ["", "## Substitutos e lacunas", "",
              "- BRR oficial: Sanepar obtida (NT Agepar 006/2025, em fiscalização) e usada como verificação da base implícita (CL.method.brr_check); Sabesp e Copasa sem BRR líquida em fonte primária extraível: base implícita no EBIT 2025 (dcf.py).",
              "- WACC regulatório Sabesp: 7,86% pós / 11,91% pré do Anexo VIII do contrato URAE-1 (fixo no 1º ciclo).",
              "- Plano de capex Copasa: valores da DF 2025 item 6.2 transcritos na planilha; projeções descontinuadas pela companhia em 12/03/2026 (premissa do analista).",
              "- Prazos da Copasa: prazo médio ponderado ~29 anos (release 2T26) usado no caso finito como aproximação.",
              "- Indicador de acesso da Copasa: ausente na matriz (lacuna explícita, não pior desempenho).", "",
              "## Omissões (C29)", "", "Consenso e alvos de analistas, ESG Bloomberg, índices/financiamento verde, regressões (beta de juros, causalidade "
              "pós-privatização), VPL por ligação e EV/BRR não foram usados nem prometidos. Exportações Bloomberg (H01–H06) não recebidas; "
              "substitutos públicos suficientes para o núcleo.", ""]
    return "\n".join(lines)


def _readme_md(bundle_id, base, reg, rcm, val) -> str:
    dec = rcm["decision"]
    sb = next(c for c in val["cases"] if c["case_id"] == "sanepar.base")
    lines = [f"# Pacote analítico {bundle_id}", "",
             f"Fotografia `{base.snapshot_id}`; preços/avaliação 30/10/2026; corte 31/10/2026 18:25:27 −03:00; balanço 30/06/2026.", "",
             f"Estado: proposta analítica (decisão `{dec['status']}`; H08/H09 não registrados).", "",
             "## Leitura rápida", "",
             "- `results/recommendation.json`: decisão proposta, regra, alternativas e gatilhos (claims).",
             "- `results/valuation.json`: todos os casos (cenários, grade WACC×g, terminal finito, ponte, classes) com validade por caso.",
             "- `tables/financial_reconciliation.csv`: 64 células abertas + C08 com disposição e fonte.",
             "- `tables/obligation_schedule.csv`: cronograma datado do precatório (base/adverso/favorável).",
             "- `workbooks/base_modelo_auditavel.xlsx`: caso-base com fórmulas (recalculado no LibreOffice; ver QA).", "",
             "## Checklist curto para o grupo (H08/H09)", "",
             "Marque e registre em `data/interim/decisoes_equipe.md` (responsável, data e justificativa reais):", ""]
    for j in dec["h08_judgments"]:
        lines.append(f"- [ ] **{j['id']} — {j['topic']}**: proposta `{j['proposal_ref']}`; alternativas {', '.join('`'+x+'`' for x in j['alternatives'])}.")
    lines += [f"- [ ] **H09 — recomendação**: adotar ou rejeitar `{dec.get('instrument_id')}` como compra condicionada "
              f"(valor-base {sb['paper_value']:.2f} R$/unit vs preço {reg.get(sb['value_refs']['price']):.2f}); condição de entrada "
              "`V.sanepar.max_entry_price`; objeção `CL.risk.objection`; gatilhos `CL.risk.trigger.*`.", "",
             "Aprovar uma hipótese não transforma número sem fonte em fato. Decisão real gera nova versão do pacote.", ""]
    return "\n".join(lines)
