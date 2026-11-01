"""Exportação HTML10 → PDF → PPTX fiel: página renderizada a 3840px e texto/falas nas notas.

O perfil PPTX9 editável continua separado. Esta exportação preserva a composição do HTML,
sem prometer interatividade ou elementos de layout editáveis no PowerPoint.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from .common import writable


def build(pdf: Path, out: Path, model: dict) -> Path:
    import pymupdf
    from pptx import Presentation
    from pptx.util import Inches

    writable(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333333), Inches(7.5)
    prs.core_properties.title = 'Saneamento e valor — asset.dev (HTML10)'
    prs.core_properties.subject = 'Design de marcadev.html; exportação fiel do HTML de dez páginas'
    prs.core_properties.author = 'asset.dev'
    with pymupdf.open(pdf) as doc:
        if len(doc) != 10:
            raise ValueError('A exportação exige exatamente dez páginas')
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=pymupdf.Matrix(3840/page.rect.width, 3840/page.rect.width), alpha=False)
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            image = slide.shapes.add_picture(BytesIO(pix.tobytes('png')), 0, 0, width=prs.slide_width, height=prs.slide_height)
            image.name = f"{model['pages'][i]['id']} — {model['pages'][i]['title']}"
            image._element.nvPicPr.cNvPr.set('descr', page.get_text().strip())
            slide.notes_slide.notes_text_frame.text = (
                f"asset.dev · {model['pages'][i]['id']} · pacote {model['bundle_id']}\n"
                'Composição renderizada a partir do HTML/PDF: imagem de alta resolução; '
                'para editar o layout ou os controles, usar o HTML-fonte.\n\n' + page.get_text().strip()
                + '\n\nAfirmações e evidências:\n' + '\n'.join(model['pages'][i]['claim_texts'].values())
            )
    prs.save(str(out))
    return out
