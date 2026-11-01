"""Marcação dos 12 slides planos (HTML + SVG gerados aqui, sem script de desenho) a partir do modelo de páginas.

Regras de gráfico: ouro = a medida que importa ou que passa no teste; cinza = comparação (preço, meta, tese alheia);
um eixo só; rótulos diretos nos valores; nada clicável.
"""
from __future__ import annotations

import html

from .brand import symbol

NBSP = (("R$ ", "R$\u00a0"), (" bi", "\u00a0bi"), (" mi", "\u00a0mi"), (" p.p.", "\u00a0p.p."), (" MWm", "\u00a0MWm"))


def E(s) -> str:
    """Escapa e prende número à unidade ("R$ 1,04", "13,7 bi") para a linha não quebrar no meio do valor."""
    out = html.escape(str(s))
    for a, b in NBSP:
        out = out.replace(a, b)
    return out


CTX = "Análise setorial · Saneamento e ESG · dados de 30/10/2026"
TOTAL = 12


# ---------------- primitivas SVG ----------------------------------------------------------------
def _f(x: float) -> str:
    return f"{x:.1f}".rstrip("0").rstrip(".")


def vbar(x, base, w, h, cls, r=4):
    """Barra vertical ancorada na base, com a ponta de dado arredondada."""
    if h <= 0:
        return ""
    r = min(r, w / 2, h)
    y = base - h
    return (f'<path class="{cls}" d="M{_f(x)},{_f(base)} V{_f(y + r)} Q{_f(x)},{_f(y)} {_f(x + r)},{_f(y)} H{_f(x + w - r)} '
            f'Q{_f(x + w)},{_f(y)} {_f(x + w)},{_f(y + r)} V{_f(base)} Z"/>')


def hbar(x0, y, length, h, cls, r=4):
    if length <= 0:
        return ""
    r = min(r, h / 2, length)
    x1 = x0 + length
    return (f'<path class="{cls}" d="M{_f(x0)},{_f(y)} H{_f(x1 - r)} Q{_f(x1)},{_f(y)} {_f(x1)},{_f(y + r)} V{_f(y + h - r)} '
            f'Q{_f(x1)},{_f(y + h)} {_f(x1 - r)},{_f(y + h)} H{_f(x0)} Z"/>')


def text(x, y, s, cls="val", anchor="middle", baseline="auto", extra=""):
    return f'<text class="{cls}" x="{_f(x)}" y="{_f(y)}" text-anchor="{anchor}" dominant-baseline="{baseline}"{extra}>{E(str(s))}</text>'


def svg(w, h, body, label):
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{E(label)}">{body}</svg>'


def legend(items):
    return '<div class="legend">' + "".join(f'<span><i style="background:var(--{c})"></i>{E(t)}</span>' for t, c in items) + "</div>"


def _wrap(s: str, width: int) -> list[str]:
    words, lines, cur = s.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + [cur]


def _short(fmt: str) -> str:
    return fmt.replace("R$ ", "").replace(" bi", "").replace(" mi", "")


# ---------------- gráficos ----------------------------------------------------------------------
def chart_origin(stocks, w=860):
    row, bh, lab = 78, 44, 150
    top = 8
    maxv = max(s["num"] for s in stocks) * 1.22
    plot = w - lab - 20
    h = top + row * len(stocks)
    out = [f'<line class="s-axis" x1="{lab}" y1="0" x2="{lab}" y2="{h}"/>']
    for i, s in enumerate(stocks):
        y = top + i * row + (row - bh) / 2
        length = plot * s["num"] / maxv
        out.append(text(lab - 18, y + bh / 2, s["name"], "cat", "end", "central"))
        out.append(hbar(lab, y, length, bh, "f-gold" if s["group"] == "model" else "f-cmp"))
        out.append(text(lab + length + 12, y + bh / 2, s["fmt"], "val", "start", "central"))
    return svg(w, h, "".join(out), "Pesos das ações na carteira da 2ª carta")


def chart_grouped(groups, w, h, ymax, series_cls, label, small=False, bw=None):
    """groups: [(categoria, [item|None, ...])]; item = dict(num, fmt). Uma barra por série, rótulo acima."""
    bottom = 70
    base = h - bottom
    gw = w / len(groups)
    ns = len(series_cls)
    bw = bw or min(110, gw * .62 / ns)
    gap = 10
    out = [f'<line class="s-axis" x1="0" y1="{_f(base)}" x2="{w}" y2="{_f(base)}"/>']
    for gi, (cat, items) in enumerate(groups):
        cx = gi * gw + gw / 2
        x0 = cx - (ns * bw + (ns - 1) * gap) / 2
        for si, it in enumerate(items):
            x = x0 + si * (bw + gap)
            if it is None or it.get("num") is None:
                out.append(text(x + bw / 2, base - 14, "N/D", "val small"))
                continue
            bh = (base - 40) * it["num"] / ymax
            out.append(vbar(x, base, bw, bh, series_cls[si]))
            out.append(text(x + bw / 2, base - bh - 12, it.get("label", it["fmt"]), "val small" if small else "val"))
        for li, line in enumerate(_wrap(cat, 18)):
            out.append(text(cx, base + 34 + li * 24, line, "cat"))
    return svg(w, h, "".join(out), label)


def chart_hbar_ref(items, ref, ref_label, w, label, xmax=None, row=120, bh=56):
    """Barras horizontais com linha de referência vertical (ex.: R$ 1,00); valores numa coluna à direita, fora da linha."""
    lab, top, col = 130, 48, 120
    xmax = xmax or max(max(i["num"] for i in items), ref) * 1.1
    plot = w - lab - col - 16
    h = top + row * len(items)
    out = []
    xr = lab + plot * ref / xmax
    out.append(f'<line class="s-ref" x1="{_f(xr)}" y1="{top - 12}" x2="{_f(xr)}" y2="{h}"/>')
    out.append(text(xr, top - 22, ref_label, "ref-t"))
    for i, it in enumerate(items):
        y = top + i * row + (row - bh) / 2
        length = plot * it["num"] / xmax
        out.append(text(lab - 16, y + bh / 2, it["name"], "cat", "end", "central"))
        out.append(hbar(lab, y, length, bh, "f-gold" if it["num"] > ref else "f-cmp"))
        out.append(text(w, y + bh / 2, it["fmt"], "val", "end", "central"))
    out.append(f'<line class="s-axis" x1="{lab}" y1="{top - 4}" x2="{lab}" y2="{h}"/>')
    return svg(w, h, "".join(out), label)


def chart_vbar_ref(items, ref, ref_label, w, h, label):
    """Barras verticais com linha de referência horizontal; o valor fica dentro da barra, longe da linha."""
    bottom, top = 56, 20
    base = h - bottom
    ymax = max(max(i["num"] for i in items), ref) * 1.12
    sc = (base - top) / ymax
    gw = (w - 250) / len(items)
    bw = min(150, gw * .58)
    out = [f'<line class="s-axis" x1="0" y1="{_f(base)}" x2="{w}" y2="{_f(base)}"/>']
    for i, it in enumerate(items):
        cx = i * gw + gw / 2
        bh = it["num"] * sc
        gold = it["num"] > ref
        out.append(vbar(cx - bw / 2, base, bw, bh, "f-gold" if gold else "f-cmp"))
        out.append(text(cx, base - 26, it["fmt"], "val in-gold" if gold else "val"))  # pé da barra: longe da linha de referência
        out.append(text(cx, base + 36, it["name"], "cat"))
    yr = base - ref * sc
    out.append(f'<line class="s-ref" x1="0" y1="{_f(yr)}" x2="{w - 238}" y2="{_f(yr)}"/>')
    out.append(text(w - 222, yr - 6, ref_label[0], "val", "start"))
    out.append(text(w - 222, yr + 22, ref_label[1], "ref-t", "start"))
    return svg(w, h, "".join(out), label)


def chart_waterfall(items, w, h, label):
    bottom, top = 76, 40
    base = h - bottom
    peak, run = 0.0, 0.0
    for it in items:
        if it["role"] == "start":
            run = it["num"]
        elif it["role"] == "delta":
            run += it["effect_num"]
        peak = max(peak, run, it["num"] if it["role"] != "delta" else 0)
    sc = (base - top) / (peak * 1.08)
    gw = w / len(items)
    bw = min(120, gw * .62)
    out = [f'<line class="s-axis" x1="0" y1="{_f(base)}" x2="{w}" y2="{_f(base)}"/>']
    run = 0.0
    prev_top = None
    for i, it in enumerate(items):
        cx = i * gw + gw / 2
        x = cx - bw / 2
        if it["role"] == "start":
            run = it["num"]
            y0, y1, cls, lab = base - run * sc, base, "f-cmp", _short(it["fmt"])
        elif it["role"] == "delta":
            new = run + it["effect_num"]
            y0, y1 = base - max(run, new) * sc, base - min(run, new) * sc
            cls, lab, run = ("f-neg" if it["effect_num"] < 0 else "f-pos"), _short(it["effect_fmt"]), new
        else:
            y0, y1, cls, lab = base - it["num"] * sc, base, "f-gold", _short(it["fmt"])
        if it["role"] == "end" or it["role"] == "start":
            out.append(vbar(x, base, bw, y1 - y0, cls))
        else:
            out.append(f'<rect class="{cls}" x="{_f(x)}" y="{_f(y0)}" width="{_f(bw)}" height="{_f(max(y1 - y0, 2))}" rx="2"/>')
        if prev_top is not None:
            out.append(f'<line class="s-link" x1="{_f(x - (gw - bw))}" y1="{_f(prev_top)}" x2="{_f(x)}" y2="{_f(prev_top)}"/>')
        prev_top = base - run * sc
        out.append(text(cx, y0 - 12, lab, "val"))
        for li, line in enumerate(_wrap(it["label"], 14)):
            out.append(text(cx, base + 30 + li * 23, line, "cat small-cat"))
    return svg(w, h, "".join(out), label)


def chart_ruler(r, w, h=270):
    lab = r["labels"]
    pts = [r["adverse"], r["rates"], r["favorable"], r["price"], r["limit"], r["value"]]
    nums = [p["num"] for p in pts if p.get("num") is not None]
    lo, hi = min(nums) * .8, max(nums) * 1.05
    X = lambda v: 20 + (w - 40) * (v - lo) / (hi - lo)
    y = 150
    out = [f'<line class="s-axis" x1="20" y1="{y}" x2="{w - 20}" y2="{y}" style="stroke-width:3"/>',
           f'<line class="s-buy" x1="20" y1="{y}" x2="{_f(X(r["limit"]["num"]))}" y2="{y}"/>',
           text(20, y - 26, lab["buy"], "axis-t", "start")]
    # acima do eixo: preço (texto para a esquerda), limite e valor-base (texto para a direita)
    for key, anchor, dx, cls in (("price", "end", -14, "f-white"), ("limit", "start", 14, "f-gold"), ("value", "start", 14, "f-gold")):
        x = X(r[key]["num"])
        out.append(f'<circle class="{cls}" cx="{_f(x)}" cy="{y}" r="12"/>')
        out.append(text(x + dx, y - 64, lab[key], "axis-t", anchor))
        out.append(text(x + dx, y - 34, _short(r[key]["fmt"]), "val", anchor))
    # abaixo do eixo: cenários
    for key in ("adverse", "rates", "favorable"):
        if r[key].get("num") is None:
            continue
        x = X(r[key]["num"])
        out.append(f'<line class="s-tick" x1="{_f(x)}" y1="{y + 10}" x2="{_f(x)}" y2="{y + 50}"/>')
        out.append(text(x, y + 80, _short(r[key]["fmt"]), "val small"))
        out.append(text(x, y + 106, lab[key], "axis-t"))
    return svg(w, h, "".join(out), "Régua de preço, limite de compra, valor-base e cenários da Sanepar")


# ---------------- molduras ----------------------------------------------------------------------
def _head(p):
    sub = f'<p class="subtitle">{E(p["subtitle"])}</p>' if p["subtitle"] else ""
    return f'<header class="head"><div class="kicker">{E(p["kicker"])}</div><h1 class="title">{E(p["title"])}</h1>{sub}</header>'


def _frame(p, n, cls, body):
    src = f'<p class="sources">Fontes: {E(p["source_line"])}</p>' if p["source_line"] else '<p class="sources"></p>'
    return (f'<section class="slide" id="p{n}" data-page="{p["id"]}" aria-label="{E(p["title"])}">{_head(p)}'
            f'<div class="body {cls}">{body}</div>{src}'
            f'<footer class="foot"><span class="wordmark">asset.dev{symbol()}</span><span>{E(CTX)}</span><span class="pg">{n}</span></footer></section>')


def _steps(steps, gold_last=False):
    out = []
    for i, s in enumerate(steps, 1):
        g = " gold" if gold_last and i == len(steps) else ""
        out.append(f'<div class="step"><span class="step-n{g}">{i}</span><div><h4>{E(s["title"])}</h4><p>{E(s["text"])}</p></div></div>')
    return '<div class="steps">' + "".join(out) + "</div>"


# ---------------- slides ------------------------------------------------------------------------
def s_cover(p, n, model):
    head, _, rest = p["title"].partition(": ")
    title = f"{E(head)}:<br><em>{E(rest)}</em>" if rest else E(p["title"])
    return (f'<section class="slide cover" id="p{n}" data-page="{p["id"]}" aria-label="{E(p["title"])}">'
            f'<div class="wordmark">asset.dev{symbol()}</div>'
            f'<div class="center"><div class="kicker">{E(p["kicker"])}</div><h1 class="title">{title}</h1><p class="subtitle">{E(p["subtitle"])}</p></div>'
            f'<div class="bottom"><span>{E(p["team"])}</span><span>{E(p["tickers"])}</span></div></section>')


def s_origin(p, n, model):
    chart = (f'<div class="card"><div class="chart-head"><h3>{E(p["chart_title"])}</h3></div>'
             + legend([(p["legend"]["view"], "compare"), (p["legend"]["model"], "gold")]) + '<div style="height:18px"></div>'
             + chart_origin(p["stocks"], 840) + "</div>")
    stat = (f'<div class="card gold stat"><div class="big">{E(p["stat"]["fmt"])}</div><div class="txt">{E(p["stat_text"])}</div>'
            f'<div class="why"><b>{E(p["reason_label"])}:</b> “{E(p["reason"])}”</div></div>')
    return _frame(p, n, "b-origin", chart + f'<div class="side">{stat}{_steps(p["steps"], True)}</div>')


def s_question(p, n, model):
    cards = "".join(f'<div class="card"><span class="n">{i:02d}</span><h3>{E(s["title"])}</h3><p>{E(s["text"])}</p></div>'
                    for i, s in enumerate(p["steps"], 1))
    qs = "".join(f"<li>{E(q)}</li>" for q in p["questions"])
    return _frame(p, n, "b-question", f'<div class="qsteps">{cards}</div><div class="card gold questions"><div class="label gold">{E(p["questions_label"])}</div><ol>{qs}</ol></div>')


def s_sector(p, n, model):
    groups = [(b["label"], [b["value"], b["target"]]) for b in p["bars"]]
    chart = (f'<div><div class="chart-head"><h3>{E(p["chart_title"])}</h3></div>'
             + legend([(p["legend"][0], "gold"), (p["legend"][1], "compare")])
             + chart_grouped(groups, 820, 470, 1.0, ["f-gold", "f-cmp"], p["chart_title"])
             + f'<p class="note" style="margin-top:14px">{E(p["note"])}</p></div>')
    cos = "".join(f'<div class="card co"><div class="nm">{E(c["name"])}<small>{E(c["ticker"])}</small></div>'
                  f'<div class="px">{E(c["price"]["fmt"])}<small>preço em 30/10</small></div>'
                  f'<div class="l1">{E(c["line1"])}</div><div class="l2">{E(c["line2"])}</div></div>' for c in p["companies"])
    return _frame(p, n, "b-sector", chart + f'<div><div class="label" style="margin-bottom:16px">{E(p["companies_label"])}</div><div class="companies">{cos}</div></div>')


def s_swot(p, n, model):
    quads = "".join(f'<div class="card quad"><h3><span class="letter">{E(q["id"])}</span>{E(q["label"])}</h3>'
                    f'<ul>{"".join(f"<li>{E(b)}</li>" for b in q["bullets"])}</ul><p class="eff">{E(q["effect"])}</p></div>' for q in p["quadrants"])
    return _frame(p, n, "b-swot", quads)


def s_medium(p, n, model):
    cards = "".join(f'<div class="card mcard"><div class="label gold">{i:02d} · {E(c["label"])}</div><div class="big">{E(c["big"]["fmt"])}</div>'
                    f'<div class="bl">{E(c["big_label"])}</div><p class="tx">{E(c["text"])}</p><p class="eff">{E(c["effect"])}</p></div>'
                    for i, c in enumerate(p["cards"], 1))
    return _frame(p, n, "b-medium", cards)


def s_matrix(p, n, model):
    names = model["entity_names"]
    head = "".join(f'<th{" class=e" if i > 1 else ""}>{E(c)}</th>' for i, c in enumerate(p["columns"]))
    rows = []
    for r in p["rows"]:
        cells = "".join(f'<td><div class="cv{" gap" if r["cells"][e]["gap"] else ""}">{E(r["cells"][e]["main"])}</div>'
                        f'<div class="cs">{E(r["cells"][e]["sub"])}</div></td>' for e in model["order"])
        rows.append(f'<tr><td><div class="fx"><span class="letter">{E(r["letter"])}</span>{E(r["factor"])}</div></td>'
                    f'<td class="ch">{E(r["channel"])}</td>{cells}</tr>')
    assert [names[e] for e in model["order"]] == p["columns"][2:], "colunas da matriz fora da ordem das empresas"
    table = (f'<table class="mx"><colgroup><col class="f"><col class="c"><col><col><col></colgroup><thead><tr>{head}</tr></thead>'
             f'<tbody>{"".join(rows)}</tbody></table>')
    return _frame(p, n, "b-matrix", f'<div>{table}</div><p class="note">{E(p["note"])}</p>')


def s_esg_value(p, n, model):
    chain = []
    for i, c in enumerate(p["chain"]):
        if i:
            chain.append('<div class="link"></div>')
        chain.append(f'<div class="card{" gold" if i == len(p["chain"]) - 1 else ""}"><h4>{E(c["title"])}</h4><p>{E(c["text"])}</p></div>')
    groups = [(e["name"], [dict(e["r50"], label=_short(e["r50"]["fmt"])), dict(e["r100"], label=_short(e["r100"]["fmt"]))]) for e in p["energy"]]
    ymax = max(e["r100"]["num"] for e in p["energy"]) * 1.12
    chart = (f'<div class="card"><div class="chart-head"><h3>{E(p["chart_title"])}</h3></div>'
             + legend([(p["legend"][0], "gold-dim"), (p["legend"][1], "gold")])
             + chart_grouped(groups, 880, 460, ymax, ["f-gold2", "f-gold"], p["chart_title"])
             + f'<p class="note" style="margin-top:12px">{E(p["note"])}</p></div>')
    return _frame(p, n, "b-esgv", f'<div class="chain">{"".join(chain)}</div>' + chart)


def s_calc(p, n, model):
    left = (f'<div class="card"><div class="label gold">{E(p["r1_title"])}</div><p class="sub">{E(p["r1_sub"])}</p>'
            + '<div style="height:18px"></div>' + chart_hbar_ref(p["r1"], 1.0, "R$ 1,00", 620, p["r1_title"], 1.3)
            + f'<p class="rn">{E(p["r1_note"])}</p></div>')
    params = "".join(f'<div><b>{E(x["fmt"])}</b><span>{E(x["text"])}</span></div>' for x in p["params"])
    right = (f'<div class="card"><div class="label gold">{E(p["bridge_title"])}</div>'
             + chart_waterfall(p["bridge"], 940, 440, p["bridge_title"])
             + f'<p class="note">{E(p["bridge_note"])}</p><div class="params">{params}</div></div>')
    return _frame(p, n, "b-calc", left + right)


def s_tir(p, n, model):
    how = f'<div class="card how"><div class="label gold">Como calculamos</div>{_steps(p["steps"], True)}</div>'
    ref = [p["wacc_label"], p["wacc"]["fmt"]]
    chart = (f'<div class="card"><div class="label gold">{E(p["chart_title"])}</div><div style="height:10px"></div>'
             + chart_vbar_ref(p["implied"], p["wacc"]["num"], [ref[1], ref[0]], 960, 330, p["chart_title"]) + "</div>")
    cards = "".join(f'<div class="card"><h4><span class="letter">{E(c["letter"])}</span>{E(c["title"])}</h4><p>{E(c["text"])}</p></div>' for c in p["esg"])
    return _frame(p, n, "b-tir", how + chart + f'<div class="esgrow"><div class="label">{E(p["esg_label"])}</div><div class="cards">{cards}</div></div>')


def s_value_price(p, n, model):
    groups = [(f'{r["name"]} · {r["ticker"]}', [r["value"], r["price"]]) for r in p["rows"]]
    ymax = max(max(x["num"] or 0 for x in (r["value"], r["price"])) for r in p["rows"]) * 1.15
    chart = (f'<div><div class="chart-head"><h3>{E(p["chart_title"])}</h3></div>' + legend([(p["legend"][0], "gold"), (p["legend"][1], "compare")])
             + chart_grouped(groups, 960, 520, ymax, ["f-gold", "f-cmp"], p["chart_title"], small=True, bw=120) + "</div>")
    ups = []
    for r in p["rows"]:
        up = r["upside"]
        cls = "" if up is None else (" pos" if up["num"] > 0 else " neg")
        hl = " gold" if r["entity"] == model["decision_entity"] else ""
        ups.append(f'<div class="card up{hl}"><span class="nm">{E(r["name"])}<small>{E(r["ticker"])}</small></span>'
                   f'<span class="v{cls}">{E(up["fmt"] if up else "N/D")}</span></div>')
    week = "".join(f'<tr><td>{E(w["name"])}<small>{E(w["ticker"])}</small></td><td class="num">{E(w["pre"]["fmt"])}</td>'
                   f'<td class="num">{E(w["post"]["fmt"])}</td><td class="num neg">{E(w["change"]["fmt"])}</td></tr>' for w in p["week"])
    week = (f'<div class="week"><div class="label">{E(p["week_label"])}</div><table><thead><tr><th></th><th>23/10</th><th>30/10</th><th>Variação</th></tr>'
            f'</thead><tbody>{week}</tbody></table><p class="note">{E(p["week_note"])}</p></div>')
    side = (f'<div><div class="label">{E(p["upside_label"])}</div><div class="ups">{"".join(ups)}</div>{week}'
            f'<p class="gridnote">{_bold_last_money(p["grid_note"], p["grid"]["worst"]["fmt"])}</p></div>')
    return _frame(p, n, "b-value", chart + side)


def _bold_last_money(note: str, money: str) -> str:
    esc = E(note)
    return esc.replace(E(money), f"<b>{E(money)}</b>", 1)


def s_conclusion(p, n, model):
    r = p["ruler"]
    ruler = f'<div class="card"><div class="label gold">{E(r["title"])}</div><div style="height:6px"></div>{chart_ruler(r, 860)}</div>'
    trig = "".join(f'<div><b>{E(t["label"])}.</b>{E(t["text"])}</div>' for t in p["triggers"])
    trig = f'<div class="card"><div class="label gold">{E(p["triggers_title"])}</div><div class="trig">{trig}</div></div>'
    closing = "".join(f'<div class="card{" gold" if c["highlight"] else ""}"><h4>{E(c["name"])}</h4><p>{E(c["text"])}</p></div>' for c in p["closing"])
    return _frame(p, n, "b-conc", ruler + trig + f'<div class="closing">{closing}</div>')


RENDER = {"cover": s_cover, "origin": s_origin, "question": s_question, "sector": s_sector, "swot": s_swot, "medium": s_medium,
          "matrix": s_matrix, "esg_value": s_esg_value, "calc": s_calc, "tir": s_tir, "value_price": s_value_price, "conclusion": s_conclusion}


def render(model: dict) -> str:
    if len(model["pages"]) != TOTAL:
        raise ValueError(f"O deck final tem {TOTAL} páginas; o modelo trouxe {len(model['pages'])}")
    return "\n".join(RENDER[p["kind"]](p, i, model) for i, p in enumerate(model["pages"], 1))
