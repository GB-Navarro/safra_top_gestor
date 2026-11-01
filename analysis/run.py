"""CLI da Parte 1: fotografia → conciliação → valuation → pacote 1.0 publicado.

Exemplos (PowerShell, a partir da raiz do repositório):
  .venv/Scripts/python.exe -m analysis.run --baseline new
  .venv/Scripts/python.exe -m analysis.run --baseline data/interim/analysis/baseline/<snapshot_id>
  .venv/Scripts/python.exe -m analysis.run --check outputs/draft/analysis_bundle/<bundle_id>
Não altera originais, caches compartilhados nem documentos globais; não envia nada a terceiros.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .common import REPO, read_json, write_json, now_iso


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m analysis.run", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baseline", help="'new', 'derive:<fotografia-mãe>' (acrescenta só data/raw/analysis) ou caminho de data/interim/analysis/baseline/<snapshot_id>")
    ap.add_argument("--config", default="config/collection.json", help="Recorte (somente config/collection.json nesta versão)")
    ap.add_argument("--output", default="outputs/draft/analysis_bundle", help="Raiz de publicação dos pacotes 1.0")
    ap.add_argument("--skip-tests", action="store_true", help="Não executar tests/analysis durante o QA (registrado como skipped)")
    ap.add_argument("--check", metavar="BUNDLE", help="Somente validar um pacote publicado contra o contrato 1.0")
    a = ap.parse_args(argv)
    from . import contract
    if a.check:
        rep = contract.validate(REPO / a.check)
        print(f"Contrato 1.0: {rep['status']} — {rep.get('counts')}")
        for e in rep["errors"][:30]:
            print("  ERRO", e)
        return 0 if rep["status"] == "passed" else 1
    if not a.baseline:
        ap.error("--baseline é obrigatório (use 'new' ou o caminho de uma fotografia)")
    if (REPO / a.config).resolve() != (REPO / "config/collection.json").resolve():
        ap.error("Esta versão usa somente config/collection.json como recorte.")
    cfg = read_json(REPO / a.config)
    if cfg["scope"]["market_asof"] != "2026-10-30" or cfg["scope"]["valuation_date"] != "2026-10-30":
        ap.error("Recorte congelado em 30/10/2026; nova fotografia exige versão e revisão explícitas.")
    from .snapshot import create_snapshot, derive_snapshot
    if a.baseline.startswith("derive:"):
        parent = REPO / a.baseline.split(":", 1)[1]
        if not (parent / "snapshot.json").is_file():
            ap.error(f"Fotografia-mãe inválida: {parent}")
        snap = derive_snapshot(parent)
    elif a.baseline == "new":
        if (REPO / "data/processed/CANONICAL_SOURCE.json").is_file():
            ap.error("data/processed contém saídas do contrato 1.0 (CANONICAL_SOURCE.json); use --baseline derive:<fotografia> "
                     "para preservar os insumos de 31/10 e acrescentar só a coleta nova.")
        snap = create_snapshot()
    else:
        snap = REPO / a.baseline
    if not (snap / "snapshot.json").is_file():
        ap.error(f"Fotografia inválida: {snap}")
    from . import bundle, progress
    print(f"Fotografia: {snap.relative_to(REPO).as_posix()}", flush=True)
    res = bundle.build(snap, bundle_root=REPO / a.output, run_tests=not a.skip_tests)
    comp = progress.complements()
    prog = progress.write_progress(res, snap, comp)
    q = res["qa"]
    report = {"run_at": now_iso(), "command": " ".join(["python -m analysis.run"] + (argv or sys.argv[1:])), "snapshot": snap.name,
              "bundle_id": res["bundle_id"], "state": res["state"], "manifest_sha256": res["manifest_sha256"],
              "qa_status": q["status"], "checks": {k: v.get("status") for k, v in q["checks"].items() if isinstance(v, dict)},
              "contract": res["contract"]["status"], "complements": comp, "decision": {k: res["decision"][k] for k in ("status", "entity_id", "instrument_id")},
              "next_action": prog["next_action"],
              "limitations": ["Premissas econômicas não certificadas por testes", "H07/H08/H09 ausentes", "Execuções anteriores (13 testes/141/102) não são desta execução"]}
    write_json(REPO / "outputs/qa/analysis" / f"run_report_{res['bundle_id']}.json", report)
    print(f"Pacote {res['bundle_id']} publicado ({res['state']}); QA {q['status']}; contrato {res['contract']['status']}.")
    for k, v in report["checks"].items():
        print(f"  {k}: {v}")
    print(f"Decisão proposta: {report['decision']}")
    return 0 if q["status"] == "passed" and res["contract"]["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
