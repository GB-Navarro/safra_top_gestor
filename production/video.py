"""EN07 — perfis de segmentos, checagem de clipes reais, montagem e teste sintético do encoder.

Nunca cria vídeo do grupo sem clipes reais; não acelera fala; duração > 10 min bloqueia.
"""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

from .common import REPO, read_json, write_json

LIMIT_SECONDS = 600
CAMERA = (1644, 540, 252, 448)  # mesma área reservada pelo modo gravação do HTML
SLIDE = (1612, 907, 0, 86)  # slide inteiro reduzido a 0,84 à esquerda, como no modo gravação: a câmera não cobre conteúdo


def _ffmpeg(args, check=True):
    import imageio_ffmpeg
    r = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", *map(str, args)], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if check and r.returncode:
        raise RuntimeError("FFmpeg: " + r.stderr[-2000:])
    return r


def probe(path: Path) -> dict:
    log = _ffmpeg(["-i", path], check=False).stderr
    hit = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", log)
    if not hit:
        raise ValueError(f"Duração indeterminada: {path.name}")
    h, m, s = map(float, hit.groups())
    size = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", log)
    return {"seconds": h * 3600 + m * 60 + s, "has_video": "Video:" in log, "has_audio": "Audio:" in log,
            "size": f"{size.group(1)}x{size.group(2)}" if size else None}


def overlay(slide_png: Path, clip: Path, target: Path, seconds: float):
    x, y, w, h = CAMERA
    sw, sh, sx, sy = SLIDE
    filt = (f"[0:v]scale={sw}:{sh},pad=1920:1080:{sx}:{sy}:black,setsar=1[bg];"
            f"[1:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,"
            f"setsar=1[cam];[bg][cam]overlay={x}:{y}:shortest=1[v]")
    _ffmpeg(["-y", "-loop", "1", "-framerate", "30", "-i", slide_png, "-i", clip, "-filter_complex", filt, "-map", "[v]", "-map", "1:a:0", "-t", seconds,
             # 2 threads: menos buffers do x264 (máquina com pouca memória comprometida livre); qualidade fixada pelo CRF
             "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-threads", "2", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
             "-ac", "2", "-movflags", "+faststart", target])


def readiness(profile_path: Path) -> dict:
    cfg = read_json(profile_path)
    rows, total, problems = [], 0.0, []
    for seg in cfg["segments"]:
        p = REPO / seg["path"]
        if not p.is_file():
            rows.append({**seg, "present": False})
            continue
        info = probe(p)
        total += info["seconds"]
        if not (info["has_video"] and info["has_audio"]):
            problems.append(f"{seg['block']}: sem trilha de vídeo ou áudio")
        rows.append({**seg, "present": True, **info})
    missing = [r["path"] for r in rows if not r["present"]]
    status = "awaiting_real_clips" if missing else ("over_limit" if total > LIMIT_SECONDS else ("clip_problems" if problems else "clips_present_unreviewed"))
    return {"profile": cfg.get("profile", "deck12"), "status": status, "segments": len(rows), "present": len(rows) - len(missing), "missing": missing,
            "measured_seconds": round(total, 2), "limit_seconds": LIMIT_SECONDS, "problems": problems, "video_created": False}


def assemble(profile_path: Path, slide_images: dict[int, Path], out_dir: Path) -> dict:
    rep = readiness(profile_path)
    if rep["status"] != "clips_present_unreviewed":
        return rep
    cfg = read_json(profile_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, seg in enumerate(cfg["segments"], 1):
        part = out_dir / f"part_{i:02d}.mp4"
        overlay(slide_images[seg["slide"]], REPO / seg["path"], part, probe(REPO / seg["path"])["seconds"])
        parts.append(part)
    listing = out_dir / "concat.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    target = out_dir / f"video_esg_{cfg.get('profile', 'deck12')}_rascunho.mp4"
    _ffmpeg(["-y", "-f", "concat", "-safe", "0", "-i", listing, "-c", "copy", "-movflags", "+faststart", target])
    measured = probe(target)["seconds"]
    rep.update(video_created=True, path=str(target.relative_to(REPO)) if target.is_relative_to(REPO) else str(target), measured_seconds=round(measured, 2),
               status="draft_video_awaiting_full_human_review" if measured <= LIMIT_SECONDS else "over_limit", submitted=False)
    return rep


def self_test(slide_png: Path) -> dict:
    """Fixture sintética em diretório temporário (cor + tom 0,6 s): testa encoder, overlay e medição. Não é vídeo do grupo."""
    with tempfile.TemporaryDirectory(prefix="prod_video_qa_") as tmp:
        d = Path(tmp)
        clip, out = d / "synthetic_fixture.mp4", d / "out.mp4"
        _ffmpeg(["-y", "-f", "lavfi", "-i", "color=c=teal:s=180x320:r=30", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000", "-t", "0.6",
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", clip])
        overlay(slide_png, clip, out, 0.6)
        info = probe(out)
    ok = .5 <= info["seconds"] <= .8 and info["has_video"] and info["has_audio"] and info["size"] == "1920x1080"
    return {"status": "passed" if ok else "failed", "fixture": "sintética, apagada ao fim", "measured": info, "group_video_created": False}


SEGMENTS = REPO / "config/video_segments.json"


def write_profiles():
    """Manifesto único de gravação (deck12): um clipe por slide; o montador legado lê o mesmo arquivo."""
    from .narrative import PROFILE, segments
    cfg = {"profile": PROFILE, "status": "template_awaiting_genuine_clips",
           "source": "HTML de 12 slides (modo gravação G reserva a área da câmera) ou o PDF/PPTX equivalentes", "segments": segments()}
    write_json(SEGMENTS, cfg)
    return cfg
