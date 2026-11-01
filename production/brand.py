"""Fontes locais e símbolo extraído do manual de marca; nenhuma dependência de rede no HTML."""
from __future__ import annotations

import base64
import re

from .common import REPO, read_json, sha256_file


def embedded_fonts() -> str:
    root = REPO / 'presentation_web/fonts'
    manifest = read_json(root / 'manifest.json')
    rules = []
    for item in manifest['files']:
        path = root / item['file']
        if sha256_file(path) != item['sha256']:
            raise ValueError('Fonte local alterada: '+str(path))
        data = base64.b64encode(path.read_bytes()).decode('ascii')
        rules.append(f"@font-face{{font-family:'{item['family']}';font-style:normal;font-weight:{item['weight']};font-display:block;src:url(data:font/ttf;base64,{data}) format('truetype');}}")
    if len(rules) != 3:
        raise ValueError('O design exige Space Grotesk, Inter e JetBrains Mono')
    return '\n'.join(rules)


def symbol() -> str:
    source = (REPO / 'resources/design_system/marcadev.html').read_text(encoding='utf-8')
    match = re.search(r'<symbol id="bolt-lk" viewBox="([^"]+)">(.*?)</symbol>', source, flags=re.S | re.I)
    if not match:
        raise ValueError('Símbolo do manual não localizado')
    return f'<svg class="blt" viewBox="{match[1]}" aria-hidden="true">{match[2]}</svg>'


def reference() -> dict:
    path = REPO / 'resources/design_system/marcadev.html'
    return {'source': path.relative_to(REPO).as_posix(), 'source_sha256': sha256_file(path), 'adapted_name': 'asset.dev',
            'fonts': read_json(REPO/'presentation_web/fonts/manifest.json'),
            'palette': {'gold':'#F5D741','black':'#0A0A0A','graphite':'#2E2F31','cyan':'#57C7C0','violet':'#9A7CF5',
                        'positive':'#4FC58B','negative':'#E5564E'}, 'signature_angle':25,
            'deck12': 'Doze slides planos em HTML; PDF impresso do HTML e PPTX com cada página renderizada em alta resolução e o script nas notas.'}
