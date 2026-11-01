"""AN01 — fixar a fotografia de entrada da Parte 1.

Copia os insumos canônicos atuais e as extrações adicionais para
data/interim/analysis/baseline/<snapshot_id>/files, com hash e origem, e verifica os
originais ativos do inventário. A análise lê somente dessa cópia; publicações globais posteriores não
alteram a entrada em uso.
"""
from __future__ import annotations

import csv
import io
import importlib.metadata as md
import platform
import zipfile
from pathlib import Path

from .common import REPO, assert_writable, copy_into, now_iso, read_json, sha256_bytes, sha256_file, write_json

BASELINE_ROOT = REPO / "data/interim/analysis/baseline"

COPY_GLOBS = [
    "config/collection.json",
    "data/catalog/completion_requirements.json",
    "data/catalog/cell_issue_mapping.csv",
    "data/catalog/original_files_manifest.json",
    "data/catalog/two_part_execution.json",
    "data/processed/*.csv",
    "data/processed/*.json",
    "data/interim/original_models.json",
    "data/interim/pdf_text/*.json",
    "data/interim/acquisitions/*.json",
    "outputs/qa/extended_input_audit.csv",
    "resources/modelos_originais/*/*.xlsx",
    "data/raw/analysis/*/*",
    "data/raw/reguladores/*.html",
    "data/raw/ri/*.html",
    "data/raw/ri/*/*.html",
]
# Grandes demais e não usadas diretamente; apenas hash registrado.
HASH_ONLY = ["data/processed/sinisa_municipal.csv"]
LEGACY_MODULES = ["scripts/model.py", "scripts/financial_audit.py", "scripts/analysis_outputs.py", "scripts/common.py"]
# PDFs/CSVs brutos já adquiridos cujo texto/linhas ainda não estavam extraídos.
EXTRA_PDFS = {
    "sanepar_release_2025": "data/raw/ri/sanepar/sanepar_release_2025__5f7297a26c7d.pdf",
    "sanepar_plano_capex_2026_2030": "data/raw/ri/sanepar/sanepar_plano_capex_2026_2030__89a39155fba4.pdf",
    "sabesp_apresentacao_institucional_2025": "data/raw/analysis/sabesp/sabesp_apresentacao_mziq_e0de9896.pdf",
    # Plano 13 (01/11/2026): fontes primárias publicadas antes do corte, lidas em 01/11.
    "urae1_anexo_viii": "data/raw/analysis/urae1/urae1_anexo_viii_formacao_tarifa_inicial_apostilado.pdf",
    "agepar_nt_006_2025": "data/raw/analysis/agepar/agepar_nt_006_2025_3rtp_sanepar.pdf",
    "copasa_fr_20260611": "data/raw/analysis/copasa/copasa_fato_relevante_20260611_preco_oferta.pdf",
    "sanepar_fr_20261028_sainp": "data/raw/analysis/sanepar/sanepar_fato_relevante_20261028_sainp.pdf",
}
# Insumos que podem crescer depois da fotografia de 31/10 sem alterar o recorte (coleta própria da Parte 1).
DERIVE_REFRESH = ["data/raw/analysis/*/*"]
CVM_CAPITAL_ZIPS = ["data/raw/cvm/cvm_itr_2026__eaac6b78aaf0.zip", "data/raw/cvm/cvm_dfp_2025__cdce6cc0e0bb.zip"]
TESOURO = "data/raw/tesouro/tesouro_taxas__84f53c4bd781.csv"
ISSUER_CNPJ = {"43.776.517/0001-80": "sabesp", "17.281.106/0001-03": "copasa", "76.484.013/0001-45": "sanepar"}
PACKAGES = ["pandas", "numpy", "openpyxl", "XlsxWriter", "PyMuPDF", "beautifulsoup4"]


def _versions() -> dict:
    out = {"python": platform.python_version()}
    for name in PACKAGES:
        try:
            out[name] = md.version(name)
        except md.PackageNotFoundError:
            out[name] = None
    return out


def _extract_pdf(src: Path) -> dict:
    import pymupdf

    doc = pymupdf.open(src)
    return {"origin": src.relative_to(REPO).as_posix(), "origin_sha256": sha256_file(src),
            "pages": [{"page": i + 1, "text": p.get_text()} for i, p in enumerate(doc)]}


def _capital_rows() -> dict:
    rows = []
    for z in CVM_CAPITAL_ZIPS:
        path = REPO / z
        with zipfile.ZipFile(path) as zf:
            name = next(n for n in zf.namelist() if "composicao_capital" in n)
            for i, r in enumerate(csv.DictReader(io.TextIOWrapper(zf.open(name), encoding="latin-1"), delimiter=";"), start=2):
                if r["CNPJ_CIA"] in ISSUER_CNPJ:
                    rows.append({**{k: v for k, v in r.items() if k != "DENOM_CIA"}, "entity_id": ISSUER_CNPJ[r["CNPJ_CIA"]],
                                 "origin": z, "origin_sha256": sha256_file(path), "locator": f"{name}; linha {i}"})
    return {"rows": rows}


def _tesouro_rows() -> dict:
    path = REPO / TESOURO
    rows = []
    with open(path, encoding="latin-1") as f:
        for i, r in enumerate(csv.DictReader(f, delimiter=";"), start=2):
            if r["Data Base"] == "30/10/2026":
                rows.append({**r, "locator": f"tesouro_taxas.csv; linha {i}"})
    return {"origin": TESOURO, "origin_sha256": sha256_file(path), "rows": rows}


def _original_check() -> dict:
    manifest = read_json(REPO / "data/catalog/original_files_manifest.json")
    checked, mismatched = 0, []
    for item in manifest["files"]:
        # Documentos mantidos (contexto/planos) mudam por desenho; só bytes preservados são conferidos.
        if item.get("content_policy") != "preserve_bytes":
            continue
        path, expected = item["current_path"], item["sha256"]
        actual = sha256_file(REPO / path) if (REPO / path).is_file() else None
        checked += 1
        if actual != expected:
            mismatched.append(path)
    return {"checked": checked, "mismatched": mismatched}


def derive_snapshot(parent: Path, baseline_root: Path = BASELINE_ROOT) -> Path:
    """Fotografia derivada: mantém os insumos da fotografia-mãe e acrescenta só a coleta própria nova.

    Depois da publicação do contrato 1.0, data/processed passou a conter as saídas do pacote; uma
    fotografia `new` capturaria essas saídas como se fossem insumos. A derivada copia os insumos
    canônicos da mãe (31/10) e atualiza apenas data/raw/analysis e as extrações de EXTRA_PDFS.
    """
    meta = read_json(parent / "snapshot.json")
    refresh = sorted({p for g in DERIVE_REFRESH for p in REPO.glob(g) if p.is_file()})
    refresh_rel = {p.relative_to(REPO).as_posix() for p in refresh}
    kept = [e for e in meta["files"] if e["role"] != "derived_extraction" and e["path"] not in refresh_rel
            and not any(Path(e["path"]).match(g) for g in DERIVE_REFRESH)]
    entries = [dict(e) for e in kept]
    entries += [{"path": r, "sha256": sha256_file(REPO / r), "bytes": (REPO / r).stat().st_size, "role": "input_copy"} for r in sorted(refresh_rel)]
    derived = {f"derived/pdf_text/{k}.json": _extract_pdf(REPO / v) for k, v in EXTRA_PDFS.items()}
    for name in ("derived/cvm_capital_composition.json", "derived/tesouro_20261030.json"):
        derived[name] = read_json(parent / "files" / name)  # mesmas extrações da mãe (insumos brutos inalterados)
    digest_src = meta["snapshot_id"] + "".join(e["path"] + e["sha256"] for e in entries) + "".join(sorted(derived))
    snapshot_id = "snap_20261031_" + sha256_bytes(digest_src.encode())[:10]
    target = assert_writable(baseline_root / snapshot_id)
    if (target / "snapshot.json").exists():
        return target
    for e in kept:
        if e["role"] == "input_copy":
            copy_into(parent / "files" / e["path"], target / "files" / e["path"])
    for r in sorted(refresh_rel):
        copy_into(REPO / r, target / "files" / r)
    for name, payload in derived.items():
        write_json(target / "files" / name, payload)
        entries.append({"path": name, "sha256": sha256_file(target / "files" / name), "bytes": (target / "files" / name).stat().st_size,
                        "role": "derived_extraction"})
    originals = _original_check()
    if originals["mismatched"]:
        raise RuntimeError(f"Originais alterados: {originals['mismatched']}")
    write_json(target / "snapshot.json", {
        "snapshot_id": snapshot_id, "created_at": now_iso(), "part_id": "analysis", "derived_from": meta["snapshot_id"],
        "scope": meta.get("scope"), "market_asof": "2026-10-30", "valuation_date": "2026-10-30",
        "information_cutoff": "2026-10-31T18:25:27-03:00", "environment": _versions(), "originals": originals, "files": entries,
        "added_or_refreshed": sorted(refresh_rel - {e["path"] for e in meta["files"]}),
        "note": "Derivada da fotografia-mãe: insumos canônicos de 31/10 preservados; só a coleta própria (data/raw/analysis) e suas extrações foram atualizadas.",
    })
    return target


def create_snapshot(baseline_root: Path = BASELINE_ROOT) -> Path:
    files, entries = [], []
    for pattern in COPY_GLOBS:
        files.extend(sorted(p for p in REPO.glob(pattern) if p.is_file() and p.relative_to(REPO).as_posix() not in HASH_ONLY))
    for path in files:
        entries.append({"path": path.relative_to(REPO).as_posix(), "sha256": sha256_file(path), "bytes": path.stat().st_size, "role": "input_copy"})
    for mod in LEGACY_MODULES:
        entries.append({"path": mod, "sha256": sha256_file(REPO / mod), "bytes": (REPO / mod).stat().st_size, "role": "legacy_module_readonly"})
    for h in HASH_ONLY:
        entries.append({"path": h, "sha256": sha256_file(REPO / h), "bytes": (REPO / h).stat().st_size, "role": "hash_only_not_copied"})
    derived = {f"derived/pdf_text/{k}.json": _extract_pdf(REPO / v) for k, v in EXTRA_PDFS.items()}
    derived["derived/cvm_capital_composition.json"] = _capital_rows()
    derived["derived/tesouro_20261030.json"] = _tesouro_rows()
    digest_src = "".join(e["path"] + e["sha256"] for e in entries) + "".join(sorted(derived))
    snapshot_id = "snap_20261031_" + sha256_bytes(digest_src.encode())[:10]
    target = assert_writable(baseline_root / snapshot_id)
    if (target / "snapshot.json").exists():
        return target  # idempotente: mesmo conteúdo, mesma fotografia
    for path in files:
        copy_into(path, target / "files" / path.relative_to(REPO))
    for name, payload in derived.items():
        write_json(target / "files" / name, payload)
        entries.append({"path": name, "sha256": sha256_file(target / "files" / name), "bytes": (target / "files" / name).stat().st_size, "role": "derived_extraction"})
    cfg = read_json(REPO / "config/collection.json")
    originals = _original_check()
    if originals["mismatched"]:
        raise RuntimeError(f"Originais alterados: {originals['mismatched']}")
    write_json(target / "snapshot.json", {
        "snapshot_id": snapshot_id, "created_at": now_iso(), "part_id": "analysis",
        "scope": cfg.get("scope"), "market_asof": "2026-10-30", "valuation_date": "2026-10-30",
        "information_cutoff": "2026-10-31T18:25:27-03:00", "environment": _versions(),
        "originals": originals, "files": entries,
        "note": "Cópia de trabalho da Parte 1; publicações globais posteriores não alteram esta entrada.",
    })
    return target
