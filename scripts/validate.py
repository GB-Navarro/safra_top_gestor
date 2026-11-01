"""Cross-artifact checks, immutable-source validation, and explicit release blockers."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from pptx import Presentation

from common import ROOT,acquisitions,read_csv,read_json,sha256,write_json,now
from analysis_outputs import text


def validate():
    errors=[];notes=[]
    sources={r['source_id']:r for r in read_csv('data/processed/sources.csv')}
    for source in sources.values():
        p=ROOT/source['local_path']
        if not p.is_file() or sha256(p)!=source['sha256']:errors.append('Source hash mismatch: '+source['source_id'])
    observed=read_csv('data/processed/observations.csv')
    definitions={r['definition_id'] for r in read_csv('data/processed/definitions.csv')}
    metrics={r['metric_id'] for r in read_csv('data/catalog/metric_dictionary.csv')}
    cutoff=read_json('config/collection.json')['scope']['information_cutoff'][:10]
    unique=set()
    for r in observed:
        if r['source_id'] not in sources:errors.append('Missing source '+r['obs_id'])
        if r['definition_id'] not in definitions or r['metric_id'] not in metrics:errors.append('Missing definition/metric '+r['obs_id'])
        if not r['source_location']:errors.append('Missing location '+r['obs_id'])
        if r['fact_type']=='realizado' and r['period_end']>cutoff:errors.append('Future realized data '+r['obs_id'])
        if r['observed_at']>cutoff:errors.append('Future observation snapshot '+r['obs_id'])
        key=tuple(r[k] for k in ['entity_id','instrument_id','metric_id','period_start','period_end','scope','definition_id','fact_type','source_id'])
        if key in unique:errors.append('Duplicate observation '+r['obs_id'])
        unique.add(key)
        if float(r['scale'])<=0:errors.append('Bad scale '+r['obs_id'])
    accounts=read_csv('data/processed/cvm_accounts.csv')
    if any(r['published_at']>cutoff for r in accounts):errors.append('Post-cutoff CVM filing')
    eps=[r for r in accounts if r['statement']=='DRE' and r['account_code'].startswith('3.99')]
    if any(r['value_brl_million']!='' for r in eps):errors.append('Per-share field improperly normalized as currency millions')
    # Stream the 97 MB municipal CSV: keeping all string columns in memory
    # while spawning tests can exhaust the workstation's available memory.
    sinisa_count=0;energy=[];energy_keys=set()
    with (ROOT/'data/processed/sinisa_municipal.csv').open(encoding='utf-8',newline='') as stream:
        for row in csv.DictReader(stream):
            sinisa_count+=1
            if row['metric_code']!='GFI2004':continue
            key=tuple(row[k] for k in ['entity_id','municipality','metric_code'])
            if key in energy_keys:errors.append('Duplicated municipal energy cost')
            energy_keys.add(key);energy.append(row)
    for entity,uf in [('sabesp','SP'),('copasa','MG'),('sanepar','PR')]:
        if {r['state'] for r in energy if r['entity_id']==entity}!={uf}:errors.append('Provider homonym/state mismatch')
    rep=read_json('outputs/qa/model_replication.json')
    if not rep['passed']:errors.append('Legacy mathematical replication failed')
    baseline=read_json('data/catalog/original_files_manifest.json')
    preserved=0
    for item in baseline['files']:
        p=ROOT/item['current_path']
        if item['content_policy']=='preserve_bytes':
            if not p.is_file() or sha256(p)!=item['sha256']:errors.append('Original asset changed: '+item['current_path'])
            else:preserved+=1
    unit=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
    text('outputs/qa/unit_tests.txt',unit.stdout+'\n'+unit.stderr)
    if unit.returncode:errors.append('Core regression tests failed')
    ppt=Presentation(ROOT/'outputs/draft/apresentacao_esg.pptx')
    if len(ppt.slides)!=9:errors.append('Presentation must contain nine slides')
    if not all(slide.has_notes_slide for slide in ppt.slides):errors.append('Missing speaker notes')
    scripted=read_json('outputs/qa/script_word_counts.json')
    if not 1050<=scripted['total_words']<=1300:errors.append('Script word count outside production range')
    if set(b['speaker'] for b in scripted['blocks'])!={'Rodrigo','Lorenzo','Michel','Navarro','Todos'}:errors.append('Speaker allocation incomplete')
    rendered=[]
    if (ROOT/'outputs/qa/rendering.json').exists():
        rendered=read_json('outputs/qa/rendering.json')
        if any(r['shapes_outside_slide'] for r in rendered):errors.append('Shapes outside slide bounds')
    else:errors.append('PDF rendering missing')
    facts=read_json('data/processed/presentation_facts.json')
    valuation=read_json('data/processed/valuation.json')
    for e,r in valuation.items():
        if facts['prices'][e]!=r['price_reference']:errors.append('Presentation price differs from model')
    chart=read_csv('outputs/draft/figuras/s06_energia.csv')
    bridge={r['entity_id']:r for r in read_json('data/processed/esg_bridge.json')}
    for r in chart:
        if abs(float(r['retention_100pct'])-bridge[r['entity_id']]['capex_break_even_upper'])>1e-8:errors.append('Chart/ESG bridge mismatch')
    for r in rendered:
        from pypdf import PdfReader
        if len(PdfReader(ROOT/r['pdf_path']).pages)!=r['pages']:errors.append('PDF page mismatch')
        if r.get('pptx_sha256')!=sha256(ROOT/'outputs/draft'/(r['name']+'.pptx')):errors.append('PDF rendering is stale after PPTX edit')
    visual_status='pending'
    if (ROOT/'outputs/qa/visual_review.json').exists():
        review=read_json('outputs/qa/visual_review.json')
        if all(review.get('pdf_hashes',{}).get(r['name'])==sha256(ROOT/r['pdf_path']) for r in rendered):
            visual_status=review['status']
    calc_status='not_checked_for_current_workbook'
    if (ROOT/'outputs/qa/workbook_recalculation.json').exists():
        calc=read_json('outputs/qa/workbook_recalculation.json')
        book_path=ROOT/'outputs/draft/base_modelo_auditavel.xlsx'
        if book_path.is_file() and calc['delivery_workbook_sha256']==sha256(book_path):calc_status=calc['status']
    extended=read_csv('outputs/qa/extended_input_audit.csv')
    report=dict(created_at=now(),status='passed_technical_checks_with_economic_review_pending' if not errors else 'failed',errors=errors,source_files_verified=len(sources),canonical_observations=len(observed),cvm_accounts=len(accounts),sinisa_municipal_observations=sinisa_count,original_assets_preserved=preserved,core_tests_exit_code=unit.returncode,core_test_count=13,extended_input_audit_cells=len(extended),extended_input_audit_statuses={s:sum(r['status']==s for r in extended) for s in sorted({r['status'] for r in extended})},script_words=scripted['total_words'],planned_video_seconds=560,rendering_and_visual_review='see rendering.json and visual_review.json; image review invalidated by changed PDF hash',verified_scope=['source hashes and original assets','CVM filing/date/unit filters including EPS exclusion','observation lineage and definitions','45 basic annual input checks and extended 195-cell audit with unresolved differences disclosed','independent reproduction of three DCFs','share class arithmetic and limited-liability guard','energy scope, horizon and retention arithmetic','slide/PDF counts, rendering freshness, chart data and script speakers'],economic_certification=False,release_blockers=['H08/H09: operating assumptions, capital cost, reinvestment and thesis review','Obligation cash-flow overlap and June-to-October balance bridge unresolved','Copasa nonpositive residual in experimental case; no approved target','H07: supplementary instructions/hour/channel','H10/H11/H13: real rehearsal, real recordings, actual submission'],optional_confirmation=['H01: terminal confirmation of public close and latest capital events'],note='Passing tests verifies described mathematics and data handling, not future forecasts or an unconditional investment recommendation.')
    write_json('outputs/qa/execution_validation.json',report)
    lines=['# Validação da execução\n',f"Status: **{report['status']}**.\n",f"Fontes: {len(sources)}; observações: {len(observed)}; contas CVM: {len(accounts)}; registros municipais SINISA: {sinisa_count}.\n",f"Originais preservados: {preserved}. Script: {scripted['total_words']} palavras; tempo planejado 9:20, ainda sem ensaio humano.\n",'## Escopo verificado\n']
    lines += ['- '+v for v in report['verified_scope']]
    lines+=['\n## Pendências materiais\n']+['- '+v for v in report['release_blockers']]
    lines+=['\n## Erros técnicos\n']+(['- '+v for v in errors] if errors else ['Nenhum erro nos controles executados. A revisão econômica e audiovisual continua pendente.'])
    report['visual_review_status']=visual_status
    report['independent_workbook_recalculation_status']=calc_status
    write_json('outputs/qa/execution_validation.json',report)
    lines += ['\n## Artefatos e segunda verificação\n',
        f'Revisão visual do PDF atual: {visual_status}. Recálculo independente da planilha atual: {calc_status}.',
        'Ver package_validation.json, workbook_recalculation.json e video_pipeline_test.json. O teste de vídeo é técnico/sintético e não substitui clipes, ensaios ou participação real.\n']
    text('outputs/qa/relatorio_validacao.md','\n'.join(lines)+'\n')
    print(json.dumps({k:report[k] for k in ['status','errors','source_files_verified','canonical_observations','cvm_accounts','sinisa_municipal_observations','script_words']},ensure_ascii=False))
    from sync_project_docs import sync
    sync()
    return report


def validate_packages():
    import openpyxl
    from math import isfinite
    errors=[];checks=0
    for name in ['base_modelo_auditavel.xlsx','coleta/base_dados_coletados.xlsx']:
        book=openpyxl.load_workbook(ROOT/'outputs/draft'/name,data_only=True,read_only=True)
        expected={'Observacoes':len(read_csv('data/processed/observations.csv')),'Contas_CVM':len(read_csv('data/processed/cvm_accounts.csv')),'Auditoria_195':195}
        for sheet,count in expected.items():
            if book[sheet].max_row!=count+1:errors.append(name+': row count '+sheet)
            checks+=1
        if name=='base_modelo_auditavel.xlsx':
            values=read_json('data/processed/valuation.json')
            for i,(e,r) in enumerate(values.items(),2):
                for col,key in [(6,'terminal_fcff'),(9,'pv_terminal'),(10,'pv_explicit'),(11,'enterprise_value'),(15,'equity_residual_before_floor'),(16,'equity_value'),(18,'average_share_value')]:
                    cached=book['Terminal'].cell(i,col).value
                    if cached is None or not isfinite(cached) or abs(cached-r['common_base'][key])>1e-7:errors.append('Terminal cache mismatch '+e+'/'+key)
                    checks+=1
            for row in book['Projecoes'].iter_rows(min_row=2):
                company,year=row[0].value,row[1].value
                f=next(f for f in values[company]['common_base']['flows'] if f['year']==year)
                if abs(row[15].value-f['discounted_fcff'])>1e-8:errors.append('FCFF cache mismatch')
                checks+=1
        book.close()
    for folder in ['outputs/draft/coleta','outputs/draft']:
        for f in read_json(folder+'/manifest.json')['files']:
            path=ROOT/f['path']
            if not path.is_file() or sha256(path)!=f['sha256']:errors.append('Manifest hash mismatch '+f['path'])
            checks+=1
    write_json('outputs/qa/package_validation.json',dict(created_at=now(),status='passed' if not errors else 'failed',checks=checks,errors=errors,
        scope='Excel rows, cached FCFF/terminal values vs Python, manifest files/hashes; not financial assumption certification'))
    if errors:raise ValueError(errors)
    print('Package checks passed',checks)


if __name__=='__main__':
    result=validate()
    sys.exit(bool(result['errors']))
