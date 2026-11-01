"""EN01 — fotografia própria da Parte 2: insumos legados e peças atuais, antes de qualquer publicação.

Feita uma vez (idempotente); registra hash/origem e H07 desconhecido. Serve ao adaptador baseline e
à reversão, e prova o estado anterior às peças regeneradas.
"""
from __future__ import annotations

import hashlib
import platform
from pathlib import Path

from .common import REPO, copy, now_iso, read_json, sha256_file, write_json

ROOT = REPO / "data/interim/production/baseline"
GLOBS = ["config/collection.json", "config/video_segments.json", "data/catalog/completion_requirements.json", "data/catalog/html_slide_plan.json",
         "data/processed/*.csv", "data/processed/*.json", "outputs/draft/*.pptx", "outputs/draft/*.pdf", "outputs/draft/*.md", "outputs/draft/*.xlsx",
         "outputs/draft/figuras/*", "outputs/draft/teleprompter/*", "outputs/draft/coleta/*", "data/interim/financial_reconciliation.csv"]
SKIP = {"data/processed/sinisa_municipal.csv", "data/processed/cvm_accounts.csv"}
LEGACY_SCRIPTS = ["scripts/presentation.py", "scripts/render_slides.py", "scripts/package_outputs.py", "scripts/assemble_video.py", "scripts/validate.py",
                  "scripts/run_esg.py"]


def ensure() -> Path:
    existing = sorted(p for p in ROOT.glob("legacy_*") if (p / "snapshot.json").is_file())
    if existing:
        return existing[0]  # a primeira fotografia é a referência do estado anterior às peças regeneradas
    files = []
    for g in GLOBS:
        files += [p for p in sorted(REPO.glob(g)) if p.is_file() and p.relative_to(REPO).as_posix() not in SKIP]
    entries = [{"path": p.relative_to(REPO).as_posix(), "sha256": sha256_file(p), "bytes": p.stat().st_size} for p in files]
    entries += [{"path": s, "sha256": sha256_file(REPO / s), "role": "legacy_script_hash_only"} for s in LEGACY_SCRIPTS]
    sid = "legacy_" + hashlib.sha256("".join(e["path"] + e["sha256"] for e in entries).encode()).hexdigest()[:10]
    target = ROOT / sid
    for p in files:
        copy(p, target / "files" / p.relative_to(REPO))
    write_json(target / "snapshot.json", {"snapshot_id": sid, "created_at": now_iso(), "part_id": "production", "python": platform.python_version(),
                                          "scope": read_json(REPO / "config/collection.json").get("scope"), "files": entries,
                                          "h07": "instruções privadas não recebidas: horário/canal/formato desconhecidos",
                                          "note": "Estado das peças e dados canônicos antes da primeira publicação da Parte 2."})
    return target
