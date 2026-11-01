"""EN03 — figuras PNG/SVG + CSV-fonte a partir do modelo de páginas (mesmos dados do HTML), para o apoio técnico e reuso."""
from __future__ import annotations

import csv
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import ScalarFormatter  # noqa: E402

from .common import writable  # noqa: E402

INK, INK2, MUTED, HAIR, AXIS, SURF = "#0b0b0b", "#52514e", "#6f6d67", "#e1e0d9", "#c3c2b7", "#fcfcfb"
GOLD, GOLD2, GRAY, NEG = "#C9A227", "#8C7420", "#9a9a9f", "#c8453e"  # mesma lógica do deck: ouro = medida principal, cinza = comparação

plt.rcParams.update({"text.parse_math": False, "font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 13, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "svg.fonttype": "none"})


def _wrap(s: str, width: int = 14) -> str:
    return "\n".join(textwrap.wrap(s, width))


class _BR(ScalarFormatter):
    """Eixo numérico em pt-BR: vírgula decimal e ponto de milhar."""

    def __call__(self, x, pos=None):
        s = super().__call__(x, pos)
        try:
            v = float(s.replace("−", "-"))
        except ValueError:
            return s.replace(".", ",")
        if abs(v) >= 1000 and v == int(v):
            return f"{int(v):,}".replace(",", ".").replace("-", "−")
        return s.replace(".", ",")


def _save(fig, out: Path, name: str, rows: list[list], header: list[str]) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    for a in fig.axes:  # rótulos fixos (FixedFormatter) ficam como estão
        for axis in (a.xaxis, a.yaxis):
            if type(axis.get_major_formatter()) is ScalarFormatter:
                axis.set_major_formatter(_BR(useOffset=False))
    paths = []
    for ext in ("png", "svg"):
        p = writable(out / f"{name}.{ext}")
        fig.savefig(p, dpi=200 if ext == "png" else None, bbox_inches="tight")
        paths.append(p)
    plt.close(fig)
    with open(writable(out / f"{name}.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return paths + [out / f"{name}.csv"]


def _kind(model, kind):
    return next(p for p in model["pages"] if p["kind"] == kind)


def _short(fmt: str) -> str:
    return fmt.replace("R$ ", "").replace(" bi", "").replace(" mi", "")


def build(model: dict, out: Path) -> dict:
    made = {}
    # 1. Setor: Brasil 2024 contra metas de 2033
    p = _kind(model, "sector")
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    for k, b in enumerate(p["bars"]):
        ax.bar(k - .2, b["value"]["num"], .38, color=GOLD)
        ax.bar(k + .2, b["target"]["num"], .38, color=GRAY)
        ax.text(k - .2, b["value"]["num"] + .02, b["value"]["fmt"], ha="center", fontsize=11, color=INK)
        ax.text(k + .2, b["target"]["num"] + .02, b["target"]["fmt"], ha="center", fontsize=11, color=INK2)
    ax.set_xticks(range(len(p["bars"])), [b["label"] for b in p["bars"]])
    ax.set_ylim(0, 1.12)
    ax.set_yticks([0, .25, .5, .75, 1], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_title(p["chart_title"], loc="left", fontsize=12, color=INK2)
    made["s04_setor"] = _save(fig, out, "s04_setor", [[b["label"], b["value"]["num"], b["value"]["ref"], b["target"]["num"], b["target"]["ref"]] for b in p["bars"]],
                              ["indicador", "valor", "value_id", "meta", "meta_value_id"])
    # 2. Energia: teto de investimento por retenção do ganho
    p = _kind(model, "esg_value")
    fig, ax = plt.subplots(figsize=(8.6, 3.4))
    for k, e in enumerate(p["energy"]):
        ax.bar(k - .2, e["r50"]["num"], .38, color=GOLD2)
        ax.bar(k + .2, e["r100"]["num"], .38, color=GOLD)
        ax.text(k - .2, e["r50"]["num"] * 1.02, _short(e["r50"]["fmt"]), ha="center", fontsize=11)
        ax.text(k + .2, e["r100"]["num"] * 1.02, _short(e["r100"]["fmt"]), ha="center", fontsize=11)
    ax.set_xticks(range(len(p["energy"])), [e["name"] for e in p["energy"]])
    ax.set_ylabel("R$ milhões")
    ax.set_title(p["chart_title"], loc="left", fontsize=11, color=INK2)
    made["s08_energia"] = _save(fig, out, "s08_energia", [[e["name"], e["r50"]["num"], e["r50"]["ref"], e["r100"]["num"], e["r100"]["ref"]] for e in p["energy"]],
                                ["empresa", "teto_r50", "value_id_r50", "teto_r100", "value_id_r100"])
    # 3. Valor de R$ 1 investido e ponte da firma ao acionista
    p = _kind(model, "calc")
    fig, ax = plt.subplots(figsize=(7, 2.8))
    for k, r in enumerate(p["r1"]):
        y = len(p["r1"]) - 1 - k
        ax.barh(y, r["num"], color=GOLD if r["num"] > 1 else GRAY, height=.6)
        ax.text(r["num"] + .02, y, r["fmt"], va="center", fontsize=12, color=INK)
    ax.axvline(1, color=INK, lw=1.5, ls="--")
    ax.set_yticks(range(len(p["r1"])), [r["name"] for r in reversed(p["r1"])])
    ax.set_xlim(0, 1.35)
    ax.set_title(f"{p['r1_title']} (linha = R$ 1,00)", loc="left", fontsize=12, color=INK2)
    made["s09_valor_por_real"] = _save(fig, out, "s09_valor_por_real", [[r["name"], r["num"], r["ref"]] for r in p["r1"]], ["empresa", "valor_por_real", "value_id"])
    fig, ax = plt.subplots(figsize=(9.5, 4))
    run, rows = 0.0, []
    for k, it in enumerate(p["bridge"]):
        if it["role"] == "start":
            bottom, height, color, run, txt = 0, it["num"], GRAY, it["num"], it["fmt"]
        elif it["role"] == "delta":
            bottom, height, color, txt = run + min(it["effect_num"], 0), abs(it["effect_num"]), NEG, it["effect_fmt"]
            run += it["effect_num"]
        else:
            bottom, height, color, txt = 0, it["num"], GOLD, it["fmt"]
        ax.bar(k, height, bottom=bottom, color=color, width=.6)
        ax.text(k, bottom + height + p["bridge"][0]["num"] * .02, _short(txt), ha="center", fontsize=11, color=INK)
        rows.append([it["label"], it["role"], it.get("effect_num", it["num"]), it["ref"]])
    ax.set_xticks(range(len(p["bridge"])), [_wrap(it["label"]) for it in p["bridge"]], fontsize=10)
    ax.set_ylabel("R$ milhões")
    ax.set_title(p["bridge_title"], loc="left", fontsize=12, color=INK2)
    made["s09_ponte_valor"] = _save(fig, out, "s09_ponte_valor", rows, ["componente", "papel", "valor", "value_id"])
    # 4. Valor contra preço
    p = _kind(model, "value_price")
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    rows = []
    for k, r in enumerate(p["rows"]):
        v, pr = r["value"]["num"], r["price"]["num"]
        if v is not None:
            ax.bar(k - .2, v, .38, color=GOLD)
        ax.bar(k + .2, pr, .38, color=GRAY)
        ax.text(k - .2, (v or 0) + 1, r["value"]["fmt"], ha="center", fontsize=10)
        ax.text(k + .2, pr + 1, r["price"]["fmt"], ha="center", fontsize=10, color=INK2)
        rows.append([r["name"], v if v is not None else "", r["value"]["ref"] or "", pr, r["price"]["ref"], r["upside"]["num"] if r["upside"] else ""])
    ax.set_xticks(range(len(p["rows"])), [f"{r['name']} · {r['ticker']}" for r in p["rows"]])
    ax.set_ylabel("R$ por ação ou unit")
    ax.set_title(p["chart_title"], loc="left", fontsize=11, color=INK2)
    made["s11_valor_preco"] = _save(fig, out, "s11_valor_preco", rows, ["empresa", "valor", "value_id", "preco", "preco_value_id", "potencial"])
    # 5. Grade custo de capital × crescimento real (empresa decidida)
    import numpy as np
    g = p["grid"]
    dec_row = next(r for r in p["rows"] if r["entity"] == model["decision_entity"])
    price = dec_row["price"]["num"]
    wv = sorted({c["wacc"]["num"] for c in g["cells"]})
    gv = sorted({c["g"]["num"] for c in g["cells"]})
    grid = np.full((len(gv), len(wv)), np.nan)
    for c in g["cells"]:
        grid[gv.index(c["g"]["num"]), wv.index(c["wacc"]["num"])] = (c["num"] / price - 1) if c["num"] is not None else np.nan
    fig, ax = plt.subplots(figsize=(8.6, 3))
    ax.imshow(grid, cmap="RdBu", vmin=-.6, vmax=.6, aspect="auto")
    for c in g["cells"]:
        ax.text(wv.index(c["wacc"]["num"]), gv.index(c["g"]["num"]), c["fmt"], ha="center", va="center", fontsize=12, fontweight="bold",
                color="white" if c["num"] is not None and abs(c["num"] / price - 1) > .33 else INK)
    lab = lambda axis, x: next(c[axis]["fmt"] for c in g["cells"] if c[axis]["num"] == x)
    ax.set_xticks(range(len(wv)), [f"WACC {lab('wacc', w)}" for w in wv])
    ax.set_yticks(range(len(gv)), [f"g real {lab('g', x)}" for x in gv])
    name = model["entity_names"][model["decision_entity"]]
    ax.set_title(f"{name}: valor por custo de capital × crescimento real (preço {dec_row['price']['fmt']}; azul = acima)", loc="left", fontsize=12, color=INK2)
    for sp in ax.spines.values():
        sp.set_visible(False)
    made["s11_grade"] = _save(fig, out, "s11_grade", [[c["wacc"]["fmt"], c["g"]["fmt"], c["num"], c["ref"], c["case"]] for c in g["cells"]],
                              ["wacc", "g_real", "valor", "value_id", "case_id"])
    # 6. Régua de compra e cenários
    p = _kind(model, "conclusion")
    R, lab = p["ruler"], p["ruler"]["labels"]
    keys = [k for k in ("adverse", "price", "rates", "limit", "value", "favorable") if R[k].get("num") is not None]
    fig, ax = plt.subplots(figsize=(8.6, 2.2))
    lo, hi = min(R[k]["num"] for k in keys) * .85, max(R[k]["num"] for k in keys) * 1.05
    ax.plot([lo, hi], [0, 0], color=AXIS, lw=2)
    ax.plot([lo, R["limit"]["num"]], [0, 0], color=GOLD, lw=6, alpha=.5)
    for k in keys:
        up = k in ("price", "limit", "value")
        ax.scatter([R[k]["num"]], [0], s=70, color=INK if k == "price" else (GOLD if up else GRAY), zorder=3)
        ax.text(R[k]["num"], .35 if up else -.35, f"{lab[k]}\n{_short(R[k]['fmt'])}", ha="center", va="bottom" if up else "top", fontsize=9.5)
    ax.set_ylim(-1.2, 1.2)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_title(R["title"], loc="left", fontsize=11, color=INK2)
    made["s12_regua"] = _save(fig, out, "s12_regua", [[lab[k], R[k]["num"], R[k]["ref"]] for k in keys], ["marco", "valor", "value_id"])
    return made
