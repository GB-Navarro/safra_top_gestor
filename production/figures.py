"""EN03 — figuras PNG/SVG + CSV-fonte a partir do modelo de páginas (mesmos dados do HTML)."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import ScalarFormatter  # noqa: E402

from .common import writable  # noqa: E402

INK, INK2, MUTED, HAIR, AXIS, SURF = "#0b0b0b", "#52514e", "#6f6d67", "#e1e0d9", "#c3c2b7", "#fcfcfb"
COLOR = {"sanepar": "#2a78d6", "sabesp": "#eb6834", "copasa": "#1baf7a"}
NAVY, DELTA = "#0d366b", "#b9b7ae"
import textwrap  # noqa: E402

plt.rcParams.update({"text.parse_math": False, "font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 13, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "svg.fonttype": "none"})


def _t(s: str) -> str:
    """Escapa '$' para o matplotlib não interpretar 'R$ … R$' como fórmula."""
    return str(s).replace("$", r"\$")


def _wrap(s: str, width: int = 14) -> str:
    return "\n".join(textwrap.wrap(s, width))


class _BR(ScalarFormatter):
    """Eixo numérico em pt-BR: vírgula decimal e ponto de milhar."""

    def __call__(self, x, pos=None):
        s = super().__call__(x, pos)
        try:
            v = float(s.replace("\u2212", "-"))
        except ValueError:
            return s.replace(".", ",")
        if abs(v) >= 1000 and v == int(v):
            return f"{int(v):,}".replace(",", ".").replace("-", "\u2212")
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


def _page(model, pid):
    return next(p for p in model["pages"] if p["id"] == pid)


def build(model: dict, out: Path) -> dict:
    names = model["entity_names"]
    made = {}
    # 1. Setor
    p = _page(model, "P02")
    fig, ax = plt.subplots(figsize=(8.6, 3.2))
    for k, b in enumerate(p["bars"]):
        y = 1 - k
        ax.barh(y, 1, color=HAIR, height=.55)
        ax.barh(y, b["value"]["num"], color=NAVY, height=.55)
        ax.text(b["value"]["num"] - .015, y, b["value"]["fmt"], ha="right", va="center", color="white", fontsize=15, fontweight="bold")
        ax.plot([b["target"]["num"]] * 2, [y - .38, y + .38], color=INK, lw=2.5)
        ax.text(b["target"]["num"] - .01, y + .42, f"Meta 2033: {b['target']['fmt']}", ha="right", va="bottom", color=INK2, fontsize=11)
    ax.set_yticks([1, 0], [b["label"] for b in p["bars"]])
    ax.set_xlim(0, 1)
    ax.set_xticks([0, .25, .5, .75, 1], ["0%", "25%", "50%", "75%", "100%"])
    ax.tick_params(axis="y", length=0, labelsize=13, labelcolor=INK)
    ax.set_title("Brasil, ano-base 2024 — % da população total", loc="left", fontsize=13, color=INK2)
    made["s02_setor"] = _save(fig, out, "s02_setor", [[b["label"], b["value"]["num"], b["value"]["ref"], b["target"]["num"], b["target"]["ref"]] for b in p["bars"]],
                              ["indicador", "valor", "value_id", "meta", "meta_value_id"])
    # 2. Ponte ESG: valor de R$ 1 investido + teto de energia (50%)
    p = _page(model, "P06")
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.6), gridspec_kw={"wspace": .45})
    order = model["order"]
    ax = axs[0]
    rab = {r["entity"]: r for r in p["rab"]}
    for k, e in enumerate(order):
        ax.barh(len(order) - 1 - k, rab[e]["num"], color=COLOR[e], height=.6)
        ax.text(rab[e]["num"] + .02, len(order) - 1 - k, rab[e]["fmt"], va="center", fontsize=12, color=INK, fontweight="bold")
    ax.axvline(1, color=INK, lw=1.8)

    ax.set_yticks(range(len(order)), [names[e] for e in reversed(order)])
    ax.set_xlim(0, max(1.2, max(r["num"] for r in p["rab"]) * 1.15))
    ax.set_title(f"Valor de R$ 1 investido (WACC {p['wacc']['fmt']}; linha = R$ 1,00)", loc="left", fontsize=12, color=INK2)
    ax.tick_params(axis="y", length=0, labelcolor=INK)
    ax = axs[1]
    en = {r["entity"]: r for r in p["energy"]["50"]}
    en100 = {r["entity"]: r for r in p["energy"]["100"]}
    for k, e in enumerate(order):
        ax.barh(len(order) - 1 - k, en100[e]["num"], color=COLOR[e], alpha=.35, height=.6)
        ax.barh(len(order) - 1 - k, en[e]["num"], color=COLOR[e], height=.6)
        ax.text(en100[e]["num"] * 1.02, len(order) - 1 - k, f"{en[e]['fmt']} a {en100[e]['fmt']}", va="center", fontsize=11, color=INK)
    ax.set_yticks(range(len(order)), [names[e] for e in reversed(order)])
    ax.set_xlim(0, max(r["num"] for r in p["energy"]["100"]) * 1.7)
    ax.set_title(f"Teto de investimento por {p['energy_saving']['fmt']} de economia de energia (retenção 50% → 100%)", loc="left", fontsize=12, color=INK2)
    ax.tick_params(axis="y", length=0, labelcolor=INK)
    made["s06_ponte_esg"] = _save(fig, out, "s06_ponte_esg",
                                  [[names[e], rab[e]["num"], rab[e]["ref"], en[e]["num"], en[e]["ref"], en100[e]["num"], en100[e]["ref"]] for e in order],
                                  ["empresa", "valor_por_real", "value_id", "teto_r50", "value_id_r50", "teto_r100", "value_id_r100"])
    # 3. Ponte da firma ao acionista (Sanepar)
    p = _page(model, "P07")
    e = order[0]
    comp = p["companies"][e]
    fig, ax = plt.subplots(figsize=(9.5, 4))
    run = 0
    rows = []
    for k, it in enumerate(comp["items"]):
        if it["role"] == "start":
            bottom, height, color, run, txt = 0, it["num"], COLOR[e], it["num"], it["fmt"]
        elif it["role"] == "delta":
            bottom, height, color, txt = run + min(it["effect_num"], 0), abs(it["effect_num"]), DELTA, it["effect_fmt"]
            run += it["effect_num"]
        else:
            bottom, height, color, txt = 0, it["num"], COLOR[e], it["fmt"]
        ax.bar(k, height, bottom=bottom, color=color, width=.6)
        ax.text(k, bottom + height + comp["items"][0]["num"] * .02, txt.replace(" mi", ""), ha="center", fontsize=11, color=INK, fontweight="bold")
        rows.append([it["label"], it["role"], it.get("effect_num", it["num"]), it["ref"]])
    ax.set_xticks(range(len(comp["items"])), [_wrap(it["label"]) for it in comp["items"]], fontsize=10)
    ax.set_ylabel("R$ milhões")
    ax.set_title(f"{names[e]}: da firma ao acionista (30/10/2026)", loc="left", fontsize=12, color=INK2)
    made["s07_ponte_valor"] = _save(fig, out, "s07_ponte_valor", rows, ["componente", "papel", "valor", "value_id"])
    # 4. Valor vs preço
    p = _page(model, "P08")
    fig, ax = plt.subplots(figsize=(8.6, 3.3))
    rows = []
    for k, e in enumerate(order):
        c = p["companies"][e]
        y = len(order) - 1 - k
        v, pr = c["value"]["num"], c["price"]["num"]
        ax.plot([min(v, pr), max(v, pr)], [y, y], color=COLOR[e], lw=3, zorder=1)
        ax.scatter([pr], [y], marker="D", s=90, color=INK, zorder=3)
        ax.scatter([v], [y], s=140, color=COLOR[e], edgecolor=SURF, linewidth=2, zorder=4)
        ax.text(v, y + .22, c["value"]["fmt"], ha="center", fontsize=11, color=INK, fontweight="bold")
        ax.text(pr, y - .38, c["price"]["fmt"], ha="center", fontsize=10, color=INK2)
        if c["upside"]:
            ax.text(1.01, y, c["upside"]["fmt"], transform=ax.get_yaxis_transform(), va="center", fontsize=12, fontweight="bold", color=INK)
        rows.append([names[e], v, c["value"]["ref"], pr, c["price"]["ref"], c["upside"]["num"] if c["upside"] else ""])
    ax.set_yticks(range(len(order)), [names[e] for e in reversed(order)])
    ax.tick_params(axis="y", length=0, labelcolor=INK)
    ax.set_xlim(0, max(max(r[1], r[3]) for r in rows) * 1.15)
    ax.set_ylim(-.7, len(order) - .4)
    ax.set_xlabel("R$ por ação/unit — ● valor no caso-base   ◆ preço de 30/10/2026")
    ax.grid(axis="x", color=HAIR)
    made["s08_valor_preco"] = _save(fig, out, "s08_valor_preco", rows, ["empresa", "valor", "value_id", "preco", "preco_value_id", "potencial"])
    # 5. Grade da empresa recomendada
    c = p["companies"][e := order[0]]
    import numpy as np
    grid = np.full((len(c["g_labels"]), len(c["wacc_labels"])), np.nan)
    for cell in c["grid"]:
        grid[cell["gi"], cell["wi"]] = (cell["num"] / c["price"]["num"] - 1) if cell["num"] is not None else np.nan
    fig, ax = plt.subplots(figsize=(8.6, 3))
    ax.imshow(grid, cmap="RdBu", vmin=-.6, vmax=.6, aspect="auto")
    for cell in c["grid"]:
        ax.text(cell["wi"], cell["gi"], cell["fmt"], ha="center", va="center", fontsize=12, fontweight="bold",
                color="white" if cell["num"] is not None and abs(cell["num"] / c["price"]["num"] - 1) > .33 else INK)
    ax.set_xticks(range(len(c["wacc_labels"])), [f"WACC {w}" for w in c["wacc_labels"]])
    ax.set_yticks(range(len(c["g_labels"])), [f"g real {g}" for g in c["g_labels"]])
    ax.set_title(f"{names[e]}: valor por WACC × crescimento real (preço {c['price']['fmt']}; azul = acima)", loc="left", fontsize=12, color=INK2)
    for sp in ax.spines.values():
        sp.set_visible(False)
    made["s08_grade"] = _save(fig, out, "s08_grade", [[cell["wacc"], cell["g"], cell["num"], cell["ref"], cell["case"]] for cell in c["grid"]],
                              ["wacc", "g_real", "valor", "value_id", "case_id"])
    # 6. Cenários
    p = _page(model, "P09")
    fig, ax = plt.subplots(figsize=(9.5, 3.6))
    sids = list(p["scenarios"])
    width = .25
    rows = []
    for j, e in enumerate(order):
        xs = [k + (j - 1) * width for k in range(len(sids))]
        vals = [p["scenarios"][s]["values"][e]["num"] for s in sids]
        ax.bar([x for x, v in zip(xs, vals) if v is not None], [v for v in vals if v is not None], width=width * .9, color=COLOR[e], label=names[e])
        for x, v, s in zip(xs, vals, sids):
            lab = p["scenarios"][s]["values"][e]["fmt"]
            ax.text(x, (v or 0) + 1, lab.replace("R$ ", ""), ha="center", fontsize=9, color=INK)
            rows.append([s, names[e], v if v is not None else "", lab, p["scenarios"][s]["values"][e]["ref"] or ""])
        for x in xs:
            ax.plot([x - width * .5, x + width * .5], [p["prices"][e]["num"]] * 2, color=INK, lw=2)
    ax.set_xticks(range(len(sids)), [p["scenarios"][s]["label"] for s in sids])
    ax.set_ylabel("R$ por ação/unit")
    ax.legend(frameon=False, ncol=3, loc="upper left")
    ax.set_title("Valor por cenário (barras) e preço de 30/10 (traço preto); N/D = resíduo negativo", loc="left", fontsize=11, color=INK2)
    made["s09_cenarios"] = _save(fig, out, "s09_cenarios", rows, ["cenario", "empresa", "valor", "rotulo", "value_id"])
    # 7. Régua de compra (decisão)
    p = _page(model, "P10")
    L, lab = p["ladder"], p["ladder"]["labels"]
    lo, hi = (L["price"]["num"] * .7 // 10) * 10, -(-L["value"]["num"] * 1.12 // 10) * 10
    fig, ax = plt.subplots(figsize=(6.4, 2.0))
    ax.barh(0, hi - lo, left=lo, height=.5, color=HAIR)
    ax.barh(0, L["limit"]["num"] - lo, left=lo, height=.5, color="#dde6f3")
    ax.text(lo + (hi - lo) * .02, 0, lab["buy"], va="center", fontsize=11, color=NAVY, fontweight="bold")
    ax.text((L["limit"]["num"] + L["value"]["num"]) / 2, 0, L["margin"]["fmt"], ha="center", va="center", fontsize=10, color=INK2)
    ax.plot([L["limit"]["num"]] * 2, [-.4, .4], color=NAVY, lw=2.5)
    ax.scatter([L["value"]["num"]], [0], s=180, color=COLOR[L["entity"]], zorder=3, edgecolors=SURF, linewidths=2)
    ax.scatter([L["price"]["num"]], [0], s=150, marker="D", color=INK, zorder=3, edgecolors=SURF, linewidths=1.5)
    for k, y, va in (("limit", .5, "bottom"), ("value", .5, "bottom"), ("price", -.5, "top")):  # nome e valor em duas linhas
        ax.text(L[k]["num"], y, lab[k] + "\n" + L[k]["fmt"], ha="center", va=va, fontsize=10.5, color=INK, linespacing=1.3)
    ax.set_xlim(lo, hi)
    ax.set_ylim(-1.45, 1.45)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xticks(range(int(lo), int(hi) + 1, 10), [f"R$ {v}" for v in range(int(lo), int(hi) + 1, 10)], fontsize=10)
    made["s10_faixa_compra"] = _save(fig, out, "s10_faixa_compra", [[lab[k], L[k]["num"], L[k]["ref"]] for k in ("price", "limit", "value")],
                                     ["marco", "valor", "value_id"])
    return made
