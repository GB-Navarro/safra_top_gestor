"""EN03 — modelo das 12 páginas da apresentação final a partir do pacote 1.0 (sem matemática financeira nova).

Cada página guarda textos já resolvidos, dados de gráfico (número + rótulo formatado + value_id), afirmações,
value_ids usados e fontes; HTML, PDF, PPTX, figuras e roteiro leem exatamente os mesmos dados. As relações que
os títulos e as falas afirmam (quem rende acima do custo de capital, quem fica acima do preço) são conferidas
contra o pacote: se deixarem de valer, o deck é recusado em vez de exibir texto falso.
"""
from __future__ import annotations

import re

from . import content as K
from . import labels as L
from .consumer import Bundle, IncompatibleState, format_value

ENT = ["sanepar", "sabesp", "copasa"]  # ordem fixa nas tabelas e gráficos
TICKER = {"sanepar": "SAPR11", "sabesp": "SBSP3", "copasa": "CSMG3"}
PROFILE = "deck12"
OWN_CALC = "Cálculos asset.dev (pacote analítico)"


class Page:
    def __init__(self, b: Bundle, spec: dict):
        self.b, self.spec, self.used, self.claims = b, spec, set(), list(spec["claims"])
        self.inputs: set[str] = set()  # insumos não exibidos cuja fonte entra no rodapé

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


def _paper(b: Bundle, case_id: str) -> float | None:
    c = b.cases.get(case_id)
    return c["paper_value"] if c and c["target_validity"] == "conditional_value" else None


def guards(b: Bundle) -> list[str]:
    """Relações afirmadas no texto do deck; devolve as que o pacote não sustenta."""
    n = b.num
    price = {e: n(b.case(f"{e}.base")["value_refs"]["price"]) for e in ENT}
    val = lambda e, s: _paper(b, f"{e}.{s}")
    below = lambda e, s: val(e, s) is None or val(e, s) < price[e]  # sem alvo exibível = não alcança o preço
    wacc = n("A.wacc_nominal.base")
    implied = {e: n(b.extras["implied_wacc"][e]) for e in ENT}
    ratio = {e: n(f"V.{e}.rab_value_ratio.base") for e in ENT}
    capex = {e: n(f"V.{e}.capex_cash.2025") for e in ENT}
    grid = [_paper(b, c["case_id"]) for c in b.cases.values() if c["entity_id"] == "sanepar" and c["scenario_id"] == "grid"]
    rates = val("sanepar", "rates_up")
    checks = [
        ("decisão proposta é Sanepar (texto escrito para ela)", b.decision.get("entity_id") == "sanepar"),
        ("S10: só a Sanepar tem TIR da firma acima do custo de capital", implied["sanepar"] > wacc > max(implied["sabesp"], implied["copasa"])),
        ("S05/S09/S12: só na Copasa R$ 1 investido vale mais de R$ 1", ratio["copasa"] > 1 > max(ratio["sanepar"], ratio["sabesp"])),
        ("S11: Sanepar acima do preço em toda a grade", bool(grid) and all(v is not None and v > price["sanepar"] for v in grid)),
        ("S11/S12: Sabesp e Copasa abaixo do preço no caso-base", below("sabesp", "base") and below("copasa", "base")),
        ("S12: Sabesp só alcança o preço no cenário favorável",
         not below("sabesp", "favorable") and below("sabesp", "rates_up") and below("sabesp", "execution_adverse")),
        ("S12: Copasa abaixo do preço até no cenário favorável", below("copasa", "favorable")),
        ("S12: com juros mais altos a Sanepar fica perto do preço", rates is not None and abs(rates / price["sanepar"] - 1) < .1),
        ("S12: o cenário adverso da Sanepar fica abaixo do preço", below("sanepar", "execution_adverse")),
        ("S12: preço abaixo do limite de compra e limite abaixo do valor-base",
         val("sanepar", "base") is not None and price["sanepar"] < n("V.sanepar.max_entry_price") < val("sanepar", "base")),
        ("S05: reajuste de 2026 abaixo do IPCA de 2025", n("V.sanepar.tariff_adjustment.2026") < n("V.macro.ipca_actual.2025")),
        ("S12: a Sabesp é a que mais investe entre as três", capex["sabesp"] == max(capex.values())),
        ("S04: Brasil abaixo das metas de 2033", n("OBS_002588") < n("V.sector.target_water_2033") and n("OBS_002589") < n("V.sector.target_sewer_2033")),
        ("S11: em 23/10 a Sanepar fechou perto do valor-base",
         val("sanepar", "base") is not None and abs(n("V.SAPR11.close.2026-10-23") / val("sanepar", "base") - 1) < .05),
        ("S11: as três caíram juntas na semana do segundo turno", all(n(f"V.{t}.change.2026-10-23_2026-10-30") < 0 for t in TICKER.values())),
        ("S11: a NTN-B subiu na semana do segundo turno", n("V.macro.ntnb_2035_real.2026-10-23") < n("V.macro.ntnb_2035_real.2026-10-30")),
    ]
    return [name for name, ok in checks if not ok]


def _origin(pg: Page, scr: dict) -> dict:
    b, stocks = pg.b, []
    for slug, name, group in scr["stocks"]:
        item = pg.v(f"V.carta2.weight.{slug}")
        reason = b.obs[item["ref"]]["note"].removeprefix("Motivo na carta: ")
        if (group == "model") != reason.startswith("Escolha do modelo"):
            raise IncompatibleState(f"grupo de {name} no slide diverge do motivo registrado na carta: {reason}")
        stocks.append(dict(item, slug=slug, name=name, group=group, reason=reason))
    sab = next(s for s in stocks if s["slug"] == "sabesp")
    return dict(stocks=stocks, legend=scr["legend"], chart_title=scr["chart_title"], stat=pg.v(scr["stat_value"]), stat_text=scr["stat_text"],
                reason_label=scr["reason_label"], reason=sab["reason"], steps=[dict(title=t, text=x) for t, x in scr["steps"]])


def _matrix(pg: Page, scr: dict) -> dict:
    b, rows = pg.b, []
    for r in b.matrix:
        letter, label = scr["factor_labels"][r["row_id"]]
        cells = {}
        for e in ENT:
            cell = r["cells"].get(e, {"value_refs": [], "text": ""})
            main, sub = scr["cells"][r["row_id"]][e]
            shown = set(_tokens(main + sub))
            if not shown <= set(cell["value_refs"]):
                raise IncompatibleState(f"matriz {r['row_id']}/{e}: valores fora da célula do pacote: {sorted(shown - set(cell['value_refs']))}")
            details = []
            for ref in cell["value_refs"]:
                o = b.obs[ref]
                src = [b.sources[s] for s in b.value_sources(ref) if s in b.sources]
                details.append(dict(ref=ref, num=b.num(ref), fmt=b.fmt(ref), metric=L.metric(o["metric_id"]),
                                    period=" a ".join(_br_date(x) for x in (o["period_start"], o["period_end"]) if x), scope=o["scope"],
                                    source=[dict(id=s["source_id"], title=L.source(s), published=s["published_at"]) for s in src]))
            cells[e] = dict(main=pg.t(main), sub=pg.t(sub), gap=not cell["value_refs"], bundle_text=cell["text"], values=details)
        rows.append(dict(id=r["row_id"], letter=letter, factor=label, bundle_factor=r["factor"], channel=scr["channels"][r["row_id"]],
                         comparability=r["comparability"], cells=cells))
    return dict(columns=scr["columns"], rows=rows, note=scr["note"])


def _waterfall(pg: Page, entity: str, labels: dict) -> list[dict]:
    vr = pg.b.case(f"{entity}.base")["value_refs"]
    items = [dict(role="start", label=labels["start"], **pg.v(vr["enterprise_value"]))]
    for key in ("net_debt_october_estimate", "debt_like", "grantor_net", "obligation_pv"):
        item = pg.v(vr[key])
        if item["num"]:
            # Efeito sobre o patrimônio = componente com sinal invertido (apresentação, não cálculo novo).
            item["effect_num"] = -item["num"]
            item["effect_fmt"] = ("+" if item["effect_num"] > 0 else "") + format_value(-item["num"], "BRL", 1e6)
            items.append(dict(role="delta", label=labels[key], **item))
    items.append(dict(role="end", label=labels["end"], **pg.v(vr["equity_residual_before_floor"])))
    return items


def _grid(pg: Page, entity: str) -> dict:
    b = pg.b
    grid = [c for c in b.cases.values() if c["entity_id"] == entity and c["scenario_id"] == "grid"]
    cells = [dict(_case_val(pg, c["case_id"]), wacc=pg.v(c["dimensions"]["wacc"]["value_ref"]), g=pg.v(c["dimensions"]["g_real"]["value_ref"]))
             for c in grid]
    worst = min((c for c in cells if c["num"] is not None), key=lambda c: c["num"])
    wv = sorted({c["wacc"]["num"] for c in cells})
    gv = sorted({c["g"]["num"] for c in cells})
    pick = lambda axis, x: next(c[axis]["fmt"] for c in cells if c[axis]["num"] == x)
    return dict(cells=cells, worst=worst, w_lo=pick("wacc", wv[0]), w_hi=pick("wacc", wv[-1]), g_lo=pick("g", gv[0]), g_hi=pick("g", gv[-1]))


def build(b: Bundle) -> dict:
    # Deck completo só com decisão proposta/adotada e alvo válido no caso-base da empresa decidida;
    # pacote incompleto continua consumível por --check/QA, mas não gera peça com tese inexistente.
    dec = b.decision.get("entity_id")
    if b.decision.get("status") not in ("proposed", "adopted") or not dec:
        raise IncompatibleState(f"decisão '{b.decision.get('status')}' sem empresa: deck completo indisponível neste estado")
    if f"{dec}.base" not in b.cases or b.case(f"{dec}.base")["target_validity"] != "conditional_value":
        raise IncompatibleState(f"caso-base de {dec} sem alvo exibível: deck completo indisponível")
    broken = guards(b)
    if broken:
        raise IncompatibleState("o texto do deck afirma relações que este pacote não sustenta: " + "; ".join(broken))
    names = {e: b.entity_name(e) for e in ENT}
    pages = []
    for spec in K.PAGES:
        pg = Page(b, spec)
        d = dict(id=spec["id"], kind=spec["kind"], slot=spec["slot"], voice=spec["voice"], seconds=spec["seconds"], block=spec["block"],
                 kicker=spec["kicker"], title=pg.t(spec["title"]), subtitle=pg.t(spec["subtitle"]))
        scr = K.SCREEN.get(spec["id"], {})
        k = spec["kind"]
        if k == "cover":
            d.update(team=scr["team"], tickers=scr["tickers"])
        elif k == "origin":
            d.update(_origin(pg, scr))
        elif k == "question":
            d.update(steps=[dict(title=t, text=x) for t, x in scr["steps"]], questions_label=scr["questions_label"], questions=scr["questions"])
        elif k == "sector":
            d.update(chart_title=scr["chart_title"], legend=list(scr["legend"]), note=scr["note"], companies_label=scr["companies_label"],
                     bars=[dict(label=lab, value=pg.v(v), target=pg.v(t)) for lab, v, t in scr["bars"]],
                     companies=[dict(entity=c["entity"], name=names[c["entity"]], ticker=c["ticker"], line1=pg.t(c["line1"]), line2=pg.t(c["line2"]),
                                     price=pg.v(b.case(f"{c['entity']}.base")["value_refs"]["price"])) for c in scr["companies"]])
        elif k == "swot":
            d["quadrants"] = [dict(id=q["id"], label=q["label"], bullets=[pg.t(x) for x in q["bullets"]], effect=pg.t(q["effect"])) for q in scr["quadrants"]]
        elif k == "medium":
            d["cards"] = [dict(label=c["label"], big=pg.v(c["big"]), big_label=c["big_label"], text=pg.t(c["text"]), effect=pg.t(c["effect"]))
                          for c in scr["cards"]]
        elif k == "matrix":
            d.update(_matrix(pg, scr))
        elif k == "esg_value":
            pg.inputs.update(f"V.{e}.water_energy_expense_sinisa.2024" for e in ENT)  # base da sensibilidade de energia
            d.update(chain=[dict(title=t, text=x) for t, x in scr["chain"]], chart_title=pg.t(scr["chart_title"]), legend=list(scr["legend"]), note=pg.t(scr["note"]),
                     energy_saving=pg.v("A.energy_saving.base"),
                     energy=[dict(entity=e, name=names[e], r50=pg.v(f"V.case.{e}.energy.r50.capex_break_even"),
                                  r100=pg.v(f"V.case.{e}.energy.r100.capex_break_even")) for e in ENT])
        elif k == "calc":
            d.update(r1_title=scr["r1_title"], r1_sub=pg.t(scr["r1_sub"]), r1_note=scr["r1_note"], wacc=pg.v("A.wacc_nominal.base"),
                     r1=[dict(entity=e, name=names[e], **pg.v(f"V.{e}.rab_value_ratio.base")) for e in ENT],
                     bridge_title=scr["bridge_title"], bridge_entity=dec, bridge=_waterfall(pg, dec, scr["bridge_labels"]), bridge_note=scr["bridge_note"],
                     params=[dict(text=pg.t(text), **pg.v(vid)) for vid, text in scr["params"]])
        elif k == "tir":
            d.update(steps=[dict(title=t, text=x) for t, x in scr["steps"]], chart_title=scr["chart_title"], wacc_label=scr["wacc_label"],
                     wacc=pg.v("A.wacc_nominal.base", "pct2"),
                     implied=[dict(entity=e, name=names[e], **pg.v(b.extras["implied_wacc"][e], "pct2")) for e in ENT],
                     esg_label=scr["esg_label"], esg=[dict(letter=l, title=t, text=pg.t(x)) for l, t, x in scr["esg"]])
        elif k == "value_price":
            rows = []
            for e in ENT:
                vr = b.case(f"{e}.base")["value_refs"]
                rows.append(dict(entity=e, name=names[e], ticker=TICKER[e], value=_case_val(pg, f"{e}.base"), price=pg.v(vr["price"]),
                                 upside=pg.v(vr["upside"], "signed1") if "upside" in vr else None))
            g = _grid(pg, dec)
            note = scr["grid_note"]
            for key, txt in (("grid_w_lo", g["w_lo"]), ("grid_w_hi", g["w_hi"]), ("grid_g_lo", g["g_lo"]), ("grid_g_hi", g["g_hi"]),
                             ("grid_min", g["worst"]["fmt"])):
                note = note.replace("{{" + key + "}}", txt)
            week = [dict(ticker=t, name=names[next(e for e, x in TICKER.items() if x == t)], pre=pg.v(f"V.{t}.close.2026-10-23"),
                         post=pg.v(f"V.{t}.close.2026-10-30"), change=pg.v(f"V.{t}.change.2026-10-23_2026-10-30", "signed1")) for t in scr["week_tickers"]]
            d.update(chart_title=scr["chart_title"], legend=list(scr["legend"]), upside_label=scr["upside_label"], rows=rows, grid=g, grid_note=note,
                     week_label=scr["week_label"], week=week, week_note=pg.t(scr["week_note"]))
        elif k == "conclusion":
            vr = b.case(f"{dec}.base")["value_refs"]
            d["ruler"] = dict(title=scr["ruler_title"], labels={k: pg.t(v) for k, v in scr["labels"].items()}, entity=dec, price=pg.v(vr["price"]), limit=pg.v(f"V.{dec}.max_entry_price"),
                              value=pg.v(vr["paper_value"]), margin=pg.v("A.margin_of_safety.base"),
                              adverse=_case_val(pg, f"{dec}.execution_adverse"), rates=_case_val(pg, f"{dec}.rates_up"),
                              favorable=_case_val(pg, f"{dec}.favorable"))
            d.update(triggers_title=scr["triggers_title"], triggers=[dict(label=t, text=pg.t(x)) for t, x in scr["triggers"]],
                     closing=[dict(entity=e, name=nm, text=pg.t(x), highlight=e == dec) for e, nm, x in scr["closing"]])
        d["claim_texts"] = {cid: b.claim_text(cid) for cid in pg.claims}
        srcs = set()
        for cid in pg.claims:
            srcs.update(b.claim_sources(cid))
        for vid in pg.used | pg.inputs:
            srcs.update(b.value_sources(vid))
        d["sources"] = sorted([dict(id=s, title=L.source(b.sources[s]), published=b.sources[s]["published_at"], url=b.sources[s]["url"])
                               for s in srcs if s in b.sources], key=lambda x: x["title"])
        own = any(b.obs[v]["value_state"] in ("derived", "assumed") for v in pg.used)
        d["source_line"] = source_line([s["title"] for s in d["sources"]], own)
        d["value_refs"] = sorted(pg.used)
        d["input_refs"] = sorted(pg.inputs)
        pages.append(d)
    return dict(bundle_id=b.bundle_id, manifest_sha256=b.manifest_sha256, state=b.manifest["state"], decision=b.decision["status"],
                profile=PROFILE, decision_entity=dec, entity_names=names, tickers=TICKER, order=ENT, pages=pages,
                valuation_date="30/10/2026", cutoff="31/10/2026 18:25", team="asset.dev")


SHORT = [("Release de resultados ", "release "), ("Demonstrações financeiras ", "DF "), ("Relatório de sustentabilidade ", "sustentabilidade "),
         ("Fato relevante de ", "fato relevante de "), ("Apresentação institucional (fev/2025)", "apresentação de fev/2025"),
         ("Ambiente regulatório (RI)", "RI"), ("ITR 2T26 (notas)", "ITR 2T26"), ("Calendário de eventos 2026", "calendário 2026"),
         ("Nota Técnica 006/2025 (3ª revisão tarifária da Sanepar)", "NT 006/2025"), ("relatório de água (base 2024)", "água 2024"),
         ("relatório de esgoto (base 2024)", "esgoto 2024"), ("planilhas de água (base 2024)", "água 2024"), ("taxas do Tesouro Direto (NTN-B 2035)", "NTN-B 2035"),
         ("séries de IPCA/Selic", "IPCA"), ("Plano de investimentos 2026–2030", "plano de investimentos 2026–30")]


def source_line(titles: list[str], own: bool) -> str:
    """Rodapé curto: agrupa documentos por emissor ("Sanepar (release 2T26; ITR 2T26)"); a lista completa fica no modelo."""
    groups: dict[str, list[str]] = {}
    for t in titles:
        if t.startswith("Organizesee — cotações"):
            groups.setdefault("Organizesee (cotações de fechamento)", [])
            continue
        issuer, _, doc = t.partition(" — ")
        for a, b in SHORT:
            doc = doc.replace(a, b)
        groups.setdefault(issuer, [])
        if doc and doc not in groups[issuer]:
            groups[issuer].append(doc)
    parts = [f"{i} ({'; '.join(d)})" if d else i for i, d in groups.items()]
    return "; ".join(parts + (["cálculos asset.dev"] if own else [])) + "." if parts or own else ""


def placements(model: dict, artifact: str, profile: str, b: Bundle) -> list[dict]:
    rows = []
    for p in model["pages"]:
        for cid in p["claim_texts"]:
            rows.append(dict(artifact=artifact, profile=profile, page=p["id"], block=p["block"], claim_id=cid,
                             value_ids=sorted(set(_tokens(b.claims[cid]["text_template"]))), source_ids=b.claim_sources(cid),
                             input_bundle=model["bundle_id"], input_manifest_sha256=model["manifest_sha256"]))
        rows.append(dict(artifact=artifact, profile=profile, page=p["id"], block=p["block"], claim_id="(screen_values)", value_ids=p["value_refs"],
                         source_ids=[s["id"] for s in p["sources"]], input_bundle=model["bundle_id"], input_manifest_sha256=model["manifest_sha256"]))
    return rows


def _br_date(iso: str) -> str:
    parts = iso.split("-")
    return f"{parts[2]}/{parts[1]}/{parts[0]}" if len(parts) == 3 else iso


def _tokens(t: str) -> list[str]:
    return re.findall(r"\{\{value:([^}|]+)", t)
