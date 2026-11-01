/* asset.dev — deck interativo de 10 páginas. Sem rede, sem bibliotecas; dados embutidos do pacote 1.0.
   A interface não calcula finanças: só posiciona, colore e alterna valores já produzidos pela análise. */
(function () {
  "use strict";
  const M = JSON.parse(document.getElementById("deck-data").textContent);
  const NS = "http://www.w3.org/2000/svg";
  const ENT = M.order;
  const NAME = M.entity_names;
  const BRAND_SYMBOL = __BRAND_SYMBOL_JSON__;
  const COLOR = { sanepar: "var(--sanepar)", sabesp: "var(--sabesp)", copasa: "var(--copasa)" };
  const stage = document.getElementById("stage");
  let current = 0, scale = 1;
  const state = {};

  // ---------------- helpers ----------------
  function h(tag, attrs, ...kids) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === null || v === undefined || v === false) continue;
      if (k === "class") e.className = v; else if (k === "html") e.innerHTML = v;
      else if (k.startsWith("on")) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v === true ? "" : v);
    }
    for (const k of kids.flat()) if (k !== null && k !== undefined && k !== false) e.append(k.nodeType ? k : document.createTextNode(k));
    return e;
  }
  function s(tag, attrs, ...kids) {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === null || v === undefined) continue;
      if (k.startsWith("on")) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v);
    }
    for (const k of kids.flat()) if (k !== null && k !== undefined) e.append(k.nodeType ? k : document.createTextNode(k));
    return e;
  }
  const ICON = {
    target: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/></svg>',
    shield: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/></svg>',
    flag: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 21V4M5 4h11l-2 4 2 4H5"/></svg>',
    warn: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18v.5"/></svg>',
    info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/></svg>',
    prev: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M15 5l-7 7 7 7"/></svg>',
    next: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M9 5l7 7-7 7"/></svg>'
  };
  function niceTicks(max, n) {
    const raw = max / (n || 4), mag = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / mag;
    const step = (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * mag, out = [];
    for (let v = 0; out.length === 0 || out[out.length - 1] < max - 1e-9; v += step) out.push(Math.round(v * 1e6) / 1e6);
    return out;
  }
  const icon = (n) => h("span", { class: "ic", "aria-hidden": "true", html: ICON[n] });
  const tip = document.getElementById("tooltip");
  function showTip(evt, html) {
    tip.innerHTML = html; tip.style.display = "block";
    const r = stage.getBoundingClientRect();
    let x, y;
    if (evt && evt.clientX !== undefined && evt.type !== "focus") { x = (evt.clientX - r.left) / scale; y = (evt.clientY - r.top) / scale; }
    else { const b = evt.target.getBoundingClientRect(); x = (b.right - r.left) / scale; y = (b.top - r.top) / scale; }
    tip.style.left = Math.min(x + 18, 1920 - 440) + "px"; tip.style.top = Math.max(y - 70, 10) + "px";
  }
  const hideTip = () => { tip.style.display = "none"; };
  function markify(g, html) {
    g.setAttribute("class", "mark"); g.setAttribute("tabindex", "0"); g.setAttribute("role", "img");
    g.setAttribute("aria-label", html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim());
    g.addEventListener("mousemove", (e) => showTip(e, html)); g.addEventListener("mouseleave", hideTip);
    g.addEventListener("focus", (e) => showTip(e, html)); g.addEventListener("blur", hideTip);
    return g;
  }
  function chartBox(title, svg, rows, header, extra) {
    const table = h("table", { class: "data", hidden: true }, h("thead", {}, h("tr", {}, header.map((x) => h("th", {}, x)))),
      h("tbody", {}, rows.map((r) => h("tr", {}, r.map((c) => h("td", {}, c))))));
    const scroll = h('div', {class:'data-scroll',hidden:true,tabindex:'0',role:'region','aria-label':`Tabela: ${title}; use as setas verticais para rolar`},table);
    const btn = h("button", { class: "ghost tablebtn no-print", "aria-pressed": "false", "data-testid": "table-toggle",
      onclick: () => { const on = table.hidden; table.hidden = !on; scroll.hidden = !on; svg.style.display = on ? "none" : ""; btn.setAttribute("aria-pressed", String(on)); btn.textContent = on ? "Ver gráfico" : "Ver tabela"; } }, "Ver tabela");
    return h("div", { class: "chartbox" }, h("div", { class: "chartbar" }, h("h3", {}, title), h("div", { style: "display:flex;gap:12px;align-items:center" }, extra || null, btn)), svg, scroll);
  }
  const legendEnt = (list) => h("div", { class: "legend" }, list.map((e) => h("span", {}, h("span", { class: "swatch", style: `background:${COLOR[e]}` }), NAME[e])));
  function segmented(options, selected, onpick, testid, label) {
    const wrap = h("div", { class: "segmented", role: "group", "aria-label": label || "" });
    options.forEach(([id, text]) => {
      const b = h("button", { "aria-pressed": String(id === selected), "data-id": id, "data-testid": `${testid}-${id}`,
        onclick: () => { wrap.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b))); onpick(id); } }, text);
      wrap.append(b);
    });
    return wrap;
  }

  // ---------------- drawer (fontes, detalhes) ----------------
  const drawer = document.getElementById("drawer"), scrim = document.getElementById("scrim");
  let lastFocus = null;
  function openDrawer(title, nodes) {
    lastFocus = document.activeElement;
    drawer.replaceChildren(h("button", { class: "ghost close", onclick: closeDrawer, "aria-label": "Fechar painel", "data-testid": "drawer-close" }, "Fechar ✕"),
      h("h2", { id: "drawer-title" }, title), ...nodes);
    drawer.classList.add("open"); scrim.classList.add("open"); drawer.setAttribute("aria-hidden", "false");
    drawer.querySelector(".close").focus();
  }
  function closeDrawer() {
    if (!drawer.classList.contains("open")) return false;
    drawer.classList.remove("open"); scrim.classList.remove("open"); drawer.setAttribute("aria-hidden", "true");
    if (lastFocus && lastFocus.focus) lastFocus.focus();
    return true;
  }
  scrim.addEventListener("click", closeDrawer);
  function sourcesDrawer(p) {
    const claims = Object.entries(p.claim_texts).map(([id, t]) => h("div", { class: "claim" }, t, h("div", { class: "small muted" }, id)));
    const srcs = h("ul", {}, p.sources.map((x) => h("li", {}, h("b", {}, x.title), x.published ? ` (publicado ${x.published})` : "",
      h("div", { class: "small muted" }, x.id))));
    openDrawer("Fontes e afirmações", [h("p", { class: "small muted" }, `Pacote analítico ${M.bundle_id} · avaliação ${M.valuation_date} · corte ${M.cutoff}. Cada número desta página vem de um value_id do pacote.`),
      h("h3", {}, "Afirmações desta página"), ...claims, h("h3", {}, "Fontes"), srcs]);
  }

  // ---------------- slide frame ----------------
  function frame(p, i, bodyClass, bodyKids) {
    const n = M.pages.length;
    const badge = (p.proposal_badge || p.kind === "thesis" || p.kind === "decision") && M.decision !== "adopted"
      ? h("span", { class: "badge", html: ICON.info + " Proposta — decisão do grupo (H09) pendente" }) : null;
    const src = p.sources.slice(0, 3).map((x) => x.title).join(" · ");
    return h("section", { class: "slide", id: `slide-${i + 1}`, role: "region", "aria-roledescription": "slide",
      "aria-label": `${i + 1} de ${n}: ${p.title}`, "data-page": p.id },
      h("div", { class: "topbar" }, h("div", { class: "brandmark" }, h("span", { class: "wordmark" }, h("span", { html: BRAND_SYMBOL }), M.team), h("span", { class: "brand-context" }, "Saneamento e valor")),
        h("div", { style: "display:flex;gap:18px;align-items:center" }, badge, h("span", { class: "pagecount" }, `${String(i + 1).padStart(2, "0")} / ${n}`))),
      h("div", { class: "head" }, h("div", { class: "kicker" }, p.kicker), h("h1", { class: "title" }, p.title), h("p", { class: "subtitle" }, p.subtitle)),
      h("div", { class: `body ${bodyClass}` }, bodyKids),
      h("div", { class: "foot" }, h("button", { class: "ghost no-print", "data-testid": "sources-open", onclick: () => sourcesDrawer(p) }, `Fontes e afirmações (${p.sources.length})`),
        h("div", { class: "srcline" }, src ? `Fontes: ${src}${p.sources.length > 3 ? " · …" : ""}` : "")));
  }

  // ---------------- P01 tese ----------------
  function pThesis(p, i) {
    const [v, pr, up] = p.hero;
    const main = h("div", { class: "card main" }, h("div", {}, h("div", { class: "label" }, v.label), h("div", { class: "num", "data-testid": "hero-value" }, v.fmt),
      h("div", { style: "font-size:24px;opacity:.85;margin-top:8px" }, v.note)),
      h("div", { class: "vs" }, h("div", {}, `${pr.label}`), h("div", { style: "font-size:56px;font-weight:750" }, pr.fmt),
        h("div", { style: "margin-top:8px" }, `${up.label}: `, h("b", { style: "font-size:34px" }, up.fmt))));
    const hero = h("div", { class: "hero" }, main,
      h("button", { class: "card soft", style: "text-align:left;cursor:pointer;grid-column:span 3", "data-testid": "price-source",
        onclick: () => openDrawer("Fonte e data do preço", [h("p", { style: "font-size:22px;line-height:1.5" }, p.source_panel), h("div", { class: "claim" }, p.claim_texts["CL.lead.price"])]) },
        h("div", { class: "label" }, "Fonte e data do preço"), h("div", { class: "small", style: "margin-top:6px" }, p.source_panel)));
    const chips = h("div", { class: "chips" }, h("div", { class: "label" }, "Condições da recomendação"),
      p.chips.map((c) => h("div", { class: "chip" }, icon(c.icon), h("div", {}, c.text))),
      h("button", { class: "ghost", style: "justify-self:start", "data-testid": "why-conditional",
        onclick: () => openDrawer("Por que condicionada?", [h("div", { class: "claim" }, p.claim_texts["CL.lead.thesis"]), h("div", { class: "claim" }, p.claim_texts["CL.conclusion.decision"])]) },
        "Por que condicionada?"));
    const cmp = h("div", { class: "compare" }, h("div", { class: "label" }, "As três no caso-base · R$ por ação/unit"),
      h("div", { class: "cmp-row" }, p.compare.map((c) => h("div", { class: "cmp", style: `border-left-color:${COLOR[c.entity]}` },
        h("div", { class: "cmp-name" }, NAME[c.entity], h("span", { class: "muted" }, ` ${c.ticker}`)),
        h("div", { class: "cmp-vals" }, h("span", {}, "Valor ", h("b", {}, c.value.fmt)), h("span", {}, "Preço ", h("b", {}, c.price.fmt))),
        h("div", { class: "cmp-up", style: `color:${c.upside && c.upside.num > 0 ? "var(--good)" : "var(--neg)"}` }, c.upside ? c.upside.fmt : "N/D")))));
    return frame(p, i, "thesis", [hero, chips, cmp]);
  }

  // ---------------- P02 setor ----------------
  function pSector(p, i) {
    const W = 1100, H = 430, x0 = 250, x1 = 1060, sx = (v) => x0 + (x1 - x0) * v;
    const svg = s("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Cobertura nacional de água e esgoto e metas de 2033" });
    [0, .25, .5, .75, 1].forEach((t) => { svg.append(s("line", { x1: sx(t), x2: sx(t), y1: 30, y2: 360, class: "gridline" }), s("text", { x: sx(t), y: 396, "text-anchor": "middle", class: "lbl2" }, `${Math.round(t * 100)}%`)); });
    const rows = {};
    p.bars.forEach((b, k) => {
      const y = 80 + k * 160;
      const g = markify(s("g", { "data-row": b.id }), `<b>${b.label}</b>Brasil 2024: ${b.value.fmt}<br>Meta 2033: ${b.target.fmt}`);
      g.append(s("text", { x: 0, y: y + 44, class: "lbl", style: "font-size:24px" }, b.label),
        s("rect", { x: x0, y, width: x1 - x0, height: 70, rx: 6, style: "fill:var(--surface-2)" }),
        s("rect", { x: x0, y, width: sx(b.value.num) - x0, height: 70, rx: 6, style: "fill:var(--neutral-bar)" }),
        s("text", { x: sx(b.value.num) - 16, y: y + 46, "text-anchor": "end", style: "fill:var(--black);font-size:30px;font-weight:600" }, b.value.fmt),
        s("line", { x1: sx(b.target.num), x2: sx(b.target.num), y1: y - 14, y2: y + 84, style: "stroke:var(--ink);stroke-width:3" }),
        s("text", { x: sx(b.target.num) - 8, y: y - 22, "text-anchor": "end", class: "lbl", style: "font-size:20px" }, `Meta 2033: ${b.target.fmt}`));
      svg.append(g); rows[b.id] = g;
    });
    const note = h("div", { class: "card note-card" }, h("h3", { "data-testid": "sector-note-title" }, ""), h("p", { "data-testid": "sector-note" }, ""));
    const pick = (id) => { state.sector = id; Object.entries(rows).forEach(([k, g]) => g.classList.toggle("dim", k !== id));
      const b = p.bars.find((x) => x.id === id); note.querySelector("h3").textContent = b.label; note.querySelector("p").textContent = p.notes[id]; };
    const seg = segmented(p.bars.map((b) => [b.id, b.label]), p.bars[1].id, pick, "sector", "Escolher indicador");
    const box = chartBox("Brasil, ano-base 2024 · % da população total", svg, p.bars.map((b) => [b.label, b.value.fmt, b.target.fmt]), ["Indicador", "2024", "Meta 2033"], seg);
    pick(p.bars[1].id);
    return frame(p, i, "sector", [box, h("div", {}, note, h("div", { class: "callout" }, p.callout))]);
  }

  // ---------------- P03 SWOT ----------------
  function pSwot(p, i) {
    const detail = h("div", { class: "card detail" });
    const btns = [];
    const pick = (q) => { state.swot = q.id; btns.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.id === q.id)));
      detail.replaceChildren(h("div", { class: "label" }, "Evidência"), h("h3", { "data-testid": "swot-detail-title" }, q.label), h("div", { class: "ev" }, q.evidence),
        h("div", { class: "label", style: "margin-top:20px" }, "Efeito na tese"), h("div", { class: "imp" }, q.implication)); };
    const grid = h("div", { class: "quad-grid" }, p.quadrants.map((q) => {
      const b = h("button", { class: "quad", "aria-pressed": "false", "data-id": q.id, "data-testid": `swot-${q.id}`, onclick: () => pick(q) },
        h("h3", {}, h("span", { class: "letter" }, q.id), q.label), h("ul", {}, q.bullets.map((x) => h("li", {}, x))));
      btns.push(b); return b; }));
    pick(p.quadrants[3]);
    return frame(p, i, "swot", [grid, detail]);
  }

  // ---------------- P04 médio prazo ----------------
  function pMedium(p, i) {
    const TABS = [["fato", "Fato"], ["prazo", "Prazo"], ["canal", "Canal econômico"]];
    return frame(p, i, "medium", p.cards.map((c) => {
      const txt = h("div", { class: "tabtext", "data-testid": `medium-text-${c.id}` }, c.tabs.fato);
      return h("div", { class: "card mcard" }, h("div", { class: "label" }, "Força"), h("h3", {}, c.label),
        segmented(TABS, "fato", (t) => { txt.textContent = c.tabs[t]; }, `medium-${c.id}`, `Detalhe de ${c.label}`), txt);
    }));
  }

  // ---------------- P05 matriz ----------------
  function pMatrix(p, i) {
    const aside = h("div", { class: "card mx-detail" });
    const cellBtns = [];
    const show = (row, e) => {
      const c = row.cells[e];
      cellBtns.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.key === `${row.id}|${e}`)));
      const items = c.values.length ? c.values.map((v) => h("div", {}, h("dt", {}, v.metric.replaceAll("_", " ")),
        h("dd", {}, h("b", {}, v.fmt), v.period ? ` · ${v.period}` : "", h("div", { class: "small muted" }, v.note || v.definition),
          h("div", { class: "small muted" }, v.source.map((x) => x.title).join("; "), v.locator ? ` · ${v.locator}` : ""))))
        : [h("dd", { class: "gap" }, "Indicador comparável não obtido — lacuna explícita, não pior desempenho.")];
      aside.replaceChildren(h("div", { class: "label" }, `${row.factor} · ${NAME[e]}`), h("h3", { style: "font-size:26px;margin:6px 0 14px", "data-testid": "matrix-detail-title" }, c.text),
        h("dl", {}, items), h("div", { class: "label", style: "margin-top:14px" }, "Canal para o caixa"), h("p", { class: "small" }, row.channel),
        h("p", { class: "small muted" }, row.comparability));
    };
    const table = h("table", { class: "mx", "data-testid": "matrix" }, h("thead", {}, h("tr", {}, h("th", {}, "Fator"),
      ENT.map((e) => h("th", { "data-col": e }, h("span", { class: "swatch", style: `background:${COLOR[e]}` }), NAME[e])))),
      h("tbody", {}, p.rows.map((r) => h("tr", {}, h("td", {}, r.factor), ENT.map((e) => {
        const c = r.cells[e];
        const b = h("button", { class: "cellbtn", "aria-pressed": "false", "data-key": `${r.id}|${e}`, "data-testid": `cell-${r.id}-${e}`, onclick: () => show(r, e) },
          c.values.length ? h("div", { class: "v" }, c.values[0].fmt) : h("div", { class: "v gap" }, "lacuna"), h("div", { class: "t" }, c.text));
        cellBtns.push(b);
        return h("td", { "data-col": e }, b); })))));
    const focusSeg = segmented([["all", "Todas"], ...ENT.map((e) => [e, NAME[e]])], "all", (id) => {
      table.querySelectorAll("[data-col]").forEach((td) => td.classList.toggle("dim", id !== "all" && td.dataset.col !== id)); }, "matrix-focus", "Destacar empresa");
    show(p.rows[4], "sanepar");
    return frame(p, i, "matrix", [h("div", {}, h("div", { class: "chartbar" }, h("h3", {}, "Cinco fatores × três empresas"), focusSeg), table), aside]);
  }

  // ---------------- P06 ponte ----------------
  function hbars(rows, max, fmtTitle, opts) {
    const W = 800, H = 78 + rows.length * 104, x0 = 170, x1 = 690, sx = (v) => x0 + (x1 - x0) * Math.max(0, v) / max;
    const svg = s("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": fmtTitle });
    if (opts && opts.ref !== undefined) {
      svg.append(s("line", { x1: sx(opts.ref), x2: sx(opts.ref), y1: 20, y2: H - 30, style: "stroke:var(--ink);stroke-width:2.5" }),
        s("text", { x: sx(opts.ref) + 8, y: H - 10, class: "lbl2" }, opts.refLabel));
    }
    rows.forEach((r, k) => {
      const y = 36 + k * 104;
      const g = markify(s("g", { "data-entity": r.entity }), `<b>${NAME[r.entity]}</b>${r.tip}`);
      g.append(s("text", { x: 0, y: y + 40, class: "lbl", style: "font-size:23px" }, NAME[r.entity]),
        s("rect", { x: x0, y, width: Math.max(4, sx(r.num) - x0), height: 64, rx: 4, style: `fill:${COLOR[r.entity]}` }),
        s("text", { x: sx(r.num) + 12, y: y + 41, class: "lbl", style: "font-size:23px", "data-testid": `bar-${r.entity}` }, r.fmt));
      svg.append(g);
    });
    return svg;
  }
  function pBridge(p, i) {
    const maxR = Math.max(1.15, ...p.rab.map((r) => r.num)) * 1.08;
    const rab = hbars(p.rab.map((r) => ({ entity: r.entity, num: r.num, fmt: r.fmt, tip: `R$ 1 investido e remunerado vale ${r.fmt} ao WACC de ${p.wacc.fmt}` })),
      maxR, "Valor de R$ 1 investido em expansão", { ref: 1, refLabel: "R$ 1,00: à direita cria valor" });
    const left = chartBox("Quanto vale R$ 1 investido e remunerado", rab, p.rab.map((r) => [NAME[r.entity], r.fmt]), ["Empresa", "Valor por R$ 1"]);
    const maxE = Math.max(...p.energy["100"].map((r) => r.num)) * 1.15;
    const holder = h("div", {});
    const draw = (ret) => { state.retention = ret;
      const rows = p.energy[ret].map((r) => ({ entity: r.entity, num: r.num, fmt: r.fmt, tip: `Teto de investimento com retenção de ${ret}%: ${r.fmt} (${r.per_share.fmt} por ação/unit, limite superior)` }));
      holder.replaceChildren(chartBox(`Teto de investimento por ${p.energy_saving.fmt} de economia de energia`, hbars(rows, maxE, "Teto de investimento em eficiência energética"),
        rows.map((r) => [NAME[r.entity], r.fmt]), ["Empresa", "Teto (R$)"],
        segmented([["50", "Retenção 50%"], ["100", "Retenção 100%"]], ret, draw, "retention", "Parcela do ganho retida"))); };
    draw("50");
    return frame(p, i, "bridge", [h("div", {}, left, h("p", { class: "small muted", style: "margin-top:10px" }, p.claim_texts["CL.bridge.rab"])),
      h("div", {}, holder, h("p", { class: "small muted", style: "margin-top:10px" }, "Sensibilidade hipotética (despesa municipal de energia da água, SINISA 2024); não é economia realizada e não foi somada ao caso-base."))]);
  }

  // ---------------- P07 método (ponte da firma ao acionista) ----------------
  function waterfall(e, comp) {
    const items = comp.items, W = 1060, H = 470, top = 40, base = 380, n = items.length, bw = 120, gap = (W - 60 - n * bw) / (n - 1);
    const max = Math.max(...items.filter((x) => x.role !== "delta").map((x) => x.num)) * 1.08;
    const sy = (v) => base - (base - top) * v / max;
    const svg = s("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": `Ponte do valor da firma ao acionista — ${NAME[e]}`, "data-testid": "waterfall" });
    svg.append(s("line", { x1: 0, x2: W, y1: base, y2: base, class: "baseline" }));
    let run = 0;
    items.forEach((it, k) => {
      const x = 30 + k * (bw + gap);
      let y0, y1, fill, txt;
      if (it.role === "start") { y0 = 0; y1 = it.num; run = it.num; fill = COLOR[e]; txt = it.fmt; }
      else if (it.role === "delta") { y0 = run; y1 = run + it.effect_num; run = y1; fill = it.effect_num < 0 ? "var(--delta-bar)" : "var(--copasa)"; txt = it.effect_fmt; }
      else { y0 = 0; y1 = it.num; fill = COLOR[e]; txt = it.fmt; }
      const yt = Math.min(sy(y0), sy(y1)), hh = Math.max(3, Math.abs(sy(y0) - sy(y1)));
      const g = markify(s("g", {}), `<b>${it.label}</b>${txt}`);
      g.append(s("rect", { x, y: yt, width: bw, height: hh, rx: 4, style: `fill:${fill}` }),
        s("text", { x: x + bw / 2, y: yt - 12, "text-anchor": "middle", class: "lbl", style: "font-size:19px" }, txt.replace(" mi", "")));
      const words = it.label.split(" "), lines = [];
      words.forEach((w) => { const l = lines[lines.length - 1]; if (l && (l + " " + w).length <= 16) lines[lines.length - 1] = l + " " + w; else lines.push(w); });
      lines.slice(0, 4).forEach((l, j) => g.append(s("text", { x: x + bw / 2, y: base + 28 + j * 21, "text-anchor": "middle", class: "lbl2" }, l)));
      svg.append(g);
      if (k < n - 1 && it.role !== "end") svg.append(s("line", { x1: x + bw, x2: x + bw + gap, y1: sy(run), y2: sy(run), style: "stroke:var(--axis);stroke-width:1.5" }));
    });
    return svg;
  }
  function pMethod(p, i) {
    const holder = h("div", {});
    const draw = (e) => { state.method = e; const c = p.companies[e];
      holder.replaceChildren(chartBox(`${NAME[e]}: da firma ao acionista (R$ milhões, 30/10/2026)`, waterfall(e, c),
        c.items.map((x) => [x.label, x.role === "delta" ? x.effect_fmt : x.fmt]), ["Componente", "Valor"],
        segmented(ENT.map((x) => [x, NAME[x]]), e, draw, "method", "Escolher empresa")),
        h("p", { class: "small muted", "data-testid": "method-note" }, `Valor presente dos fluxos até 2035: ${c.pv_explicit.fmt}; valor terminal: ${c.pv_terminal.fmt} (${c.terminal_share.fmt} do total). Resultado por papel: ${c.paper.fmt}.`)); };
    draw(M.order[0]);
    const params = h("div", { class: "card params" }, h("div", { class: "label" }, "Premissas centrais (propostas para H08)"),
      p.params.map((x) => h("div", { class: "param" }, h("span", {}, x.label), h("b", {}, x.fmt))),
      h("p", { class: "small muted", style: "margin:4px 0 0" }, p.claim_texts["CL.method.precatorio"]));
    return frame(p, i, "method", [holder, params]);
  }

  // ---------------- P08 valor vs preço + grade ----------------
  function dumbbell(p) {
    const W = 860, H = 300, x0 = 150, x1 = 800;
    const all = ENT.flatMap((e) => [p.companies[e].price.num, p.companies[e].value.num || 0]);
    const ticks = niceTicks(Math.max(...all) * 1.05, 5), max = ticks[ticks.length - 1], sx = (v) => x0 + (x1 - x0) * v / max;
    const svg = s("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Valor do caso-base contra preço de mercado" });
    ticks.forEach((v) => svg.append(s("line", { x1: sx(v), x2: sx(v), y1: 10, y2: H - 40, class: "gridline" }),
      s("text", { x: sx(v), y: H - 14, "text-anchor": "middle", class: "lbl2" }, `R$ ${v}`)));
    ENT.forEach((e, k) => {
      const c = p.companies[e], y = 40 + k * 80, xv = sx(c.value.num || 0), xp = sx(c.price.num);
      const g = markify(s("g", {}), `<b>${NAME[e]}</b>Valor caso-base: ${c.value.fmt}<br>Preço 30/10: ${c.price.fmt}<br>${c.upside ? "Potencial: " + c.upside.fmt : ""}<br>WACC implícito no preço: ${c.implied.fmt}`);
      g.append(s("text", { x: 0, y: y + 7, class: "lbl" }, NAME[e]),
        s("line", { x1: Math.min(xv, xp), x2: Math.max(xv, xp), y1: y, y2: y, style: `stroke:${COLOR[e]};stroke-width:4` }),
        s("path", { d: `M${xp} ${y - 13} l13 13 l-13 13 l-13 -13z`, style: "fill:var(--ink)" }),
        s("circle", { cx: xv, cy: y, r: 13, style: `fill:${COLOR[e]};stroke:var(--surface);stroke-width:2` }),
        s("text", { x: xv, y: y - 22, "text-anchor": "middle", class: "lbl", style: "font-size:18px" }, c.value.fmt),
        s("text", { x: xp, y: y + 36, "text-anchor": "middle", class: "lbl2" }, c.price.fmt),
        c.upside ? s("text", { x: x1 + 10, y: y + 7, class: "lbl", style: "font-size:19px" }, c.upside.fmt) : null);
      svg.append(g);
    });
    return chartBox("Valor no caso-base (●) contra preço de 30/10 (◆)", svg,
      ENT.map((e) => [NAME[e], p.companies[e].value.fmt, p.companies[e].price.fmt, p.companies[e].upside ? p.companies[e].upside.fmt : "N/D", p.companies[e].implied.fmt]),
      ["Empresa", "Valor", "Preço", "Potencial", "WACC implícito"]);
  }
  function divColor(ratio) {
    const t = Math.max(-1, Math.min(1, ratio / 0.6));
    return { fill: t >= 0 ? `color-mix(in srgb, var(--pos) ${Math.round(t * 35)}%, var(--mid))` : `color-mix(in srgb, var(--neg) ${Math.round(-t * 35)}%, var(--mid))` };
  }
  function heatmap(e, comp, onpick) {
    const W = 900, H = 330, x0 = 150, y0 = 50, cw = 140, ch = 78;
    const svg = s("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "grid", "aria-label": `Grade WACC × crescimento real — ${NAME[e]}`, "data-testid": "heatmap" });
    comp.wacc_labels.forEach((l, k) => svg.append(s("text", { x: x0 + k * cw + cw / 2, y: y0 - 16, "text-anchor": "middle", class: "lbl2" }, `WACC ${l}`)));
    comp.g_labels.forEach((l, k) => svg.append(s("text", { x: x0 - 14, y: y0 + k * ch + ch / 2 + 6, "text-anchor": "end", class: "lbl2" }, `g real ${l}`)));
    const cells = [];
    comp.grid.forEach((c) => {
      const x = x0 + c.wi * cw, y = y0 + c.gi * ch;
      const ratio = c.num === null ? -1 : c.num / comp.price.num - 1, col = divColor(ratio);
      const g = markify(s("g", { "data-wi": c.wi, "data-gi": c.gi, "data-testid": `cell-${c.wi}-${c.gi}` }),
        `<b>WACC ${c.wacc} · g real ${c.g}</b>${c.valid ? "Valor: " + c.fmt : "N/D — " + c.why}<br>Preço: ${comp.price.fmt}`);
      g.append(s("rect", { x: x + 2, y: y + 2, width: cw - 4, height: ch - 4, rx: 8, style: `fill:${c.valid ? col.fill : "var(--surface-2)"}` }),
        s("text", { x: x + cw / 2, y: y + ch / 2 + 7, "text-anchor": "middle", style: "font-size:21px;font-weight:600;fill:var(--ink)" }, c.fmt));
      g.addEventListener("click", () => onpick(c)); g.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); onpick(c); } });
      svg.append(g); cells.push([g, c]);
    });
    const leg = s("g", {});
    leg.append(s("text", { x: x0, y: H - 6, class: "lbl2" }, "Vermelho: abaixo do preço · cinza: no preço · verde: acima do preço"));
    svg.append(leg);
    return { svg, cells };
  }
  function pResult(p, i) {
    const right = h("div", {});
    const detail = h("div", { class: "heat-detail", "data-testid": "heat-detail" });
    const drawGrid = (e) => { state.result = e; const comp = p.companies[e];
      const pick = (c) => { state.cell = c.case;
        hm.cells.forEach(([g, cc]) => { g.querySelector("rect").style.stroke = cc === c ? "var(--ink)" : "none"; g.querySelector("rect").style.strokeWidth = cc === c ? 3 : 0; });
        detail.replaceChildren(h("b", {}, `WACC ${c.wacc} · crescimento real ${c.g}: ${c.fmt}`), ` contra preço de ${comp.price.fmt}. `,
          c.valid ? "" : `(${c.why})`); };
      const hm = heatmap(e, comp, pick);
      const baseCell = comp.grid.find((c) => c.wi === comp.base_wi && c.gi === 1) || comp.grid[0];
      const reset = h("button", { class: "ghost", "data-testid": "grid-reset", onclick: () => pick(baseCell) }, "Voltar ao caso-base");
      right.replaceChildren(chartBox("Valor por WACC × crescimento real", hm.svg,
        comp.grid.map((c) => [`${c.wacc}`, `${c.g}`, c.fmt]), ["WACC", "g real", "Valor"],
        h("div", { style: "display:flex;gap:12px" }, segmented(ENT.map((x) => [x, NAME[x]]), e, drawGrid, "result", "Escolher empresa"), reset)), detail);
      pick(baseCell); };
    drawGrid(M.order[0]);
    const imp = h("p", { class: "small muted", style: "margin-top:10px" }, p.claim_texts["CL.result.implied"]);
    return frame(p, i, "result", [h("div", {}, dumbbell(p), imp, h("p", { class: "small muted" }, p.claim_texts["CL.result.market_view"])), right]);
  }

  // ---------------- P09 riscos ----------------
  function scenarioBars(p, sid) {
    const W = 880, H = 420, base = 360, top = 30, x0 = 60;
    const all = Object.values(p.scenarios).flatMap((sc) => ENT.map((e) => sc.values[e].num || 0)).concat(ENT.map((e) => p.prices[e].num));
    const ticks = niceTicks(Math.max(...all) * 1.05, 4), max = ticks[ticks.length - 1], sy = (v) => base - (base - top) * v / max, slot = (W - x0) / 3, bw = 130;
    const svg = s("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Valor por cenário contra preço", "data-testid": "scenario-chart" });
    ticks.forEach((v) => svg.append(s("line", { x1: x0, x2: W, y1: sy(v), y2: sy(v), class: "gridline" }),
      s("text", { x: x0 - 10, y: sy(v) + 6, "text-anchor": "end", class: "lbl2" }, `R$ ${v}`)));
    svg.append(s("line", { x1: x0, x2: W, y1: base, y2: base, class: "baseline" }));
    ENT.forEach((e, k) => {
      const v = p.scenarios[sid].values[e], pr = p.prices[e], cx = x0 + k * slot + slot / 2;
      const g = markify(s("g", { "data-entity": e }), `<b>${NAME[e]} · ${p.scenarios[sid].label}</b>${v.valid ? "Valor: " + v.fmt : "N/D — " + v.why}<br>Preço 30/10: ${pr.fmt}`);
      if (v.valid) g.append(s("rect", { x: cx - bw / 2, y: sy(v.num), width: bw, height: base - sy(v.num), rx: 4, style: `fill:${COLOR[e]}` }),
        s("text", { x: cx, y: sy(v.num) - 12, "text-anchor": "middle", class: "lbl", "data-testid": `scen-${e}` }, v.fmt));
      else g.append(s("text", { x: cx, y: base - 20, "text-anchor": "middle", class: "lbl", "data-testid": `scen-${e}` }, "N/D"),
        s("text", { x: cx, y: base - 52, "text-anchor": "middle", class: "lbl2" }, "resíduo negativo"));
      g.append(s("line", { x1: cx - bw / 2 - 14, x2: cx + bw / 2 + 14, y1: sy(pr.num), y2: sy(pr.num), style: "stroke:var(--ink);stroke-width:3" }),
        s("text", { x: cx + bw / 2 + 16, y: sy(pr.num) + 6, class: "lbl2" }, "preço"),
        s("text", { x: cx, y: base + 32, "text-anchor": "middle", class: "lbl" }, NAME[e]));
      svg.append(g);
    });
    return svg;
  }
  function pRisks(p, i) {
    const holder = h("div", {}), note = h("div", { class: "scen-note", "data-testid": "scen-note" });
    const ids = Object.keys(p.scenarios);
    const draw = (sid) => { state.scenario = sid;
      holder.replaceChildren(chartBox("Valor por cenário (barras) e preço de 30/10 (traço)", scenarioBars(p, sid),
        ENT.map((e) => [NAME[e], p.scenarios[sid].values[e].fmt, p.prices[e].fmt]), ["Empresa", "Valor", "Preço"],
        segmented(ids.map((x) => [x, p.scenarios[x].label]), sid, draw, "scenario", "Escolher cenário"))); note.textContent = p.scenarios[sid].note; };
    draw("base");
    const trig = h("div", { class: "triggers" }, h("div", { class: "label" }, "Gatilhos de revisão (status: monitorar)"),
      p.triggers.map((t) => h("div", { class: "trig" }, icon("warn"), h("div", {}, h("h4", {}, t.label, h("span", { class: "status" }, "monitorar")),
        h("p", {}, h("b", {}, "Métrica: "), t.metric), h("p", {}, h("b", {}, "Limite: "), t.limit), h("p", {}, h("b", {}, "Quando: "), t.when, " · ", h("b", {}, "Ação: "), t.action)))),
      h("button", { class: "ghost", style: "justify-self:start", "data-testid": "objection", onclick: () => openDrawer("Melhor objeção", [h("div", { class: "claim" }, p.objection)]) }, "Melhor objeção e resposta"));
    return frame(p, i, "risks", [h("div", {}, holder, note), trig]);
  }

  // ---------------- P10 decisão ----------------
  function pDecision(p, i) {
    const all = {};
    M.pages.forEach((x) => x.sources.forEach((sr) => { all[sr.id] = sr; }));
    const left = h("div", { class: "bigdecision" }, h("div", { class: "label" }, "Proposta"), h("h2", {}, p.title.replace(/^Nossa proposta:\s*/, "")),
      h("p", {}, p.points[1].text));
    const right = h("div", {}, h("div", { class: "dpoints" }, p.points.map((x) => h("div", { class: "dpoint" }, h("b", {}, x.label), h("span", {}, x.text)))),
      h("div", { class: "endbtns no-print" },
        h("button", { class: "ghost", "data-testid": "all-sources", onclick: () => openDrawer("Todas as fontes do deck", [h("ul", {}, Object.values(all).sort((a, b) => a.title.localeCompare(b.title)).map((x) => h("li", {}, h("b", {}, x.title), x.published ? ` (${x.published})` : "", h("div", { class: "small muted" }, x.id))))]) }, "Todas as fontes"),
        h("button", { class: "ghost", "data-testid": "restart", onclick: () => go(0) }, "Recomeçar")));
    const L = p.ladder, lab = L.labels, W = 820, H = 186, x0 = 30, x1 = W - 30, ty = 74;
    const lo = Math.floor(L.price.num * .7 / 10) * 10, hi = Math.ceil(L.value.num * 1.12 / 10) * 10, sx = (v) => x0 + (x1 - x0) * (v - lo) / (hi - lo);
    const tag = (x, y, name, val, below) => [s("text", { x, y: below ? y : y - 24, "text-anchor": "middle", class: "lbl2" }, name),
      s("text", { x, y: below ? y + 24 : y, "text-anchor": "middle", class: "lbl" }, val)];
    const lsvg = s("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": lab.title, "data-testid": "buy-ladder" });
    for (let v = lo; v <= hi + 1e-9; v += 10) lsvg.append(s("line", { x1: sx(v), x2: sx(v), y1: ty + 16, y2: ty + 24, class: "baseline" }),
      s("text", { x: sx(v), y: H - 4, "text-anchor": "middle", class: "lbl2" }, `R$ ${v}`));
    lsvg.append(s("rect", { x: x0, y: ty - 14, width: x1 - x0, height: 28, rx: 14, style: "fill:var(--surface-2)" }),
      markify(s("g", {}, s("rect", { x: x0, y: ty - 14, width: sx(L.limit.num) - x0, height: 28, rx: 14, style: "fill:var(--brand-soft)" }),
        s("text", { x: x0 + 16, y: ty + 7, class: "lbl2", style: "font-weight:700;fill:var(--brand)" }, lab.buy)),
        `<b>${lab.buy}</b>Até ${L.limit.fmt}`),
      markify(s("g", {}, s("rect", { x: sx(L.limit.num), y: ty - 14, width: sx(L.value.num) - sx(L.limit.num), height: 28, style: "fill:var(--hair)" }),
        s("text", { x: (sx(L.limit.num) + sx(L.value.num)) / 2 - 6, y: ty + 7, "text-anchor": "middle", class: "lbl2" }, L.margin.fmt)),
        `<b>${lab.margin}</b>${L.margin.fmt} abaixo do valor no caso-base`));
    lsvg.append(markify(s("g", { "data-testid": "ladder-limit" }, s("line", { x1: sx(L.limit.num), x2: sx(L.limit.num), y1: ty - 22, y2: ty + 22, style: "stroke:var(--brand);stroke-width:3" }),
        tag(sx(L.limit.num), ty - 30, lab.limit, L.limit.fmt)), `<b>${lab.limit}</b>${L.limit.fmt}`),
      markify(s("g", {}, s("circle", { cx: sx(L.value.num), cy: ty, r: 13, style: `fill:${COLOR[L.entity]};stroke:var(--surface);stroke-width:3` }),
        tag(sx(L.value.num), ty - 30, lab.value, L.value.fmt)), `<b>${lab.value}</b>${L.value.fmt}`),
      markify(s("g", {}, s("path", { d: `M${sx(L.price.num)} ${ty - 13}l13 13-13 13-13-13z`, style: "fill:var(--ink);stroke:var(--surface);stroke-width:2" }),
        tag(sx(L.price.num), ty + 50, lab.price, L.price.fmt, true)), `<b>${lab.price}</b>${L.price.fmt}`));
    const ladder = chartBox(lab.title, lsvg, [[lab.price, L.price.fmt], [lab.limit, L.limit.fmt], [lab.value, L.value.fmt]], ["Marco", "R$ por unit"]);
    const trig = h("div", { class: "dtrig" }, h("h3", {}, p.triggers_title), p.triggers.map((t) =>
      h("div", { class: "dtrig-row", "data-testid": `dtrig-${t.id}` }, h("b", {}, t.label), h("span", {}, t.limit))));
    return frame(p, i, "decision", [left, right, h("div", { class: "dfoot" }, ladder, trig)]);
  }

  // ---------------- montagem, navegação ----------------
  const BUILD = { thesis: pThesis, sector: pSector, swot: pSwot, medium: pMedium, matrix: pMatrix, bridge: pBridge, method: pMethod, result: pResult, risks: pRisks, decision: pDecision };
  const slides = M.pages.map((p, i) => BUILD[p.kind](p, i));
  stage.prepend(...slides);
  const live = document.getElementById("live");
  function go(i) {
    current = Math.max(0, Math.min(slides.length - 1, i));
    closeDrawer(); hideTip();
    slides.forEach((sl, k) => { sl.classList.toggle("active", k === current); sl.setAttribute("aria-hidden", String(k !== current)); });
    document.getElementById("progress").style.width = `${(current + 1) / slides.length * 100}%`;
    history.replaceState(null, "", `#p${current + 1}`);
    live.textContent = `Página ${current + 1} de ${slides.length}: ${M.pages[current].title}`;
    return current;
  }
  function fit() {
    const pad = document.body.classList.contains("recording") ? 1 : .985;
    scale = Math.min(innerWidth / 1920, innerHeight / 1080) * pad;
    stage.style.transform = `translate(-50%, -50%) scale(${scale})`;
  }
  addEventListener("resize", fit);
  document.getElementById("prev").addEventListener("click", () => go(current - 1));
  document.getElementById("next").addEventListener("click", () => go(current + 1));
  const help = document.getElementById("help");
  const toggleHelp = (on) => { help.classList.toggle("open", on === undefined ? !help.classList.contains("open") : on); };
  const toggleRec = () => { document.body.classList.toggle("recording"); fit(); };
  const toggleTheme = () => { const r = document.documentElement; const dark = r.dataset.theme === "dark" || (!r.dataset.theme && matchMedia("(prefers-color-scheme: dark)").matches); r.dataset.theme = dark ? "light" : "dark"; };
  document.getElementById("t-theme").addEventListener("click", toggleTheme);
  document.getElementById("t-rec").addEventListener("click", toggleRec);
  document.getElementById("t-help").addEventListener("click", () => toggleHelp());
  document.getElementById("help").addEventListener("click", (e) => { if (e.target.id === "help") toggleHelp(false); });
  addEventListener("keydown", (e) => {
    if (e.target.closest && e.target.closest("input,textarea")) return;
    const k = e.key;
    if (k === "Escape") { if (!closeDrawer()) { toggleHelp(false); if (document.body.classList.contains("recording")) toggleRec(); } return; }
    if (drawer.classList.contains("open")) return;
    if (["ArrowRight", "PageDown"].includes(k) || (k === " " && !(e.target.closest && e.target.closest("button,[tabindex]")))) { e.preventDefault(); go(current + 1); }
    else if (["ArrowLeft", "PageUp"].includes(k)) { e.preventDefault(); go(current - 1); }
    else if (k === "Home") go(0); else if (k === "End") go(slides.length - 1);
    else if (k === "g" || k === "G") toggleRec(); else if (k === "t" || k === "T") toggleTheme(); else if (k === "?") toggleHelp();
    else if (/^[0-9]$/.test(k)) go(k === "0" ? 9 : Number(k) - 1);
  });
  const m = /#p(\d+)/.exec(location.hash);
  if (/[?&]rec=1/.test(location.search)) document.body.classList.add("recording");
  if (/[?&]theme=light/.test(location.search)) document.documentElement.dataset.theme = "light";
  if (/[?&]theme=dark/.test(location.search)) document.documentElement.dataset.theme = "dark";
  fit(); go(m ? Number(m[1]) - 1 : 0);

  // ---------------- autoteste (?selftest=1) ----------------
  function auditLayout() {
    const errors = [], samples = [];
    const inspect = (label) => {
      const slide = slides[current], body = slide.querySelector('.body'), foot = slide.querySelector('.foot');
      const br = body.getBoundingClientRect(), fr = foot.getBoundingClientRect(), sr = slide.getBoundingClientRect();
      const rects = [], walker = document.createTreeWalker(slide, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        if (!node.textContent.trim()) continue;
        const parent = node.parentElement, cs = getComputedStyle(parent);
        if (cs.display === 'none' || cs.visibility === 'hidden' || parent.closest('[hidden]')) continue;
        const range = document.createRange(); range.selectNodeContents(node);
        for (const r of range.getClientRects()) {
          if (!r.width || !r.height) continue;
          const scroll=parent.closest('.data-scroll');
          if (scroll) { const clip=scroll.getBoundingClientRect(); if(r.top<clip.top || r.bottom>clip.bottom) continue; }
          // Footnotes are deliberately clamped; the full evidence is in the source panel.
          if (parent.closest('.srcline')) continue;
          const data = {x:r.left,y:r.top,w:r.width,h:r.height,text:node.textContent.trim().slice(0,100),parent};
          rects.push(data);
          if (r.left < sr.left - scale || r.right > sr.right + scale || r.top < sr.top - scale || r.bottom > sr.bottom + scale)
            errors.push({page:current+1,state:label,kind:'outside_slide',text:data.text});
          if (body.contains(parent) && r.bottom > fr.top - 2 * scale)
            errors.push({page:current+1,state:label,kind:'body_enters_footer',text:data.text});
        }
      }
      for (let a=0; a<rects.length; a++) for (let b=a+1; b<rects.length; b++) {
        const x=rects[a], y=rects[b];
        if (x.parent===y.parent || x.parent.contains(y.parent) || y.parent.contains(x.parent)) continue;
        const iw=Math.min(x.x+x.w,y.x+y.w)-Math.max(x.x,y.x), ih=Math.min(x.y+x.h,y.y+y.h)-Math.max(x.y,y.y);
        if (iw > 4*scale && ih > 5*scale)
          errors.push({page:current+1,state:label,kind:'text_overlap',a:x.text,b:y.text});
      }
      samples.push({page:current+1,state:label,text_rectangles:rects.length,body_height:Math.round(br.height/scale)});
    };
    for (let i=0; i<slides.length; i++) {
      go(i); inspect('default');
      for (const group of slides[i].querySelectorAll('.segmented')) {
        const first=group.querySelector('[aria-pressed="true"]');
        for (const button of group.querySelectorAll('button')) {
          button.click(); inspect(button.dataset.testid || button.textContent);
          if (button.dataset.testid?.startsWith('result-'))
            for (const cell of slides[i].querySelectorAll('[data-wi]')) {
              cell.dispatchEvent(new MouseEvent('click',{bubbles:true})); inspect(`${button.dataset.testid}:${cell.dataset.testid}`);
            }
        }
        if (first) first.click();
      }
      for (const button of slides[i].querySelectorAll('.quad,.cellbtn')) { button.click(); inspect(button.dataset.testid || button.textContent.slice(0,30)); }
      for (const button of slides[i].querySelectorAll('[data-testid="table-toggle"]')) {
        button.click(); inspect('table');
        const scroll=button.closest('.chartbox').querySelector('.data-scroll');
        scroll.scrollTop=scroll.scrollHeight; inspect('table-bottom'); scroll.scrollTop=0;
        button.click();
      }
    }
    go(0);
    return {status:errors.length?'failed':'passed',samples,errors};
  }
  function selftest() {
    const R = [];
    const ok = (name, cond, info) => R.push({ name, pass: !!cond, info: info === undefined ? "" : String(info) });
    const q = (sel, root) => (root || document).querySelector(sel);
    const click = (sel, root) => { const e = q(sel, root); if (!e) throw new Error("ausente: " + sel); e.click(); return e; };
    const txt = (sel, root) => (q(sel, root) || {}).textContent || "";
    try {
      ok("dez páginas", slides.length === 10, slides.length);
      ok("navegação: próxima", go(0) === 0 && (document.getElementById("next").click(), current === 1));
      ok("teclado: ArrowRight", (dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight" })), current === 2));
      ok("teclado: End/Home", (dispatchEvent(new KeyboardEvent("keydown", { key: "End" })), current === 9) && (dispatchEvent(new KeyboardEvent("keydown", { key: "Home" })), current === 0));
      ok("teclado: número 5", (dispatchEvent(new KeyboardEvent("keydown", { key: "5" })), current === 4));
      go(0); const s1 = slides[0];
      click('[data-testid="price-source"]', s1); ok("P01: painel da fonte abre", drawer.classList.contains("open") && /Fonte/.test(txt("#drawer-title")));
      ok("P01: foco vai ao painel", drawer.contains(document.activeElement));
      dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" })); ok("Esc fecha painel", !drawer.classList.contains("open"));
      ok("P01: valor do caso-base", /R\$/.test(txt('[data-testid="hero-value"]', s1)));
      go(1); const s2 = slides[1]; const n0 = txt('[data-testid="sector-note"]', s2);
      click('[data-testid="sector-water"]', s2); ok("P02: alternar indicador muda nota", txt('[data-testid="sector-note"]', s2) !== n0 && state.sector === "water");
      click('[data-testid="table-toggle"]', s2); ok("P02: visão em tabela", !q("table.data", s2).hidden); click('[data-testid="table-toggle"]', s2);
      go(2); const s3 = slides[2]; click('[data-testid="swot-S"]', s3); ok("P03: quadrante revela evidência", txt('[data-testid="swot-detail-title"]', s3) === "Forças");
      go(3); const s4 = slides[3]; const f0 = txt('[data-testid="medium-text-reg"]', s4);
      click('[data-testid="medium-reg-canal"]', s4); ok("P04: aba muda texto", txt('[data-testid="medium-text-reg"]', s4) !== f0);
      go(4); const s5 = slides[4]; click('[data-testid="cell-ESG.water_efficiency-copasa"]', s5);
      ok("P05: célula abre definição/fonte", /Copasa/.test(txt(".mx-detail .label", s5)));
      click('[data-testid="matrix-focus-sabesp"]', s5); ok("P05: destaque de empresa", q('td[data-col="sanepar"]', s5).classList.contains("dim"));
      go(5); const s6 = slides[5]; const e50 = txt('[data-testid="bar-sanepar"]', slides[5].querySelectorAll(".chartbox")[1]);
      click('[data-testid="retention-100"]', s6); const e100 = txt('[data-testid="bar-sanepar"]', slides[5].querySelectorAll(".chartbox")[1]);
      ok("P06: retenção muda teto", e50 && e100 && e50 !== e100 && state.retention === "100", `${e50} → ${e100}`);
      go(6); const s7 = slides[6]; click('[data-testid="method-sabesp"]', s7); ok("P07: troca de empresa", state.method === "sabesp" && /Sabesp/.test(txt(".chartbar h3", s7)));
      go(7); const s8 = slides[7]; click('[data-testid="result-copasa"]', s8); ok("P08: troca de empresa na grade", state.result === "copasa");
      const cell = q('[data-testid="cell-0-0"]', s8); cell.dispatchEvent(new MouseEvent("click", { bubbles: true }));
      ok("P08: ponto da grade selecionado", /WACC/.test(txt('[data-testid="heat-detail"]', s8)) && /grid/.test(state.cell));
      click('[data-testid="grid-reset"]', s8);
      const comp8 = M.pages[7].companies[state.result], base8 = comp8.grid.find((c) => c.wi === comp8.base_wi && c.gi === 1);
      ok("P08: restaurar caso-base", base8 && state.cell === base8.case, state.cell);
      go(8); const s9 = slides[8]; click('[data-testid="scenario-execution_adverse"]', s9);
      ok("P09: cenário adverso mostra N/D", state.scenario === "execution_adverse" && /N\/D/.test(txt('[data-testid="scen-copasa"]', s9)));
      ok("P09: três gatilhos", s9.querySelectorAll(".trig").length === 3);
      go(9); const s10 = slides[9]; ok("P10: régua de compra e três gatilhos", !!q('[data-testid="buy-ladder"]', s10) && s10.querySelectorAll(".dtrig-row").length === 3);
      click('[data-testid="all-sources"]', s10); ok("P10: todas as fontes", drawer.classList.contains("open") && q("#drawer li"));
      closeDrawer(); click('[data-testid="restart"]', s10); ok("P10: recomeçar", current === 0);
      const sr = stage.getBoundingClientRect();
      ok("palco cabe na janela", sr.left >= -1 && sr.top >= -1 && sr.right <= innerWidth + 1 && sr.bottom <= innerHeight + 1, `${Math.round(sr.left)},${Math.round(sr.top)},${Math.round(sr.right)},${Math.round(sr.bottom)} em ${innerWidth}×${innerHeight}`);
      toggleRec(); ok("modo gravação reserva câmera", document.body.classList.contains("recording") && getComputedStyle(document.getElementById("camera")).display !== "none");
      const cam = document.getElementById("camera").getBoundingClientRect(), hits = [];
      for (let i = 0; i < slides.length; i++) {
        go(i);
        for (const el of slides[i].querySelectorAll("*")) {
          const b = el.getBoundingClientRect();
          if (b.width && b.height && b.left < cam.right && b.right > cam.left && b.top < cam.bottom && b.bottom > cam.top) { hits.push(`P${i + 1}:${el.tagName}`); break; }
        }
      }
      ok("gravação: nada sob a câmera (10 páginas)", hits.length === 0, hits.join(" ")); toggleRec();
      const ext = [...document.querySelectorAll("script[src],link[href],img[src],iframe,object")].filter((e) => /^https?:/i.test(e.getAttribute("src") || e.getAttribute("href") || ""));
      ok("sem recursos externos", ext.length === 0, ext.length);
      ok("marcas focáveis com rótulo", [...document.querySelectorAll(".mark")].every((g) => g.getAttribute("tabindex") === "0" && g.getAttribute("aria-label")));
      ok("cada página tem fontes", M.pages.every((x) => x.sources.length > 0));
      go(0);
    } catch (err) { ok("execução do autoteste", false, err.message); }
    const layout = auditLayout();
    ok('geometria: textos sem sobreposição ou corte', layout.status==='passed', JSON.stringify(layout.errors.slice(0,12)));
    ok('fontes da marca carregadas', ['Space Grotesk','Inter','JetBrains Mono'].every(f => document.fonts.check(`500 20px "${f}"`)));
    const passed = R.every((r) => r.pass);
    const pre = h("pre", { id: "selftest-result" }, JSON.stringify({ status: passed ? "passed" : "failed", checks: R, layout }));
    pre.style.display = "none"; document.body.append(pre);
    document.title = `SELFTEST ${passed ? "passed" : "failed"}`;
  }
  if (/[?&]selftest=1/.test(location.search)) document.fonts.ready.then(selftest);
})();
