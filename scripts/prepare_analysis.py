"""Prepare auditable public market/capital references and observed accounting checks."""
from __future__ import annotations

import json
import re
import zipfile

import pandas as pd
from bs4 import BeautifulSoup

from common import ROOT, acquisitions, read_csv, read_json, write_csv, write_json


def brnumber(text):
    return float(re.sub(r"[^0-9,.-]", "", text).replace(".", "").replace(",", "."))


def prepare():
    sources = {s["key"]:s for s in acquisitions() if s["status"] == "downloaded"}
    market=[]
    for ticker in ("SBSP3","CSMG3","SAPR3","SAPR4","SAPR11"):
        source=sources["market_public_"+ticker.lower()]
        soup=BeautifulSoup((ROOT/source["local_path"]).read_bytes(),"html.parser")
        candidates=[]
        for table in soup.select("table"):
            header=table.find("tr")
            if not header or "Fech" not in header.get_text():
                continue
            for row in table.select("tr"):
                cells=[c.get_text(" ",strip=True) for c in row.find_all(["td","th"])]
                if len(cells)>=5 and cells[0]=="30/10/2026":
                    candidates.append(brnumber(cells[4]))
        if len(set(candidates))!=1:
            raise ValueError(f"Unambiguous dated close missing: {ticker}/{candidates}")
        market.append(dict(instrument_id=ticker,close=candidates[0],date="2026-10-30",source_id=source["source_id"],source_location="HTML table Cotacoes Recentes; row 30/10/2026; Fechamento",url=source["url"],status="public_provider_reference; awaiting_terminal_confirmation"))
    write_json("data/processed/market_reference.json",market)
    src=sources["cvm_itr_2026"]
    with zipfile.ZipFile(ROOT/src["local_path"]) as archive:
        member="itr_cia_aberta_composicao_capital_2026.csv"
        capital_raw=pd.read_csv(archive.open(member),sep=";",encoding="latin1",dtype=str)
        selected=capital_raw[(capital_raw.CNPJ_CIA.isin(["43.776.517/0001-80","17.281.106/0001-03","76.484.013/0001-45"]))&(capital_raw.DT_REFER=="2026-06-30")]
        write_csv("data/interim/capital_cvm_raw.csv",selected.to_dict("records"))
    cnpjs={"sabesp":"43.776.517/0001-80","copasa":"17.281.106/0001-03","sanepar":"76.484.013/0001-45"}
    capital={}
    for entity,cnpj in cnpjs.items():
        r=selected[selected.CNPJ_CIA==cnpj].iloc[0]
        ordinary=float(r.QT_ACAO_ORDIN_CAP_INTEGR)-float(r.QT_ACAO_ORDIN_TESOURO)
        preferred=float(r.QT_ACAO_PREF_CAP_INTEGR)-float(r.QT_ACAO_PREF_TESOURO)
        if entity=="copasa":
            # The composition CSV carries thousands for this issuer, unlike the
            # other two. Use the explicitly labelled release, not magnitude inference.
            outstanding=379.181
            note="Release 2T26 p26 labels shares in thousands: 379.181 thousand = 379.181 million. Rounded to source precision. Composition CSV is not uniformly unit-scaled across issuers."
            source_id=sources["doc_csmg_2t26"]["source_id"]
            location="PDF p26; Acoes em Circulacao no Fim do Periodo (milhares)"
        else:
            outstanding=(ordinary+preferred)/1e6
            note="CVM share units; Sabesp includes one special preferred share, economically immaterial at displayed precision. Capital date June, not a guarantee of unchanged October shares."
            source_id=src["source_id"]
            location=member+"; CNPJ="+cnpj+"; DT_REFER=2026-06-30; VERSAO=1"
        capital[entity]=dict(outstanding_million=outstanding,capital_date="2026-06-30",source_id=source_id,source_location=location,note=note)
    write_json("data/processed/capital_reference.json",capital)
    accounts=read_csv("data/processed/cvm_accounts.csv")
    models=read_json("data/interim/original_models.json")
    checks=[]
    for name,model in models.items():
        for row,code,label in [(6,"3.01","Receita total"),(17,"3.07","LAIR"),(18,"3.08","IR/CSLL com sinal")]:
            for year,column in zip(range(2021,2026),"CDEFG"):
                found=[r for r in accounts if r["entity_id"]==model["entity_id"] and r["statement"]=="DRE" and r["account_code"]==code and r["period_start"]==f"{year}-01-01" and r["period_end"]==f"{year}-12-31"]
                if len(found)!=1:
                    continue
                original=model["cells"]["Dados_RI"][f"{column}{row}"]["cached"]
                official=float(found[0]["value_brl_million"])*(-1 if row==18 else 1)
                difference=original-official
                checks.append(dict(workbook=name,entity_id=model["entity_id"],year=year,item=label,cell=f"Dados_RI!{column}{row}",original=original,cvm=official,difference=difference,status="within_rounding" if abs(difference)<=.1 else "difference_requires_scope_or_restatement_review",source_id=found[0]["source_id"],source_location=found[0]["source_location"]))
    write_csv("outputs/qa/workbook_input_checks.csv",checks)
    # Refresh the issuer seeds from actual CVM registration, not a guessed name.
    cad=pd.read_csv(ROOT/sources["cvm_cadastro"]["local_path"],sep=";",encoding="latin1",dtype=str)
    entities=read_csv("data/processed/entities.csv")
    for entity in entities:
        matches=cad[cad.CNPJ_CIA==entity["cnpj"]]
        if matches.empty:
            raise ValueError("CNPJ not found in official registry: "+entity["entity_id"])
        entity["legal_name"]=matches.iloc[0]["DENOM_SOCIAL"]
        entity["identity_status"]="verified_cvm_registry"
    write_csv("data/processed/entities.csv",entities)
    print("Market",{r["instrument_id"]:r["close"] for r in market})
    print("Capital",{e:r["outstanding_million"] for e,r in capital.items()})
    print("Input checks",len(checks),"differences",sum(r["status"]!="within_rounding" for r in checks))


if __name__=="__main__":
    prepare()
