"""Retain municipal SINISA observations; never average municipal percentages."""
from __future__ import annotations

import io
import unicodedata
import zipfile

import pandas as pd

from common import ROOT, acquisitions, write_csv, write_json


def plain(x):
    return "".join(c for c in unicodedata.normalize("NFKD", str(x)) if not unicodedata.combining(c)).lower()


def number(x):
    if pd.isna(x):
        return None
    if isinstance(x, (float, int)):
        return float(x)
    try:
        return float(str(x).replace(".", "").replace(",", "."))
    except ValueError:
        return None


def extract():
    records, metadata = [], []
    for source in acquisitions():
        if source["status"] != "downloaded" or source["key"] not in ("sinisa_agua_planilhas", "sinisa_esgoto_planilhas"):
            continue
        with zipfile.ZipFile(ROOT / source["local_path"]) as archive:
            for member in archive.namelist():
                if not member.endswith(".xlsx") or "Locais e Regionais" not in member or "balanc" in plain(member):
                    continue
                frame = pd.read_excel(io.BytesIO(archive.read(member)), header=None)
                header = next((i for i in range(min(20, len(frame))) if frame.iloc[i].astype(str).eq("CAD0006").any()), None)
                if header is None:
                    continue
                columns = frame.iloc[header].fillna("").astype(str).tolist()
                descriptions = frame.iloc[header - 2].fillna("").astype(str).tolist()
                units = frame.iloc[header - 1].fillna("").astype(str).tolist()
                data = frame.iloc[header + 1:].copy()
                data.columns = columns
                if "UF" not in data or "CAD0006" not in data:
                    continue
                for entity, state, acronym in [("sabesp", "SP", "SABESP"), ("copasa", "MG", "COPASA"), ("sanepar", "PR", "SANEPAR")]:
                    selected = data[(data["UF"] == state) & (data["CAD0006"].astype(str).str.strip().str.upper() == acronym)]
                    # State+full issuer name matters: SANEPAR also names a PA utility.
                    for idx, row in selected.iterrows():
                        for j, code in enumerate(columns):
                            if not code.startswith(("IAG", "IES", "GFI", "GTA", "GTE")):
                                continue
                            value = number(row.iloc[j])
                            if value is None:
                                continue
                            records.append(dict(entity_id=entity, state=state, municipality=row.get("cod_IBGE", ""), provider_name=row.get("CAD0005", ""), metric_code=code, description=descriptions[j], unit=units[j], value=value, reference_year=2024, source_id=source["source_id"], source_location=f"{member}; sheet 1; row {idx+1}; column {j+1}"))
                    metadata.append(dict(entity_id=entity, workbook=member, municipal_rows=len(selected), source_id=source["source_id"]))
    write_csv("data/processed/sinisa_municipal.csv", records)
    energy = []
    for entity in ("sabesp", "copasa", "sanepar"):
        selected = [r for r in records if r["entity_id"] == entity and r["metric_code"] == "GFI2004"]
        if selected:
            energy.append(dict(entity_id=entity, metric_id="water_electricity_expense_sinisa", value_brl_million=sum(r["value"] for r in selected) / 1e6, scope="municipal reported water service; not consolidated financial statement", municipalities=len(selected), source_id=selected[0]["source_id"], reference_year=2024))
    write_json("data/processed/sinisa_energy.json", energy)
    write_json("outputs/qa/sinisa_extraction.json", {"observations": len(records), "workbooks": metadata, "energy": energy, "warning": "Municipal ratios are not averaged. Company acronym matched jointly with state to exclude homonyms; cost sums retain water/municipal scope."})
    print("SINISA observations", len(records), "energy", energy)


if __name__ == "__main__":
    extract()
