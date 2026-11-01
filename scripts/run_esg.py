"""Real, sequential project stages. No automatic final sign-off or submission.

Since the contract 1.0 publication (data/processed/CANONICAL_SOURCE.json), the default path delegates to the
two-part components by subprocess (no finance is recalculated here):
  --stage analysis    -> python -m analysis.run --baseline new      (new analysis bundle, Part 1)
  --stage production  -> python -m production.run --input-bundle latest   (pieces + QA, Part 2 draft build)
  --stage publish     -> python -m production.run --publish <build>       (integrator, requires visual review)
  --stage release     -> python -m production.run --release-report
  --mode final        -> python -m production.run --promote-final <stage> (gates decide; refuses with reasons)
Legacy stages that rewrite canonical outputs (model/charts/slides/render/validate/package) need --legacy.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import subprocess

from common import ROOT, read_json

LEGACY_CANONICAL = ['model','charts','slides','render','validate','package']


def delegate(*args):
    print('Executing',' '.join(args),flush=True)
    return subprocess.run([sys.executable,*args],cwd=ROOT).returncode


def main():
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--stage',choices=['collect','model','charts','slides','render','validate','package','docs','analysis','production','publish','release','all'],default='all')
    p.add_argument('--config',default='config/collection.json')
    p.add_argument('--mode',choices=['draft','final'],default='draft')
    p.add_argument('--final-stage',choices=['group_material','video_submission'],default='group_material',help='Gate evaluated by --mode final')
    p.add_argument('--build',help='outputs/draft/production/<build_id> for --stage publish')
    p.add_argument('--profile',choices=['all','pptx9','html10'],default='all')
    p.add_argument('--legacy',action='store_true',help='Run the legacy pipeline even if it rewrites the canonical contract 1.0 outputs')
    p.add_argument('--offline',action='store_true')
    p.add_argument('--refresh',action='store_true',help='Reparse already extracted CVM, models and SINISA files')
    a=p.parse_args()
    if (ROOT/a.config).resolve()!=(ROOT/'config/collection.json').resolve():
        p.error('This implementation uses config/collection.json as the sole scope; custom config not silently ignored.')
    cfg=read_json(a.config)
    if cfg['scope']['market_asof']!='2026-10-30' or cfg['scope']['valuation_date']!='2026-10-30':
        p.error('This snapshot is frozen at 30/10/2026. A date migration requires explicit review of collectors/models.')
    if a.mode=='final':
        # Release gates replace the unconditional refusal: promotion only with real evidence; never submits.
        return delegate('-m','production.run','--promote-final',a.final_stage)
    canonical=(ROOT/'data/processed/CANONICAL_SOURCE.json').is_file()
    if canonical and not a.legacy and a.stage in LEGACY_CANONICAL:
        src=read_json('data/processed/CANONICAL_SOURCE.json')
        p.error(f"Canonical source is bundle {src['bundle_id']} (contract 1.0). Stage '{a.stage}' would rewrite it with the legacy schema. "
                "Use --stage analysis/production/publish/release, or add --legacy deliberately.")
    if a.stage=='analysis':return delegate('-m','analysis.run','--baseline','new')
    if a.stage=='production' or (a.stage=='all' and canonical and not a.legacy):
        code=delegate('-m','production.run','--input-bundle','latest','--profile',a.profile)
        from sync_project_docs import sync
        sync()
        return code
    if a.stage=='publish':
        if not a.build:p.error('--stage publish requires --build outputs/draft/production/<build_id>')
        return delegate('-m','production.run','--publish',a.build)
    if a.stage=='release':return delegate('-m','production.run','--release-report')
    if a.stage=='all':
        # Legacy sequence. Release each stage's scientific/plotting libraries before the next.
        # In-process imports retained enough memory to starve the test child.
        for stage in ['collect','model','slides','render','validate','package']:
            command=[sys.executable,str(Path(__file__).resolve()),'--stage',stage,'--config',a.config,'--mode',a.mode]
            if a.offline:command.append('--offline')
            if a.refresh:command.append('--refresh')
            if a.legacy:command.append('--legacy')
            print('Executing stage',stage,flush=True)
            result=subprocess.run(command,cwd=ROOT)
            if result.returncode:
                from sync_project_docs import sync
                sync()
                return result.returncode
        return 0
    if a.stage=='docs':
        from sync_project_docs import sync,check
        sync()
        report=check()
        print('Documentation',report['status'])
        return bool(report['errors'])
    def chosen(*stages):return a.stage in stages or a.stage=='all'
    if chosen('collect'):
        from collect_data import collect
        from extract_data import extract_cvm,extract_models
        from sinisa_data import extract
        if not a.offline:collect()
        else:print('Offline: using locally cached sources; absent downloads are not silently synthesized.',flush=True)
        if a.refresh or not (ROOT/'data/processed/cvm_accounts.csv').exists():extract_cvm()
        if a.refresh or not (ROOT/'data/interim/original_models.json').exists():extract_models()
        if a.refresh or not (ROOT/'data/processed/sinisa_municipal.csv').exists():extract()
    if chosen('model'):
        from prepare_analysis import prepare
        from normalize_data import normalize
        from model import build
        from analysis_outputs import build_outputs
        from financial_audit import audit
        prepare();normalize();build();build_outputs();audit()
    if chosen('charts','slides'):
        from presentation import build
        build()
    if chosen('render'):
        from render_slides import render
        render()
    if chosen('validate'):
        from validate import validate
        report=validate()
        if report['errors']:
            from sync_project_docs import sync
            sync()
            return 1
    if chosen('package'):
        from execution_status import update
        from package_outputs import package
        update();package()
        from validate import validate_packages
        validate_packages()
    from sync_project_docs import sync
    sync()
    return 0


if __name__=='__main__':sys.exit(main())
