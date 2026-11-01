"""EN03 — modelo de visões/páginas a partir do pacote 1.0 (sem matemática financeira nova).

Cada página guarda textos já resolvidos, dados de gráfico (número + rótulo formatado + value_id),
claims, value_ids usados e fontes, para HTML10, PPTX9 e figuras usarem exatamente os mesmos dados.
"""
from __future__ import annotations

from . import content as K
from . import labels as L
from .consumer import Bundle, IncompatibleState, format_value

ENT = ["sanepar", "sabesp", "copasa"]  # ordem fixa de cor: slot 1, 2, 3
TICKER = {"sanepar": "SAPR11", "sabesp": "SBSP3", "copasa": "CSMG3"}


class Page:
    def __init__(self, b: Bundle, spec: dict):
        self.b, self.spec, self.used, self.claims = b, spec, set(), list(spec["claims"])

    def t(self, template: str) -> str:
        return self.b.render(template, self.used)

    def v(self, vid: str, style: str = "") -> dict:
        self.used.add(vid)
        return {"ref": vid, "num": self.b.num(vid), "fmt": self.b.fmt(vid, style)}


def _case_val(pg: Page, case_id: str) -> dict:
    c = pg.b.case(case_id)
    vr = c["value_refs"]
    if c["target_validity"] == "conditional_value":
        out = pg.v(vr["paper_value"])
        out.update(valid=True, case=case_id)
    else:
        out = {"ref": vr.get("equity_residual_before_floor"), "num": None, "fmt": "N/D", "valid": False, "case": case_id,
               "why": "Resíduo acionário não positivo neste caso" if c["target_validity"] == "no_meaningful_target" else "Caso não calculável"}
        if vr.get("equity_residual_before_floor"):
            pg.used.add(vr["equity_residual_before_floor"])
    return out


def build(b: Bundle) -> dict:
    # Deck completo só com decisão proposta/adotada e alvo válido no caso-base da empresa decidida;
    # pacote incompleto continua consumível por --check/QA, mas não gera peça com tese inexistente.
    dec = b.decision.get("entity_id")
    if b.decision.get("status") not in ("proposed", "adopted") or not dec:
        raise IncompatibleState(f"decisão '{b.decision.get('status')}' sem empresa: deck completo indisponível neste estado")
    if f"{dec}.base" not in b.cases or b.case(f"{dec}.base")["target_validity"] != "conditional_value":
        raise IncompatibleState(f"caso-base de {dec} sem alvo exibível: deck completo indisponível")
    pages = []
    for spec in K.PAGES:
        pg = Page(b, spec)
        d = dict(id=spec["id"], kind=spec["kind"], slot=spec["slot"], voice=spec["voice"], seconds=spec["seconds"], block=spec["block"],
                 slide9=spec["slide9"], kicker=spec["kicker"], title=pg.t(spec["title"]), subtitle=pg.t(spec["subtitle"]))
        scr = K.SCREEN.get(spec["id"], {})
        k = spec["kind"]
        if k == "thesis":
            d["hero"] = [dict(label=h["label"], note=h["note"], **pg.v(h["value"], h.get("style", ""))) for h in scr["hero"]]
            d["chips"] = [dict(icon=c["icon"], text=pg.t(c["text"])) for c in scr["chips"]]
            d["source_panel"] = scr["source_panel"]
            d["proposal_badge"] = b.decision["status"] != "adopted"
            d["compare"] = []
            for e in ENT:
                bc = b.case(f"{e}.base")
                d["compare"].append(dict(entity=e, ticker=TICKER[e], value=_case_val(pg, f"{e}.base"), price=pg.v(bc["value_refs"]["price"]),
                                         upside=pg.v(bc["value_refs"]["upside"], "signed1") if "upside" in bc["value_refs"] else None))
        elif k == "sector":
            d["bars"] = [dict(id=x["id"], label=x["label"], value=pg.v(x["value"]), target=pg.v(x["target"])) for x in scr["bars"]]
            d["notes"] = {k2: pg.t(v2) for k2, v2 in scr["notes"].items()}
            d["callout"] = pg.t(scr["callout"])
        elif k == "swot":
            d["quadrants"] = [dict(id=q["id"], label=q["label"], bullets=[pg.t(x) for x in q["bullets"]],
                                   evidence=b.claim_text(q["claim"], pg.used), implication=pg.t(q["implication"]), claim=q["claim"])
                              for q in scr["quadrants"]]
        elif k == "medium":
            d["cards"] = [dict(id=c["id"], label=c["label"], claim=c["claim"], tabs={t: pg.t(x) for t, x in c["tabs"].items()}) for c in scr["cards"]]
        elif k == "matrix":
            rows = []
            for r in b.matrix:
                cells = {}
                for e in ENT:
                    cell = r["cells"].get(e, {"value_refs": [], "text": ""})
                    vals = []
                    for ref in cell["value_refs"]:
                        o = b.obs[ref]
                        dd = b.defs.get(o["definition_id"], {})
                        src = [b.sources[s] for s in b.value_sources(ref) if s in b.sources]
                        vals.append(dict(pg.v(ref), metric=L.metric(o["metric_id"]), period=" a ".join(_br_date(x) for x in (o["period_start"], o["period_end"]) if x),
                                         scope=o["scope"], definition=dd.get("methodology", ""), note=o.get("note", ""),
                                         source=[dict(id=s["source_id"], title=L.source(s), published=s["published_at"]) for s in src],
                                         locator=o.get("source_location", "")))
                    cells[e] = dict(text=cell["text"], values=vals)
                rows.append(dict(id=r["row_id"], factor=r["factor"], channel=r["channel"], value_link=r["value_link"],
                                 comparability=r["comparability"], cells=cells))
            d["rows"] = rows
        elif k == "bridge":
            d["rab"] = [dict(entity=e, **pg.v(f"V.{e}.rab_value_ratio.base")) for e in ENT]
            d["energy"] = {str(r): [dict(entity=e, **pg.v(f"V.case.{e}.energy.r{r}.capex_break_even", "precise"),
                                         case=f"{e}.energy.r{r}", per_share=pg.v(f"V.case.{e}.energy.r{r}.value_per_share"))
                                    for e in ENT] for r in (50, 100)}
            d["energy_saving"] = pg.v(scr["energy_saving"])
            d["wacc"] = pg.v("A.wacc_nominal.base")
        elif k == "method":
            comps = {}
            for e in ENT:
                c = b.case(f"{e}.base")
                vr = c["value_refs"]
                items = [("start", "Valor da firma", pg.v(vr["enterprise_value"], "precise"))]
                for key, label in (("net_debt_october_estimate", "Dívida líquida (out/26, estimada)"), ("debt_like", "PPP, derivativos, pensões e outros"),
                                   ("grantor_net", "Poder concedente (líquido do crédito na base)"), ("obligation_pv", "Precatório a valor presente")):
                    item = pg.v(vr[key], "precise")
                    if item["num"]:
                        # Efeito sobre o patrimônio = componente com sinal invertido (apresentação, não cálculo novo).
                        item["effect_num"] = -item["num"]
                        item["effect_fmt"] = format_value(-item["num"], "BRL", 1e6, "precise")
                        if item["effect_num"] > 0:
                            item["effect_fmt"] = "+" + item["effect_fmt"]
                        items.append(("delta", label, item))
                items.append(("end", "Patrimônio do acionista", pg.v(vr["equity_residual_before_floor"], "precise")))
                comps[e] = dict(items=[dict(role=r, label=l, **x) for r, l, x in items],
                                pv_explicit=pg.v(vr["pv_explicit"], "precise"), pv_terminal=pg.v(vr["pv_terminal"], "precise"),
                                terminal_share=pg.v(vr["terminal_share"]), paper=_case_val(pg, f"{e}.base"))
            d["companies"] = comps
            d["params"] = [dict(label=p["label"], **pg.v(p["value"])) for p in scr["params"]]
        elif k == "result":
            res = {}
            for e in ENT:
                grid = [c for c in b.cases.values() if c["entity_id"] == e and c["scenario_id"] == "grid"]
                waccs = sorted({c["wacc"] for c in grid})
                gs = sorted({c["dimensions"]["g_real"]["option_id"] for c in grid}, key=lambda x: int(x[1:]))
                cells = []
                for c in grid:
                    cell = _case_val(pg, c["case_id"])
                    cell.update(wacc=pg.v(c["dimensions"]["wacc"]["value_ref"])["fmt"], g=pg.v(c["dimensions"]["g_real"]["value_ref"])["fmt"],
                                wi=waccs.index(c["wacc"]), gi=gs.index(c["dimensions"]["g_real"]["option_id"]))
                    cells.append(cell)
                base = b.case(f"{e}.base")
                dim_ref = lambda axis, pick: next(c["dimensions"][axis]["value_ref"] for c in grid if pick(c))
                res[e] = dict(price=pg.v(base["value_refs"]["price"]), value=_case_val(pg, f"{e}.base"),
                              upside=pg.v(base["value_refs"]["upside"], "signed1") if "upside" in base["value_refs"] else None,
                              implied=pg.v(b.extras["implied_wacc"][e]), grid=cells,
                              wacc_labels=[pg.v(dim_ref("wacc", lambda c, w=w: c["wacc"] == w))["fmt"] for w in waccs],
                              g_labels=[pg.v(dim_ref("g_real", lambda c, g=g: c["dimensions"]["g_real"]["option_id"] == g))["fmt"] for g in gs],
                              base_wi=waccs.index(base["wacc"]) if base["wacc"] in waccs else None)
            d["companies"] = res
            d["wacc"] = pg.v("A.wacc_nominal.base")
        elif k == "risks":
            sc = {}
            for sid, label in scr["scenarios"]:
                sc[sid] = dict(label=label, note=pg.t(scr["scenario_notes"][sid]),
                               values={e: _case_val(pg, f"{e}.{sid}") for e in ENT})
            d["scenarios"] = sc
            d["prices"] = {e: pg.v(b.case(f"{e}.base")["value_refs"]["price"]) for e in ENT}
            d["triggers"] = [dict(id=t["id"], label=t["label"], metric=t["metric"], limit=pg.t(t["limit"]), when=t["when"], action=t["action"],
                                  claim=t["claim"]) for t in scr["triggers"]]
            d["objection"] = b.claim_text("CL.risk.objection", pg.used)
        elif k == "decision":
            d["points"] = [dict(label=p["label"], text=pg.t(p["text"])) for p in scr["points"]]
            d["proposal_badge"] = b.decision["status"] != "adopted"
            dec = b.decision["entity_id"]
            vr = b.case(f"{dec}.base")["value_refs"]
            d["ladder"] = dict(labels=scr["ladder"], entity=dec, price=pg.v(vr["price"]), limit=pg.v(f"V.{dec}.max_entry_price"),
                               value=pg.v(vr["paper_value"]), margin=pg.v("A.margin_of_safety.base"))
            d["triggers_title"] = scr["triggers_title"]
            d["triggers"] = [dict(id=t["id"], label=t["label"], limit=pg.t(t["limit"]), when=t["when"]) for t in K.SCREEN["P09"]["triggers"]]
        d["claim_texts"] = {cid: b.claim_text(cid, pg.used) for cid in pg.claims}
        srcs = set()
        for cid in pg.claims:
            srcs.update(b.claim_sources(cid))
        for vid in pg.used:
            srcs.update(b.value_sources(vid))
        d["sources"] = sorted([dict(id=s, title=L.source(b.sources[s]), published=b.sources[s]["published_at"],
                                    url=b.sources[s]["url"]) for s in srcs if s in b.sources], key=lambda x: x["title"])
        d["value_refs"] = sorted(pg.used)
        pages.append(d)
    return dict(bundle_id=b.bundle_id, manifest_sha256=b.manifest_sha256, state=b.manifest["state"], decision=b.decision["status"],
                entity_names={e: b.entity_name(e) for e in ENT}, tickers=TICKER, order=ENT, pages=pages,
                valuation_date="30/10/2026", cutoff="31/10/2026 18:25", team="asset.dev")


def placements(model: dict, artifact: str, profile: str, b: Bundle) -> list[dict]:
    rows = []
    for p in model["pages"]:
        page = p["slide9"] if profile == "pptx9" else p["id"]
        for cid in p["claim_texts"]:
            rows.append(dict(artifact=artifact, profile=profile, page=page, block=p["block"], claim_id=cid,
                             value_ids=sorted(set(_tokens(b.claims[cid]["text_template"]))), source_ids=b.claim_sources(cid),
                             input_bundle=model["bundle_id"], input_manifest_sha256=model["manifest_sha256"]))
        rows.append(dict(artifact=artifact, profile=profile, page=page, block=p["block"], claim_id="(screen_values)", value_ids=p["value_refs"],
                         source_ids=[s["id"] for s in p["sources"]], input_bundle=model["bundle_id"], input_manifest_sha256=model["manifest_sha256"]))
    return rows


def _br_date(iso: str) -> str:
    parts = iso.split("-")
    return f"{parts[2]}/{parts[1]}/{parts[0]}" if len(parts) == 3 else iso


def _tokens(t: str) -> list[str]:
    import re
    return re.findall(r"\{\{value:([^}|]+)", t)
