"""EN06 — script da apresentação final (12 slides), teleprompters, perguntas e guia; contagem de palavras e lints.

Lints: números digitados fora de tokens; marcas de texto que as cartas não usam (travessão, seta, exclamação,
chavões); e o modelo de alocação citado depois do slide 2 (a análise segue independente dele).
"""
from __future__ import annotations

import re
from pathlib import Path

from . import content as K
from .common import write_json, write_text
from .consumer import TOKEN, Bundle

WPM = 140
PROFILE = "deck12"
PEOPLE = ["Rodrigo", "Lorenzo", "Navarro", "Michel"]
BLOCKS = [p["block"] for p in K.PAGES]
INTRO = {"S01", "S02"}  # únicos slides em que o modelo de alocação pode ser citado
# Literais permitidos fora de tokens: datas, anos, rótulos estruturais e regras explícitas da proposta.
ALLOWED = re.compile(r"(\b(19|20)\d{2}\b|\b\d{1,2}/\d{1,2}(/\d{2,4})?\b|\b(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)/\d{2}\b|"
                     r"\b\d{1,2} de [a-zç]+\b|\b99 municípios\b|\b1 ON\b|\b4 PN\b|\bR\$ 1\b|\bR\$ 1,00\b|\b[A-Z]{4}\d{1,2}\b|\b12 meses\b|"
                     r"> 10%|\b10%|\b2T26\b|\b4T25\b|\b[1-9]ª|\b64 células\b|\bS\d\d\b|\bH\d\d\b|\bC\d\d\b|^\d\d · )")
STYLE = re.compile(r"—|→|←|≠|!|\b(crucial|robust[oa]s?|alavancar|jornada|mergulh\w+|vale ressaltar|é importante (destacar|notar)|"
                   r"nesse sentido|em suma|em resumo|além disso|desafiador\w*|potencializ\w+|sinergia\w*|disruptiv\w+)\b", re.I)
MODEL = re.compile(r"\b(modelo de alocação|Black-Litterman|o modelo|do modelo|pelo modelo)\b", re.I)


def speech(b: Bundle) -> dict:
    return {k: b.render(v) for k, v in K.SPEECH.items()}


def _texts():
    """(onde, slide, texto) de todas as fontes editoriais visíveis ou faladas."""
    out = []
    for k, v in K.SPEECH.items():
        out.append((f"SPEECH.{k}", k, v))
    def walk(where, sid, obj):
        if isinstance(obj, dict):
            for v in obj.values():
                walk(where, sid, v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                walk(where, sid, v)
        elif isinstance(obj, str) and " " in obj:  # IDs (value_id/claim) não têm espaço; só texto visível é varrido
            out.append((where, sid, obj))
    for pid, scr in K.SCREEN.items():
        walk(f"SCREEN.{pid}", pid, scr)
    for p in K.PAGES:
        out.append((f"PAGES.{p['id']}", p["id"], " ".join((p["kicker"], p["title"], p["subtitle"]))))
    for q, a in K.QUESTIONS:
        out.append(("QUESTIONS", "QA", q + " " + a))
    out.append(("GUIDE", "GUIDE", K.GUIDE))
    return out


def lint_literals() -> list[dict]:
    """Números digitados fora de tokens nas fontes editoriais (exceto datas/regras permitidas)."""
    issues = []
    for where, _, text in _texts():
        if where == "GUIDE":
            continue
        clean = ALLOWED.sub("", TOKEN.sub("", text))
        for m in re.finditer(r"\d+(?:[.,]\d+)?\s?%?", clean):
            issues.append({"where": where, "literal": m.group(0).strip(), "context": clean[max(0, m.start() - 30):m.end() + 20]})
    return issues


def lint_style() -> list[dict]:
    """Marcas que as cartas não usam e citação do modelo depois da introdução."""
    issues = []
    for where, sid, text in _texts():
        for m in STYLE.finditer(text):
            issues.append({"where": where, "rule": "estilo das cartas", "match": m.group(0)})
        if sid not in INTRO and sid != "GUIDE":
            for m in MODEL.finditer(text):
                issues.append({"where": where, "rule": "modelo citado depois do slide 2", "match": m.group(0)})
    return issues


def _words(t: str) -> int:
    return len(re.findall(r"\b[\wÀ-ÿ$.,%]+\b", t))


def _clock(s: int) -> str:
    return f"{s // 60}:{s % 60:02d}"


def build(b: Bundle, model: dict, out: Path) -> dict:
    sp = speech(b)
    pages = {p["block"]: p for p in model["pages"]}
    lines = ["# Script da apresentação", "",
             f"Falas exatas dos 12 slides, geradas do pacote {model['bundle_id']} (proposta do agente; decisão do grupo H09 pendente). "
             "Tempos são orçamento a 140 palavras por minuto; só o ensaio mede a duração real. As fontes no rodapé dos slides não são fala.", ""]
    total_w = total_s = cursor = 0
    blocks = {}
    for n, blk in enumerate(BLOCKS, 1):
        p, sec, w = pages[blk], K.BLOCK_SECONDS[blk], _words(sp[blk])
        total_w, total_s = total_w + w, total_s + sec
        lines += [f"## Slide {n} · {p['title']}", "", f"**{K.BLOCK_VOICE[blk]}** · {_clock(cursor)} a {_clock(cursor + sec)}", "", sp[blk], "",
                  f"*{w} palavras; orçamento de {sec} s (cerca de {round(w / WPM * 60)} s a 140 palavras por minuto).*", ""]
        blocks[blk] = {"slide": n, "speaker": K.BLOCK_VOICE[blk], "seconds": sec, "words": w}
        cursor += sec
    lines += [f"**Total:** {total_w} palavras; orçamento de {total_s} s ({_clock(total_s)}); limite do desafio, 10:00.", ""]
    write_text(out / "script_apresentacao.md", "\n".join(lines))
    counts = {PROFILE: {"total_words": total_w, "planned_seconds": total_s, "estimated_seconds_at_140wpm": round(total_w / WPM * 60),
                        "blocks": {k: v["words"] for k, v in blocks.items()}}}
    for person in PEOPLE:
        mine = [(n, blk) for n, blk in enumerate(BLOCKS, 1) if K.BLOCK_VOICE[blk] == person]
        tp = [f"# Teleprompter · {person}", "", "Só as suas falas, na ordem da apresentação.", ""]
        for n, blk in mine:
            tp += [f"## Slide {n} · {pages[blk]['title']}", "", sp[blk], ""]
        write_text(out / "teleprompter" / f"{person.lower()}.md", "\n".join(tp))
    qa = ["# Perguntas prováveis da banca", "", f"Respostas curtas geradas do pacote {model['bundle_id']}; são proposta do agente até o grupo assumir (H09).", ""]
    for k, (q, a) in enumerate(K.QUESTIONS, 1):
        qa += [f"## {k}. {q}", "", b.render(a), ""]
    write_text(out / "perguntas_banca.md", "\n".join(qa))
    write_text(out / "guia_gravacao.md", K.GUIDE)
    nar = ["# Roteiro narrativo", "", "Sequência de argumentos (slots do contrato 1.0) com as afirmações do pacote; cada uma tem fonte e limitação em claims.csv.", ""]
    for slot, ids in b.slots.items():
        nar += [f"## {slot}", ""] + [f"- {b.claim_text(cid)} *({cid})*" for cid in ids] + [""]
    write_text(out / "roteiro_narrativo.md", "\n".join(nar))
    lint, style = lint_literals(), lint_style()
    write_json(out / "script_word_counts.json", {"bundle_id": model["bundle_id"], "wpm": WPM, "profiles": counts, "blocks": blocks,
                                                  "literal_numbers_outside_tokens": lint, "style_issues": style,
                                                  "note": "Contagem estima plausibilidade; não substitui ensaio real (H10)."})
    return {"counts": counts, "lint": lint, "style": style, "speech": sp, "blocks": blocks}


def segments() -> list[dict]:
    """Manifesto de gravação do deck12: um clipe por slide, na voz de quem apresenta o slide."""
    return [{"block": blk, "speaker": K.BLOCK_VOICE[blk], "slide": n, "path": f"data/raw/gravacao/{blk}.mp4"}
            for n, blk in enumerate(BLOCKS, 1)]
