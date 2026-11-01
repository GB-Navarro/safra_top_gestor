"""AN11 — complementos opcionais; AN12 — progresso próprio, entrega e relatório da execução."""
from __future__ import annotations

from pathlib import Path

from .common import REPO, now_iso, sha256_file, write_json

PROGRESS = REPO / "data/catalog/parallel_progress/analysis.json"


def complements() -> dict:
    """C29: verifica se exportações Bloomberg/consenso chegaram; ausência não bloqueia o núcleo público."""
    folder = REPO / "data/raw/bloomberg"
    received = sorted(p.name for p in folder.glob("*") if p.is_file() and p.name != ".gitkeep") if folder.is_dir() else []
    return {"bloomberg_exports": received, "status": "received_needs_import" if received else "not_received_public_substitutes_used",
            "omitted": ["consenso/alvos de analistas", "ESG Bloomberg", "índices e financiamento verde", "beta de juros (N22)",
                        "causalidade pós-privatização", "VPL por ligação (N23)", "EV/BRR (N04)"],
            "rule": "Nenhum número omitido é prometido; complemento recebido exige repetir AN03/AN06+ afetados."}


def write_progress(result: dict, snapshot_dir: Path, comp: dict) -> dict:
    bid = result["bundle_id"]
    final = result["path"]
    evidence = {p: sha256_file(final / p) for p in ("manifest.json", "qa/analysis_validation.json", "results/recommendation.json",
                                                    "tables/financial_reconciliation.csv")}
    tasks = [
        ("AN01", "done", "Fotografia com hash, originais conferidos"),
        ("AN02", "done", "64 células + C08 com disposição"),
        ("AN03", "done_with_limitations", "Preços públicos sem H01; eventos jul–out pesquisados em fontes públicas (sem mudança de ações)"),
        ("AN04", "done_with_limitations", "EMAE sem valoração separada"),
        ("AN05", "done_with_limitations", "Copasa: indicador de acesso ausente; prazo por média ponderada"),
        ("AN06", "done_proposed", "Premissas para H08; WACC regulatório Sabesp do contrato; capex Copasa premissa do analista"),
        ("AN07", "done_with_limitations", "Calendário mensal do precatório estimado"),
        ("AN08", "done", "Ramo revisado + legado reproduzido"),
        ("AN09", "done_proposed", "Decisão proposta por regra; claims e 10 slots"),
        ("AN10", "done" if result["qa"]["status"] == "passed" and result["contract"]["status"] == "passed" else "failed", "Pacote 1.0 publicado"),
        ("AN11", "done", comp["status"]),
        ("AN12", "awaiting_human", "Checklist H08/H09 entregue; decisões reais não registradas"),
    ]
    data = {"part_id": "analysis", "updated_at": now_iso(), "bundle_id": bid, "bundle_path": final.relative_to(REPO).as_posix(),
            "manifest_sha256": result["manifest_sha256"], "state": result["state"], "snapshot_id": snapshot_dir.name,
            "tasks": [{"task_id": t, "status": s, "note": n} for t, s, n in tasks],
            "requirement_slices": {d["requirement_id"]: d["status"] for d in _dispositions(final)},
            "evidence_paths": {f"{final.relative_to(REPO).as_posix()}/{k}": v for k, v in evidence.items()},
            "unresolved": ["BRR líquida oficial de Sabesp e Copasa (Sanepar só como verificação)", "plano de capex Copasa vigente (projeções descontinuadas)",
                           "prazos Copasa por contrato (usada a média ponderada)", "EMAE sem valoração separada", "confirmação de preços e recompras (H01)"],
            "human_needed": ["H08 (cinco julgamentos)", "H09 (adoção da recomendação)", "H07 (instruções privadas)", "H01 (opcional)"],
            "next_action": ("Grupo: revisar checklist em LEIA_PRIMEIRO.md e registrar H08/H09 em data/interim/decisoes_equipe.md; "
                            "Parte 2: consumir outputs/draft/analysis_bundle/latest.json. Reexecução: "
                            ".venv/Scripts/python.exe -m analysis.run --baseline " + snapshot_dir.relative_to(REPO).as_posix())}
    write_json(PROGRESS, data)
    return data


def _dispositions(final: Path) -> list[dict]:
    import json
    return json.loads((final / "manifest.json").read_text(encoding="utf-8"))["requirement_dispositions"]
