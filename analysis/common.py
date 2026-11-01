"""I/O estrito, hashes, raízes explícitas e publicação atômica da Parte 1.

Não usa scripts/common.ROOT: toda função recebe caminhos explícitos.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SAO_PAULO = timezone(timedelta(hours=-3))

# Raízes de escrita exclusivas da Parte 1 (two_part_execution.json).
EXCLUSIVE_WRITES = (
    "analysis/", "tests/analysis/", "data/raw/analysis/", "data/interim/analysis/",
    "data/processed/analysis/", "outputs/draft/analysis_bundle/", "outputs/qa/analysis/",
    "data/catalog/parallel_progress/analysis.json",
)


def now_iso() -> str:
    return datetime.now(SAO_PAULO).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def assert_writable(path: Path, repo: Path = REPO) -> Path:
    """Recusa escrita fora das raízes exclusivas (ou de diretórios temporários de teste)."""
    path = Path(path).resolve()
    try:
        rel = path.relative_to(repo.resolve()).as_posix()
    except ValueError:
        return path  # fora do repositório: sandbox de teste/temp explícito
    if not any(rel == root.rstrip("/") or rel.startswith(root) for root in EXCLUSIVE_WRITES):
        raise PermissionError(f"Escrita fora das raízes da Parte 1: {rel}")
    return path


def _clean(obj):
    """JSON estrito: rejeita NaN/Infinity em vez de serializá-los."""
    if isinstance(obj, float):
        if not math.isfinite(obj):
            raise ValueError("Valor não finito no JSON estrito")
        return obj
    if isinstance(obj, dict):
        return {str(k): _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(v) for v in obj]
    return obj


def dumps(obj) -> str:
    return json.dumps(_clean(obj), ensure_ascii=False, indent=2, allow_nan=False, sort_keys=False) + "\n"


def write_json(path: Path, obj, repo: Path = REPO) -> Path:
    path = assert_writable(path, repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(obj), encoding="utf-8")
    return path


def read_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f, parse_constant=lambda c: (_ for _ in ()).throw(ValueError(f"Constante JSON inválida: {c}")))


def cell(value) -> str:
    """Serialização CSV: listas/objetos como JSON, None como vazio, número com ponto."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Valor não finito no CSV")
        return repr(value)
    if isinstance(value, (list, dict, tuple)):
        return json.dumps(_clean(value), ensure_ascii=False, separators=(",", ":"))
    return str(value)


def write_csv(path: Path, rows: list[dict], header: list[str], repo: Path = REPO) -> Path:
    path = assert_writable(path, repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=header, extrasaction="raise", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for row in rows:
        writer.writerow({k: cell(row.get(k)) for k in header})
    path.write_text(buffer.getvalue(), encoding="utf-8")
    return path


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def copy_into(src: Path, dst: Path, repo: Path = REPO) -> Path:
    dst = assert_writable(dst, repo)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def publish_directory(temp_dir: Path, final_dir: Path, repo: Path = REPO) -> Path:
    """Renomeia um diretório completo e validado para seu nome definitivo; nunca sobrescreve."""
    assert_writable(final_dir, repo)
    if final_dir.exists():
        raise FileExistsError(f"Versão já publicada não pode ser sobrescrita: {final_dir}")
    os.replace(temp_dir, final_dir)
    return final_dir


def atomic_write_json(path: Path, obj, repo: Path = REPO) -> Path:
    """Ponteiro de versão: escreve em arquivo temporário e substitui atomicamente."""
    path = assert_writable(path, repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(dumps(obj), encoding="utf-8")
    os.replace(tmp, path)
    return path


def rel(path: Path, base: Path) -> str:
    return Path(path).resolve().relative_to(Path(base).resolve()).as_posix()
