"""EN09 — verificação do sistema e de todos os formatos (software/rastreabilidade; não valida economia)."""
from __future__ import annotations

import subprocess
from pathlib import Path

from . import browser, deck_model, html_pptx, release, video
from .common import REPO, sha256_file, write_json
from .consumer import Bundle
from .narrative import PROFILE, WPM

SOFFICE = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
LO_PROFILE = REPO / "outputs/qa/production/lo_profile"
CONTROLS = ("<button", "<nav", "<input", "<select", "<a ", 'role="button"', "tabindex")


def pptx_to_pdf(pptx: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / (pptx.stem + ".pdf")
    for _ in range(2):  # primeira execução com perfil novo pode só inicializá-lo
        subprocess.run([str(SOFFICE), f"-env:UserInstallation={LO_PROFILE.resolve().as_uri()}", "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(pptx)],
                       capture_output=True, text=True, timeout=240, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if target.is_file():
            return target
    raise RuntimeError(f"Conversão PDF falhou: {pptx.name}")


def render_pages(pdf: Path, out_dir: Path, prefix: str, width: int = 1600) -> list[Path]:
    import pymupdf
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    with pymupdf.open(pdf) as doc:
        for i, page in enumerate(doc, 1):
            zoom = width / page.rect.width
            p = out_dir / f"{prefix}_{i:02d}.png"
            page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom)).save(p)
            paths.append(p)
    return paths


def contact_sheet(images: list[Path], out: Path, cols: int = 2, w: int = 800) -> Path:
    from PIL import Image
    ims = [Image.open(p) for p in images]
    h = int(ims[0].height * w / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, h * rows), "white")
    for k, im in enumerate(ims):
        sheet.paste(im.resize((w, h)), ((k % cols) * w, (k // cols) * h))
    sheet.save(out)
    return out


def _pages(pdf: Path) -> int:
    import pymupdf
    with pymupdf.open(pdf) as d:
        return d.page_count


def _pptx_text(path: Path) -> str:
    """Texto do PPTX: caixas, tabelas, texto alternativo das imagens e notas."""
    from pptx import Presentation
    prs = Presentation(str(path))
    parts = []
    for s in prs.slides:
        for sh in s.shapes:
            if sh.has_text_frame:
                parts.append(sh.text_frame.text)
            if getattr(sh, "has_table", False) and sh.has_table:
                parts += [c.text for r in sh.table.rows for c in r.cells]
            parts += [str(d) for d in sh._element.xpath("./*[1]/p:cNvPr/@descr")]
        if s.has_notes_slide:
            parts.append(s.notes_slide.notes_text_frame.text)
    return "\n".join(parts)


def _notes(path: Path) -> list[str]:
    from pptx import Presentation
    return [s.notes_slide.notes_text_frame.text if s.has_notes_slide else "" for s in Presentation(str(path)).slides]


def run(b: Bundle, model: dict, build: Path, qa_dir: Path, placements: list[dict], text_res: dict, profile: str = PROFILE) -> dict:
    checks, artifacts, captures = {}, [], []
    n = len(model["pages"])
    html = build / "html/apresentacao_esg.html"
    texts = {"script": (build / "script_apresentacao.md").read_text(encoding="utf-8")}
    # HTML: navegação, geometria (sem sobreposição/transbordo) e ausência de controles, em duas resoluções
    st1, st2 = browser.selftest(html, 1920, 1080), browser.selftest(html, 1366, 768)
    write_json(qa_dir / "html_selftest_1920x1080.json", st1)
    write_json(qa_dir / "html_selftest_1366x768.json", st2)
    for key, st in (("html_selftest_1920", st1), ("html_selftest_1366", st2)):
        checks[key] = {"status": st.get("status"), "checks": len(st.get("checks", [])), "browser": str(browser.executable()),
                       "failed": [c["name"] for c in st.get("checks", []) if not c["pass"]]}
    doc = html.read_text(encoding="utf-8")
    low = doc.lower()
    ext = [m for m in ('src="http', "src='http", 'href="http', "href='http", "@import", "url(http") if m in low]
    checks["html_offline"] = {"status": "passed" if not ext else "failed", "external_refs": ext, "bytes": html.stat().st_size}
    markup = low[low.index("<main"):low.index("</main>")]  # só a marcação dos slides; o autoteste do script cita seletores
    controls = [t for t in CONTROLS if t in markup]
    checks["html_flat_no_controls"] = {"status": "passed" if not controls else "failed", "found": controls}
    pdf = browser.print_pdf(html, build / "html/apresentacao_esg.pdf")
    n_pdf = _pages(pdf)
    checks["html_pdf_pages"] = {"status": "passed" if n_pdf == n else "failed", "pages": n_pdf, "expected": n}
    pptx = html_pptx.build(pdf, build / "html/apresentacao_esg.pptx", model, text_res["speech"])
    roundtrip = pptx_to_pdf(pptx, qa_dir / "pptx")
    n_rt = _pages(roundtrip)
    checks["pptx_pages"] = {"status": "passed" if n_rt == n else "failed", "pages": n_rt,
                            "source": "HTML → PDF → páginas renderizadas a 3840 px; fala do slide nas notas; texto do slide no texto alternativo"}
    notes = _notes(pptx)
    missing_notes = [p["id"] for p, t in zip(model["pages"], notes) if text_res["speech"][p["block"]] not in t]
    checks["pptx_notes_have_script"] = {"status": "passed" if not missing_notes and len(notes) == n else "failed", "missing": missing_notes}
    pptx_caps = render_pages(roundtrip, qa_dir / "pptx", "p", 1920)
    contact_sheet(pptx_caps, qa_dir / "pptx_contact_sheet.png")
    caps = [browser.screenshot(html, qa_dir / "html" / f"p{i:02d}.png", i) for i in range(1, n + 1)]
    rec = [browser.screenshot(html, qa_dir / "html" / f"rec_p{i:02d}.png", i, query="rec=1") for i in (1, 7, 12)]
    small = [browser.screenshot(html, qa_dir / "html" / f"p{i:02d}_1366x768.png", i, 1366, 768) for i in (7, 9)]
    contact_sheet(caps, qa_dir / "html_contact_sheet.png")
    pdf_caps = render_pages(pdf, qa_dir / "pdf", "p", 1920)
    contact_sheet(pdf_caps, qa_dir / "pdf_contact_sheet.png")
    texts["html"], texts["pptx"] = doc.replace(" ", " "), _pptx_text(pptx).replace(" ", " ")  # espaço não separável entre número e unidade
    artifacts += [html, pdf, pptx]
    captures += caps + rec + small + pdf_caps + pptx_caps
    # Apoio técnico (7 páginas)
    sup_pdf = pptx_to_pdf(build / "apoio_tecnico.pptx", build)
    n7 = _pages(sup_pdf)
    checks["support7_pages"] = {"status": "passed" if n7 == 7 else "failed", "pages": n7}
    s7 = render_pages(sup_pdf, qa_dir / "apoio", "a")
    contact_sheet(s7, qa_dir / "support7_contact_sheet.png")
    artifacts += [sup_pdf, build / "apoio_tecnico.pptx"]
    captures += s7
    # Consistência de números entre formatos
    key = ["V.case.sanepar.base.paper_value", "V.SAPR11.close.2026-10-30", "V.sanepar.max_entry_price", "V.case.sabesp.base.paper_value",
           "V.case.copasa.base.paper_value", "A.wacc_nominal.base"]
    miss = {k: [b.fmt(v) for v in key if b.fmt(v) not in t] for k, t in texts.items()}
    ent = b.entity_name(b.decision["entity_id"])
    checks["cross_format_numbers"] = {"status": "passed" if not any(miss.values()) and all(ent in t for t in texts.values()) else "failed",
                                      "missing": miss, "entity": ent}
    bad_fmt = [(p["id"], r) for p in model["pages"] for r in p["value_refs"] + p.get("input_refs", []) if r not in b.obs]
    checks["value_refs_resolve"] = {"status": "passed" if not bad_fmt else "failed", "unresolved": bad_fmt}
    items = next(p for p in model["pages"] if p["kind"] == "calc")["bridge"]
    gap = abs(items[0]["num"] + sum(i.get("effect_num", 0) for i in items[1:-1]) - items[-1]["num"])
    checks["bridge_consistency"] = {"status": "passed" if gap < 1e-6 else "failed", "abs_gap": gap}
    broken = deck_model.guards(b)
    checks["narrative_relations"] = {"status": "passed" if not broken else "failed", "broken": broken,
                                     "note": "Relações afirmadas nos títulos e falas conferidas contra o pacote (quem rende acima do custo de capital etc.)"}
    slot_claims = {c for ids in b.slots.values() for c in ids}
    placed = {r["claim_id"] for r in placements if r["profile"] == profile}
    checks["claims_placed"] = {"status": "passed" if slot_claims <= placed else "failed", "missing": sorted(slot_claims - placed)}
    checks["literal_numbers"] = {"status": "passed" if not text_res["lint"] else "failed", "issues": text_res["lint"]}
    checks["letter_style"] = {"status": "passed" if not text_res["style"] else "failed", "issues": text_res["style"]}
    c = text_res["counts"][profile]
    over = c["estimated_seconds_at_140wpm"] > c["planned_seconds"] or c["planned_seconds"] > 600
    slow = {k: v for k, v in text_res["blocks"].items() if v["words"] / WPM * 60 > v["seconds"] + 2}
    checks["speech_budget"] = {"status": "passed" if not over and not slow else "failed", "profile": c, "blocks_over_budget": slow}
    # Vídeo: prontidão (sem clipes não há vídeo) e teste sintético do encoder
    vr = video.readiness(video.SEGMENTS)
    write_json(qa_dir / "video_readiness.json", vr)
    vt = video.self_test(caps[0])  # slide inteiro: o montador reduz e põe a câmera ao lado
    write_json(qa_dir / "video_selftest.json", vt)
    checks["video_encoder_selftest"] = {"status": vt["status"]}
    checks["video_readiness"] = {"status": "passed", "note": "Relato de prontidão; ausência de clipes é esperada e não gera vídeo",
                                 "readiness": vr["status"], "segments": vr["segments"]}
    status = "passed" if all(c.get("status") == "passed" for c in checks.values()) else "failed"
    summary = {"build_id": build.name, "input_bundle": b.bundle_id, "input_manifest_sha256": b.manifest_sha256, "profile": profile, "status": status,
               "checks": checks, "artifacts": {p.relative_to(build).as_posix(): sha256_file(p) for p in artifacts},
               "captures": [str(p.relative_to(REPO)) for p in captures],
               "scope": "Software, formatos, geometria dos slides e rastreabilidade das peças; não valida premissas econômicas nem substitui H08–H13."}
    write_json(qa_dir / "production_qa.json", summary)
    gates = release.report(release.collect(b.path, qa_dir / "production_qa.json"))
    write_json(qa_dir / "release_gates.json", {"build_id": build.name, "gates": gates})
    summary["release_gates"] = gates
    return summary
