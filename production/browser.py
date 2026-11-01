"""Navegador headless (Edge/Chrome instalados) para autoteste de interação, capturas e PDF do HTML."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from .common import REPO

CANDIDATES = [Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"), Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
              Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")]
PROFILE = REPO / "outputs/qa/production/browser_profile"


def executable() -> Path | None:
    return next((p for p in CANDIDATES if p.is_file()), None)


def _run(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    exe = executable()
    if exe is None:
        raise FileNotFoundError("Nenhum navegador Chromium encontrado")
    PROFILE.mkdir(parents=True, exist_ok=True)
    base = [str(exe), "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check", "--disable-extensions",
            f"--user-data-dir={PROFILE}", "--hide-scrollbars", "--force-device-scale-factor=1", "--disable-features=Translate"]
    return subprocess.run(base + args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def url(path: Path, query: str = "", page: int | None = None) -> str:
    u = Path(path).resolve().as_uri()
    return u + (f"?{query}" if query else "") + (f"#p{page}" if page else "")


def selftest(path: Path, width: int = 1920, height: int = 1080, query: str = "selftest=1") -> dict:
    p = _run([f"--window-size={width},{height}", "--virtual-time-budget=8000", "--dump-dom", url(path, query)])
    m = re.search(r'<pre id="selftest-result"[^>]*>(.*?)</pre>', p.stdout, flags=re.S)
    if not m:
        return {"status": "not_run", "stderr": p.stderr[-1500:], "stdout_tail": p.stdout[-500:]}
    raw = m.group(1).replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    out = json.loads(raw)
    out["viewport"] = f"{width}x{height}"
    return out


def screenshot(path: Path, out: Path, page: int, width: int = 1920, height: int = 1080, query: str = "") -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    p = _run([f"--window-size={width},{height}", "--virtual-time-budget=4000", f"--screenshot={out}", url(path, query, page)])
    if not out.is_file():
        raise RuntimeError(f"Captura falhou: {p.stderr[-800:]}")
    return out


def print_pdf(path: Path, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    p = _run(["--virtual-time-budget=6000", "--no-pdf-header-footer", "--print-to-pdf-no-header", f"--print-to-pdf={out}", url(path)], timeout=180)
    if not out.is_file():
        raise RuntimeError(f"PDF falhou: {p.stderr[-800:]}")
    return out
