"""EN04 — apresentação final em HTML de 12 slides planos: arquivo único, offline, sem controles na tela.

A marcação e os gráficos vêm prontos de production.slides; o script só navega, ajusta à janela, liga o modo
gravação (G) e roda o autoteste. Imprimir gera exatamente 12 páginas.
"""
from __future__ import annotations

import html
from pathlib import Path

from . import slides
from .brand import embedded_fonts
from .common import REPO, write_text

WEB = REPO / "presentation_web"

TEMPLATE = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Saneamento e valor — asset.dev</title>
<meta name="generator" content="production.html_deck; pacote __BUNDLE__">
<style>
__CSS__
</style>
</head>
<body>
<div id="viewport">
  <main id="stage" aria-label="Apresentação: Saneamento e valor">
__SLIDES__
    <div id="camera" aria-hidden="true"></div>
  </main>
</div>
<script>
__JS__
</script>
</body>
</html>
"""


def build(model: dict, out: Path) -> Path:
    css = embedded_fonts() + "\n" + (WEB / "deck.css").read_text(encoding="utf-8")
    js = (WEB / "deck.js").read_text(encoding="utf-8")
    doc = (TEMPLATE.replace("__BUNDLE__", html.escape(model["bundle_id"])).replace("__CSS__", css)
           .replace("__SLIDES__", slides.render(model)).replace("__JS__", js))
    lowered = doc.lower()
    if any(m in lowered for m in ('src="http', "src='http", 'href="http', "href='http", "@import", "url(http")):
        raise ValueError("HTML não pode depender de recurso externo")
    return write_text(out, doc)
