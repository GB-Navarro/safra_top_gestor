"""Synchronize project documentation from recorded evidence; never certify financial work."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import unquote

from common import ROOT, now, read_csv, read_json, sha256, write_csv, write_json

CENTRAL=ROOT/'ESTADO_DO_PROJETO.md'
EVIDENCE_START='<!-- PROJECT_EVIDENCE:START -->'
EVIDENCE_END='<!-- PROJECT_EVIDENCE:END -->'
BANNER_START='<!-- PROJECT_STATUS:START -->'
BANNER_END='<!-- PROJECT_STATUS:END -->'
# Pacotes analíticos versionados (contrato 1.0) e builds de peças da Parte 2: imutáveis, com manifesto/hashes próprios.
IMMUTABLE_BUNDLES=ROOT/'outputs/draft/analysis_bundle'
IMMUTABLE_BUILDS=ROOT/'outputs/draft/production'


_LOCK_HELD=False


@contextmanager
def doc_lock(operation):
    """Trava documental (data/interim/coordination/documentation.lock); reentrante dentro do mesmo processo."""
    global _LOCK_HELD
    if _LOCK_HELD:
        yield
        return
    import sys
    if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
    from production.common import documentation_lock
    with documentation_lock(operation,wait_seconds=120):
        _LOCK_HELD=True
        try:
            yield
        finally:
            _LOCK_HELD=False


def is_immutable(path):
    parents=Path(path).parents
    return IMMUTABLE_BUNDLES in parents or IMMUTABLE_BUILDS in parents


def optional_json(path):
    return read_json(path) if (ROOT/path).is_file() else {}


def optional_csv(path):
    return read_csv(path) if (ROOT/path).is_file() else []


def local_time(value):
    if not value:return 'não registrada'
    try:
        # Fixed -03:00 is the client timezone offset for this 2026 snapshot.
        return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(timezone(timedelta(hours=-3))).strftime('%d/%m/%Y %H:%M:%S (-03:00)')
    except ValueError:return value


def relative(path,target=CENTRAL):
    return Path(os.path.relpath(target,path.parent)).as_posix()


def managed_docs():
    fixed=[ROOT/p for p in ['README.md','EXECUTION_CONTEXT.md','SAFRA_TOP_GESTOR_2026_CONTEXT.md',
        'data/interim/decisoes_equipe.md','data/interim/feedback_ensaio.md','outputs/qa/relatorio_validacao.md']]
    paths=fixed+list((ROOT/'plans').glob('*.md'))+list((ROOT/'outputs/draft').rglob('*.md'))
    return sorted({p for p in paths if p.is_file() and not is_immutable(p)})


def review_date():
    m=re.search(r'Revisão documental: \*\*(\d{2}/\d{2}/\d{4})\*\*',CENTRAL.read_text(encoding='utf-8'))
    if not m:raise ValueError('Central document must declare its actual documentation review date.')
    return m.group(1)


def replace_block(content,start,end,replacement,insert=False):
    if start in content:
        if content.count(start)!=1 or content.count(end)!=1:raise ValueError('Duplicate/incomplete documentation markers')
        return re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda m:replacement,content,flags=re.S)
    if not insert:raise ValueError('Missing automatic evidence markers')
    lines=content.splitlines(keepends=True)
    at=next((i+1 for i,line in enumerate(lines) if line.startswith('# ')),0)
    lines.insert(at,'\n'+replacement+'\n')
    return ''.join(lines)


def banner(path):
    rel=path.relative_to(ROOT).as_posix()
    if rel.startswith('plans/'):kind='Plano de método e critérios; conclusão de cada fase depende de evidência.'
    elif rel.startswith('outputs/qa/'):kind='Relatório da execução indicada no próprio arquivo; sincronizar documentos não reexecuta os testes.'
    elif rel.startswith('outputs/draft/'):kind='Material de rascunho; conferir as limitações e o fechamento econômico na fonte central.'
    elif rel.startswith('data/interim/'):kind='Registro de trabalho; presença do formulário não comprova revisão ou ensaio.'
    elif path.name=='SAFRA_TOP_GESTOR_2026_CONTEXT.md':kind='Contexto de pesquisa e histórico; esta revisão documental não verifica novas regras ou fontes.'
    else:kind='Guia de leitura e continuidade; consultar o andamento na fonte central.'
    if path.name=='script_apresentacao.md' or 'teleprompter' in path.parts:
        kind+=' Aviso editorial: não pronunciar este bloco.'
    return f'{BANNER_START}\n> [Estado central do projeto]({relative(path)}) · Revisão documental: {review_date()}. {kind}\n{BANNER_END}'


def evidence():
    qa=optional_json('outputs/qa/execution_validation.json')
    recalc=optional_json('outputs/qa/workbook_recalculation.json')
    package=optional_json('outputs/qa/package_validation.json')
    word=optional_json('outputs/qa/script_word_counts.json')
    cfg=optional_json('config/collection.json')
    cells=optional_csv('outputs/qa/extended_input_audit.csv')
    counts=Counter(r['status'] for r in cells)
    sources=optional_csv('data/processed/sources.csv')
    observations=optional_csv('data/processed/observations.csv')
    accounts=optional_csv('data/processed/cvm_accounts.csv')
    backlog=optional_csv('data/catalog/collection_backlog.csv')
    actions=optional_csv('data/catalog/manual_export_requests.csv')
    model=ROOT/'outputs/draft/base_modelo_auditavel.xlsx'
    recalc_current=model.is_file() and recalc.get('delivery_workbook_sha256')==sha256(model)
    rendered=optional_json('outputs/qa/rendering.json') or []
    pages=', '.join(f"{r['name']}: {r['pages']} páginas" for r in rendered) or 'renderização não registrada'
    final_files=[p for p in (ROOT/'outputs/final').rglob('*') if p.is_file() and p.name!='.gitkeep']
    segments=optional_json('config/video_segments.json').get('segments',[])
    clips=sum((ROOT/s['path']).is_file() for s in segments)
    core_status='controles técnicos aprovados; revisão econômica pendente' if qa.get('status')=='passed_technical_checks_with_economic_review_pending' else qa.get('status','sem registro')
    cash_differences=counts['difference_requires_review']+counts['reported_vs_adjusted_ebitda_bridge_required']
    n=lambda v:f'{v:,}'.replace(',','.')
    rows=[('Última execução da análise/QA central registrada',local_time(qa.get('created_at'))),
        ('Estado do relatório',core_status),
        ('Fontes adquiridas / observações / contas CVM',f'{n(len(sources))} / {n(len(observations))} / {n(len(accounts))}'),
        ('Registros municipais SINISA (última extração registrada)',n(qa.get('sinisa_municipal_observations',0))),
        ('Originais preservados na execução registrada',str(qa.get('original_assets_preserved','sem registro'))),
        ('Testes centrais na última execução',f"{qa.get('core_test_count','?')}; código de saída {qa.get('core_tests_exit_code','?')}"),
        ('Recálculo independente Excel/Python',f"{recalc.get('checks',0)} comparações; {recalc.get('status','sem registro')}; "+('hash da planilha atual coincide' if recalc_current else 'não confirmado para a planilha atual')),
        ('Pacote — verificações registradas',f"{package.get('checks',0)}; {package.get('status','sem registro')} (não certifica premissas)"),
        ('Auditoria de entradas históricas',f"{len(cells)} células: {counts['within_rounding']} coincidências dentro do arredondamento, {cash_differences} diferenças a conciliar e {counts['semantic_mapping_not_certified']} sem mapeamento suficiente"),
        ('PDFs na última renderização',pages),
        ('Script / duração planejada',f"{word.get('total_words','?')} palavras, incluindo marcadores; {word.get('planned_seconds','?')} segundos planejados; ensaio real não inferido"),
        ('Fila / ações humanas cadastradas',f'{len(backlog)} tarefas de dados / {len(actions)} ações'),
        ('Clipes indicados presentes',f'{clips} de {len(segments)}; presença de arquivo não comprova qualidade/revisão'),
        ('Arquivos em outputs/final (exceto .gitkeep)',f'{len(final_files)}; quantidade não equivale a submissão')]
    pointer=optional_json('outputs/draft/analysis_bundle/latest.json')
    if pointer:
        bundle_dir=ROOT/'outputs/draft/analysis_bundle'/pointer.get('bundle_id','')
        man=optional_json((bundle_dir/'manifest.json').relative_to(ROOT).as_posix()) if (bundle_dir/'manifest.json').is_file() else {}
        aqa=optional_json((bundle_dir/'qa/analysis_validation.json').relative_to(ROOT).as_posix()) if (bundle_dir/'qa/analysis_validation.json').is_file() else {}
        rows.append(('Pacote analítico 1.0 (Parte 1)',f"{pointer.get('bundle_id')}; estado {man.get('state','?')}; QA analítica {aqa.get('status','sem registro')}"))
    published=optional_json('outputs/draft/production/published.json')
    if published:
        visual=optional_json('outputs/qa/visual_review.json')
        rows.append(('Peças publicadas (Parte 2)',f"build {published.get('build_id')} ({published.get('publish_id')}); validação {published.get('validation_status','sem registro')}; "
                     f"revisão visual {visual.get('status','sem registro')} ({'agente' if not visual.get('human_review') else 'grupo'})"))
    html=optional_json('outputs/qa/html/html_validation.json')
    if html:
        rows.append(('HTML10 — interação/offline/impressão',f"1920: {html.get('interaction_1920',{}).get('checks','?')} verificações {html.get('interaction_1920',{}).get('status','?')}; "
                     f"1366: {html.get('interaction_1366',{}).get('status','?')}; offline {html.get('offline',{}).get('status','?')}; PDF {html.get('pdf_pages',{}).get('pages','?')} páginas"))
    gates=optional_json('outputs/qa/release_validation.json')
    if gates:
        rows.append(('Portões de liberação (evidência real)','; '.join(f"{g['stage']}: {'liberado' if g['passed'] else 'bloqueado'}" for g in gates.get('gates',[]))))
    html10=optional_json('config/video_segments_html10.json').get('segments',[])
    if html10:
        rows.append(('Clipes do perfil HTML10',f"{sum((ROOT/s['path']).is_file() for s in html10)} de {len(html10)}"))
    completion=optional_json('outputs/qa/completion_documentation_validation.json')
    if completion:
        current=all((ROOT/p).is_file() and sha256(ROOT/p)==digest for p,digest in completion.get('source_snapshot',{}).items())
        freshness='fontes correspondem à revisão' if current else 'revalidação documental pendente para as fontes alteradas'
        rows += [('Contrato de fechamento — documentação',f"{completion.get('requirements','?')} requisitos; {completion.get('mapped_historical_cells','?')} células vinculadas; {freshness}; não é conclusão financeira"),
                 ('HTML interativo — plano',f"{completion.get('html_plan_pages','?')} páginas / {completion.get('html_plan_seconds','?')} segundos; "+('artefato presente, consultar validação HTML própria' if completion.get('html_artifact_present') else 'artefato ainda não gerado'))]
    inputs=['config/collection.json','data/catalog/collection_backlog.csv','data/catalog/manual_export_requests.csv',
        'outputs/draft/analysis_bundle/latest.json','outputs/draft/production/published.json','outputs/qa/visual_review.json',
        'outputs/qa/html/html_validation.json','outputs/qa/release_validation.json',
        'data/processed/sources.csv','data/processed/observations.csv','data/processed/cvm_accounts.csv',
        'outputs/qa/execution_validation.json','outputs/qa/workbook_recalculation.json','outputs/qa/extended_input_audit.csv',
        'outputs/qa/rendering.json','outputs/qa/script_word_counts.json']
    inputs += [p for p in ['data/catalog/completion_requirements.json','data/catalog/html_slide_plan.json'] if (ROOT/p).is_file()]
    fingerprint=hashlib.sha256(json.dumps({f:sha256(ROOT/f) for f in inputs if (ROOT/f).is_file()},sort_keys=True).encode()).hexdigest()
    lines=[EVIDENCE_START,'',
        'Trecho automático. Números extraídos dos arquivos atuais e das verificações **já registradas**; esta sincronização não executa nova validação econômica.','',
        '| Indicador | Registro |','|---|---|']
    lines += [f'| {a} | {b} |' for a,b in rows]
    lines += ['',
        'Evidências: [relatório técnico](outputs/qa/relatorio_validacao.md), [recálculo da planilha](outputs/qa/workbook_recalculation.json), [auditoria de células](outputs/qa/extended_input_audit.csv), [cobertura](data/processed/coverage.csv) e [ações humanas](data/catalog/manual_export_requests.csv).',
        '',f'<!-- PROJECT_SNAPSHOT_SHA256:{fingerprint} -->',EVIDENCE_END]
    return '\n'.join(lines)


def save_if_changed(path,content):
    if path.read_text(encoding='utf-8-sig')==content:return False
    path.write_text(content,encoding='utf-8')
    return True


def manifest_files(folder):
    return [dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha256(p))
            for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='manifest.json' and not is_immutable(p)]


def refresh_manifests():
    for name in ['outputs/draft/coleta','outputs/draft']:
        p=ROOT/name/'manifest.json'
        if not p.is_file():continue
        doc=read_json(p.relative_to(ROOT).as_posix());files=manifest_files(p.parent)
        if doc.get('files')!=files:
            doc['files']=files;doc['documentation_updated_at']=now()
            write_json(p.relative_to(ROOT).as_posix(),doc)


def refresh_audit():
    name='data/catalog/reorganization_audit.csv'
    if not (ROOT/name).is_file():return
    rows=read_csv(name);changed=False
    for row in rows:
        if row['content_policy']!='maintained_document':continue
        digest=sha256(ROOT/row['current_path'])
        if row['sha256_after']!=digest:
            row['sha256_after']=digest;row['bytes_preserved']=str(row['sha256_before']==digest)
            row['status']='documentation_updated';changed=True
    if changed:write_csv(name,rows)


def sync(review=None):
    with doc_lock('sync_project_docs: sincronização'):
        return _sync(review)


def _sync(review=None):
    if (ROOT/'data/catalog/completion_requirements.json').is_file():
        from validate_completion_docs import render_tables,validate
        render_tables()
        validate()
    if (ROOT/'data/catalog/two_part_execution.json').is_file():
        from validate_two_part_plans import render, validate as validate_parts
        render()
        validate_parts()
    if review:
        value=datetime.strptime(review,'%Y-%m-%d').strftime('%d/%m/%Y')
        content=CENTRAL.read_text(encoding='utf-8')
        content=re.sub(r'(Revisão documental: \*\*)\d{2}/\d{2}/\d{4}(\*\*)',lambda m:m[1]+value+m[2],content,count=1)
        save_if_changed(CENTRAL,content)
    changed=[]
    if save_if_changed(CENTRAL,replace_block(CENTRAL.read_text(encoding='utf-8'),EVIDENCE_START,EVIDENCE_END,evidence())):
        changed.append(CENTRAL.relative_to(ROOT).as_posix())
    for path in managed_docs():
        content=path.read_text(encoding='utf-8-sig')
        if save_if_changed(path,replace_block(content,BANNER_START,BANNER_END,banner(path),insert=True)):
            changed.append(path.relative_to(ROOT).as_posix())
    refresh_audit();refresh_manifests()
    return changed


def check():
    with doc_lock('sync_project_docs: verificação'):
        return _check()


def _check():
    errors=[];preserved=0;links=0
    if (ROOT/'data/catalog/completion_requirements.json').is_file():
        from validate_completion_docs import validate
        completion=validate()
        errors += ['Completion contract: '+error for error in completion['errors']]
    if (ROOT/'data/catalog/two_part_execution.json').is_file():
        from validate_two_part_plans import validate as validate_parts
        part_report=validate_parts()
        errors += ['Two-part plans: '+error for error in part_report['errors']]
    content=CENTRAL.read_text(encoding='utf-8')
    if replace_block(content,EVIDENCE_START,EVIDENCE_END,evidence())!=content:errors.append('Central evidence block is stale')
    phases=re.findall(r'^\| (A\d{2}) —',content,flags=re.M)
    if phases!=[f'A{i:02}' for i in range(1,12)]:errors.append('Central phase table must cover A01–A11 once, in order')
    handoff=ROOT/'EXECUTION_CONTEXT.md'
    if not handoff.is_file():
        errors.append('Agent handoff is missing')
    else:
        handoff_text=handoff.read_text(encoding='utf-8-sig')
        required_handoff=['## Ordem de leitura','## Escopo e instruções do usuário','## Ponto de retomada',
            '## Ambiente e dependências','## Arquivos, autoria e reconstrução','## Mapa de implementação',
            '## Comandos de retomada','## Registro de continuidade',
            '| Última tarefa |','| Verificações |','| Próxima ação |','| Dependências humanas |']
        for marker in required_handoff:
            if marker not in handoff_text:errors.append('Agent handoff lacks '+marker)
        stamp=re.search(r'Revisão de continuidade: \*\*(\d{2}/\d{2}/\d{4})\*\*',handoff_text)
        if not stamp or stamp[1]!=review_date():errors.append('Review the manual handoff and align its review date with the central document')
    docs=managed_docs()
    for path in docs:
        text=path.read_text(encoding='utf-8-sig')
        if replace_block(text,BANNER_START,BANNER_END,banner(path),insert=True)!=text:errors.append('Stale/missing central pointer: '+path.relative_to(ROOT).as_posix())
    all_docs=docs+[CENTRAL,ROOT/'AGENTS.md']
    pattern=r'\[[^\]]+\]\((<[^>]+>|(?:[^()\n]|\([^()\n]*\))*)\)'
    for path in all_docs:
        for raw in re.findall(pattern,path.read_text(encoding='utf-8-sig')):
            target=raw.strip().strip('<>')
            if re.match(r'^(https?://|mailto:|#)',target):continue
            target=unquote(target.split('#',1)[0])
            if not target:continue
            links+=1
            if not (path.parent/target).exists():errors.append(f'Broken local link: {path.relative_to(ROOT).as_posix()} -> {target}')
    baseline=optional_json('data/catalog/original_files_manifest.json')
    for item in baseline.get('files',[]):
        if item['content_policy']!='preserve_bytes':continue
        path=ROOT/item['current_path']
        if not path.is_file() or sha256(path)!=item['sha256']:errors.append('Original asset changed: '+item['current_path'])
        else:preserved+=1
    for name in ['outputs/draft/coleta','outputs/draft']:
        if (ROOT/name/'manifest.json').is_file() and read_json(name+'/manifest.json')['files']!=manifest_files(ROOT/name):
            errors.append('Draft manifest is stale: '+name)
    result=dict(checked_at=now(),status='passed' if not errors else 'failed',documentation_review_date=review_date(),
        central_document=CENTRAL.relative_to(ROOT).as_posix(),agent_handoff='EXECUTION_CONTEXT.md',managed_markdown_files=len(docs),
        local_links_checked=links,original_assets_preserved=preserved,errors=errors,
        scope='Documentation pointers/evidence/links, all eleven phase rows, original hashes and draft manifests; no financial rerun or human approval.')
    write_json('outputs/qa/documentation_validation.json',result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true',help='Check freshness and integrity without editing documentation')
    p.add_argument('--review-date',help='Actual client documentation review date, YYYY-MM-DD; does not change data cutoff')
    args=p.parse_args()
    if args.check and args.review_date:p.error('--check cannot change the review date')
    with doc_lock('sync_project_docs: CLI'):
        changed=[] if args.check else sync(args.review_date)
        result=check()
    print(json.dumps(dict(status=result['status'],changed=changed,markdown_files=result['managed_markdown_files'],links=result['local_links_checked'],originals_preserved=result['original_assets_preserved'],errors=result['errors']),ensure_ascii=False))
    return bool(result['errors'])


if __name__=='__main__':raise SystemExit(main())
