"""Raízes explícitas, I/O estrito, hashes e trava documental da Parte 2 (independente de analysis/)."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import shutil
import socket
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SAO_PAULO = timezone(timedelta(hours=-3))
LOCK_PATH = REPO / "data/interim/coordination/documentation.lock"

# Escrita exclusiva de trabalho (two_part_execution.json, parte production).
EXCLUSIVE = ("production/", "presentation_web/", "tests/production/", "data/interim/production/", "outputs/draft/production/",
             "outputs/qa/production/", "data/catalog/parallel_progress/production.json", "config/video_segments.json",
             "config/production_profile.json")
# Destinos canônicos: só o integrador escreve, sob trava e com manifesto.
PUBLISH = ("data/processed/", "outputs/final/", "outputs/draft/", "outputs/qa/", "data/interim/financial_reconciliation.csv",
           "data/interim/obligation_schedule.csv")


def now_iso() -> str:
    return datetime.now(SAO_PAULO).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _rel(path: Path) -> str | None:
    try:
        return Path(path).resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return None


def writable(path: Path, publishing: bool = False) -> Path:
    rel = _rel(path)
    if rel is None:
        return Path(path)  # sandbox temporária de teste
    roots = EXCLUSIVE + (PUBLISH if publishing else ())
    if not any(rel == r.rstrip("/") or rel.startswith(r) for r in roots):
        raise PermissionError(f"Escrita fora das raízes da Parte 2{' (publicação)' if publishing else ''}: {rel}")
    if rel.startswith("outputs/draft/analysis_bundle/"):
        raise PermissionError("Pacotes analíticos publicados são imutáveis")
    return Path(path)


def _clean(obj):
    if isinstance(obj, float) and not math.isfinite(obj):
        raise ValueError("Valor não finito no JSON estrito")
    if isinstance(obj, dict):
        return {str(k): _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(v) for v in obj]
    return obj


def dumps(obj, indent=2) -> str:
    return json.dumps(_clean(obj), ensure_ascii=False, indent=indent, allow_nan=False) + "\n"


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      parse_constant=lambda c: (_ for _ in ()).throw(ValueError(f"Constante JSON inválida: {c}")))


def write_text(path: Path, text: str, publishing: bool = False) -> Path:
    path = writable(path, publishing)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def write_json(path: Path, obj, publishing: bool = False) -> Path:
    return write_text(path, dumps(obj), publishing)


def write_csv(path: Path, rows: list[dict], header: list[str], publishing: bool = False) -> Path:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else ("" if v is None else v)) for k, v in r.items()})
    return write_text(path, buf.getvalue(), publishing)


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def copy(src: Path, dst: Path, publishing: bool = False) -> Path:
    dst = writable(dst, publishing)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


# ---------------- trava documental (mesmo protocolo da Parte 1) ---------------------------
class LockBusy(RuntimeError):
    pass


def _read_lock(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError):
        return {"owner": "unknown"}


def acquire(owner: str, operation: str, path: Path = LOCK_PATH, wait_seconds: float = 0.0) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    token = {"owner": owner, "operation": operation, "started_at": now_iso(), "pid": os.getpid(), "host": socket.gethostname()}
    deadline = time.monotonic() + wait_seconds
    while True:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise LockBusy(f"Trava ocupada: {_read_lock(path)}")
            time.sleep(0.5)
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(token, f, ensure_ascii=False)
        return token


def release(token: dict, path: Path = LOCK_PATH) -> None:
    cur = _read_lock(path)
    if cur is None:
        return
    if (cur.get("owner"), cur.get("pid"), cur.get("started_at")) != (token["owner"], token["pid"], token["started_at"]):
        raise LockBusy(f"Trava pertence a outro processo; não removida: {cur}")
    path.unlink()


@contextmanager
def documentation_lock(operation: str, path: Path = LOCK_PATH, wait_seconds: float = 0.0):
    token = acquire("production", operation, path, wait_seconds)
    try:
        yield token
    finally:
        release(token, path)
