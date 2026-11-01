"""Check coverage of known completion requirements, not completion of the financial work."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import re

from common import ROOT, now, read_csv, read_json, sha256, write_csv, write_json

CONTRACT='data/catalog/completion_requirements.json'
PAGES='data/catalog/html_slide_plan.json'
MAPPING='data/catalog/cell_issue_mapping.csv'
DOC='plans/09_contrato_de_fechamento.md'
HTML_DOC='plans/10_plano_html_interativo.md'


def expanded_requirements():
    c=read_json(CONTRACT)
    return c,[{**c['defaults'],**r} for r in c['requirements']]


def cell_mapping():
    rows=[];uncovered=[]
    audit=read_csv('outputs/qa/extended_input_audit.csv')
    for r in audit:
        if r['status']=='within_rounding':continue
        match=re.search(r'(\d+)$',r['cell'])
        cell_row=int(match.group(1)) if match else None
        e=r['entity_id'];key=None
        if cell_row in (14,16):key='C05'
        elif e=='sabesp' and cell_row in (7,8):key='C02'
        elif e=='sabesp' and cell_row==9:key='C03'
        elif e=='sabesp' and cell_row==11:key='C04'
        elif e=='copasa' and cell_row==11:key='C06'
        elif e=='sanepar' and cell_row in (7,8):key='C07'
        if key is None:uncovered.append(f"{r['workbook']}:{r['cell']}:{r['status']}");continue
        rows.append(dict(requirement_id=key,entity_id=e,workbook=r['workbook'],year=r['year'],cell=r['cell'],
            concept=r['concept'],current_status=r['status'],original=r['original'],cvm_comparator=r['cvm_comparator'],
            difference=r['difference'],unit='BRL',scale='1000000',source_ids=r['source_ids'],source_locations=r['source_locations']))
    return rows,uncovered


def replace_section(path,label,lines):
    p=ROOT/path;text=p.read_text(encoding='utf-8')
    start=f'<!-- {label}:START -->';end=f'<!-- {label}:END -->'
    if text.count(start)!=1 or text.count(end)!=1:raise ValueError('Missing/duplicate generated markers: '+path)
    block=start+'\n\n'+'\n'.join(lines)+'\n\n'+end
    new=re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda m:block,text,flags=re.S)
    if new!=text:p.write_text(new,encoding='utf-8')


def required_sections():
    contract,rows=expanded_requirements()
    table=['| ID / responsável / prioridade | Trabalho | Critério de fechamento |','|---|---|---|']
    for r in rows:
        scope=' · HTML futuro' if r['scope']=='html_extension' else (' · condicional' if r['scope']=='conditional' else '')
        table.append(f"| {r['id']} · {r['owner']} · {r['priority']}{scope} | **{r['title']}** — {r['need']} | {' '.join(r['acceptance'])} |")
    mapping,uncovered=cell_mapping();counts=Counter(r['requirement_id'] for r in mapping)
    titles={r['id']:r['title'] for r in rows}
    cells=['| Requisito | Lacuna atual | Células abertas vinculadas |','|---|---|---:|']
    cells += [f'| {key} | {titles.get(key,"REQUISITO AUSENTE")} | {value} |' for key,value in sorted(counts.items())]
    cells += [f"\nTotal vinculado: **{len(mapping)}**. Ocorrências sem regra de cobertura: **{len(uncovered)}**. Esse vínculo não resolve a ocorrência."]
    pages=read_json(PAGES);web=['| Página / origem | Conteúdo e voz | Janela planejada | Interação |','|---|---|---|---|']
    elapsed=0
    def mmss(v):return f'{v//60}:{v%60:02}'
    for r in pages['pages']:
        end=elapsed+r['seconds']
        source='/'.join('S'+str(i) for i in r['source_slides'])
        web.append(f"| {r['id']} ← {source} ({', '.join(r['source_blocks'])}) | **{r['title']}** · {r['speaker']} | {mmss(elapsed)}–{mmss(end)} | {r['interaction']} |")
        elapsed=end
    artifacts=['| Família | Destino / escopo | Artefatos a gerar ou regenerar | Requisitos responsáveis |','|---|---|---|---|']
    for group in contract.get('deliverable_groups',[]):
        artifacts.append(f"| {group['id']} — {group['name']} | {group['root']} | {'; '.join(group['artifacts'])} | {', '.join(group['covered_by'])} |")
    return table,cells,web,artifacts


def render_tables():
    table,cells,web,artifacts=required_sections()
    mapping,_=cell_mapping()
    write_csv(MAPPING,mapping,['requirement_id','entity_id','workbook','year','cell','concept','current_status','original','cvm_comparator','difference','unit','scale','source_ids','source_locations'])
    replace_section(DOC,'COMPLETION_REQUIREMENTS',table)
    replace_section(DOC,'CELL_COVERAGE',cells)
    replace_section(HTML_DOC,'HTML_SLIDE_MAP',web)
    replace_section(DOC,'COMPLETION_DELIVERABLES',artifacts)


def optional_published_build():
    published=ROOT/'outputs/draft/production/published.json'
    return read_json('outputs/draft/production/published.json')['build_id'] if published.is_file() else None


def validate():
    errors=[];contract,rows=expanded_requirements();by_id={r['id']:r for r in rows}
    if len(by_id)!=len(rows):errors.append('Duplicate completion IDs')
    routes={r['registry_id'] for r in read_csv('data/catalog/source_registry.csv')}
    required=['id','title','owner','priority','scope','status','need','method','existing_evidence','source_routes',
              'phases','tasks','human_actions','numbers','depends_on','outputs','acceptance','if_unavailable','closure_evidence']
    for r in rows:
        for f in required:
            if f not in r:errors.append(f"{r.get('id','?')}: missing {f}")
        for f in ['title','owner','priority','need','method','if_unavailable']:
            if not r.get(f):errors.append(r['id']+': blank '+f)
        if not r.get('acceptance') or not r.get('outputs') or not r.get('existing_evidence'):errors.append(r['id']+': not actionable')
        for path in r.get('existing_evidence',[]):
            if not (ROOT/path).exists():errors.append(r['id']+': missing existing evidence '+path)
        for route in r.get('source_routes',[]):
            if route not in routes:errors.append(r['id']+': unknown source route '+route)
        for dependency in r.get('depends_on',[]):
            if dependency not in by_id:errors.append(r['id']+': unknown prerequisite '+dependency)
        if r.get('status')=='closed':
            if not r.get('closure_evidence'):errors.append(r['id']+': closed without evidence')
            for path in r.get('closure_evidence',[]):
                if not (ROOT/path).exists():errors.append(r['id']+': closure evidence missing '+path)
    visiting=set();done=set()
    def visit(key):
        if key in visiting:errors.append('Cyclic requirement dependencies: '+key);return
        if key in done or key not in by_id:return
        visiting.add(key)
        for parent in by_id[key].get('depends_on',[]):visit(parent)
        visiting.remove(key);done.add(key)
    for key in by_id:visit(key)
    coverage={}
    registries=[('phases',{f'A{i:02}' for i in range(1,12)}),
        ('tasks',{r['task_id'] for r in read_csv('data/catalog/collection_backlog.csv')}),
        ('human_actions',{r['request_id'] for r in read_csv('data/catalog/manual_export_requests.csv')}),
        ('numbers',{r['n_id'] for r in read_csv('data/processed/n_status.csv')})]
    for field,expected in registries:
        actual={value for r in rows for value in r.get(field,[])}
        missing=sorted(expected-actual);unknown=sorted(actual-expected)
        coverage[field]=dict(expected=len(expected),covered=len(actual&expected),missing=missing,unknown=unknown)
        if missing or unknown:errors.append(field+': incomplete or invalid references')
    rule_ids=[r['id'] for r in contract['rules']]
    if len(rule_ids)!=len(set(rule_ids)):errors.append('Duplicate rule IDs')
    if not {f'R{i:02}' for i in range(1,11)}.issubset(rule_ids):errors.append('Missing known rule/plan/user requirement R01–R10')
    if set(contract.get('rule_origins',{}))!={'R01-R06','R07-R09','R10'}:errors.append('Requirement origins must separate public/H07, team quality criteria and HTML request')
    for rule in contract['rules']:
        if not rule['covered_by'] or any(c not in by_id for c in rule['covered_by']):errors.append('Uncovered requirement '+rule['id'])
    groups=contract.get('deliverable_groups',[])
    if not {f'G{i:02}' for i in range(1,9)}.issubset({g['id'] for g in groups}):errors.append('Missing known deliverable family G01–G08')
    if len(groups)!=len({g['id'] for g in groups}):errors.append('Duplicate deliverable family')
    for group in groups:
        if not group.get('artifacts') or not group.get('root') or not group.get('covered_by') or any(c not in by_id for c in group.get('covered_by',[])):
            errors.append('Unspecified deliverable family '+group['id'])
    mapping,uncovered=cell_mapping()
    if uncovered:errors.append('Unmapped historical issues: '+str(uncovered))
    if any(r['requirement_id'] not in by_id for r in mapping):errors.append('Historical cell mapping references an absent requirement')
    if read_csv(MAPPING)!=[{k:str(v) for k,v in r.items()} for r in mapping]:errors.append('Cell issue mapping is stale')
    expected_open=[r for r in read_csv('outputs/qa/extended_input_audit.csv') if r['status']!='within_rounding']
    if len(mapping)!=len(expected_open):errors.append('Cell coverage count differs from open audit')
    keys=[(r['workbook'],r['cell']) for r in mapping]
    if len(keys)!=len(set(keys)):errors.append('Repeated historical cell mapping')
    pages=read_json(PAGES)
    if [r['id'] for r in pages['pages']]!=[f'P{i:02}' for i in range(1,11)]:errors.append('HTML map must have exactly P01–P10')
    source_script=read_json('outputs/qa/script_word_counts.json')
    if sum(r['seconds'] for r in pages['pages'])!=pages['planned_seconds'] or pages['planned_seconds']!=source_script['planned_seconds']:errors.append('HTML timing differs from registered script allocation')
    if any(not isinstance(r['seconds'],int) or r['seconds']<=0 for r in pages['pages']):errors.append('HTML page duration must be a positive integer')
    if pages['planned_seconds']>=pages['max_video_seconds_public']:errors.append('Planned video lacks buffer')
    from pptx import Presentation
    source_pages=len(Presentation(ROOT/pages['source_pptx']).slides)
    source_use=Counter(n for r in pages['pages'] for n in r['source_slides'])
    if source_pages!=9 or source_use!=Counter({n:2 if n==7 else 1 for n in range(1,10)}):errors.append('HTML map does not cover current nine slides with only S7 split')
    for r in pages['pages']:
        for field in ['title','speaker','interaction','acceptance','inputs','source_blocks']:
            if not r.get(field):errors.append(r['id']+': missing plan '+field)
        for path in r['inputs']:
            if not (ROOT/path).is_file():errors.append(r['id']+': missing current input '+path)
        speakers={b['speaker'] for b in source_script['blocks'] if b['block'] in {s.split('.')[0] for s in r['source_blocks']}}
        if speakers!={r['speaker']}:errors.append(r['id']+': voice differs from source script blocks')
    table,cells,web,artifacts=required_sections()
    for path,label,lines in [(DOC,'COMPLETION_REQUIREMENTS',table),(DOC,'CELL_COVERAGE',cells),(HTML_DOC,'HTML_SLIDE_MAP',web),(DOC,'COMPLETION_DELIVERABLES',artifacts)]:
        text=(ROOT/path).read_text(encoding='utf-8')
        block=f'<!-- {label}:START -->\n\n'+'\n'.join(lines)+f'\n\n<!-- {label}:END -->'
        if block not in text:errors.append('Stale generated completion view: '+path+'/'+label)
    claims=read_csv('data/processed/claims.csv');valuation=read_json('data/processed/valuation.json')
    if (ROOT/'data/processed/CANONICAL_SOURCE.json').is_file():
        # Contrato 1.0 publicado: casos com flags próprias; posição dos claims vem do build publicado
        missing_flags=sum('equity_floor_applied' not in c or 'equity_residual_before_floor' not in c for c in valuation['cases'])
        published=optional_published_build()
        claim_pages=sorted({r['page'] for r in read_csv(f'outputs/draft/production/{published}/claim_placements.csv')}) if published else []
    else:
        missing_flags=sum('equity_floor_applied' not in s or 'equity_residual_before_floor' not in s for r in valuation.values() for s in r['scenarios']+r['sensitivity'])
        claim_pages=sorted({r['slide_id'] for r in claims})
    html_validation=ROOT/'outputs/qa/html/html_validation.json'
    html_checks=read_json('outputs/qa/html/html_validation.json') if html_validation.is_file() else {}
    html_checked=bool(html_checks) and all(html_checks.get(k,{}).get('status')=='passed' for k in ['interaction_1920','interaction_1366','offline','pdf_pages'])
    report=dict(checked_at=now(),status='passed_known_requirement_coverage' if not errors else 'failed',
        review_date=contract['review_date'],requirements=len(rows),coverage=coverage,rules_covered=len(rule_ids),
        deliverable_families=len(groups),
        execution_status_counts=dict(sorted(Counter(r['status'] for r in rows).items())),
        open_historical_cells=len(expected_open),mapped_historical_cells=len(mapping),cell_groups=dict(sorted(Counter(r['requirement_id'] for r in mapping).items())),
        html_plan_pages=len(pages['pages']),html_plan_seconds=pages['planned_seconds'],current_pptx_pages=source_pages,
        planned_html_video_segments_if_adopted=len(pages['pages'])-1+5,
        dependency_graph_acyclic=not any(e.startswith('Cyclic') for e in errors),
        observed_open_evidence=dict(claims=len(claims),claim_slide_ids=claim_pages,
            corporate_actions=len(read_csv('data/processed/corporate_actions.csv')),scenario_or_grid_points_without_residual_flags=missing_flags),
        source_snapshot={p:sha256(ROOT/p) for p in [CONTRACT,PAGES,'outputs/qa/extended_input_audit.csv','data/processed/claims.csv','data/processed/corporate_actions.csv','data/processed/valuation.json',pages['source_pptx']]},
        errors=errors,financial_reconciliation_performed=False,
        html_artifact_present=(ROOT/'outputs/draft/html/apresentacao_esg.html').is_file(),html_implementation_checks_executed=html_checked,
        scope='Covers known plans/rules and observed gaps. No proof of financial correctness, final release, human participation, submission or unknown private H07 requirements.')
    write_json('outputs/qa/completion_documentation_validation.json',report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sync',action='store_true',help='Refresh derived cell map and documentation tables before checking')
    args=p.parse_args()
    if args.sync:render_tables()
    report=validate()
    print(json.dumps({k:report[k] for k in ['status','requirements','coverage','mapped_historical_cells','html_plan_pages','html_plan_seconds','errors']},ensure_ascii=False))
    return bool(report['errors'])


if __name__=='__main__':raise SystemExit(main())
