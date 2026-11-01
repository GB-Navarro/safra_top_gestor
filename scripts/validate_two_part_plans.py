"""Render/check the two execution plans; this never executes financial or presentation work."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import PurePosixPath
import re

from common import ROOT, now, read_csv, read_json, sha256, write_json

SPEC = 'data/catalog/two_part_execution.json'
REPORT = 'outputs/qa/two_part_plan_validation.json'
LABELS = ['TWO_PART_PATHS', 'TWO_PART_TASKS', 'TWO_PART_CONTRACT', 'TWO_PART_SHARED']


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def blocks(spec, part):
    b = spec['bundle_contract']
    paths = ['Escrita exclusiva de trabalho:', ''] + [f'- `{p}`' for p in part['exclusive_writes']]
    if part.get('integration_only_writes'):
        paths += ['', 'Publicação somente pelo integrador, com trava/manifesto:', '']
        paths += [f'- `{p}`' for p in part['integration_only_writes']]
    paths += ['', 'Insumos existentes para iniciar, somente leitura:', '']
    paths += [f'- `{p}`' for p in part['inputs']]
    tasks = ['| Tarefa / depende de | O que fazer e por quê / cobertura | Aceite |', '|---|---|---|']
    for t in part['tasks']:
        tasks.append(f"| **{t['id']} — {cell(t['title'])}** / {', '.join(t['depends_on']) or 'início'} | {cell(t['action'])} ({', '.join(t['requirements'])}) | {cell(t['acceptance'])} |")
    contract = [f"Versão: **{b['version']}**. Produtor `{b['publisher']}`; consumidor `{b['consumer']}`. Diretório `{b['candidate_root']}`.", '',
                'Arquivos mínimos (incluem arquivos de auditoria, não só dados de renderização):', '']
    contract += [f'- `{p}`' for p in b['minimum_files']]
    contract += ['', '| Objeto | Campos/estados normativos |', '|---|---|']
    for key, title in [('manifest_required', 'Manifesto'), ('states', 'Estados analíticos publicados'),
                       ('value_required', 'Observação/valor'), ('value_states', 'Estado do valor'),
                       ('valuation_case_required', 'Cada case, inclusive grade'), ('target_validity', 'Validade do alvo'),
                       ('claim_required', 'Afirmação'), ('narrative_slots', 'Slots narrativos')]:
        contract.append(f"| {title} | {', '.join('`'+v+'`' for v in b[key])} |")
    contract += ['', 'Cabeçalhos mínimos das tabelas de identidade e evidência; campos adicionais compatíveis são permitidos:', '', '| Tabela | Campos |', '|---|---|']
    contract += [f"| `{name}` | {', '.join('`'+v+'`' for v in fields)} |" for name, fields in b['table_core_headers'].items()]
    for key in ['serialization', 'manifest_rule', 'result_envelope', 'presentation_views', 'narrative_rule', 'evidence_rule', 'case_rule',
                'publish_rule', 'baseline_rule', 'major_version_rule', 'progress_rule']:
        contract += ['', b[key]]
    shared = ['| Requisito compartilhado | Responsabilidade desta parte |', '|---|---|']
    shared += [f"| {key} | {cell(value[part['id']])} |" for key, value in spec['shared_requirement_slices'].items()]
    result = dict(zip(LABELS, [paths, tasks, contract, shared]))
    if part['id'] == 'production':
        pages = ['| Página / origem | Conteúdo | Voz / segundos planejados |', '|---|---|---|']
        for page in read_json('data/catalog/html_slide_plan.json')['pages']:
            pages.append(f"| {page['id']} ← {'/'.join('S'+str(i) for i in page['source_slides'])} | {page['title']} | {page['speaker']} / {page['seconds']} |")
        result['TWO_PART_PAGES'] = pages
    return result


def block_text(label, lines):
    return f'<!-- {label}:START -->\n\n' + '\n'.join(lines) + f'\n\n<!-- {label}:END -->'


def render(spec=None):
    spec = spec or read_json(SPEC)
    for part in spec['parts']:
        p = ROOT / part['document']
        text = p.read_text(encoding='utf-8')
        for label, lines in blocks(spec, part).items():
            start, end = f'<!-- {label}:START -->', f'<!-- {label}:END -->'
            if text.count(start) != 1 or text.count(end) != 1:
                raise ValueError('Missing/duplicate plan markers: ' + str(p))
            text = re.sub(re.escape(start)+r'.*?'+re.escape(end), lambda _: block_text(label, lines), text, flags=re.S)
        if text != p.read_text(encoding='utf-8'):
            p.write_text(text, encoding='utf-8')


def overlaps(a, b):
    a, b = a.rstrip('/'), b.rstrip('/')
    return a == b or a.startswith(b+'/') or b.startswith(a+'/')


def validate_spec(spec, check_docs=True):
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    contract = read_json('data/catalog/completion_requirements.json')
    expected = {r['id'] for r in contract['requirements']}
    parts = spec['parts']
    require(len(parts) == 2 and {p['id'] for p in parts} == {'analysis', 'production'}, 'Exactly two named parts required')
    require(spec['status'] == 'plans_created_not_executed', 'Planning must not claim implementation')
    try:
        date.fromisoformat(spec['review_date'])
    except (ValueError, TypeError):
        errors.append('Invalid plan review date')
    require({p['document'] for p in parts} == {'plans/11_plano_agente_analise_dados.md', 'plans/12_plano_agente_engenharia_entrega.md'}, 'Two distinct plan documents required')
    seen = Counter(t['id'] for p in parts for t in p['tasks'])
    require(all(n == 1 for n in seen.values()), 'Duplicate task IDs')
    coverage, writers = {}, []
    for part in parts:
        pid = part['id']
        require(not part['required_other_part_outputs_to_start'], 'Cross-part start dependency: '+pid)
        require(not part['required_other_part_outputs_for_autonomous_delivery'], 'Cross-part autonomous delivery dependency: '+pid)
        tasks = {t['id']: t for t in part['tasks']}
        require(bool(tasks) and bool(part['autonomous_deliverable']), 'Missing autonomous work/deliverable: '+pid)
        require(all(t.startswith(part['prefix']) for t in tasks), 'Wrong task prefix: '+pid)
        coverage[pid] = {r for t in tasks.values() for r in t['requirements']}
        require(coverage[pid] <= expected, 'Unknown completion requirement: '+pid)
        for t in tasks.values():
            require(bool(t['action']) and bool(t['acceptance']) and bool(t['requirements']), 'Incomplete task: '+t['id'])
            require(set(t['depends_on']) <= tasks.keys(), 'Nonlocal or unknown task dependency: '+t['id'])
        visiting, visited = set(), set()
        def visit(tid):
            if tid in visiting:
                errors.append('Cyclic task dependency: '+tid)
                return
            if tid in visited or tid not in tasks:
                return
            visiting.add(tid)
            for dependency in tasks[tid]['depends_on']:
                visit(dependency)
            visiting.remove(tid)
            visited.add(tid)
        for tid in tasks:
            visit(tid)
        for path in part['inputs']:
            require((ROOT/path).exists(), 'Starting input unavailable: '+path)
        for path in part['exclusive_writes'] + part.get('integration_only_writes', []):
            require(not PurePosixPath(path).is_absolute() and '..' not in PurePosixPath(path).parts and ':' not in path, 'Unsafe write path: '+path)
            writers.append((pid, path))
        if check_docs:
            path = ROOT/part['document']
            require(path.is_file(), 'Plan missing: '+str(path))
            if path.is_file():
                text = path.read_text(encoding='utf-8-sig')
                for label, lines in blocks(spec, part).items():
                    require(text.count(f'<!-- {label}:START -->') == 1 and block_text(label, lines) in text,
                            'Generated plan section stale/missing: '+part['document']+':'+label)
                for marker in ['baseline', 'documentation.lock', 'H08/H09', 'testes', 'independência']:
                    require(marker.casefold() in text.casefold(), 'Operational guard missing: '+part['document']+':'+marker)
    require(set().union(*coverage.values()) == expected, 'Uncovered completion requirements')
    shared = {r for r in expected if sum(r in v for v in coverage.values()) > 1}
    require(shared == set(spec['shared_requirement_slices']), 'Shared requirement slices must match overlap exactly')
    for r, slices in spec['shared_requirement_slices'].items():
        require(set(slices) == {'analysis', 'production'} and all(slices.values()), 'Incomplete ownership slices: '+r)
    for i, (owner, path) in enumerate(writers):
        for other, other_path in writers[i+1:]:
            if owner != other:
                require(not overlaps(path, other_path), 'Conflicting write ownership: '+path+' / '+other_path)
        for script in spec['baseline_readonly_scripts']:
            require(not overlaps(path, script), 'Read-only script assigned for writing: '+script)
        for original in read_json('data/catalog/original_files_manifest.json')['files']:
            if original['content_policy'] == 'preserve_bytes':
                require(not overlaps(path, original['current_path']), 'Protected original assigned for writing: '+path)
    require('documentation.lock' in spec['shared_control_protocol'], 'Shared writes lack serialization protocol')
    require({'ESTADO_DO_PROJETO.md', 'EXECUTION_CONTEXT.md'} <= set(spec['shared_control_writes']), 'Both continuity documents must be maintained')
    require(set(spec['deliverable_ownership']) == {g['id'] for g in contract['deliverable_groups']}, 'Artifact families uncovered')
    for group, ownership in spec['deliverable_ownership'].items():
        require(bool(ownership.get('producer')) and bool(ownership.get('publisher')), 'No artifact producer/publisher: '+group)
    require(spec['deliverable_ownership']['G05']['publisher'] == 'group_for_submission', 'Agent must not submit video')
    require(set(spec['human_policy']) == {r['request_id'] for r in read_csv('data/catalog/manual_export_requests.csv')}, 'Human conditions uncovered')
    require(set(spec['human_performance_only']) == {'H08', 'H09', 'H10', 'H11', 'H13'}, 'Human performance/judgment must be real')
    b = spec['bundle_contract']
    require(b['version'] == '1.0' and b['publisher'] == 'analysis' and b['consumer'] == 'production', 'Invalid producer/consumer contract')
    require(len(b['minimum_files']) == len(set(b['minimum_files'])), 'Duplicate interface files')
    require({'model_inputs.json', 'relatorio_cobertura.md', 'tables/claims.csv', 'tables/obligation_schedule.csv',
             'workbooks/base_dados_coletados.xlsx', 'workbooks/base_modelo_auditavel.xlsx', 'results/narrative.json',
             'results/recommendation.json', 'qa/analysis_validation.json'} <= set(b['minimum_files']), 'Incomplete handoff payload')
    require(set(b['states']) == {'analysis_incomplete', 'analysis_proposed', 'group_adopted'}, 'Invalid analytical states')
    require('baseline_unreconciled' in b['baseline_rule'] and 'baseline_unreconciled' not in b['states'], 'Baseline must remain separate from reviewed analysis')
    require({'equity_residual_before_floor', 'equity_floor_applied', 'target_validity', 'value_refs', 'dimensions'} <= set(b['valuation_case_required']), 'Missing per-case validity guards')
    require({'source_refs', 'value_state', 'unit', 'scale', 'scope', 'calculation_ref'} <= set(b['value_required']), 'Value provenance incomplete')
    require(len(set(b['narrative_slots'])) == 10 and 'medium_term' in b['narrative_slots'], 'Narrative coverage incomplete')
    require({'entities.csv', 'instruments.csv', 'sources.csv', 'definitions.csv', 'assumptions.csv'} <= set(b['table_core_headers']), 'Missing identity/evidence table schemas')
    for key in ['serialization', 'manifest_rule', 'result_envelope', 'presentation_views', 'narrative_rule', 'evidence_rule', 'case_rule', 'publish_rule', 'progress_rule']:
        require(bool(b.get(key)), 'Missing contract rule: '+key)
    return errors


def validate():
    spec = read_json(SPEC)
    errors = validate_spec(spec)
    files = [SPEC, 'scripts/validate_two_part_plans.py', 'data/catalog/completion_requirements.json',
             'data/catalog/html_slide_plan.json', 'data/catalog/manual_export_requests.csv',
             'data/catalog/original_files_manifest.json'] + [p['document'] for p in spec['parts']]
    result = dict(checked_at=now(), status='passed' if not errors else 'failed', parts=len(spec['parts']),
                  tasks=sum(len(p['tasks']) for p in spec['parts']), requirements_covered=len({r for p in spec['parts'] for t in p['tasks'] for r in t['requirements']}),
                  artifact_groups=len(spec['deliverable_ownership']), human_conditions=len(spec['human_policy']),
                  cross_part_start_dependencies=sum(len(p['required_other_part_outputs_to_start']) for p in spec['parts']),
                  cross_part_autonomous_delivery_dependencies=sum(len(p['required_other_part_outputs_for_autonomous_delivery']) for p in spec['parts']),
                  source_snapshot={p: sha256(ROOT/p) for p in files if (ROOT/p).is_file()}, errors=errors,
                  scope='Known requirements, internal task DAGs, independent start/autonomous delivery, write ownership, shared slices, producer/consumer interface and human boundaries. No financial execution, HTML implementation or proof that undisclosed rules cannot add requirements.')
    write_json(REPORT, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sync', action='store_true', help='Render plan tables from the execution specification before checking')
    args = parser.parse_args()
    if args.sync:
        render()
    result = validate()
    print(json.dumps({k: result[k] for k in ['status', 'parts', 'tasks', 'requirements_covered', 'artifact_groups', 'human_conditions', 'errors']}, ensure_ascii=False))
    return bool(result['errors'])


if __name__ == '__main__':
    raise SystemExit(main())
