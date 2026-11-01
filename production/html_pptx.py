"""Exportação HTML → PDF → PPTX fiel: cada slide é a página renderizada a 3840 px, com a fala nas notas.

O PPTX preserva a composição do HTML para quem prefere apresentar ou gravar pelo PowerPoint; o texto do slide vai
no texto alternativo da imagem e o script do falante vai nas notas. Para editar o layout, usar o HTML-fonte.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from .common import writable

PAGES = 12


def notes(page: dict, n: int, speech: str, bundle_id: str) -> str:
    sources = "; ".join(s["title"] for s in page["sources"]) or "não se aplica"
    return (f"Slide {n} · {page['voice']} · cerca de {page['seconds']} s\n\n{speech}\n\n"
            f"Fontes do slide: {sources}.\nPacote analítico {bundle_id}.")


def build(pdf: Path, out: Path, model: dict, speech: dict) -> Path:
    import pymupdf
    from pptx import Presentation
    from pptx.util import Inches

    writable(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333333), Inches(7.5)
    prs.core_properties.title = "Saneamento: onde está o valor do setor listado"
    prs.core_properties.subject = "asset.dev · Desafio Safra Top Gestor 2026 · análise setorial ESG"
    prs.core_properties.author = "asset.dev"
    with pymupdf.open(pdf) as doc:
        if len(doc) != PAGES or len(model["pages"]) != PAGES:
            raise ValueError(f"A exportação exige exatamente {PAGES} páginas")
        for i, page in enumerate(doc):
            p = model["pages"][i]
            pix = page.get_pixmap(matrix=pymupdf.Matrix(3840 / page.rect.width, 3840 / page.rect.width), alpha=False)
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            image = slide.shapes.add_picture(BytesIO(pix.tobytes("png")), 0, 0, width=prs.slide_width, height=prs.slide_height)
            image.name = f"{p['id']} · {p['title']}"
            image._element.nvPicPr.cNvPr.set("descr", page.get_text().strip())
            slide.notes_slide.notes_text_frame.text = notes(p, i + 1, speech[p["block"]], model["bundle_id"])
    prs.save(str(out))
    return out
