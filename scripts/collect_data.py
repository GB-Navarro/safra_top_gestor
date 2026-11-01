"""Public acquisition; manual imports are never manufactured."""
from __future__ import annotations

import argparse
import concurrent.futures
from urllib.parse import quote, urlencode

from common import ROOT, acquisitions, fetch, read_csv, read_json, sync_sources, write_json


def jobs():
    cfg = read_json("config/collection.json")
    sources = cfg["sources"]
    out = []
    def add(key, url, directory, extension, issuer="", **extra):
        out.append(dict(key=key, url=url, directory=f"data/raw/{directory}", extension=extension, issuer=issuer, **extra))
    add("cvm_cadastro", sources["cvm"]["cadastro"], "cvm", "csv", "CVM")
    for year in cfg["scope"]["historical_financial_years"]:
        add(f"cvm_dfp_{year}", sources["cvm"]["dfp_pattern"].format(year=year), "cvm", "zip", "CVM", reference_date=f"{year}-12-31")
    for year in cfg["scope"]["itr_years"]:
        add(f"cvm_itr_{year}", sources["cvm"]["itr_pattern"].format(year=year), "cvm", "zip", "CVM")
    for series, start in [(432, "01/01/2021"), (433, "01/01/2021")]:
        url = sources["bcb"]["sgs_pattern"].format(series=series) + "?" + urlencode(dict(formato="json", dataInicial=start, dataFinal="30/10/2026"))
        add(f"bcb_sgs_{series}", url, "bcb", "json", "BCB")
    for year in sources["bcb"]["focus_reference_years"]:
        params = {"$filter": f"Indicador eq 'IPCA' and Data le '2026-10-31' and DataReferencia eq '{year}' and baseCalculo eq 0", "$orderby": "Data desc", "$top": "1", "$format": "json"}
        add(f"bcb_focus_ipca_{year}", sources["bcb"]["focus_endpoint"] + "?" + urlencode(params, quote_via=quote), "bcb", "json", "BCB")
    add("tesouro_discovery", sources["tesouro"]["discovery_url"], "tesouro", "json", "Tesouro Nacional")
    registry = read_csv("data/catalog/source_registry.csv")
    for row in registry:
        if row["registry_id"].startswith("DOC_"):
            add(row["registry_id"].lower(), row["entry_url"], row["raw_directory"].removeprefix("data/raw/"), "pdf", row["issuer"])
        elif row["registry_id"] in ("SINISA", "MARCO_LEGAL", "COMPETICAO", "AGEPAR", "RI_SAPR"):
            add(row["registry_id"].lower(), row["entry_url"], row["raw_directory"].removeprefix("data/raw/"), "html", row["issuer"])
    add("safra_landing_2026", "https://www.safra.com.br/lp/safra-top-gestor.htm", "orientacoes", "html", "Safra")
    add("safra_regulamento_2026", "https://www.safra.com.br/data/files/76/64/7B/85/0ABCE910FDA2D4E9E3ADF9C2/Regulamento_Safra_Top_Gestor_2026.pdf", "orientacoes", "pdf", "Safra")
    extra_path = ROOT / "config/extra_sources.json"
    if extra_path.exists():
        known = {j["key"] for j in out}
        out.extend(j for j in read_json("config/extra_sources.json") if j["key"] not in known)
    return out


def collect(offline=False, selected=None):
    requested = [j for j in jobs() if selected is None or j["key"] in selected]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(fetch, job, offline): job for job in requested}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print(result["key"], result["status"], result.get("bytes", result.get("http_status", "")), flush=True)
    sync_sources()
    all_sources = acquisitions()
    write_json("outputs/qa/acquisition_status.json", {"downloaded": sum(s["status"] == "downloaded" for s in all_sources), "failed": [s for s in all_sources if s["status"] != "downloaded"]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--keys", nargs="*")
    args = parser.parse_args()
    collect(args.offline, args.keys)
