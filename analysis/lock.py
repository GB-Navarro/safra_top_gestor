"""Exclusão de escrita para atualizações globais (data/interim/coordination/documentation.lock).

Protocolo: criação atômica (O_CREAT|O_EXCL) com dono, início e operação; liberação em
finally apenas pelo próprio dono. Trava ativa de outro processo nunca é apagada.
"""
from __future__ import annotations

import json
import os
import socket
import time
from contextlib import contextmanager
from pathlib import Path

from .common import REPO, now_iso

LOCK_PATH = REPO / "data/interim/coordination/documentation.lock"


class LockBusy(RuntimeError):
    pass


def read_lock(path: Path = LOCK_PATH) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, OSError):
        return {"owner": "unknown", "unreadable": True}


def acquire(owner: str, operation: str, path: Path = LOCK_PATH, wait_seconds: float = 0.0, poll: float = 0.5) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    token = {"owner": owner, "operation": operation, "started_at": now_iso(), "pid": os.getpid(), "host": socket.gethostname()}
    deadline = time.monotonic() + wait_seconds
    while True:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise LockBusy(f"Trava ocupada: {read_lock(path)}")
            time.sleep(poll)
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(token, f, ensure_ascii=False)
        return token


def release(token: dict, path: Path = LOCK_PATH) -> None:
    current = read_lock(path)
    if current is None:
        return
    if current.get("owner") != token["owner"] or current.get("pid") != token["pid"] or current.get("started_at") != token["started_at"]:
        raise LockBusy(f"Trava pertence a outro processo; não removida: {current}")
    path.unlink()


@contextmanager
def documentation_lock(owner: str, operation: str, path: Path = LOCK_PATH, wait_seconds: float = 0.0):
    token = acquire(owner, operation, path, wait_seconds)
    try:
        yield token
    finally:
        release(token, path)
