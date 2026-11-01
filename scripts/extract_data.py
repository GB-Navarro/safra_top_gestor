"""Version-aware CVM extraction and lossless local model/PDF audit."""
from __future__ import annotations

import json
import re
import unicodedata
import zipfile
from datetime import date, datetime

import openpyxl
import pandas as pd
from pypdf import PdfReader

from common import ROOT, acquisitions, now, read_json, sha256, sync_sources, write_csv, write_json

ENTITIES = {14443: "sabesp", 19445: "copasa", 18627: "sanepar"}


def plain(value):
    return "".join(c for c in unicodedata.normalize("NFKD", str(value)) if not unicodedata.combining(c)).upper().strip()


def extract_cvm():
    cutoff = read_json("config/collection.json")["scope"]["information_cutoff"][:10]
    account_rows, doc_rows, checks = [], [], []
    for source in acquisitions():
        if source["status"] != "downloaded" or not re.fullmatch(r"cvm_(dfp|itr)_\d{4}", source["key"]):
            continue
        with zipfile.ZipFile(ROOT / source["local_path"]) as archive:
            main_name = next(n for n in archive.namelist() if re.fullmatch(r"(?:dfp|itr)_cia_aberta_\d{4}\.csv", n))
            with archive.open(main_name) as stream:
                main = pd.read_csv(stream, sep=";", encoding="latin1", dtype=str, keep_default_na=False)
            main["code"] = pd.to_numeric(main["CD_CVM"], errors="coerce")
            main = main[main["code"].isin(ENTITIES)].copy()
            main["received_date"] = pd.to_datetime(main["DT_RECEB"], errors="coerce").dt.strftime("%Y-%m-%d")
            main = main[(main["received_date"] <= cutoff) & (main["DT_REFER"] <= cutoff)]
            main["numeric_version"] = pd.to_numeric(main["VERSAO"])
            main = main.sort_values("numeric_version").drop_duplicates(["code", "DT_REFER"], keep="last")
            eligible = {(int(r["code"]), r["DT_REFER"]): r for _, r in main.iterrows()}
            for _, row in main.iterrows():
                doc_rows.append({"entity_id": ENTITIES[int(row["code"])], "reference_date": row["DT_REFER"], "version": row["VERSAO"], "published_at": row["received_date"], "document_id": row["ID_DOC"], "document_url": row["LINK_DOC"], "source_id": source["source_id"], "source_location": main_name})
            picked = []
            for member in archive.namelist():
                match = re.search(r"_(BPA|BPP|DRE|DFC_MI|DFC_MD|DVA)_(con|ind)_", member)
                if not match:
                    continue
                statement, consolidation = match.groups()
                with archive.open(member) as stream:
                    for chunk in pd.read_csv(stream, sep=";", encoding="latin1", dtype=str, keep_default_na=False, chunksize=120000):
                        code_series = pd.to_numeric(chunk["CD_CVM"], errors="coerce")
                        selected = chunk[code_series.isin(ENTITIES)]
                        for idx, row in selected.iterrows():
                            code = int(row["CD_CVM"])
                            document = eligible.get((code, row["DT_REFER"]))
                            if document is None or int(row["VERSAO"]) != int(document["VERSAO"]) or plain(row["ORDEM_EXERC"]) != "ULTIMO":
                                continue
                            if row["DT_FIM_EXERC"] > cutoff:
                                continue
                            scale = plain(row["ESCALA_MOEDA"])
                            if scale not in ("MIL", "UNIDADE") or plain(row["MOEDA"]) != "REAL":
                                raise ValueError(f"Unexpected CVM currency/scale: {row['MOEDA']}/{scale}")
                            # Earnings per share is expressed in reais/share even when
                            # the statement's currency scale is MIL. Keep this subtree
                            # raw, never label it millions of reais or divide by 1000.
                            per_share = statement == "DRE" and row["CD_CONTA"].startswith("3.99")
                            picked.append({"entity_id": ENTITIES[code], "statement": statement, "scope": "consolidated" if consolidation == "con" else "individual", "reference_date": row["DT_REFER"], "period_start": row.get("DT_INI_EXERC", ""), "period_end": row["DT_FIM_EXERC"], "account_code": row["CD_CONTA"], "account_name": row["DS_CONTA"], "value_brl_million": "" if per_share else float(row["VL_CONTA"]) / (1000 if scale == "MIL" else 1000000), "value_unit": "BRL_per_share_source_raw" if per_share else "BRL_million", "raw_value": row["VL_CONTA"], "raw_scale": scale, "version": row["VERSAO"], "published_at": document["received_date"], "document_id": document["ID_DOC"], "source_id": source["source_id"], "source_location": f"{member}; CSV linha {idx + 2}; conta {row['CD_CONTA']}"})
            # Use consolidated per issuer/statement/document, individual only if absent.
            con_keys = {(r["entity_id"], r["statement"], r["reference_date"]) for r in picked if r["scope"] == "consolidated"}
            kept = [r for r in picked if r["scope"] == "consolidated" or (r["entity_id"], r["statement"], r["reference_date"]) not in con_keys]
            account_rows.extend(kept)
            checks.append({"source": source["key"], "documents": len(main), "accounts": len(kept)})
    write_csv("data/processed/cvm_accounts.csv", account_rows)
    write_csv("data/processed/cvm_documents.csv", doc_rows)
    write_json("outputs/qa/cvm_extraction.json", {"cutoff": cutoff, "packages": checks, "accounts": len(account_rows), "note": "Account/version/unit extraction verified; semantic mapping and notes are separate."})
    return account_rows


def serialize(value):
    return value.isoformat() if isinstance(value, (datetime, date)) else value


def extract_models():
    result = {}
    for path in sorted((ROOT / "resources/modelos_originais").rglob("*.xlsx")):
        cached = openpyxl.load_workbook(path, data_only=True)
        formulas = openpyxl.load_workbook(path, data_only=False)
        entity = path.parent.name
        cells = {}
        for sheet in cached.sheetnames:
            cells[sheet] = {}
            for row in cached[sheet].iter_rows():
                for cell in row:
                    formula = formulas[sheet][cell.coordinate].value
                    if cell.value is not None or formula is not None:
                        cells[sheet][cell.coordinate] = {"cached": serialize(cell.value), "formula_or_literal": serialize(formula)}
        result[path.name] = {"entity_id": entity, "path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "external_links": len(formulas._external_links), "cells": cells}
    write_json("data/interim/original_models.json", result)
    return result


def extract_pdfs():
    for source in acquisitions():
        if source["status"] != "downloaded" or not source.get("local_path", "").endswith(".pdf"):
            continue
        target = ROOT / "data/interim/pdf_text" / f"{source['key']}.json"
        if target.exists():
            continue
        reader = PdfReader(ROOT / source["local_path"])
        pages = [{"page": i + 1, "text": page.extract_text()} for i, page in enumerate(reader.pages)]
        write_json(target.relative_to(ROOT).as_posix(), {"source_id": source["source_id"], "sha256": source["sha256"], "pages": pages})
        print("PDF", source["key"], len(pages), flush=True)
    for path in (ROOT / "resources/documentos_financeiros").rglob("*.pdf"):
        key = "local_" + sha256(path)[:12]
        target = ROOT / "data/interim/pdf_text" / f"{key}.json"
        if target.exists():
            continue
        reader = PdfReader(path)
        write_json(target.relative_to(ROOT).as_posix(), {"source_id": key, "local_path": path.relative_to(ROOT).as_posix(), "pages": [{"page": i + 1, "text": p.extract_text()} for i, p in enumerate(reader.pages)]})


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1 or "--models" in sys.argv:
        print("Models", len(extract_models()), flush=True)
    if len(sys.argv) == 1 or "--pdf" in sys.argv:
        extract_pdfs()
    if len(sys.argv) == 1 or "--cvm" in sys.argv:
        print("Accounts", len(extract_cvm()), flush=True)
    sync_sources()
