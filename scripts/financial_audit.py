"""Extended historical checks and accounting bridges, without fitting unknown mappings."""
from __future__ import annotations

from common import acquisitions, read_csv, read_json, write_csv, write_json
from analysis_outputs import br, text
from model import MODEL_NAMES


def audit():
    accounts=read_csv('data/processed/cvm_accounts.csv')
    models=read_json('data/interim/original_models.json')
    sources={s['key']:s for s in acquisitions() if s['status']=='downloaded'}
    checks=[]
    for entity,name in MODEL_NAMES.items():
        cells=models[name]['cells']['Dados_RI']
        for year,col in zip(range(2021,2026),'CDEFG'):
            pool=[r for r in accounts if r['entity_id']==entity and r['period_end']==f'{year}-12-31']
            def find(statement,code=None,contains=None):
                return [r for r in pool if r['statement']==statement and
                        (code is None or r['account_code']==code) and
                        (contains is None or contains in r['account_name'].lower())]
            da=find('DFC_MI',contains='deprecia')
            ebit=find('DRE','3.05')
            choices={6:find('DRE','3.01'),10:da,12:find('BPA','1.01.03.01'),
                     13:find('BPA','1.01.04'),15:find('BPP','2.01.02'),
                     17:find('DRE','3.07'),18:find('DRE','3.08')}
            if entity=='copasa':
                choices[7]=find('DRE','3.01.03');choices[8]=find('DRE','3.02.02')
            if entity in ('sabesp','sanepar'):choices[11]=find('DFC_MI','6.02.01')
            for row in range(6,19):
                selected=choices.get(row,[])
                official=None;status='semantic_mapping_not_certified';method=''
                if len(selected)==1:
                    official=float(selected[0]['value_brl_million'])*(-1 if row in (8,11,18) else 1)
                    status='within_rounding' if abs(cells[f'{col}{row}']['cached']-official)<=.1 else 'difference_requires_review'
                    method='CVM account, sign converted to original positive expense convention'
                elif row==9 and len(ebit)==1 and len(da)==1:
                    selected=ebit+da
                    official=sum(float(r['value_brl_million']) for r in selected)
                    status='within_rounding' if abs(cells[f'{col}{row}']['cached']-official)<=.1 else 'reported_vs_adjusted_ebitda_bridge_required'
                    method='EBIT + D&A; differs from adjusted EBITDA when nonrecurring/other adjustments exist'
                original=cells[f'{col}{row}']['cached']
                checks.append(dict(entity_id=entity,workbook=name,year=year,cell=f'Dados_RI!{col}{row}',
                    concept=cells[f'A{row}']['cached'],original=original,cvm_comparator=official,
                    difference=None if official is None else original-official,status=status,method=method,
                    source_ids=';'.join(sorted({r['source_id'] for r in selected})),
                    source_locations=' | '.join(r['source_location'] for r in selected),
                    limitation='Numeric match does not certify the selected economic perimeter or recurring/cash interpretation.'))
    write_csv('outputs/qa/extended_input_audit.csv',checks)
    # An observed bridge stops in June. There is no fabricated October balance.
    bridges=[]
    for entity in MODEL_NAMES:
        vals={}
        for end in ['2025-12-31','2026-06-30']:
            def a(st,code):
                found=[r for r in accounts if r['entity_id']==entity and r['period_end']==end and r['statement']==st and r['account_code']==code]
                if len(found)!=1:raise ValueError((entity,end,st,code))
                return found[0]
            selected=[a('BPP','2.01.04'),a('BPP','2.02.01'),a('BPA','1.01.01'),a('BPA','1.01.02')]
            debt=sum(float(r['value_brl_million']) for r in selected[:2])
            cash=sum(float(r['value_brl_million']) for r in selected[2:])
            vals[end]=dict(gross_debt=debt,cash=cash,net_debt=debt-cash,source_ids=sorted({r['source_id'] for r in selected}))
        bridges.append(dict(entity_id=entity,observed_balances=vals,
            net_debt_change_to_june=vals['2026-06-30']['net_debt']-vals['2025-12-31']['net_debt'],
            october_status='Not observed; model retains last published June balance and +/-10% net debt sensitivity.'))
    write_json('data/processed/balance_bridges.json',bridges)
    terms=[
        ('sanepar','Agepar','precatorio','100% aos usuários: 50% investimentos não onerosos e 50% modicidade tarifária; atualização por WACC real pós-impostos 8,08% + IPCA.','doc_sapr_itr','PDF p61–62; nota 20'),
        ('sanepar','Agepar','tariff_discount','Desconto de 25% da tarifa mínima a partir de 24/08/2026, estimado em cerca de 30 meses; calendário efetivo sujeito à execução.','agepar_precatorio_20260819','HTML notícia 19/08/2026'),
        ('sanepar','Contrato','concession_duration','Prorrogação de 343 contratos até 05/06/2048; exceções: Maringá 2040, Andirá 2032 e Porto União 03/2048. Não representa todos os contratos com a mesma data.','doc_sapr_2t26','PDF p3; quadro descritivo das concessões'),
        ('copasa','Arsae-MG','investment_recognition','Terceira RTP: reconhecimento anual de investimentos; projeção de capex precisa ser conciliada com base e calendário tarifário.','doc_csmg_2t26','PDF p24'),
        ('sabesp','Arsesp/URAE-1','universalization','Meta de universalização URAE-1 em 2029; vencimento 19/10/2060. Compromisso contratual não é realização automática.','sabesp_ambiente_regulatorio','HTML; Contrato de Concessão nº 01/2024 da URAE 1')]
    write_csv('data/processed/regulatory_terms.csv',[
        dict(term_id=f'REG_{i:03}',entity_id=e,contract_or_cluster='source_specific',regulator=reg,term_type=kind,
             term_text=t,effective_from='',effective_to='',source_id=sources[key]['source_id'],source_location=loc,
             review_status='source_extracted_partial_contract_coverage')
        for i,(e,reg,kind,t,key,loc) in enumerate(terms,1)])
    da_results=[r for r in checks if r['year']==2025 and r['method'].startswith('EBIT +')]
    counts={s:sum(r['status']==s for r in checks) for s in sorted({r['status'] for r in checks})}
    lines=['# Conciliação ampliada das entradas históricas\n',
        f'{len(checks)} células candidatas examinadas. Contagens: '+str(counts)+'.\n',
        'Não foi procurada uma combinação de contas que apenas reproduzisse o número da planilha. Itens sem definição suficiente permanecem explicitamente não certificados. Diferença pode vir de reclassificação, reapresentação, escopo ou EBITDA ajustado; não é automaticamente erro.\n',
        '| Empresa | EBITDA informado 2025 | EBIT + D&A CVM | Diferença |',
        '|---|---:|---:|---:|']
    lines += [f"| {r['entity_id']} | {br(r['original'])} | {br(r['cvm_comparator'])} | {br(r['difference'])} |" for r in da_results]
    lines += ['\nA DRE da Sanepar de 2025 contém receita de precatório e provisão regulatória. EBITDA e alíquota efetiva históricos não são automaticamente recorrentes. A Sabesp requer ponte entre receita de serviços, construção e remuneração de ativo financeiro/itens não recorrentes. A Copasa distingue investimento físico anunciado de desembolso nas linhas da DFC.\n',
        'Plano Sanepar 2026–30: R$ 13.077,0 milhões, dos quais R$ 212,8 milhões de doações de redes. Sem identificar o desembolso por ano e por modalidade, o total não pode virar capex caixa integral. Os valores arredondados do original foram preservados apenas para reprodução e sensibilidades.\n',
        'Precatório: o passivo identificado e a regra foram coletados. O impacto incremental exige separar descontos e capex não oneroso já representados no cenário, taxa/tributação e datas de execução. A dedução nominal integral não foi promovida a ajuste econômico certificado.\n',
        'Ver `outputs/qa/extended_input_audit.csv`, `data/processed/balance_bridges.json`, `data/processed/cvm_accounts.csv` e `regulatory_terms.csv`. O grupo recebe as diferenças e as alternativas prontas para julgar; não precisa iniciar a busca de dados do zero.\n']
    text('outputs/draft/conciliacao_financeira.md','\n'.join(lines))
    from sync_project_docs import sync
    sync()
    print('Extended audit',counts)


if __name__=='__main__':audit()
