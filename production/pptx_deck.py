"""EN05 — PPTX9 (apresentação) e apoio técnico de 7 páginas, a partir do mesmo modelo/figuras do HTML."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

from . import content as K
from .common import writable
from .consumer import Bundle

NAVY, INK, INK2, MUTED, SOFT, ACCENT = (RGBColor(0x0D, 0x36, 0x6B), RGBColor(0x0B, 0x0B, 0x0B), RGBColor(0x52, 0x51, 0x4E),
                                        RGBColor(0x6F, 0x6D, 0x67), RGBColor(0xF4, 0xF3, 0xEF), RGBColor(0x1C, 0x5C, 0xAB))
ENT_RGB = {"sanepar": RGBColor(0x2A, 0x78, 0xD6), "sabesp": RGBColor(0xEB, 0x68, 0x34), "copasa": RGBColor(0x1B, 0xAF, 0x7A)}
FONT = "Segoe UI"


def _tb(slide, x, y, w, h, text, size=18, bold=False, color=INK, align=None, wrap=True):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    lines = text if isinstance(text, list) else [text]
    for k, line in enumerate(lines):
        par = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        run = par.add_run()
        run.text = line
        run.font.size, run.font.bold, run.font.name = Pt(size), bold, FONT
        run.font.color.rgb = color
        if align:
            par.alignment = align
        par.space_after = Pt(6)
    return box


def _rect(slide, x, y, w, h, fill, line=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
    shp.adjustments[0] = .08
    shp.shadow.inherit = False
    return shp


def _frame(prs, n, total, kicker, title, subtitle, sources, badge=False):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(.07))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    _tb(s, .55, .25, 6, .35, "asset.dev · Saneamento e valor", 11, True, NAVY)
    _tb(s, 11.6, .25, 1.2, .35, f"{n:02d} / {total}", 11, False, MUTED, PP_ALIGN.RIGHT)
    if badge:
        _tb(s, 7.4, .25, 4.1, .35, "Proposta — decisão do grupo (H09) pendente", 10, True, ACCENT, PP_ALIGN.RIGHT)
    _tb(s, .55, .62, 10, .35, kicker.upper(), 12, True, ACCENT)
    long = len(title) > 58  # acima disso o título quebra a 30 pt: reduz e desce o subtítulo
    _tb(s, .55, .9, 12.2, 1.1, title, 26 if long else 30, True, INK)
    _tb(s, .55, 1.86 if long else 1.72, 12.2, .45, subtitle, 14, False, INK2)
    _tb(s, .55, 7.02, 12.2, .35, "Fontes: " + " · ".join(sources[:4]) + (" · …" if len(sources) > 4 else ""), 9, False, MUTED)
    return s


def _notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def _img(slide, path: Path, x, y, w=None, h=None):
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)


def _table(slide, x, y, w, rows, col_w=None, size=11, header=True):
    nr, nc = len(rows), len(rows[0])
    tbl = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(.3 * nr)).table
    for j in range(nc):
        if col_w:
            tbl.columns[j].width = Inches(col_w[j])
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.text = str(val)
            for par in cell.text_frame.paragraphs:
                for r in par.runs:
                    r.font.size, r.font.name = Pt(size), FONT
                    r.font.bold = header and i == 0
                    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if header and i == 0 else INK
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY if header and i == 0 else (SOFT if i % 2 else RGBColor(0xFF, 0xFF, 0xFF))
    return tbl


STATE = {"analysis_proposed": "análise proposta (premissas H08 e recomendação H09 pendentes do grupo)",
         "analysis_adopted": "análise adotada pelo grupo", "baseline_unreconciled": "baseline legado sem conciliação"}
DISPOSITION = {"confirmed": "Confirmado", "confirmed_net_presentation": "Confirmado (apresentação líquida)",
               "reclassified": "Reclassificado", "limited_excluded_from_model": "Limitado — fora do modelo",
               "excluded_from_projection": "Excluído da projeção", "resolved_single_treatment": "Resolvido — tratamento único"}
SIDE = {"adverse": "adverso", "favorable": "favorável", "base": "base"}
STEM = {"A.recognition_lag": "defasagem", "A.recognition_share": "captura"}


def _alt(b: Bundle, ref: str, refs: list[str]) -> str:
    """Alternativa H08 legível: premissa (lado + valor) ou caso (empresa: rótulo, valor no papel)."""
    if ref in b.obs:
        stem, side = ref.rsplit(".", 1)
        mixed = len({r.rsplit(".", 1)[0] for r in refs if r in b.obs}) > 1
        side = SIDE.get(side, side)
        return f"{STEM.get(stem, stem)} ({side}): {b.fmt(ref)}" if mixed else f"{side}: {b.fmt(ref)}"
    c = b.case(ref)
    dim = next(iter(c["dimensions"].values()))
    pv = c["value_refs"].get("paper_value")
    val = b.fmt(pv) if pv and c["target_validity"] == "conditional_value" else "N/D"
    return f"{b.entity_name(c['entity_id'])} — {dim['label'].lower()}: {val}"


def build_main(model: dict, b: Bundle, speech: dict, figs: Path, out: Path) -> Path:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    P = {p["id"]: p for p in model["pages"]}
    names = model["entity_names"]
    total = 9
    src = lambda *ids: sorted({s["title"] for i in ids for s in P[i]["sources"]})
    # S1
    p = P["P01"]
    s = _frame(prs, 1, total, p["kicker"], p["title"], p["subtitle"], src("P01"), True)
    _rect(s, .55, 2.45, 6.4, 2.35, NAVY)
    v, pr, up = p["hero"]
    _tb(s, .85, 2.6, 4, .4, v["label"].upper(), 12, True, RGBColor(0xDD, 0xE6, 0xF3))
    _tb(s, .85, 2.95, 4.2, 1.2, v["fmt"], 54, True, RGBColor(0xFF, 0xFF, 0xFF))
    _tb(s, .85, 4.15, 3, .4, v["note"], 13, False, RGBColor(0xDD, 0xE6, 0xF3))
    _tb(s, 4.3, 2.75, 2.5, 1.8, [pr["label"], pr["fmt"], f"{up['label']}: {up['fmt']}"], 15, True, RGBColor(0xFF, 0xFF, 0xFF), PP_ALIGN.RIGHT)
    _tb(s, 7.35, 2.45, 5.4, .4, "CONDIÇÕES DA RECOMENDAÇÃO", 12, True, MUTED)
    _tb(s, 7.35, 2.85, 5.4, 2.2, ["• " + c["text"] for c in p["chips"]], 15, False, INK)
    for k, c in enumerate(p["compare"]):
        x = .55 + k * 4.1
        _rect(s, x, 5.25, 3.9, 1.45, SOFT)
        acc = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(5.25), Inches(.09), Inches(1.45))
        acc.fill.solid()
        acc.fill.fore_color.rgb = ENT_RGB[c["entity"]]
        acc.line.fill.background()
        _tb(s, x + .25, 5.35, 2.6, .4, f"{names[c['entity']]} {c['ticker']}", 16, True)
        _tb(s, x + .25, 5.85, 2.8, .7, [f"Valor {c['value']['fmt']} · Preço {c['price']['fmt']}"], 12, False, INK2)
        _tb(s, x + 2.7, 5.5, 1.1, .5, c["upside"]["fmt"] if c["upside"] else "N/D", 17, True, INK, PP_ALIGN.RIGHT)
    _notes(s, speech["B1"])
    # S2
    p = P["P02"]
    s = _frame(prs, 2, total, p["kicker"], p["title"], p["subtitle"], src("P02"))
    _img(s, figs / "s02_setor.png", .55, 2.45, w=7.6)
    _rect(s, 8.5, 2.5, 4.3, 3.6, SOFT)
    _tb(s, 8.75, 2.65, 3.9, 3.3, [p["notes"]["sewer"], "", p["callout"]], 14, False, INK)
    _notes(s, speech["B2"])
    # S3
    p = P["P03"]
    s = _frame(prs, 3, total, p["kicker"], p["title"], "Forças, fraquezas, oportunidades e ameaças — e o efeito de cada uma na tese.", src("P03"))
    for k, q in enumerate(p["quadrants"]):
        x, y = .55 + (k % 2) * 6.2, 2.4 + (k // 2) * 2.3
        _rect(s, x, y, 6.0, 2.15, SOFT)
        _tb(s, x + .25, y + .12, 5.5, .4, q["label"], 18, True, NAVY)
        _tb(s, x + .25, y + .55, 5.5, 1.0, ["• " + t for t in q["bullets"]], 12.5, False, INK)
        _tb(s, x + .25, y + 1.55, 5.5, .55, "→ " + q["implication"], 11.5, True, INK2)
    _notes(s, speech["B3"])
    # S4
    p = P["P04"]
    s = _frame(prs, 4, total, p["kicker"], p["title"], p["subtitle"], src("P04"))
    for k, c in enumerate(p["cards"]):
        x = .55 + k * 4.15
        _rect(s, x, 2.45, 3.95, 4.4, SOFT)
        _tb(s, x + .25, 2.6, 3.5, .45, c["label"], 20, True, NAVY)
        _tb(s, x + .25, 3.1, 3.5, 3.7, [c["tabs"]["fato"], "", "Canal: " + c["tabs"]["canal"]], 12.5, False, INK)
    _notes(s, speech["B4"])
    # S5
    p = P["P05"]
    s = _frame(prs, 5, total, p["kicker"], p["title"], "Sem nota sintética: definições e períodos diferem; cada linha mostra o canal para o caixa.", src("P05"))
    rows = [["Fator"] + [names[e] for e in model["order"]] + ["Canal para o caixa"]]
    for r in p["rows"]:
        rows.append([r["factor"]] + [(f"{r['cells'][e]['values'][0]['fmt']} — " if r["cells"][e]["values"] else "lacuna — ") + r["cells"][e]["text"]
                                    for e in model["order"]] + [r["channel"]])
    _table(s, .55, 2.35, 12.2, rows, [1.9, 2.75, 2.75, 2.75, 2.05], 10.5)
    _notes(s, speech["B5"])
    # S6
    p = P["P06"]
    s = _frame(prs, 6, total, p["kicker"], p["title"], p["subtitle"], src("P06"))
    _img(s, figs / "s06_ponte_esg.png", .55, 2.5, w=12.2)
    _tb(s, .55, 6.2, 12.2, .7, p["claim_texts"]["CL.bridge.energy"], 11.5, False, INK2)
    _notes(s, speech["B6"])
    # S7 (P07 + P08)
    p7, p8 = P["P07"], P["P08"]
    s = _frame(prs, 7, total, "Valuation", p8["title"], "Do valor da firma ao acionista (esquerda) e valor contra preço nas três empresas (direita).", src("P07", "P08"))
    _img(s, figs / "s07_ponte_valor.png", .45, 2.4, w=6.3)
    _img(s, figs / "s08_valor_preco.png", 6.9, 2.5, w=5.9)
    _tb(s, 6.9, 5.0, 5.9, 1.9, [p8["claim_texts"]["CL.result.implied"], p7["claim_texts"]["CL.method.fcff"]], 11, False, INK2)
    _notes(s, speech["B7.a"] + "\n\n" + speech["B7.b"])
    # S8
    p = P["P09"]
    s = _frame(prs, 8, total, p["kicker"], p["title"], p["subtitle"], src("P09"))
    _img(s, figs / "s09_cenarios.png", .45, 2.35, w=6.6)
    for k, t in enumerate(p["triggers"]):
        y = 2.4 + k * 1.45
        _rect(s, 7.35, y, 5.45, 1.32, SOFT)
        _tb(s, 7.55, y + .07, 5.1, .35, f"⚠ {t['label']} — monitorar", 13.5, True, RGBColor(0x7A, 0x52, 0x00))
        _tb(s, 7.55, y + .42, 5.1, .9, [f"Limite: {t['limit']}", f"Quando: {t['when']} · Ação: {t['action']}"], 10.5, False, INK)
    _notes(s, speech["B8"])
    # S9
    p = P["P10"]
    s = _frame(prs, 9, total, p["kicker"], p["title"], p["subtitle"], src("P10"), True)
    _rect(s, .55, 2.4, 5.6, 2.35, NAVY)
    _tb(s, .85, 2.55, 5.0, .9, p["title"].split(": ", 1)[-1], 24, True, RGBColor(0xFF, 0xFF, 0xFF))
    _tb(s, .85, 3.45, 5.0, 1.2, p["points"][1]["text"], 14, False, RGBColor(0xDD, 0xE6, 0xF3))
    _tb(s, 6.6, 2.4, 6.2, 2.4, [f"{x['label']}: {x['text']}" for x in p["points"]], 13.5, False, INK)
    _tb(s, .55, 4.95, 5.6, .3, p["ladder"]["labels"]["title"].upper(), 11, True, MUTED)
    _img(s, figs / "s10_faixa_compra.png", .55, 5.25, h=1.65)
    _tb(s, 6.6, 4.95, 6.2, .3, p["triggers_title"].upper(), 11, True, MUTED)
    for k, t in enumerate(p["triggers"]):
        _rect(s, 6.6, 5.3 + k * .54, 6.2, .48, SOFT)
        _tb(s, 6.75, 5.31 + k * .54, 6.0, .46, f"⚠ {t['label']}: {t['limit']}", 10.5, False, INK)
    _notes(s, speech["B9"])
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(writable(out)))
    return out


def build_support(model: dict, b: Bundle, figs: Path, out: Path) -> Path:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    total = 7
    srcs = sorted({s["title"] for p in model["pages"] for s in p["sources"]})
    # 1 método
    state = STATE.get(b.manifest["state"], b.manifest["state"])
    s = _frame(prs, 1, total, "Apoio técnico", "Método, recortes e rastreabilidade", f"Pacote analítico {b.bundle_id} · {state}.", srcs)
    md = b.metadata
    _tb(s, .55, 2.4, 12.2, 4.4, [f"Preços e avaliação: {md['market_asof']} · corte informacional: {md['information_cutoff']} · balanço: {md['balance_date']}.",
                                 f"Escopo: {md['scope']}.", "Método: " + "; ".join(md["method"]) + ".",
                                 "Cada número das peças vem de um value_id do pacote (observations.csv), com fonte, período, unidade e definição.",
                                 "Recálculo independente da planilha (LibreOffice) e reprodução das planilhas originais registrados no QA do pacote."]
        + ([b.claim_text("CL.method.brr_check")] if "CL.method.brr_check" in b.claims else []), 14)
    # 2 conciliação
    s = _frame(prs, 2, total, "Apoio técnico", "Conciliação das 64 células históricas e da recorrência", "Disposição por requisito (confirmado, reclassificado, limitado).", srcs)
    cnt = Counter((r["requirement_id"], r["disposition"]) for r in b.reconciliation)
    rows = [["Requisito", "Disposição", "Linhas"]] + [[k[0], DISPOSITION.get(k[1], k[1]), v] for k, v in sorted(cnt.items())]
    _table(s, .55, 2.35, 7.5, rows, [1.4, 4.5, 1.6], 11)
    _tb(s, 8.4, 2.35, 4.4, 4.2, ["C02/C04: valores da planilha confirmados nas demonstrações (DVA, custos por natureza, DFC).",
                                 "C03: EBITDA 2023–24 com resíduos não itemizados — fora da base.",
                                 "C05: giro com definição única; C06: capex em caixa; C07: zeros fundamentados; C08: base recorrente publicada."], 13)
    # 3 premissas H08
    s = _frame(prs, 3, total, "Apoio técnico", "Cinco julgamentos para o grupo (H08)", "Proposta do agente com alternativas calculadas.", srcs)
    rows = [["Tema", "Proposta", "Alternativas"]]
    for j in b.decision.get("h08_judgments", []):
        ref = j["proposal_ref"]
        prop = b.fmt(ref) if ref in b.obs else ref
        alts = "; ".join(_alt(b, a, j["alternatives"]) for a in j["alternatives"])
        rows.append([j["topic"], prop, alts])
    _table(s, .55, 2.35, 12.2, rows, [4.2, 2.6, 5.4], 12)
    # 4 precatório
    s = _frame(prs, 4, total, "Apoio técnico", "Precatório da Sanepar: cronograma e valor presente", "Regra Agepar: 100% aos usuários — metade em descontos (até mai/2029), metade em investimentos não onerosos (até dez/2030).", srcs)
    by = Counter()
    for r in b.schedule:
        if ".base." in r["schedule_id"]:
            by[(r["flow_date"][:4], r["component"])] += float(r["nominal_value"])
    rows = [["Ano", "Descontos tarifários (R$ mi)", "Investimento não oneroso (R$ mi)"]]
    for y in sorted({k[0] for k in by}):
        rows.append([y, f"{by[(y, 'tariff_discount')]:,.1f}".replace(",", "X").replace(".", ",").replace("X", "."),
                     f"{by[(y, 'non_onerous_capex')]:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")])
    _table(s, .55, 2.35, 7.2, rows, [1.2, 3.0, 3.0], 12)
    _tb(s, 8.1, 2.35, 4.7, 4.2, [b.claim_text("CL.method.precatorio"), "", "Favorável: 75% e benefício fiscal; adverso: descontos concentrados até fev/2029."], 13)
    # 5 grade
    s = _frame(prs, 5, total, "Apoio técnico", "Sensibilidade: custo de capital × crescimento real", b.claim_text("CL.result.implied"), srcs)
    _img(s, figs / "s08_grade.png", .55, 2.5, w=8.6)
    _tb(s, 9.4, 2.5, 3.4, 4.0, [b.claim_text("CL.result.market_view")], 12)
    # 6 ESG
    s = _frame(prs, 6, total, "Apoio técnico", "Matriz ESG: definições, períodos e fontes", "Valores de perímetros e períodos diferentes não formam ranking.", srcs)
    p5 = next(p for p in model["pages"] if p["id"] == "P05")
    rows = [["Fator", "Empresa", "Valor", "Período", "Fonte"]]
    for r in p5["rows"]:
        for e in model["order"]:
            for v in r["cells"][e]["values"][:1]:
                rows.append([r["factor"], model["entity_names"][e], v["fmt"], v["period"] or "—", "; ".join(x["title"] for x in v["source"])[:70]])
    _table(s, .55, 2.25, 12.2, rows[:16], [2.1, 1.3, 1.6, 2.6, 4.6], 9.5)
    # 7 limitações
    s = _frame(prs, 7, total, "Apoio técnico", "Limitações e pendências", "O que a análise não certifica e o que depende do grupo.", srcs)
    _tb(s, .55, 2.35, 12.2, 4.5, ["• " + x for x in b.metadata["limitations"]] +
        ["• Testes e recálculos verificam contas e rastreabilidade; não certificam premissas econômicas.",
         "• Pendências humanas: H07 (instruções/canal), H08/H09 (premissas e recomendação), H10/H11 (ensaios e gravação), H13 (envio)."], 14)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(writable(out)))
    return out
