"""EN06 — roteiro, script por perfil, teleprompters, perguntas e guia; contagem de palavras e lint de números."""
from __future__ import annotations

import re
from pathlib import Path

from . import content as K
from .common import write_json, write_text
from .consumer import TOKEN, Bundle

WPM = 140
PEOPLE = ["Rodrigo", "Lorenzo", "Navarro", "Michel"]
PROFILE_BLOCKS = {"html10": ["B1", "B2", "B3", "B4", "B5", "B6", "B7.a", "B7.b", "B8", "B9"],
                  "pptx9": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9"]}
# Literais permitidos fora de tokens: datas, anos, rótulos estruturais e regras explícitas da proposta.
ALLOWED = re.compile(r"(\b(19|20)\d{2}\b|\b\d{1,2}/\d{1,2}(/\d{2,4})?\b|\b\d{1,2} de [a-zç]+\b|\b99 municípios\b|\b1 ON\b|\b4 PN\b|"
                     r"\bR\$ 1\b|\bR\$ 1,00\b|\b[A-Z]{4}\d{1,2}\b|\b1 ação\b|\b12 meses\b|− 1\b|> 10%|\b10%|\b2T26\b|\b4T25\b|\b3ª\b|\b64 células\b|\bB7\.[ab]\b|\b75%|\b100%|\bP0?\d+\b|\bH0\d\b|\bC\d\d\b)")


def speech(b: Bundle) -> dict:
    out = {k: b.render(v) for k, v in K.SPEECH.items()}
    out["B7"] = out["B7.a"] + " " + out["B7.b"]
    return out


def lint_literals() -> list[dict]:
    """Números digitados fora de tokens nas fontes editoriais (exceto datas/regras permitidas)."""
    issues = []
    def scan(where, text):
        clean = ALLOWED.sub("", TOKEN.sub("", text))
        for m in re.finditer(r"\d+(?:[.,]\d+)?\s?%?", clean):
            issues.append({"where": where, "literal": m.group(0).strip(), "context": clean[max(0, m.start() - 30):m.end() + 20]})
    for k, v in K.SPEECH.items():
        scan(f"SPEECH.{k}", v)
    def walk(where, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                walk(where, v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                walk(where, v)
        elif isinstance(obj, str) and " " in obj:  # IDs (value_id/claim) não têm espaço; só texto visível é varrido
            scan(where, obj)
    for pid, scr in K.SCREEN.items():
        walk(f"SCREEN.{pid}", scr)
    for p in K.PAGES:
        scan(f"PAGES.{p['id']}", p["title"] + " " + p["subtitle"])
    for q, a in K.QUESTIONS:
        scan("QUESTIONS", q + " " + a)
    return issues


def _words(t: str) -> int:
    return len(re.findall(r"\b[\wÀ-ÿ$.,%]+\b", t))


def _voice_lines(block: str, text: str):
    if block == "B9":
        return [(m.group(1), m.group(2).strip()) for m in re.finditer(r"(Rodrigo|Lorenzo|Michel|Navarro|Todos):\s*([^:]+?)(?=\s+(?:Rodrigo|Lorenzo|Michel|Navarro|Todos):|$)", text)]
    return [(K.BLOCK_VOICE.get(block, "Rodrigo"), text)]


def build(b: Bundle, model: dict, out: Path) -> dict:
    sp = speech(b)
    seconds = dict(K.BLOCK_SECONDS)
    seconds["B7"] = seconds["B7.a"] + seconds["B7.b"]
    voice = dict(K.BLOCK_VOICE, B7="Rodrigo")
    pages = {p["block"]: p for p in model["pages"]}
    counts = {}
    for profile, blocks in PROFILE_BLOCKS.items():
        lines = [f"# Script de apresentação — perfil {profile}", "",
                 f"Falas exatas para ensaio, geradas do pacote {model['bundle_id']} (proposta; decisão do grupo H09 pendente). "
                 "Tempos são orçamento a 140 palavras/min; só o ensaio mede a duração real. Notas de fonte não são fala.", ""]
        total_w = total_s = 0
        cursor = 0
        for blk in blocks:
            w = _words(sp[blk])
            total_w += w
            total_s += seconds[blk]
            page = pages.get(blk) or pages.get(blk + ".a")
            where = (f"P{page['id'][1:]}" if profile == "html10" else f"S{page['slide9']}") if page else ""
            lines += [f"## {blk} — {voice[blk]} — {cursor // 60}:{cursor % 60:02d}–{(cursor + seconds[blk]) // 60}:{(cursor + seconds[blk]) % 60:02d} · {where}",
                      "", sp[blk], "", f"*{w} palavras; orçamento {seconds[blk]} s (~{round(w / WPM * 60)} s a 140 ppm).*", ""]
            cursor += seconds[blk]
        lines += [f"Total: {total_w} palavras; orçamento {total_s} s ({total_s // 60}:{total_s % 60:02d}); teto público 10:00.", ""]
        name = "script_apresentacao.md" if profile == "pptx9" else "script_apresentacao_html10.md"
        write_text(out / name, "\n".join(lines))
        counts[profile] = {"total_words": total_w, "planned_seconds": total_s, "estimated_seconds_at_140wpm": round(total_w / WPM * 60),
                           "blocks": {blk: _words(sp[blk]) for blk in blocks}}
    for person in PEOPLE:
        lines = [f"# Teleprompter — {person}", "", "Leia só o texto abaixo de cada bloco. Perfil html10 (B7 dividido); no pptx9, B7.a e B7.b são lidos em sequência no slide 7.", ""]
        for blk in PROFILE_BLOCKS["html10"]:
            for who, text in _voice_lines(blk, sp[blk]):
                if who in (person, "Todos"):
                    lines += [f"## {blk}{' (todos)' if who == 'Todos' else ''}", "", text, ""]
        write_text(out / "teleprompter" / f"{person.lower()}.md", "\n".join(lines))
    qa = ["# Perguntas prováveis da banca — respostas curtas", "", f"Geradas do pacote {model['bundle_id']}. Respostas são proposta do agente até o grupo assumir (H09).", ""]
    for k, (q, a) in enumerate(K.QUESTIONS, 1):
        qa += [f"## {k}. {q}", "", b.render(a), ""]
    write_text(out / "perguntas_banca.md", "\n".join(qa))
    write_text(out / "guia_gravacao.md", K.GUIDE)
    nar = ["# Roteiro narrativo", "", "Sequência de argumentos (slots do contrato 1.0) com as afirmações do pacote; cada uma tem fonte e limitação em claims.csv.", ""]
    for slot, ids in b.slots.items():
        nar += [f"## {slot}", ""] + [f"- {b.claim_text(cid)} *({cid})*" for cid in ids] + [""]
    write_text(out / "roteiro_narrativo.md", "\n".join(nar))
    lint = lint_literals()
    write_json(out / "script_word_counts.json", {"bundle_id": model["bundle_id"], "wpm": WPM, "profiles": counts, "literal_numbers_outside_tokens": lint,
                                                  "note": "Contagem estima plausibilidade; não substitui ensaio real (H10)."})
    return {"counts": counts, "lint": lint, "speech": sp}


def segments(profile: str) -> list[dict]:
    """Manifesto de segmentos de gravação por perfil (pptx9: 13; html10: 14)."""
    out = []
    page_of = {"pptx9": {"B1": 1, "B2": 2, "B3": 3, "B4": 4, "B5": 5, "B6": 6, "B7": 7, "B8": 8, "B9": 9},
               "html10": {"B1": 1, "B2": 2, "B3": 3, "B4": 4, "B5": 5, "B6": 6, "B7.a": 7, "B7.b": 8, "B8": 9, "B9": 10}}[profile]
    for blk in PROFILE_BLOCKS[profile]:
        if blk == "B9":
            for who in ["Rodrigo", "Lorenzo", "Michel", "Navarro", "Todos"]:
                out.append({"block": f"B9_{who}", "speaker": who, "slide": page_of["B9"], "path": f"data/raw/gravacao/{'' if profile == 'pptx9' else 'html10/'}B9_{who}.mp4"})
        else:
            tag = blk.replace(".", "")
            out.append({"block": blk, "speaker": K.BLOCK_VOICE.get(blk, "Rodrigo"), "slide": page_of[blk],
                        "path": f"data/raw/gravacao/{'' if profile == 'pptx9' else 'html10/'}{tag}.mp4"})
    return out
