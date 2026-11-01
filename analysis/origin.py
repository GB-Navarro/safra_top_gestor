"""Ponto de partida da apresentação (plano 14): carteira de ações da 2ª carta ao investidor.

Lê a tabela "A carteira e o risco" (seção 9) e a descrição do método (seção 8) do .docx original
copiado na fotografia, e registra pesos e motivos como observações com a carta como fonte.
"""
from __future__ import annotations

import re
import zipfile
from xml.etree import ElementTree as ET

from .data import Baseline, Registry, file_source

LETTER = "cartas/Asset_dev_Carta_ao_Investidor_2a.docx"
SOURCE_ID = "SRC_carta_2a_asset_dev"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
SLUG = {"Petrobras": "petrobras", "Vale": "vale", "WEG": "weg", "Suzano": "suzano", "Bradesco": "bradesco", "Sabesp": "sabesp"}


def _text(el) -> str:
    return "".join(t.text or "" for t in el.iter(W + "t")).strip()


def _document(base: Baseline):
    with zipfile.ZipFile(base.files / LETTER) as z:
        return ET.fromstring(z.read("word/document.xml")).find(W + "body")


def build(reg: Registry, base: Baseline) -> dict:
    file_source(reg, base, SOURCE_ID, LETTER, issuer="asset.dev", title="Carta ao Investidor — 2ª entrega (Desafio Safra Top Gestor 2026)",
                url="", published_at="2026-09-18", retrieved_at="2026-11-01", access_method="original_local",
                access_status="original_team_document", reference_date="2026-09-21/2026-10-09")
    body = _document(base)
    paragraphs = [_text(p) for p in body if p.tag == W + "p"]
    method = next((p for p in paragraphs if p.startswith("Usamos o método Black-Litterman")), "")
    if "O ponto de partida é o carrego" not in method or "Sobre ele entram as nossas views" not in method:
        raise AssertionError("Descrição do método não encontrada na seção 8 da 2ª carta")
    if not any("Período de referência: 21/09/2026 a 09/10/2026" in p for p in paragraphs):
        raise AssertionError("Janela da 2ª carta não confere")
    # Teses citadas na apresentação: exportadoras pelo real fraco (§ ações) e Petrobras pelo petróleo (§ Ormuz).
    if not any(p.startswith("A outra metade da tese está nas exportadoras: Vale, WEG e Suzano") and "lucro subir com o real fraco" in p
               for p in paragraphs):
        raise AssertionError("Tese das exportadoras (real fraco) não encontrada na 2ª carta")
    if not any("Petrobras em 5% é a nossa posição" in p and "Ormuz" in p for p in paragraphs):
        raise AssertionError("Tese da Petrobras (petróleo/Ormuz) não encontrada na 2ª carta")
    table = None
    for tbl in body.iter(W + "tbl"):
        rows = [[_text(tc) for tc in tr.iter(W + "tc")] for tr in tbl.iter(W + "tr")]
        if rows and rows[0][:4] == ["Bloco", "Ativo", "Posição", "Por que está na carteira"]:
            table = rows
    if table is None:
        raise AssertionError("Tabela 'A carteira e o risco' não encontrada na 2ª carta")
    weights, reasons = {}, {}
    for bloco, ativo, posicao, motivo in (r[:4] for r in table[1:]):
        if bloco != "Ações":
            continue
        m = re.match(r"(\d+),(\d+)% comprad", posicao)
        if not m or ativo not in SLUG:
            raise AssertionError(f"Linha de ações inesperada na 2ª carta: {ativo} / {posicao}")
        value = float(f"{m[1]}.{m[2]}") / 100
        slug = SLUG[ativo]
        weights[slug] = reg.value(f"V.carta2.weight.{slug}", metric_id="portfolio_weight_letter2", value=value, unit="ratio",
                                  value_state="observed", fact_type="fact", period_start="2026-09-21", period_end="2026-10-09",
                                  scope=f"{ativo}; % do patrimônio na carteira da 2ª entrega", source_refs=[SOURCE_ID],
                                  locator=f"Seção 9, tabela 'A carteira e o risco', linha {ativo} ({posicao})", note=f"Motivo na carta: {motivo}")
        reasons[slug] = motivo
    if set(weights) != set(SLUG.values()):
        raise AssertionError(f"Ações da 2ª carta incompletas: {sorted(weights)}")
    if reasons["sabesp"] != "Escolha do modelo (prêmio de risco)" or reasons["bradesco"] != "Escolha do modelo (prêmio de risco)":
        raise AssertionError("Motivo de Sabesp/Bradesco diverge da carta")
    stocks = reg.value("V.carta2.equity_share", metric_id="portfolio_equity_share_letter2", value=sum(reg.get(v) for v in weights.values()),
                       unit="ratio", value_state="derived", fact_type="derived", period_start="2026-09-21", period_end="2026-10-09",
                       source_refs=[SOURCE_ID], calculation_ref="soma dos pesos das seis ações da tabela da seção 9",
                       note="Parcela do patrimônio em ações na 2ª entrega.")
    reg.claim("CL.lead.origin", claim_type="fact",
              text_template=("Na carteira da 2ª carta (21/09 a 09/10/2026), a Sabesp tinha {{value:V.carta2.weight.sabesp}} do patrimônio, "
                             "com o motivo registrado como escolha do modelo de alocação pelo prêmio de risco; era a única empresa de saneamento. "
                             "Petrobras, Vale, WEG e Suzano ({{value:V.carta2.weight.petrobras}} cada) vinham das nossas teses de petróleo e real mais fraco."),
              value_refs=[weights["sabesp"], weights["petrobras"], stocks], source_refs=[SOURCE_ID],
              limitations=("A carta não detalha por que o prêmio de risco favoreceu a Sabesp; não inferimos além do motivo registrado. "
                           "Teses: seção 9 (tabela), parágrafos das exportadoras (real fraco) e da Petrobras (Ormuz)."))
    return {"weights": weights, "equity_share": stocks, "reasons": reasons, "claim": "CL.lead.origin"}
