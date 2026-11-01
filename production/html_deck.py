"""EN04 — HTML interativo de dez páginas: arquivo único, offline, dados do pacote embutidos."""
from __future__ import annotations

import html
import json
from pathlib import Path

from .common import REPO, write_text
from .brand import embedded_fonts, symbol

WEB = REPO / "presentation_web"

TEMPLATE = """<!doctype html>
<html lang="pt-BR" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Saneamento e valor — asset.dev</title>
<meta name="generator" content="production.html_deck; bundle __BUNDLE__">
<style>
__CSS__
</style>
</head>
<body>
<div id="viewport">
  <main id="stage" aria-label="Apresentação: Saneamento e valor">
    <div id="progress"></div>
    <div id="camera" aria-hidden="true">Área reservada<br>para a câmera</div>
    <div id="tools">
      <button class="ghost" id="t-theme" title="Alternar tema (T)">Tema</button>
      <button class="ghost" id="t-rec" title="Modo gravação (G)">Gravação</button>
      <button class="ghost" id="t-help" title="Atalhos (?)">?</button>
    </div>
    <nav id="nav" aria-label="Navegação">
      <button class="navbtn" id="prev" aria-label="Página anterior"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M15 5l-7 7 7 7"/></svg></button>
      <button class="navbtn" id="next" aria-label="Próxima página"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M9 5l7 7-7 7"/></svg></button>
    </nav>
    <div id="scrim"></div>
    <aside id="drawer" role="dialog" aria-modal="true" aria-labelledby="drawer-title" aria-hidden="true"></aside>
    <div id="help" role="dialog" aria-label="Atalhos">
      <div class="card">
        <h2 style="margin-top:0">Atalhos</h2>
        <p><kbd>→</kbd> <kbd>Espaço</kbd> próxima · <kbd>←</kbd> anterior · <kbd>Home</kbd>/<kbd>End</kbd> início/fim · <kbd>1</kbd>–<kbd>0</kbd> ir para a página</p>
        <p><kbd>G</kbd> modo gravação (reserva a câmera) · <kbd>T</kbd> tema claro/escuro · <kbd>Esc</kbd> fecha painéis · <kbd>?</kbd> esta ajuda</p>
        <p>Clique nos gráficos, quadrantes, abas e células. Cada número vem do pacote analítico __BUNDLE__; "Fontes e afirmações" abre a origem.</p>
        <p class="small muted">Imprimir (Ctrl+P) gera exatamente 10 páginas no estado padrão.</p>
      </div>
    </div>
    <div id="tooltip" role="tooltip"></div>
  </main>
</div>
<div id="live" class="sr-only" aria-live="polite" style="position:absolute;left:-9999px"></div>
<script id="deck-data" type="application/json">__DATA__</script>
<script>
__JS__
</script>
</body>
</html>
"""


def build(model: dict, out: Path) -> Path:
    css = embedded_fonts() + '\n' + (WEB / "deck.css").read_text(encoding="utf-8")
    js = (WEB / "deck.js").read_text(encoding="utf-8").replace('__BRAND_SYMBOL_JSON__', json.dumps(symbol()))
    data = json.dumps(model, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    doc = TEMPLATE.replace("__BUNDLE__", html.escape(model["bundle_id"])).replace("__CSS__", css).replace("__DATA__", data).replace("__JS__", js)
    lowered = doc.lower()
    if any(m in lowered for m in ('src="http', "src='http", 'href="http', "href='http", "@import", "url(http")):
        raise ValueError("HTML não pode depender de recurso externo")
    return write_text(out, doc)
