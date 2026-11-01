"""Fixtures isoladas da Parte 2 (kind=fixture), sempre em diretório temporário.

Derivam do pacote publicado para ter forma realista, mas recebem kind=fixture e hashes refeitos; o
carregador padrão as recusa. Nada aqui escreve no repositório nem simula registro humano real.
"""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

from production import consumer
from production.common import sha256_file


def make(tmp: Path, name: str, mutate=None, kind: str = "fixture", **manifest) -> Path:
    dst = Path(tmp) / name
    shutil.copytree(consumer.resolve("latest"), dst)
    if mutate:
        mutate(dst)
    rehash(dst, kind=kind, **manifest)
    return dst


def rehash(path: Path, kind: str = "fixture", **manifest) -> None:
    man = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    man.update(kind=kind, bundle_id=f"fixture_{path.name}", **manifest)
    man["files"] = [{"path": p.relative_to(path).as_posix(), "bytes": p.stat().st_size, "sha256": sha256_file(p)}
                    for p in sorted(path.rglob("*")) if p.is_file() and p.name != "manifest.json"]
    (path / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")


def edit_csv(path: Path, rel: str, fn) -> None:
    """fn(rows) devolve as linhas novas; preserva o cabeçalho."""
    with open(path / rel, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        header, rows = reader.fieldnames, list(reader)
    rows = fn(rows)
    with open(path / rel, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def edit_json(path: Path, rel: str, fn) -> None:
    p = path / rel
    obj = json.loads(p.read_text(encoding="utf-8"))
    obj = fn(obj) or obj
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def set_value(vid: str, value: str, **fields):
    def fn(rows):
        hit = [r for r in rows if r["value_id"] == vid]
        assert hit, vid
        for r in hit:
            r["value"] = value
            r.update(fields)
        return rows
    return lambda d: edit_csv(d, "tables/observations.csv", fn)
