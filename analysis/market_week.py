"""Semana do segundo turno (plano 14): fechamentos de 23/10/2026 e NTN-B da mesma data, das mesmas fontes dos valores de 30/10.

Os preços de 30/10 usados no valor já são posteriores ao primeiro pregão depois do segundo turno (26/10). O fechamento
de 23/10 mostra quanto do desconto nasceu nessa semana. A reportagem só data o evento; os números vêm das tabelas de
cotação e da série do Tesouro já usadas no pacote.
"""
from __future__ import annotations

import csv
import io
import re

from .data import Baseline, Registry, file_source

TICKERS = {"SAPR11": ("sanepar", "BRL/unit"), "SBSP3": ("sabesp", "BRL/share"), "CSMG3": ("copasa", "BRL/share")}
PRE, POST = "23/10/2026", "30/10/2026"
TESOURO = "data/raw/tesouro/tesouro_taxas__84f53c4bd781.csv"
NEWS = "data/raw/analysis/mercado/poder360_queda_acoes_pos_eleicao.html"
NEWS_ID = "SRC_poder360_20261026_queda_bolsa"
HEADER = ["Data", "Abertura", "Máxima", "Mínima", "Fechamento", "Volume"]


def _num(cell: str) -> float:
    return float(cell.replace("R$", "").replace("\xa0", "").strip().replace(".", "").replace(",", "."))


def _closes(base: Baseline, rel: str) -> dict:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup((base.files / rel).read_text(encoding="utf-8", errors="replace"), "html.parser")
    rows = [[c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])] for tr in soup.find_all("tr")]
    if rows[0][:6] != HEADER:
        raise AssertionError(f"Tabela de cotações com cabeçalho inesperado em {rel}: {rows[0]}")
    return {r[0]: _num(r[4]) for r in rows[1:] if len(r) >= 5 and re.fullmatch(r"\d{2}/\d{2}/\d{4}", r[0])}


def build(reg: Registry, base: Baseline) -> dict:
    news = re.sub(r"\s+", " ", (base.files / NEWS).read_text(encoding="utf-8"))
    for needle in ("26.out.2026", "reeleição de Lula", "16,8% na Sanepar (SAPR11)", '"datePublished": "2026-10-26T21:11:10-03:00"'):
        if needle not in news:
            raise AssertionError(f"Reportagem do Poder360 sem o trecho esperado: {needle!r}")
    file_source(reg, base, NEWS_ID, NEWS, issuer="Poder360", title="Queda das ações atinge quase todos os setores da Bolsa",
                url="https://www.poder360.com.br/poder-economia/queda-das-acoes-atinge-quase-todos-os-setores-da-bolsa/",
                published_at="2026-10-26", retrieved_at="2026-11-01", access_method="web_fetch", access_status="downloaded_published_before_cutoff",
                reference_date="2026-10-26")
    out = {"close_pre": {}, "change": {}}
    for t, (entity, unit) in TICKERS.items():
        post_ref = f"V.{t}.close.2026-10-30"
        src = reg.observations[post_ref]["source_refs"]
        closes = _closes(base, reg.sources[src[0]]["local_path"])
        if abs(closes[POST] - reg.get(post_ref)) > 1e-9:
            raise AssertionError(f"{t}: fechamento de 30/10 da tabela ({closes[POST]}) difere do preço do pacote ({reg.get(post_ref)})")
        pre = reg.value(f"V.{t}.close.2026-10-23", metric_id="close_price", entity_id=entity, instrument_id=t, value=closes[PRE], unit=unit,
                        value_state="observed", fact_type="fact", period_end="2026-10-23", observed_at="2026-10-23", scope="B3 fechamento",
                        source_refs=src, locator="HTML table Cotacoes Recentes; row 23/10/2026; Fechamento",
                        note="Último pregão antes do segundo turno (25/10/2026); mesma fonte do preço de 30/10.")
        out["close_pre"][t] = pre
        out["change"][t] = reg.value(f"V.{t}.change.2026-10-23_2026-10-30", metric_id="price_change", entity_id=entity, instrument_id=t,
                                     value=reg.get(post_ref) / closes[PRE] - 1, unit="ratio", value_state="derived", fact_type="derived",
                                     period_start="2026-10-23", period_end="2026-10-30", source_refs=src,
                                     calculation_ref="fechamento de 30/10 ÷ fechamento de 23/10 − 1",
                                     note="Variação na semana do segundo turno; não identifica causa.")
    rows = list(csv.DictReader(io.StringIO((base.files / TESOURO).read_text(encoding="latin-1")), delimiter=";"))
    ntnb = {r["Data Base"]: (i, r) for i, r in enumerate(rows, start=2)
            if r["Tipo Titulo"] == "Tesouro IPCA+" and r["Data Vencimento"] == "15/05/2035" and r["Data Base"] in (PRE, POST)}
    rate = lambda d: float(ntnb[d][1]["Taxa Compra Manha"].replace(",", ".")) / 100
    if abs(rate(POST) - reg.get("V.macro.ntnb_2035_real.2026-10-30")) > 1e-12:
        raise AssertionError("NTN-B de 30/10 da série difere da taxa usada no custo de capital")
    out["ntnb_pre"] = reg.value("V.macro.ntnb_2035_real.2026-10-23", metric_id="real_risk_free", value=rate(PRE), unit="ratio",
                                value_state="observed", fact_type="fact", period_end="2026-10-23", observed_at="2026-10-23",
                                scope="Tesouro IPCA+ 15/05/2035, taxa de compra manhã", source_refs=["SRC_tesouro_taxas_84f53c4b"],
                                locator=f"tesouro_taxas.csv; linha {ntnb[PRE][0]}", note="Último dia útil antes do segundo turno; o caso-base usa a taxa de 30/10.")
    srcs = sorted({s for t in TICKERS for s in reg.observations[f"V.{t}.close.2026-10-30"]["source_refs"]} | {"SRC_tesouro_taxas_84f53c4b", NEWS_ID})
    out["claim"] = reg.claim(
        "CL.result.election_week", claim_type="fact",
        text_template=("No último pregão antes do segundo turno (23/10/2026), SAPR11 fechou a {{value:V.SAPR11.close.2026-10-23}}; em 30/10, a "
                       "{{value:V.SAPR11.close.2026-10-30}} ({{value:V.SAPR11.change.2026-10-23_2026-10-30}}). No mesmo período, SBSP3 variou "
                       "{{value:V.SBSP3.change.2026-10-23_2026-10-30}} e CSMG3 {{value:V.CSMG3.change.2026-10-23_2026-10-30}}, e a NTN-B 2035 foi de "
                       "{{value:V.macro.ntnb_2035_real.2026-10-23}} para {{value:V.macro.ntnb_2035_real.2026-10-30}}; o custo de capital do caso-base usa a taxa de 30/10."),
        source_refs=srcs,
        limitations="A variação de preço não identifica a causa; a reportagem de 26/10 associa a queda daquele dia à reeleição do presidente.")
    return out
