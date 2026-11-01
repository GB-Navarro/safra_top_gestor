"""AN02 — histórico, definições e recorrência (C02–C08).

Uma linha de conciliação por célula aberta do mapa (64) e linhas adicionais de C08.
A definição econômica é escolhida antes da comparação; diferença contra a CVM não é
tratada automaticamente como erro da planilha. Também produz a base 2025 do ramo revisado.
"""
from __future__ import annotations

import re

from .data import Baseline, Registry, loc_of

YEARS = [2021, 2022, 2023, 2024, 2025]
CVM_SRC = {2021: "SRC_cvm_dfp_2021_64b8693b", 2022: "SRC_cvm_dfp_2022_4379d3b8", 2023: "SRC_cvm_dfp_2023_e2be633d",
           2024: "SRC_cvm_dfp_2024_c4def759", 2025: "SRC_cvm_dfp_2025_cdce6cc0"}
SAB_DF2022, SAB_DFP2024, SAB_DF2025 = "local_63d5afcacc50", "local_85acbb6423e6", "local_45586543e35a"
HEADER = ["reconciliation_id", "requirement_id", "entity_id", "period", "cell", "concept", "original_value", "original_source",
          "selected_definition", "selected_value", "selected_value_id", "difference", "unit", "scale", "sign_convention", "scope",
          "components", "transformation", "source_refs", "source_locators", "disposition", "justification", "model_effect",
          "used_in_revised_model", "owner", "reviewed_at"]

# Contas operacionais de "Outros" (2.01.05.02.xx) incluídas no giro; demais filhas são financeiras,
# regulatórias, dividendos ou obrigações tratadas na ponte EV→acionista (AN04).
OOL_INCLUDE = re.compile(r"Servi[çc]os a Pagar|Outras Obriga|Obriga[çc][õo]es Diversas|Outras Contas a Pagar|Cau[çc][õo]es|"
                         r"Receitas a Apropriar|Conv[êe]nio|Valores a Restituir|Contratos? de Performance|Empreiteiros", re.I)


def _yid(entity, metric, year):
    return f"V.{entity}.{metric}.{year}"


def _cvm_value(reg: Registry, base: Baseline, entity: str, statement: str, year: int, code: str, metric: str,
               annual_flow: bool = True, sign: float = 1.0) -> tuple[str, float, str]:
    end = f"{year}-12-31"
    value, row = base.cvm(entity, statement, end, code=code, period_start=f"{year}-01-01" if annual_flow else None)
    vid = reg.value(f"{_yid(entity, metric, year)}", metric_id=metric, entity_id=entity, value=sign * value, unit="BRL", scale=1e6,
                    value_state="observed", fact_type="fact", period_start=f"{year}-01-01" if annual_flow else "", period_end=end,
                    observed_at=row["published_at"], scope=row["scope"], source_refs=[row["source_id"]], locator=loc_of(row),
                    note=f"CVM {statement} {code} ({row['account_name']}); sinal {'invertido' if sign < 0 else 'original'}.")
    return vid, sign * value, f"{row['source_id']}: {loc_of(row)}"


def _row(rows, **kw):
    full = {k: kw.get(k, "") for k in HEADER}
    full["owner"] = "agente_analise"
    rows.append(full)


def _original(mapping, entity, year, cell_suffix):
    for r in mapping:
        if r["entity_id"] == entity and int(r["year"]) == year and r["cell"].endswith(cell_suffix):
            return r
    raise KeyError((entity, year, cell_suffix))


def _named_rows(base, entity, statement, year, pattern):
    """Todas as contas anuais cujo nome casa o padrão (códigos mudam entre anos; zeros duplicados são inofensivos)."""
    end = f"{year}-12-31"
    rx = re.compile(pattern, re.I)
    rows = [r for r in base.accounts() if r["entity_id"] == entity and r["statement"] == statement and r["period_end"] == end
            and (r["period_start"] or "") == f"{year}-01-01" and rx.search(r["account_name"])]
    refs = {r["reference_date"] for r in rows}
    chosen = end if end in refs else max(refs)
    picked = {}
    for r in sorted((r for r in rows if r["reference_date"] == chosen), key=lambda r: int(r["version"] or 0)):
        picked[r["account_code"]] = r
    if not picked:
        raise KeyError((entity, statement, year, pattern))
    return [(float(r["value_brl_million"]), r) for r in picked.values()]


def _sum_children(base, entity, statement, end, parent, include=None, exclude_names=()):
    picked, skipped = [], []
    for r in base.children(entity, statement, end, parent):
        name = r["account_name"]
        if (include is None or include.search(name)) and not any(re.search(x, name, re.I) for x in exclude_names):
            picked.append(r)
        else:
            skipped.append(r)
    return picked, skipped


def build(reg: Registry, base: Baseline, reviewed_at: str) -> dict:
    mapping = base.csv("data/catalog/cell_issue_mapping.csv")
    rows: list[dict] = []
    basis: dict = {"sabesp": {}, "copasa": {}, "sanepar": {}}

    # ---------------- C02 — Sabesp receita/custo de construção -----------------------------
    cost_pdf = {2021: (SAB_DF2022, 142, "(4.754.383) (4.278.337)"), 2022: (SAB_DF2022, 142, "(4.754.383) (4.278.337)"),
                2023: (SAB_DFP2024, 120, "(5.474.729)"), 2024: (SAB_DFP2024, 120, "(6.085.895)"),
                2025: (SAB_DF2025, 110, "(14.437.363)")}
    for y in YEARS:
        vid, val, loc = _cvm_value(reg, base, "sabesp", "DVA", y, "7.01.03", "construction_revenue")
        o = _original(mapping, "sabesp", y, "7")
        orig = float(o["original"])
        _row(rows, reconciliation_id=f"R.C02.sabesp.{y}.rev", requirement_id="C02", entity_id="sabesp", period=y, cell=o["cell"],
             concept=o["concept"], original_value=orig, original_source="Modelo_TIR_Sabesp.xlsx (célula vermelha)",
             selected_definition="Receita de construção ICPC 01/IFRIC 12 = DVA 7.01.03 'Receitas refs. à Construção de Ativos Próprios'",
             selected_value=val, selected_value_id=vid, difference=round(orig - val, 6), unit="BRL", scale=1e6,
             sign_convention="positivo = receita", scope=base.scope_of("sabesp", f"{y}-12-31"), components=[{"value_id": vid}],
             transformation="nenhuma", source_refs=[CVM_SRC[y]], source_locators=[loc],
             disposition="confirmed" if abs(orig - val) < 0.0015 else "corrected",
             justification="Valor da planilha coincide com a DVA publicada; receita sem caixa associada à construção da infraestrutura.",
             model_effect="Excluída da receita-base recorrente (ramo revisado) e da margem; capex permanece pela DFC.",
             used_in_revised_model=(y == 2025), reviewed_at=reviewed_at)
        doc, page, needle = cost_pdf[y]
        base.require_text(doc, page, "Custos de construção", needle)
        cost = None
        cv, crow = base.cvm("sabesp", "DRE", f"{y}-12-31", code="3.02.02", period_start=f"{y}-01-01", required=False)
        if cv is not None:
            cost = -cv
            cvid = reg.value(_yid("sabesp", "construction_cost", y), metric_id="construction_cost", entity_id="sabesp", value=cost,
                             unit="BRL", scale=1e6, value_state="observed", fact_type="fact", period_start=f"{y}-01-01",
                             period_end=f"{y}-12-31", observed_at=crow["published_at"], scope=crow["scope"],
                             source_refs=[crow["source_id"], doc], locator=f"{loc_of(crow)} | {doc} p{page}",
                             note="Custo de construção (despesa positiva); DRE 3.02.02 e nota de custos por natureza.")
        else:
            cost = 14437.363
            cvid = reg.value(_yid("sabesp", "construction_cost", y), metric_id="construction_cost", entity_id="sabesp", value=cost,
                             unit="BRL", scale=1e6, value_state="observed", fact_type="fact", period_start=f"{y}-01-01",
                             period_end=f"{y}-12-31", observed_at="2026-03", scope="consolidated", source_refs=[doc],
                             locator=f"{doc} p{page}: Custos de construção (Nota 30), consolidado",
                             note="DF 2025: custos por natureza, coluna consolidado 2025 (14.437.363 mil).")
        o = _original(mapping, "sabesp", y, "8")
        orig = float(o["original"])
        _row(rows, reconciliation_id=f"R.C02.sabesp.{y}.cost", requirement_id="C02", entity_id="sabesp", period=y, cell=o["cell"],
             concept=o["concept"], original_value=orig, original_source="Modelo_TIR_Sabesp.xlsx",
             selected_definition="Custo de construção (nota de custos por natureza; DRE 3.02.02 quando aberta)",
             selected_value=cost, selected_value_id=cvid, difference=round(orig - cost, 6), unit="BRL", scale=1e6,
             sign_convention="positivo = custo", scope=base.scope_of("sabesp", f"{y}-12-31"), components=[{"value_id": cvid}],
             transformation="sinal convertido para custo positivo", source_refs=[doc], source_locators=[f"{doc} p{page}"],
             disposition="confirmed" if abs(orig - cost) < 0.0015 else "corrected",
             justification=("Margem de construção = receita − custo; zero desde 01/01/2025 (custo = receita). "
                            "2021–22 individual, 2023–25 consolidado: não comparar margem entre perímetros sem ressalva."),
             model_effect="Margem de construção removida do EBITDA recorrente; não gera caixa.", used_in_revised_model=(y == 2025),
             reviewed_at=reviewed_at)

    # ---------------- C03 — Sabesp ponte do EBITDA -----------------------------------------
    fin_asset = {2024: (9151.310, 822.482, SAB_DF2025, 107), 2025: (1676.434, 179.084, SAB_DF2025, 107)}
    base.require_text(SAB_DF2025, 107, "Ativo financeiro (indenização) (ii) 1.676.434 9.151.310")
    base.require_text(SAB_DF2025, 21, "PIS e Cofins diferidos sobre ativo financeiro da concessão 179.084 822.482")
    base.require_text(SAB_DF2022, 25, "R$ 6.372,7 milhões em 2021 para R$ 7.087,7 milhões")
    for y in YEARS:
        ebit_id, ebit, l1 = _cvm_value(reg, base, "sabesp", "DRE", y, "3.05", "ebit_reported")
        da_id, da, l2 = _cvm_value(reg, base, "sabesp", "DVA", y, "7.04.01", "da", sign=-1.0)
        oi = base.cvm("sabesp", "DRE", f"{y}-12-31", code="3.04.04", period_start=f"{y}-01-01")[0]
        oe = base.cvm("sabesp", "DRE", f"{y}-12-31", code="3.04.05", period_start=f"{y}-01-01")[0]
        other_id = reg.value(_yid("sabesp", "other_operating_net", y), metric_id="other_operating_net", entity_id="sabesp",
                             value=oi + oe, unit="BRL", scale=1e6, value_state="derived", fact_type="derived",
                             period_end=f"{y}-12-31", calculation_ref="DRE 3.04.04 + 3.04.05",
                             note="Outras receitas e despesas operacionais líquidas (excluídas na definição de EBITDA ajustado da Sabesp).")
        rev = reg.get(_yid("sabesp", "construction_revenue", y))
        cost = reg.get(_yid("sabesp", "construction_cost", y))
        margin = rev - cost
        fa_gross, fa_tax, _, _ = fin_asset.get(y, (0.0, 0.0, None, None))
        fa_net = fa_gross - fa_tax
        recurring = ebit + da - (oi + oe) - margin - fa_net
        comps = [{"value_id": ebit_id, "op": "+"}, {"value_id": da_id, "op": "+"}, {"value_id": other_id, "op": "-"},
                 {"construction_margin": round(margin, 6), "op": "-"}, {"financial_asset_update_net": round(fa_net, 6), "op": "-"}]
        rid = reg.value(_yid("sabesp", "ebitda_recurring", y), metric_id="ebitda_recurring", entity_id="sabesp", value=recurring,
                        unit="BRL", scale=1e6, value_state="derived", fact_type="derived", period_start=f"{y}-01-01",
                        period_end=f"{y}-12-31", scope=base.scope_of("sabesp", f"{y}-12-31"),
                        calculation_ref="EBIT + D&A − outras operacionais líquidas − margem de construção − atualização do ativo financeiro (líq. PIS/Cofins diferidos)",
                        source_refs=[CVM_SRC[y], SAB_DF2025] if y >= 2024 else [CVM_SRC[y]],
                        note="Definição da Sabesp para EBITDA ajustado (confirmada em 2021–22), sem margem de construção e sem ativo financeiro.")
        o = _original(mapping, "sabesp", y, "9")
        orig = float(o["original"])
        planilha_ex_margin = orig - margin
        residual = planilha_ex_margin - recurring
        if y in (2021, 2022):
            disp, just, used = ("confirmed", "EBITDA ajustado do Relatório da Administração 2022 (p25) = EBIT + D&A − outras operacionais "
                                "líquidas; resíduo é arredondamento do valor publicado em R$ milhões com uma casa.", False)
        elif y == 2025:
            disp, just, used = ("reclassified", "Valor da planilha (EBITDA ajustado Bloomberg) não reproduzido por componentes locais; "
                                "adotada a definição com componentes rastreáveis (ativo financeiro líquido de PIS/Cofins diferidos, "
                                "margem de construção zero, outras operacionais). O valor da planilha fica como alternativa favorável.", True)
        else:
            disp, just, used = ("limited_excluded_from_model", "Resíduo não itemizado nas fontes locais (ajustes Bloomberg/não recorrentes "
                                "da privatização). Ano não sustenta base, premissa ou afirmação do ramo revisado.", False)
        _row(rows, reconciliation_id=f"R.C03.sabesp.{y}", requirement_id="C03", entity_id="sabesp", period=y, cell=o["cell"],
             concept=o["concept"], original_value=orig, original_source="Rel. Administração (2021–22) / Bloomberg (2023–25), via planilha",
             selected_definition="EBITDA recorrente Sabesp (ver calculation_ref)", selected_value=recurring, selected_value_id=rid,
             difference=round(residual, 6), unit="BRL", scale=1e6, sign_convention="positivo", scope=base.scope_of("sabesp", f"{y}-12-31"),
             components=comps, transformation="ponte reportado→ajustado→recorrente; diferença = (planilha − margem) − recorrente",
             source_refs=[CVM_SRC[y]] + ([SAB_DF2025] if y >= 2024 else []) + ([SAB_DF2022] if y <= 2022 else []),
             source_locators=[l1, l2] + ([f"{SAB_DF2025} p107 (receita ativo financeiro); p21 (PIS/Cofins diferidos)"] if y >= 2024 else []),
             disposition=disp, justification=just,
             model_effect="2025 fixa a margem-base recorrente do ramo revisado" if used else "Sem uso no ramo revisado",
             used_in_revised_model=used, reviewed_at=reviewed_at)
        if y == 2025:
            basis["sabesp"]["ebitda_2025"] = rid
            reg.value("V.sabesp.ebitda_recurring_alt_planilha.2025", metric_id="ebitda_recurring_alternative", entity_id="sabesp",
                      value=orig, unit="BRL", scale=1e6, value_state="observed", fact_type="fact", period_end="2025-12-31",
                      source_refs=["local_87ac99e100be"], locator="Modelo_TIR_Sabesp.xlsx Dados_RI!G9 (Bloomberg, não verificado localmente)",
                      note="Alternativa: EBITDA ajustado registrado na planilha original.")

    # ---------------- C04 — Sabesp capex caixa ----------------------------------------------
    for y in YEARS:
        end = f"{y}-12-31"
        if y == 2025:
            v, r = base.cvm("sabesp", "DFC_MI", end, name=r"Aquisi..o de ativo de contrato, intang", period_start=f"{y}-01-01")
            parts = [(v, r)]
        else:
            parts = [base.cvm("sabesp", "DFC_MI", end, code="6.02.01", period_start=f"{y}-01-01"),
                     base.cvm("sabesp", "DFC_MI", end, code="6.02.02", period_start=f"{y}-01-01")]
        capex = -sum(p[0] for p in parts)
        vid = reg.value(_yid("sabesp", "capex_cash", y), metric_id="capex_cash", entity_id="sabesp", value=capex, unit="BRL", scale=1e6,
                        value_state="derived", fact_type="derived", period_start=f"{y}-01-01", period_end=end,
                        scope=parts[0][1]["scope"], source_refs=[parts[0][1]["source_id"]],
                        calculation_ref="−(DFC 6.02.01 ativo de contrato/intangível + 6.02.02 imobilizado)",
                        locator=" | ".join(loc_of(p[1]) for p in parts), note="Capex caixa (desembolso) para FCFF.")
        basis["sabesp"][f"capex_{y}"] = vid
        if y == 2025:
            continue
        o = _original(mapping, "sabesp", y, "11")
        orig = float(o["original"])
        _row(rows, reconciliation_id=f"R.C04.sabesp.{y}", requirement_id="C04", entity_id="sabesp", period=y, cell=o["cell"],
             concept=o["concept"], original_value=orig, original_source="Modelo_TIR_Sabesp.xlsx",
             selected_definition="Capex caixa = DFC 6.02.01 + 6.02.02 (ativo de contrato/intangível + imobilizado)",
             selected_value=capex, selected_value_id=vid, difference=round(orig - capex, 6), unit="BRL", scale=1e6,
             sign_convention="positivo = desembolso", scope=parts[0][1]["scope"],
             components=[{"account": p[1]["account_code"], "value": -p[0]} for p in parts],
             transformation="soma de duas linhas de investimento; sinal invertido", source_refs=[CVM_SRC[y]],
             source_locators=[loc_of(p[1]) for p in parts], disposition="confirmed" if abs(orig - capex) < 0.0015 else "corrected",
             justification=("A diferença registrada antes vinha do comparador usar só 6.02.01; a planilha soma também o imobilizado. "
                            "Exclui aplicações financeiras, caixa restrito e aportes em investidas."),
             model_effect="Histórico de capex caixa coerente com DFC; projeções usam plano/guidance (AN06).",
             used_in_revised_model=False, reviewed_at=reviewed_at)

    # ---------------- C05 — giro operacional ------------------------------------------------
    for entity in ("sabesp", "copasa", "sanepar"):
        for y in YEARS:
            end = f"{y}-12-31"
            src = CVM_SRC[y]
            ooa_parts = []
            for code in ("1.01.06", "1.01.03.02"):
                v, r = base.cvm(entity, "BPA", end, code=code, required=False)
                if v is not None:
                    ooa_parts.append((code, r["account_name"], v, loc_of(r)))
            # 1.01.08.03 'Outros' exceto caixa restrito/vinculado e ativos à venda
            kids, _ = _sum_children(base, entity, "BPA", end, "1.01.08.03", exclude_names=(r"Caixa Restrito", r"Vinculad"))
            if kids:
                ooa_parts += [(k["account_code"], k["account_name"], float(k["value_brl_million"]), loc_of(k)) for k in kids]
            else:
                v, r = base.cvm(entity, "BPA", end, code="1.01.08.03", required=False)
                if v is not None:
                    ooa_parts.append(("1.01.08.03", r["account_name"], v, loc_of(r)))
            ooa = sum(p[2] for p in ooa_parts)
            ool_parts = []
            for code in ("2.01.01", "2.01.03"):
                v, r = base.cvm(entity, "BPP", end, code=code)
                ool_parts.append((code, r["account_name"], v, loc_of(r)))
            picked, skipped = _sum_children(base, entity, "BPP", end, "2.01.05.02", include=OOL_INCLUDE)
            ool_parts += [(k["account_code"], k["account_name"], float(k["value_brl_million"]), loc_of(k)) for k in picked]
            ool = sum(p[2] for p in ool_parts)
            for metric, value, parts, suffix, label in (("other_operating_assets", ooa, ooa_parts, "14", "OOA"),
                                                         ("other_operating_liabilities", ool, ool_parts, "16", "OOL")):
                vid = reg.value(_yid(entity, metric, y), metric_id=metric, entity_id=entity, value=value, unit="BRL", scale=1e6,
                                value_state="derived", fact_type="derived", period_end=end, scope=base.scope_of(entity, end),
                                source_refs=[src], calculation_ref=" + ".join(p[0] for p in parts),
                                locator=" | ".join(p[3] for p in parts),
                                note=("OOA = tributos a recuperar + outras contas a receber + outros ativos circulantes (sem caixa restrito/vinculado)"
                                      if label == "OOA" else
                                      "OOL = obrigações sociais/trabalhistas + fiscais + filhas operacionais de 'Outros' (serviços a pagar, "
                                      "outras obrigações/contas a pagar, cauções, receitas a apropriar, convênios, contratos de performance)"))
                o = _original(mapping, entity, y, suffix)
                orig = float(o["original"])
                excluded = [f"{k['account_code']} {k['account_name']}" for k in skipped] if label == "OOL" else ["caixa restrito/vinculado"]
                _row(rows, reconciliation_id=f"R.C05.{entity}.{y}.{label}", requirement_id="C05", entity_id=entity, period=y,
                     cell=o["cell"], concept=o["concept"], original_value=orig, original_source=o["workbook"],
                     selected_definition=f"{label} canônico (definição única para as três empresas)", selected_value=value,
                     selected_value_id=vid, difference=round(orig - value, 6), unit="BRL", scale=1e6,
                     sign_convention="saldo positivo", scope=base.scope_of(entity, end),
                     components=[{"account": p[0], "name": p[1], "value": p[2]} for p in parts],
                     transformation="soma de contas CVM; exclusões listadas", source_refs=[src], source_locators=[p[3] for p in parts],
                     disposition="confirmed" if abs(orig - value) < 0.5 else "reclassified",
                     justification=("Definição única evita incluir dividendos, PPP, arrendamentos, derivativos, passivo regulatório, "
                                    "poder concedente, PIS/Cofins diferidos e provisões no giro; esses itens são tratados uma única vez na "
                                    f"ponte EV→acionista. Excluídos: {'; '.join(excluded) or 'nenhum'}. Tributos a recuperar podem conter IR/CS "
                                    "(não separável no nível CVM disponível)."),
                     model_effect="Saldo 2025 define a razão de giro do ramo revisado" if y == 2025 else "Histórico de referência",
                     used_in_revised_model=(y == 2025), reviewed_at=reviewed_at)
            basis[entity][f"ooa_2025" if y == 2025 else f"ooa_{y}"] = _yid(entity, "other_operating_assets", y)
            basis[entity][f"ool_2025" if y == 2025 else f"ool_{y}"] = _yid(entity, "other_operating_liabilities", y)

    # ---------------- C06 — Copasa capex caixa ---------------------------------------------
    for y in YEARS:
        end = f"{y}-12-31"
        parts = []
        for pattern in (r"Aquisi..o de Ativos? de Contrato", r"Aquisi..o de Ativos? Intang", r"Aquisi..o de Ativos? Imobiliz"):
            parts.extend(_named_rows(base, "copasa", "DFC_MI", y, pattern))
        capex = -sum(p[0] for p in parts)
        vid = reg.value(_yid("copasa", "capex_cash", y), metric_id="capex_cash", entity_id="copasa", value=capex, unit="BRL", scale=1e6,
                        value_state="derived", fact_type="derived", period_start=f"{y}-01-01", period_end=end, scope="consolidated",
                        source_refs=[CVM_SRC[y]], calculation_ref="−(DFC aquisição de ativo de contrato + intangível + imobilizado)",
                        locator=" | ".join(loc_of(p[1]) for p in parts), note="Capex caixa Copasa; pagamentos de PPP tratados como serviço de obrigação.")
        basis["copasa"][f"capex_{y}"] = vid
        o = _original(mapping, "copasa", y, "11")
        orig = float(o["original"])
        _row(rows, reconciliation_id=f"R.C06.copasa.{y}", requirement_id="C06", entity_id="copasa", period=y, cell=o["cell"],
             concept=o["concept"], original_value=orig, original_source="Modelo_TIR_Copasa.xlsx (release 'investimentos realizados')",
             selected_definition="Capex caixa = DFC aquisição de ativo de contrato + intangível + imobilizado", selected_value=capex,
             selected_value_id=vid, difference=round(orig - capex, 6), unit="BRL", scale=1e6, sign_convention="positivo = desembolso",
             scope="consolidated", components=[{"account": p[1]["account_code"], "name": p[1]["account_name"], "value": -p[0]} for p in parts],
             transformation="soma de três linhas da DFC; sinal invertido", source_refs=[CVM_SRC[y]],
             source_locators=[loc_of(p[1]) for p in parts], disposition="reclassified",
             justification=("A planilha usa o investimento por competência do release (inclui adições sem caixa no período, como "
                            "capitalizações e fornecedores de obra). FCFF exige desembolso; a diferença fica como alternativa adversa."),
             model_effect="Capex 2025 caixa entra na base regulatória implícita; projeções usam o plano 2026–30 (AN06).",
             used_in_revised_model=(y >= 2024), reviewed_at=reviewed_at)

    # ---------------- C07 — Sanepar zeros de construção ------------------------------------
    base.require_text("doc_sapr_itr", 67, "margem nula", "A receita está apresentada líquida dos custos de")
    for y in YEARS:
        vid, val, loc = _cvm_value(reg, base, "sanepar", "DVA", y, "7.01.03", "construction_revenue")
        for suffix, concept_key in (("7", "rev"), ("8", "cost")):
            o = _original(mapping, "sanepar", y, suffix)
            _row(rows, reconciliation_id=f"R.C07.sanepar.{y}.{concept_key}", requirement_id="C07", entity_id="sanepar", period=y,
                 cell=o["cell"], concept=o["concept"], original_value=float(o["original"]), original_source="Modelo_para_TIR_Sanepar.xlsx",
                 selected_definition="Receita/custo de construção apresentados líquidos (margem nula) — sem dedução da receita-base",
                 selected_value=0.0, selected_value_id=vid, difference=float(o["original"]) - 0.0, unit="BRL", scale=1e6,
                 sign_convention="zero fundamentado", scope="individual", components=[{"value_id": vid}],
                 transformation="nenhuma", source_refs=[CVM_SRC[y], "SRC_doc_sapr_itr_d93332d6"],
                 source_locators=[loc, "doc_sapr_itr p67: receitas e custos de construção com margem nula; receita líquida dos custos"],
                 disposition="confirmed_net_presentation",
                 justification=("O zero não é dado faltante: a Sanepar apresenta a construção líquida (margem nula) e a DVA 7.01.03 é zero. "
                                "A receita-base é comparável à receita ajustada (sem construção) de Sabesp e Copasa."),
                 model_effect="Receita-base Sanepar = receita líquida reportada; investimento entra pela DFC.",
                 used_in_revised_model=(y == 2025), reviewed_at=reviewed_at)

    # ---------------- Bases 2025 por empresa ------------------------------------------------
    rev_sab, rrow = base.cvm("sabesp", "DRE", "2025-12-31", code="3.01", period_start="2025-01-01")
    fa_net = 1676.434 - 179.084
    reg.value("V.sabesp.revenue_reported.2025", metric_id="revenue_reported", entity_id="sabesp", value=rev_sab, unit="BRL", scale=1e6,
              value_state="observed", fact_type="fact", period_start="2025-01-01", period_end="2025-12-31", scope="consolidated",
              source_refs=[rrow["source_id"]], locator=loc_of(rrow), note="Receita líquida reportada (inclui construção e ativo financeiro).")
    basis["sabesp"]["revenue_2025"] = reg.value(
        "V.sabesp.revenue_recurring.2025", metric_id="revenue_recurring", entity_id="sabesp",
        value=rev_sab - reg.get("V.sabesp.construction_revenue.2025") - fa_net, unit="BRL", scale=1e6, value_state="derived",
        fact_type="derived", period_start="2025-01-01", period_end="2025-12-31", scope="consolidated",
        source_refs=[rrow["source_id"], SAB_DF2025], locator="DRE 3.01 − DVA 7.01.03 − (DF2025 p107 1.676.434 − p21 179.084)",
        calculation_ref="receita reportada − receita de construção − atualização do ativo financeiro líquida de PIS/Cofins diferidos",
        note="Receita líquida de saneamento ajustada; DF2025 p12 informa ~R$ 22,2 bilhões.")
    base.require_text(SAB_DF2025, 12, "atingindo R$ 22,2 bilhões")
    rev_cop, crow = base.cvm("copasa", "DRE", "2025-12-31", code="3.01", period_start="2025-01-01")
    con_cop, ccrow = base.cvm("copasa", "DRE", "2025-12-31", name=r"Receitas? de Constru", period_start="2025-01-01")
    basis["copasa"]["revenue_2025"] = reg.value(
        "V.copasa.revenue_recurring.2025", metric_id="revenue_recurring", entity_id="copasa", value=rev_cop - con_cop, unit="BRL",
        scale=1e6, value_state="derived", fact_type="derived", period_start="2025-01-01", period_end="2025-12-31", scope="consolidated",
        source_refs=[crow["source_id"]], locator=f"{loc_of(crow)} − {loc_of(ccrow)}", calculation_ref="DRE 3.01 − receita de construção",
        note="Receita de água, esgoto e resíduos sem construção (margem de construção nula).")
    ebit_c = base.cvm("copasa", "DRE", "2025-12-31", code="3.05", period_start="2025-01-01")[0]
    da_c = -base.cvm("copasa", "DVA", "2025-12-31", code="7.04.01", period_start="2025-01-01")[0]
    reg.value("V.copasa.da.2025", metric_id="da", entity_id="copasa", value=da_c, unit="BRL", scale=1e6, value_state="observed",
              fact_type="fact", period_start="2025-01-01", period_end="2025-12-31", scope="consolidated",
              source_refs=[CVM_SRC[2025]], locator="DVA 7.04.01", note="Depreciação, amortização e exaustão (positivo).")
    basis["copasa"]["ebitda_2025"] = reg.value(
        "V.copasa.ebitda_recurring.2025", metric_id="ebitda_recurring", entity_id="copasa", value=ebit_c + da_c, unit="BRL", scale=1e6,
        value_state="derived", fact_type="derived", period_start="2025-01-01", period_end="2025-12-31", scope="consolidated",
        source_refs=[CVM_SRC[2025]], calculation_ref="DRE 3.05 + DVA 7.04.01",
        note="Sem itens não recorrentes itemizados em fonte local para 2025; coincide com a planilha (2.953,5).")
    rev_s, srow = base.cvm("sanepar", "DRE", "2025-12-31", code="3.01", period_start="2025-01-01")
    basis["sanepar"]["revenue_2025"] = reg.value(
        "V.sanepar.revenue_recurring.2025", metric_id="revenue_recurring", entity_id="sanepar", value=rev_s, unit="BRL", scale=1e6,
        value_state="observed", fact_type="fact", period_start="2025-01-01", period_end="2025-12-31", scope="individual",
        source_refs=[srow["source_id"]], locator=loc_of(srow),
        note="Receita líquida reportada; construção apresentada líquida (C07). Inclui doações de clientes (R$ 38,6 mi brutos, sem caixa).")
    da_s = -base.cvm("sanepar", "DVA", "2025-12-31", code="7.04.01", period_start="2025-01-01")[0]
    reg.value("V.sanepar.da.2025", metric_id="da", entity_id="sanepar", value=da_s, unit="BRL", scale=1e6, value_state="observed",
              fact_type="fact", period_start="2025-01-01", period_end="2025-12-31", scope="individual", source_refs=[CVM_SRC[2025]],
              locator="DVA 7.04.01", note="Depreciação e amortização (positivo).")
    basis["sabesp"]["revenue_reported"] = "V.sabesp.revenue_reported.2025"
    for e in basis:
        basis[e]["da_2025"] = f"V.{e}.da.2025"

    # ---------------- C08 — Sanepar recorrência, imposto, plano ----------------------------
    rel = "sanepar_release_2025"
    base.require_text(rel, 11, "EBITDA Ajustado de itens não recorrentes", "3.101,5", "3.000,0", "-4.303,2", "3.399,7")
    ebitda_rep = base.cvm("sanepar", "DRE", "2025-12-31", code="3.05", period_start="2025-01-01")[0] + da_s
    reg.value("V.sanepar.ebitda_reported.2025", metric_id="ebitda_reported", entity_id="sanepar", value=ebitda_rep, unit="BRL",
              scale=1e6, value_state="derived", fact_type="derived", period_end="2025-12-31", scope="individual",
              source_refs=[CVM_SRC[2025]], calculation_ref="DRE 3.05 + DVA 7.04.01", note="EBITDA reportado 2025.")
    basis["sanepar"]["ebitda_2025"] = reg.value(
        "V.sanepar.ebitda_recurring.2025", metric_id="ebitda_recurring", entity_id="sanepar", value=3101.5, unit="BRL", scale=1e6,
        value_state="observed", fact_type="fact", period_start="2025-01-01", period_end="2025-12-31", scope="individual",
        source_refs=["SRC_sanepar_release_2025_5f7297a2"], locator="Release 4T25 p11, tabela 'Itens não Recorrentes': EBITDA Ajustado de itens não recorrentes 2025",
        note="Exclui receita do precatório (−4.303,2), provisão do passivo regulatório/honorários (3.399,7), PDV, PPR, PCLD complementar e provisões contingenciais itemizadas.")
    _row(rows, reconciliation_id="R.C08.sanepar.2025.ebitda", requirement_id="C08", entity_id="sanepar", period=2025, cell="Dados_RI!G9",
         concept="EBITDA reportado vs recorrente", original_value=2963.8, original_source="Modelo_para_TIR_Sanepar.xlsx",
         selected_definition="EBITDA ajustado de itens não recorrentes (release 4T25)", selected_value=3101.5,
         selected_value_id=basis["sanepar"]["ebitda_2025"], difference=round(2963.8 - 3101.5, 6), unit="BRL", scale=1e6,
         sign_convention="positivo", scope="individual",
         components=[{"reported": round(ebitda_rep, 3)}, {"precatorio_revenue": -4303.2}, {"regulatory_provision_fees_fv": 3399.7},
                     {"cofins_pasep_precatorio": 104.5}, {"ppr": 61.2}, {"pdv": 174.0}, {"pcld_complementar": 146.0},
                     {"provisoes_contingenciais": 54.0 + 87.3}, {"ibama": 40.3}],
         transformation="ajustes da própria companhia (parte operacional dos itens não recorrentes)",
         source_refs=["SRC_sanepar_release_2025_5f7297a2", CVM_SRC[2025]], source_locators=["release 4T25 p11"],
         disposition="reclassified",
         justification="2025 mistura o reconhecimento do precatório e da provisão regulatória; a base recorrente usa o ajuste publicado.",
         model_effect="Margem-base Sanepar 2025 = 3.101,5/7.205,7.", used_in_revised_model=True, reviewed_at=reviewed_at)
    tax = -base.cvm("sanepar", "DRE", "2025-12-31", code="3.08", period_start="2025-01-01")[0]
    lair = base.cvm("sanepar", "DRE", "2025-12-31", code="3.07", period_start="2025-01-01")[0]
    reg.value("V.sanepar.effective_tax_rate.2025", metric_id="effective_tax_rate", entity_id="sanepar", value=tax / lair, unit="ratio",
              value_state="derived", fact_type="derived", period_end="2025-12-31", scope="individual", source_refs=[CVM_SRC[2025]],
              calculation_ref="DRE −3.08 / 3.07", note="Alíquota efetiva 2025 afetada pelo precatório e efeitos tributários não recorrentes.")
    _row(rows, reconciliation_id="R.C08.sanepar.2025.tax", requirement_id="C08", entity_id="sanepar", period=2025, cell="Dados_RI!G18",
         concept="Imposto efetivo 2025", original_value=223.087, original_source="Modelo_para_TIR_Sanepar.xlsx",
         selected_definition="Alíquota normalizada 34% sobre EBIT na projeção", selected_value=tax / lair,
         selected_value_id="V.sanepar.effective_tax_rate.2025", difference="", unit="ratio", scale=1, sign_convention="",
         scope="individual", components=[{"ir_cs": tax}, {"lair": lair}], transformation="tax/LAIR",
         source_refs=[CVM_SRC[2025], "SRC_sanepar_release_2025_5f7297a2"], source_locators=["DRE 3.07/3.08", "release p11 'Efeitos Tributários' −258,9"],
         disposition="excluded_from_projection",
         justification="Efetiva de ~9,7% decorre do precatório; não se perpetua alíquota extraordinária. JCP não é projetado (conservador).",
         model_effect="Projeção usa 34% (premissa A.tax_rate).", used_in_revised_model=True, reviewed_at=reviewed_at)
    plan = "sanepar_plano_capex_2026_2030"
    base.require_text(plan, 1, "Capex Regulatório", "9.320,0", "Capitalizações", "1.028,5", "Doações de Redes", "212,8", "Parcerias", "2.511,4", "13.077,0")
    _row(rows, reconciliation_id="R.C08.sanepar.plan", requirement_id="C08", entity_id="sanepar", period="2026-2030", cell="Dados_RI!C34:G34",
         concept="Plano de investimentos 2026–30", original_value=13060.0, original_source="Modelo_para_TIR_Sanepar.xlsx (2620/2420/2160/2970/2890)",
         selected_definition="Capex caixa da companhia = capex regulatório + resíduos/água industrial + capitalizações",
         selected_value=9320.0 + 4.3 + 1028.5, selected_value_id="", difference=round(13060.0 - 10352.8, 6), unit="BRL", scale=1e6,
         sign_convention="positivo = desembolso", scope="individual",
         components=[{"regulatorio": 9320.0}, {"residuos": 4.3}, {"capitalizacoes": 1028.5}, {"doacoes_excluidas": 212.8},
                     {"parcerias_excluidas_base": 2511.4}],
         transformation="exclusão de doações (sem caixa) e parcerias (financiadas por parceiros; alternativa adversa as inclui)",
         source_refs=["SRC_sanepar_plano_capex_2026_2030_89a39155"], source_locators=["Plano de investimentos p1 (publicado 11/12/2025)"],
         disposition="reclassified",
         justification=("Nem todo investimento econômico é desembolso da empresa. O plano é anterior à decisão Agepar de 23/06/2026; "
                        "os investimentos não onerosos do precatório são tratados à parte (AN07), sem dupla contagem."),
         model_effect="Capex anual Sanepar 2026–30 do ramo revisado (AN06).", used_in_revised_model=True, reviewed_at=reviewed_at)
    _row(rows, reconciliation_id="R.C08.sanepar.precatorio", requirement_id="C08", entity_id="sanepar", period="2025-2026",
         cell="n/a", concept="Precatório: recebimento, tributos, passivo, tarifa e investimento", original_value="",
         original_source="Dedução nominal integral (rascunho anterior)", selected_definition="Componente único por natureza",
         selected_value=4407.957, selected_value_id="", difference="", unit="BRL", scale=1e6, sign_convention="passivo positivo",
         scope="individual",
         components=[{"caixa_recebido_set2025": "no caixa de junho/2026 (dívida líquida)"}, {"receita_2025": "excluída do EBITDA recorrente"},
                     {"passivo_regulatorio_jun2026": 4407.957}, {"descontos_tarifarios": "fluxo AN07 (não no EBITDA-base)"},
                     {"investimento_nao_oneroso": "fluxo AN07 (fora do plano e da base remunerada)"}],
         transformation="ver obligation_schedule.csv", source_refs=["SRC_doc_sapr_itr_d93332d6", "SRC_doc_sapr_prec_39f99f35"],
         source_locators=["ITR 2T26 nota 20 p61–62", "Fato relevante 23/06/2026"], disposition="resolved_single_treatment",
         justification="Caixa no balanço, obrigação deduzida pelo valor presente de seus fluxos, receita/provisão fora da base recorrente.",
         model_effect="PV da obrigação na ponte EV→acionista; nenhuma linha duplicada em FCFF.", used_in_revised_model=True,
         reviewed_at=reviewed_at)

    # Capex histórico Sanepar (base regulatória implícita) e razões de giro 2025
    for y in YEARS:
        v, r = base.cvm("sanepar", "DFC_MI", f"{y}-12-31", code="6.02.01", period_start=f"{y}-01-01")
        basis["sanepar"][f"capex_{y}"] = reg.value(
            _yid("sanepar", "capex_cash", y), metric_id="capex_cash", entity_id="sanepar", value=-v, unit="BRL", scale=1e6,
            value_state="observed", fact_type="fact", period_start=f"{y}-01-01", period_end=f"{y}-12-31", scope="individual",
            source_refs=[r["source_id"]], locator=loc_of(r), note="DFC 6.02.01 aplicação no imobilizado e intangível (positivo).")
    for entity in ("sabesp", "copasa", "sanepar"):
        end = "2025-12-31"
        recv = base.cvm(entity, "BPA", end, code="1.01.03.01")[0]
        inv = base.cvm(entity, "BPA", end, code="1.01.04")[0]
        sup = base.cvm(entity, "BPP", end, code="2.01.02")[0]
        wc = recv + inv + reg.get(_yid(entity, "other_operating_assets", 2025)) - sup - reg.get(_yid(entity, "other_operating_liabilities", 2025))
        wid = reg.value(f"V.{entity}.working_capital.2025", metric_id="operating_working_capital", entity_id=entity, value=wc, unit="BRL",
                        scale=1e6, value_state="derived", fact_type="derived", period_end=end, scope=base.scope_of(entity, end),
                        source_refs=[CVM_SRC[2025]], calculation_ref="clientes + estoques + OOA − fornecedores − OOL (C05)",
                        note="Giro operacional canônico.")
        basis[entity]["wc_ratio"] = reg.value(
            f"V.{entity}.wc_ratio.2025", metric_id="wc_to_revenue", entity_id=entity, value=wc / reg.get(basis[entity]["revenue_2025"]),
            unit="ratio", value_state="derived", fact_type="derived", period_end=end, calculation_ref=f"{wid} / receita recorrente 2025",
            note="Razão giro/receita usada para ΔGiro no ramo revisado.")
    return {"rows": rows, "basis": basis}
