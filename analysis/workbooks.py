"""AN10 — planilhas auditáveis do pacote analítico.

base_dados_coletados.xlsx: tabelas do pacote (sem fórmulas).
base_modelo_auditavel.xlsx: caso-base das três empresas com fórmulas vivas (defasagem de 2 anos),
cronograma do precatório com PV por fórmula, tabela de todos os casos (valores) e ramo legado.
"""
from __future__ import annotations

import json
from pathlib import Path

import xlsxwriter

from . import dcf

ENT_SHEET = {"sabesp": "Sabesp", "copasa": "Copasa", "sanepar": "Sanepar"}


def _cellv(x):
    if isinstance(x, (list, dict)):
        return json.dumps(x, ensure_ascii=False)
    return x


def data_workbook(path: Path, tables: dict[str, tuple[list[str], list[dict]]], readme: list[str]) -> None:
    wb = xlsxwriter.Workbook(str(path), {"nan_inf_to_errors": False})
    bold = wb.add_format({"bold": True, "bg_color": "#DDEBF7"})
    ws = wb.add_worksheet("LEIA")
    for i, line in enumerate(readme):
        ws.write(i, 0, line)
    ws.set_column(0, 0, 140)
    for name, (header, rows) in tables.items():
        ws = wb.add_worksheet(name[:31])
        ws.write_row(0, 0, header, bold)
        for r, row in enumerate(rows, start=1):
            for col, key in enumerate(header):
                val = _cellv(row.get(key))
                if val is None:
                    continue
                ws.write(r, col, val)
        ws.freeze_panes(1, 0)
        ws.autofilter(0, 0, max(len(rows), 1), len(header) - 1)
    wb.close()


def model_workbook(path: Path, inputs: dict, cases: list[dict], legacy: list[dict], schedule: list[dict], readme: list[str]) -> dict:
    """Escreve fórmulas e devolve o mapa {(entidade, campo): (aba, célula)} para o recálculo independente."""
    wb = xlsxwriter.Workbook(str(path), {"nan_inf_to_errors": False})
    bold = wb.add_format({"bold": True})
    inp = wb.add_format({"bg_color": "#E2EFDA"})
    pct = wb.add_format({"num_format": "0.00%"})
    num = wb.add_format({"num_format": "#,##0.00"})
    ws = wb.add_worksheet("LEIA")
    for i, line in enumerate(readme):
        ws.write(i, 0, line)
    ws.set_column(0, 0, 140)
    cellmap = {}
    # Cronograma do precatório (Sanepar) com PV por fórmula.
    pre = wb.add_worksheet("Precatorio")
    pre.write_row(0, 0, ["data", "componente", "valor_nominal", "valor_apos_ir", "t_anos", "fator", "pv_30out"], bold)
    pre.write(0, 8, "WACC")
    pre.write(1, 8, inputs["sanepar"]["wacc"], inp)
    for i, f in enumerate(schedule, start=1):
        r = i + 1
        y, mth, d = (int(x) for x in f["date"].split("-"))
        pre.write_formula(i, 0, f"=DATE({y},{mth},{d})")
        pre.write(i, 1, f["component"])
        pre.write(i, 2, f["nominal"], num)
        pre.write(i, 3, f["after_tax"], num)
        pre.write_formula(i, 4, f"=(A{r}-DATE(2026,10,30))/365")
        pre.write_formula(i, 5, f"=(1+$I$2)^(-E{r})")
        pre.write_formula(i, 6, f"=D{r}*F{r}")
    last = len(schedule) + 1
    pre.write(3, 8, "PV total (futuro + jul–out capitalizado)")
    pre.write_formula(4, 8, f"=SUM(G2:G{last})")
    cellmap[("sanepar", "obligation_pv")] = ("Precatorio", "I5")
    for entity, p in inputs.items():
        ws = wb.add_worksheet(ENT_SHEET[entity])
        labels = [("EBITDA recorrente 2025", "ebitda0"), ("D&A 2025", "da0"), ("Receita recorrente 2025", "revenue0"), ("Giro/receita", "wc_ratio"),
                  ("r regulatório real pré-IR", "r_pre"), ("r regulatório real pós-IR", "r_post"), ("IR+CSLL", "tax"), ("Captura", "share"),
                  ("Desvio de opex/receita", "opex_shock"), ("Fração elegível", "eligible"), ("g real da base", "g_real"), ("WACC nominal", "wacc"),
                  ("IPCA longo prazo", "pi_lr"), ("Capex caixa 2024", "capex_2024"), ("Capex caixa 2025", "capex_2025"), ("IPCA 2025 realizado", "infl_2025"),
                  ("Dívida líquida 30/06/2026", "net_debt"), ("Outros direitos de terceiros", "debt_like"), ("Poder concedente", "grantor"),
                  ("Precatório PV", "obligation_pv"), ("Fator por papel (1/ações ou unit/capitalização)", "per_paper"), ("Preço 30/10", "price"),
                  ("Fração do stub (62/365)", "stub"), ("Fração jul–out (122/365)", "rollforward")]
        ws.write_row(0, 0, ["Entrada", "Valor"], bold)
        addr = {}
        for i, (label, key) in enumerate(labels, start=1):
            ws.write(i, 0, label)
            if key == "obligation_pv" and entity == "sanepar":
                ws.write_formula(i, 1, "=Precatorio!I5", inp)
            else:
                ws.write(i, 1, p[key], inp)
            addr[key] = f"$B${i + 1}"
        a = addr
        ws.write(27, 0, "B0 (base remunerada implícita, preços 2025)")
        ws.write_formula(27, 1, f"=({a['ebitda0']}-{a['da0']})/{a['r_pre']}")
        ws.write(28, 0, "δ (depreciação/base)")
        ws.write_formula(28, 1, f"={a['da0']}/$B$28")
        ws.write(29, 0, "Margem-base")
        ws.write_formula(29, 1, f"={a['ebitda0']}/{a['revenue0']}")
        B0, DELTA, M0 = "$B$28", "$B$29", "$B$30"
        hdr = ["ano", "IPCA", "índice", "capex", "base total K", "base remunerada", "EBITDA regulado", "receita", "EBITDA", "D&A fiscal",
               "IR", "Δ giro", "FCFF", "peso", "t", "fator", "PV"]
        ws.write_row(32, 0, hdr, bold)
        # linha 34 = 2023, 35 = 2024, 36 = 2025, 37..46 = 2026..2035 (1-based)
        ws.write(33, 0, 2023)
        ws.write_formula(33, 4, f"={B0}")
        ws.write(34, 0, 2024)
        ws.write_formula(34, 2, f"=1/(1+{a['infl_2025']})")
        ws.write_formula(34, 4, f"=E34*(1-{DELTA})+{a['eligible']}*{a['capex_2024']}/C35")
        ws.write(35, 0, 2025)
        ws.write(35, 2, 1)
        ws.write_formula(35, 4, f"=E35*(1-{DELTA})+{a['eligible']}*{a['capex_2025']}/C36")
        ws.write_formula(35, 7, f"={a['revenue0']}")
        for k, y in enumerate(range(2026, 2036)):
            r = 37 + k  # linha Excel
            row0 = r - 1
            ws.write(row0, 0, y)
            ws.write(row0, 1, p["infl"][y], pct)
            ws.write_formula(row0, 2, f"=C{r - 1}*(1+B{r})")
            if y in p["capex_plan"]:
                ws.write(row0, 3, p["capex_plan"][y], inp)
            else:
                ws.write_formula(row0, 3, f"=C{r}*E{r - 1}*({DELTA}+{a['g_real']})/{a['eligible']}")
            ws.write_formula(row0, 4, f"=E{r - 1}*(1-{DELTA})+{a['eligible']}*D{r}/C{r}")
            ws.write_formula(row0, 5, f"=E{r - 2}")
            ws.write_formula(row0, 6, f"=({a['r_pre']}+{DELTA})*F{r}*C{r}")
            ws.write_formula(row0, 7, f"=G{r}/{M0}")
            ws.write_formula(row0, 8, f"={a['share']}*G{r}-{a['opex_shock']}*H{r}")
            ws.write_formula(row0, 9, f"={DELTA}*E{r - 1}*C{r}")
            ws.write_formula(row0, 10, f"={a['tax']}*MAX(I{r}-J{r},0)")
            ws.write_formula(row0, 11, f"={a['wc_ratio']}*(H{r}-H{r - 1})")
            ws.write_formula(row0, 12, f"=I{r}-K{r}-D{r}-L{r}")
            if y == 2026:
                ws.write_formula(row0, 13, f"={a['stub']}")
                ws.write_formula(row0, 14, f"={a['stub']}/2")
            else:
                ws.write(row0, 13, 1)
                ws.write_formula(row0, 14, f"=(DATE({y},7,1)-DATE(2026,10,30))/365")
            ws.write_formula(row0, 15, f"=(1+{a['wacc']})^(-O{r})")
            ws.write_formula(row0, 16, f"=M{r}*N{r}*P{r}")
            cellmap[(entity, f"fcff_{y}")] = (ENT_SHEET[entity], f"M{r}")
            cellmap[(entity, f"ebitda_{y}")] = (ENT_SHEET[entity], f"I{r}")
        t = [("g nominal", f"=(1+{a['pi_lr']})*(1+{a['g_real']})-1"),
             ("Índice T+1", f"=C46*(1+{a['pi_lr']})"),
             ("EBITDA regulado T+1", f"=({a['r_pre']}+{DELTA})*E46*B50"),
             ("Receita T+1", f"=B51/{M0}"),
             ("EBITDA T+1", f"={a['share']}*B51-{a['opex_shock']}*B52"),
             ("NOPAT T+1", f"=(B53-{DELTA}*E46*B50)*(1-{a['tax']})"),
             ("FCFF T+1", f"=B54-{a['g_real']}*E46*B50-{a['wc_ratio']}*B52*B49/(1+B49)"),
             ("Valor terminal (perpetuidade)", f"=B55/({a['wacc']}-B49)"),
             ("t fim de 2035", "=(DATE(2035,12,31)-DATE(2026,10,30))/365"),
             ("PV terminal", f"=B56*(1+{a['wacc']})^(-B57)"),
             ("PV explícito", "=SUM(Q37:Q46)"),
             ("Valor da firma (EV)", "=B58+B59"),
             ("WACC real", f"=(1+{a['wacc']})/(1+{a['pi_lr']})-1"),
             ("Valor por R$ de base (v)", f"=({a['share']}*{a['r_post']}-{a['g_real']})/(B61-{a['g_real']})"),
             ("Dívida líquida estimada 30/10", f"={a['net_debt']}-M37*{a['rollforward']}"),
             ("Patrimônio (resíduo bruto)", f"=B60-B63-{a['debt_like']}-{a['grantor']}+{a['grantor']}*B62-{a['obligation_pv']}"),
             ("Valor por papel", f"=IF(B64>0,B64*{a['per_paper']},NA())"),
             ("Potencial vs preço", f"=IF(B64>0,B65/{a['price']}-1,NA())")]
        for i, (label, formula) in enumerate(t):
            ws.write(48 + i, 0, label, bold)
            ws.write_formula(48 + i, 1, formula)
        for key, cell in (("enterprise_value", "B60"), ("pv_explicit", "B59"), ("pv_terminal", "B58"), ("equity_residual", "B64"),
                          ("paper_value", "B65"), ("terminal_fcff", "B55"), ("b0", "B28")):
            cellmap[(entity, key)] = (ENT_SHEET[entity], cell)
        ws.set_column(0, 0, 44)
        ws.set_column(1, 16, 14)
    cs = wb.add_worksheet("Casos")
    hdr = ["case_id", "entity_id", "instrument_id", "scenario_id", "dimensions", "wacc", "g", "terminal_method", "equity_residual_before_floor",
           "equity_floor_applied", "paper_value", "target_validity"]
    cs.write_row(0, 0, hdr, bold)
    for r, c in enumerate(cases, start=1):
        for col, key in enumerate(hdr):
            val = c.get(key)
            if key == "dimensions":
                val = json.dumps({k: v["label"] for k, v in c["dimensions"].items()}, ensure_ascii=False)
            if val is None:
                cs.write(r, col, "N/D" if key == "paper_value" else "")
            elif isinstance(val, bool):
                cs.write(r, col, "sim" if val else "não")
            else:
                cs.write(r, col, val)
    lg = wb.add_worksheet("Legado")
    lg.write_row(0, 0, ["entity_id", "workbook", "calculated_share", "cached_share", "share_abs_error", "ev_abs_error", "passed"], bold)
    for r, row in enumerate(legacy, start=1):
        lg.write_row(r, 0, [row["entity_id"], row["workbook"], row["calculated_share"], row["cached_share"], row["share_abs_error"],
                            row["ev_abs_error"], "sim" if row["passed"] else "não"])
    wb.close()
    return cellmap


def inputs_from_case(reg, rec, cap, bal, a, m, case: dict, p: dcf.Params, entity: str) -> dict:
    """Entradas do caso-base com os mesmos números do motor Python (para a planilha)."""
    from .valuation import DEBT_LIKE
    items = bal["items"][entity]
    vr = case["value_refs"]
    per_paper = (reg.get(cap["class_weights"]["sapr11_per_mcap"]) if entity == "sanepar" else 1 / reg.get(cap["shares"][entity]["total"]))
    return dict(ebitda0=p.ebitda0, da0=p.da0, revenue0=p.revenue0, wc_ratio=p.wc_ratio, r_pre=p.r_pre, r_post=p.r_post, tax=p.tax,
                share=p.share, opex_shock=p.opex_shock, eligible=p.eligible, g_real=p.g_real, wacc=p.wacc, pi_lr=p.infl[2035],
                capex_2024=p.capex_hist[2024], capex_2025=p.capex_hist[2025], infl_2025=p.infl[2025], net_debt=reg.get(items["net_debt"]),
                debt_like=sum(reg.get(items[k]) for k in DEBT_LIKE if k in items),
                grantor=reg.get(items["grantor"]) if "grantor" in items else 0.0, obligation_pv=reg.get(vr["obligation_pv"]),
                per_paper=per_paper, price=reg.get(vr["price"]), stub=dcf.STUB_FRACTION, rollforward=dcf.ROLLFORWARD_FRACTION,
                infl=p.infl, capex_plan=p.capex_plan)
