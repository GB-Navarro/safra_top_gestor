"""EN05 — apoio técnico de 7 páginas (PPTX editável), a partir do mesmo modelo e figuras da apresentação de 12 slides."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

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
    _img(s, figs / "s11_grade.png", .55, 2.5, w=8.6)
    _tb(s, 9.4, 2.5, 3.4, 4.0, [b.claim_text("CL.result.market_view")], 12)
    # 6 ESG
    s = _frame(prs, 6, total, "Apoio técnico", "Matriz ESG: definições, períodos e fontes", "Valores de perímetros e períodos diferentes não formam ranking.", srcs)
    p5 = next(p for p in model["pages"] if p["kind"] == "matrix")
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
