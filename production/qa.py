"""EN09 — verificação do sistema e de todos os formatos (software/rastreabilidade; não valida economia)."""
from __future__ import annotations

import subprocess
from pathlib import Path

from . import browser, html_pptx, narrative, release, video
from .common import REPO, sha256_file, write_json
from .consumer import Bundle

SOFFICE = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
LO_PROFILE = REPO / "outputs/qa/production/lo_profile"


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
    from pptx import Presentation
    prs = Presentation(str(path))
    parts = []
    for s in prs.slides:
        for sh in s.shapes:
            if sh.has_text_frame:
                parts.append(sh.text_frame.text)
            if getattr(sh, "has_table", False) and sh.has_table:
                parts += [c.text for r in sh.table.rows for c in r.cells]
        if s.has_notes_slide:
            parts.append(s.notes_slide.notes_text_frame.text)
    return "\n".join(parts)


def run(b: Bundle, model: dict, build: Path, qa_dir: Path, placements: list[dict], text_res: dict, profile: str = "all") -> dict:
    checks, artifacts, captures = {}, [], []
    want = {"pptx9", "html10"} if profile == "all" else {profile}
    html = build / "html/apresentacao_esg.html"
    texts = {"script": (build / "script_apresentacao.md").read_text(encoding="utf-8")}
    rec = None
    if "html10" in want:
        # HTML: interação real no navegador em duas resoluções
        st1, st2 = browser.selftest(html, 1920, 1080), browser.selftest(html, 1366, 768)
        write_json(qa_dir / "html_selftest_1920x1080.json", st1)
        write_json(qa_dir / "html_selftest_1366x768.json", st2)
        checks["html_interaction_1920"] = {"status": st1.get("status"), "checks": len(st1.get("checks", [])), "browser": str(browser.executable())}
        checks["html_interaction_1366"] = {"status": st2.get("status"), "checks": len(st2.get("checks", []))}
        doc = html.read_text(encoding="utf-8").lower()
        ext = [m for m in ('src="http', "src='http", 'href="http', "href='http", "@import", "url(http") if m in doc]
        checks["html_offline"] = {"status": "passed" if not ext else "failed", "external_refs": ext, "bytes": html.stat().st_size}
        pdf10 = browser.print_pdf(html, build / "html/apresentacao_esg.pdf")
        n10 = _pages(pdf10)
        checks["html_pdf_10_pages"] = {"status": "passed" if n10 == 10 else "failed", "pages": n10}
        pptx10 = html_pptx.build(pdf10, build / 'html/apresentacao_esg.pptx', model)
        roundtrip = pptx_to_pdf(pptx10, qa_dir / 'pptx_html10')
        n_pptx10 = _pages(roundtrip)
        checks['html_pptx_10_pages'] = {'status': 'passed' if n_pptx10 == 10 else 'failed', 'pages': n_pptx10,
                                      'source': 'HTML → PDF → páginas renderizadas a 3840px; notas com texto e evidência'}
        pptx_caps = render_pages(roundtrip, qa_dir / 'pptx_html10', 'p', 1920)
        contact_sheet(pptx_caps, qa_dir / 'pptx_html10_contact_sheet.png')
        captures += pptx_caps
        caps = [browser.screenshot(html, qa_dir / "html" / f"p{i:02d}.png", i) for i in range(1, 11)]
        rec = browser.screenshot(html, qa_dir / "html" / "rec_p01.png", 1, query="rec=1")
        small = browser.screenshot(html, qa_dir / "html" / "p08_1366x768.png", 8, 1366, 768)
        dark = [browser.screenshot(html, qa_dir / "html" / f"p{i:02d}_dark.png", i, query="theme=dark") for i in (1, 8, 10)]
        contact_sheet(caps, qa_dir / "html_contact_sheet.png")
        texts["html"] = html.read_text(encoding="utf-8")
        artifacts += [html, pdf10, pptx10]
        captures += caps + [rec, small] + dark
    if "pptx9" in want:
        # PPTX9 / apoio7
        main_pdf = pptx_to_pdf(build / "apresentacao_esg.pptx", build)
        sup_pdf = pptx_to_pdf(build / "apoio_tecnico.pptx", build)
        n9, n7 = _pages(main_pdf), _pages(sup_pdf)
        checks["pptx9_pages"] = {"status": "passed" if n9 == 9 else "failed", "pages": n9}
        checks["support7_pages"] = {"status": "passed" if n7 == 7 else "failed", "pages": n7}
        s9, s7 = render_pages(main_pdf, qa_dir / "pptx", "s"), render_pages(sup_pdf, qa_dir / "apoio", "a")
        contact_sheet(s9, qa_dir / "pptx9_contact_sheet.png")
        contact_sheet(s7, qa_dir / "support7_contact_sheet.png")
        texts["pptx9"] = _pptx_text(build / "apresentacao_esg.pptx")
        artifacts += [main_pdf, sup_pdf, build / "apresentacao_esg.pptx", build / "apoio_tecnico.pptx"]
        captures += s9 + s7
    # Consistência de números entre formatos
    key = ["V.case.sanepar.base.paper_value", "V.SAPR11.close.2026-10-30", "V.sanepar.max_entry_price", "V.case.sabesp.base.paper_value",
           "V.case.copasa.base.paper_value", "A.wacc_nominal.base"]
    miss = {k: [b.fmt(v) for v in key if b.fmt(v) not in t] for k, t in texts.items()}
    ent = b.entity_name(b.decision["entity_id"])
    checks["cross_format_numbers"] = {"status": "passed" if not any(miss.values()) and all(ent in t for t in texts.values()) else "failed",
                                      "missing": miss, "entity": ent}
    bad_fmt = [(p["id"], r) for p in model["pages"] for r in p["value_refs"] if r not in b.obs]
    checks["value_refs_resolve"] = {"status": "passed" if not bad_fmt else "failed", "unresolved": bad_fmt}
    wf = {}
    for e, comp in next(p for p in model["pages"] if p["id"] == "P07")["companies"].items():
        start = comp["items"][0]["num"]
        end = comp["items"][-1]["num"]
        wf[e] = abs(start + sum(i.get("effect_num", 0) for i in comp["items"][1:-1]) - end)
    checks["bridge_consistency"] = {"status": "passed" if max(wf.values()) < 1e-6 else "failed", "abs_gap": wf}
    slot_claims = {c for ids in b.slots.values() for c in ids}
    for prof in sorted(want):
        placed = {r["claim_id"] for r in placements if r["profile"] == prof}
        checks[f"claims_placed_{prof}"] = {"status": "passed" if slot_claims <= placed else "failed", "missing": sorted(slot_claims - placed)}
    checks["literal_numbers"] = {"status": "passed" if not text_res["lint"] else "failed", "issues": text_res["lint"]}
    over = {p: c for p, c in text_res["counts"].items() if c["estimated_seconds_at_140wpm"] > c["planned_seconds"] or c["planned_seconds"] > 600}
    checks["speech_budget"] = {"status": "passed" if not over else "failed", "profiles": text_res["counts"]}
    # Vídeo: prontidão (sem clipes não há vídeo) e teste sintético do encoder
    vr = {p: video.readiness(REPO / cfg) for p, cfg in (("pptx9", "config/video_segments.json"), ("html10", "config/video_segments_html10.json"))}
    write_json(qa_dir / "video_readiness.json", vr)
    if rec is None:  # sem HTML: quadro branco do tamanho do vídeo como fundo do teste sintético
        from PIL import Image
        rec = qa_dir / "video_selftest_frame.png"
        rec.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (1920, 1080), "white").save(rec)
    vt = video.self_test(rec)
    write_json(qa_dir / "video_selftest.json", vt)
    checks["video_encoder_selftest"] = {"status": vt["status"]}
    checks["video_readiness"] = {"status": "passed", "note": "Relato de prontidão; ausência de clipes é esperada e não gera vídeo",
                                 "profiles": {p: v["status"] for p, v in vr.items()}, "segments": {p: v["segments"] for p, v in vr.items()}}
    status = "passed" if all(c.get("status") == "passed" for c in checks.values()) else "failed"
    summary = {"build_id": build.name, "input_bundle": b.bundle_id, "input_manifest_sha256": b.manifest_sha256, "profile": profile, "status": status,
               "checks": checks, "artifacts": {p.relative_to(build).as_posix(): sha256_file(p) for p in artifacts},
               "captures": [str(p.relative_to(REPO)) for p in captures],
               "scope": "Software, formatos, interação e rastreabilidade das peças; não valida premissas econômicas nem substitui H08–H13."}
    write_json(qa_dir / "production_qa.json", summary)
    gates = release.report(release.collect(b.path, qa_dir / "production_qa.json"))
    write_json(qa_dir / "release_gates.json", {"build_id": build.name, "gates": gates})
    summary["release_gates"] = gates
    return summary
