"""Shared IO, immutable acquisition and provenance utilities."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def write_json(path, data):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def read_csv(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows, fields=None):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def fetch(job, offline=False):
    """Cache by request key, immutable payload by content hash; never fetch B3."""
    key = job["key"]
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", key):
        raise ValueError("Unsafe acquisition key")
    url = job["url"]
    if "b3.com.br" in url.lower() or "bvmf" in url.lower():
        raise ValueError("B3 acquisition is manual only")
    meta_path = ROOT / "data/interim/acquisitions" / f"{key}.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        local = ROOT / meta.get("local_path", "missing")
        if meta.get("status") == "downloaded" and meta.get("url") == url and local.is_file() and sha256(local) == meta["sha256"]:
            return meta
    if offline:
        raise FileNotFoundError(f"No verified cached source: {key}")
    result = {**job, "retrieved_at": now(), "status": "failed"}
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=(15, 90), headers={"User-Agent": "asset.dev research/1.0"})
            result.update(http_status=response.status_code, final_url=response.url, content_type=response.headers.get("Content-Type", ""))
            if response.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(1 + attempt)
                continue
            response.raise_for_status()
            payload = response.content
            ext = job.get("extension", "bin")
            if ext == "pdf" and not payload.startswith(b"%PDF"):
                raise ValueError("Response is not PDF")
            if ext == "zip" and not payload.startswith(b"PK"):
                raise ValueError("Response is not ZIP")
            if ext == "json":
                response.json()
            if not payload:
                raise ValueError("Empty response")
            digest = hashlib.sha256(payload).hexdigest()
            folder = ROOT / job["directory"]
            folder.mkdir(parents=True, exist_ok=True)
            target = folder / f"{key}__{digest[:12]}.{ext}"
            if not target.exists():
                target.write_bytes(payload)
            result.update(status="downloaded", sha256=digest, bytes=len(payload), local_path=target.relative_to(ROOT).as_posix(), source_id=f"SRC_{key}_{digest[:8]}")
            break
        except (requests.RequestException, ValueError) as exc:
            result["error"] = f"{type(exc).__name__}: {str(exc)[:350]}"
            if result.get("http_status") in (400, 401, 403, 404) or attempt == 2:
                break
            time.sleep(1 + attempt)
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def acquisitions():
    folder = ROOT / "data/interim/acquisitions"
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))]


def sync_sources():
    fields = ["source_id", "issuer", "title", "url", "local_path", "published_at", "retrieved_at", "sha256", "access_method", "reference_date", "version", "access_status"]
    rows = []
    for item in acquisitions():
        if item["status"] != "downloaded":
            continue
        rows.append(dict(source_id=item["source_id"], issuer=item.get("issuer", ""), title=item.get("title", item["key"]), url=item.get("url", ""), local_path=item["local_path"], published_at=item.get("published_at", ""), retrieved_at=item["retrieved_at"], sha256=item["sha256"], access_method=item.get("access_method", "http"), reference_date=item.get("reference_date", ""), version=item.get("version", ""), access_status="downloaded_publication_check_separate"))
    write_csv("data/processed/sources.csv", rows, fields)
    return rows
