#!/usr/bin/env python3
"""
gerar_apresentacao.py — Quintal Barigui · Apresentação a Investidores
======================================================================
Combina duas etapas em um único script:
  1. Substitui os placeholders pelas imagens reais
  2. Aplica escala de legibilidade nas fontes

USO:
  python gerar_apresentacao.py

REQUISITOS:
  - Este script na mesma pasta que o HTML e as imagens
  - Python 3.8+  (sem dependências externas)

ARQUIVOS DE ENTRADA:
  quintal-barigui-investidores.html   ← HTML base (baixado do Claude)
  capa.png, aerea.png, fachada.png... ← imagens (ver mapeamento abaixo)

ARQUIVO DE SAÍDA:
  quintal-barigui-investidores-FINAL.html
"""

import base64, os, re

# ─── Pasta do script (independe de onde o terminal está) ──────────────────
PASTA = os.path.dirname(os.path.abspath(__file__))

# ─── Arquivos ─────────────────────────────────────────────────────────────
INPUT_HTML  = os.path.join(PASTA, 'index.html')
OUTPUT_HTML = os.path.join(PASTA, 'quintal-barigui-investidores-FINAL.html')

# ─── Mapeamento de imagens ─────────────────────────────────────────────────
# Ajuste os nomes dos arquivos conforme o que estiver na sua pasta.
# Se um arquivo não existir, o placeholder original é mantido.
IMAGE_MAP = [
    # (como localizar no HTML,  valor do atributo,        nome do arquivo)
    ('alt',   'Quintal Barigui',       'capa.png'),
    ('alt',   'Vista aérea Mêrces',    'aerea.png'),
    ('alt',   'Fachada do condomínio', 'fachada.png'),
    ('alt',   'Estilo de vida',        'publico.png.png'),  # dupla extensão
    ('class', 'cover-logo',            'logo-skandi.svg'),
    ('alt',   'Planta do subsolo',     'planta-subsolo.png'),
    ('alt',   'Planta Tipo 1',         'planta-tipo1.png'),
    ('alt',   'Planta Tipo 2',         'planta-tipo2.png'),
    ('alt',   'Planta Tipo 3',         'planta-tipo3.png'),
    ('alt',   'Interior Tipo 1',       'render-tipo1-a.jpg'),
    ('alt',   'Interior Tipo 2',       'render-tipo2-a.jpg'),
    ('alt',   'Interior Tipo 3',       'render-tipo3-a.jpg'),
]

# Renders secundários (2ª ocorrência de cada tipo)
SECOND_RENDER = [
    ('render-tipo1-B.jpg', 'Interior Tipo 1'),
    ('render-tipo2-b.jpg', 'Interior Tipo 2'),
    ('render-tipo3-b.jpg', 'Interior Tipo 3'),
]

# ─── Escala de legibilidade de fontes ─────────────────────────────────────
# Apenas aumenta — nunca diminui tamanhos.
FONT_SCALE = {
    8.5: 11.0,
    9.0: 11.0,
    9.5: 11.0,
    10.0: 12.0,
    10.5: 13.0,
    11.0: 13.0,
    11.5: 13.5,
    12.0: 14.0,
    12.5: 14.0,
    13.0: 15.0,
    13.5: 15.0,
    # 14px+ → sem alteração
}

# ══════════════════════════════════════════════════════════════════════════

def to_data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    mime = {
        '.png':  'image/png',
        '.jpg':  'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp',
        '.svg':  'image/svg+xml',
        '.gif':  'image/gif',
    }.get(ext, 'image/png')
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()


def replace_img_src(html, attr, value, new_src, occurrence=1):
    """Substitui o src do N-ésimo <img> que tenha attr="value"."""
    count = [0]

    def make_replacer(g1, g2):
        def r(m):
            count[0] += 1
            if count[0] == occurrence:
                return m.group(g1) + new_src + m.group(g2)
            return m.group(0)
        return r

    # Caso 1: atributo buscado vem antes de src
    p1 = rf'(<img\s(?:[^>]*?\s)?{attr}="{re.escape(value)}"[^>]*?src=")[^"]*?(")'
    new = re.sub(p1, make_replacer(1, 2), html, flags=re.DOTALL)
    if new != html:
        return new

    # Caso 2: src vem antes do atributo buscado
    count[0] = 0
    p2 = rf'(<img\s(?:[^>]*?\s)?src=")[^"]*?("[^>]*?\s{attr}="{re.escape(value)}"[^>]*?>)'
    return re.sub(p2, make_replacer(1, 2), html, flags=re.DOTALL)


def embed_images(html):
    """Etapa 1 — substitui placeholders pelas imagens reais."""
    print('\n[1/2] Incorporando imagens...')
    ok, skip = 0, []

    for attr, value, filename in IMAGE_MAP:
        full = os.path.join(PASTA, filename)
        if not os.path.exists(full):
            skip.append(filename)
            continue
        kb = os.path.getsize(full) // 1024
        new = replace_img_src(html, attr, value, to_data_uri(full))
        if new != html:
            html = new
            ok += 1
            print(f'    OK  {filename}  ({kb} KB)')
        else:
            skip.append(f'{filename} (não encontrado no HTML)')

    for filename, alt_val in SECOND_RENDER:
        full = os.path.join(PASTA, filename)
        if not os.path.exists(full):
            continue
        kb = os.path.getsize(full) // 1024
        new = replace_img_src(html, 'alt', alt_val, to_data_uri(full), occurrence=2)
        if new != html:
            html = new
            ok += 1
            print(f'    OK  {filename}  ({kb} KB)  [2ª ocorrência]')

    print(f'    → {ok} imagens incorporadas', end='')
    if skip:
        print(f'  |  {len(skip)} não encontradas: {", ".join(skip)}')
    else:
        print()
    return html


def scale_fonts(html):
    """Etapa 2 — aumenta fontes pequenas para melhor legibilidade."""
    print('\n[2/2] Ajustando escala tipográfica...')

    def replacer(m):
        val = float(m.group(1))
        new = FONT_SCALE.get(val, val)
        fmt = f'{new:.0f}' if new == int(new) else f'{new}'
        return f'font-size:{fmt}px'

    before = len(re.findall(r'font-size\s*:\s*([\d.]+)px', html))
    html_new = re.sub(r'font-size\s*:\s*([\d.]+)px', replacer, html)
    changed = sum(
        1 for old, new in FONT_SCALE.items()
        if old != new and f'font-size:{old}px' in html
    )
    print(f'    → {before} declarações processadas  |  escala aplicada a tamanhos < 14px')
    return html_new


def main():
    print('=' * 60)
    print('  Quintal Barigui — Gerador de Apresentação')
    print('=' * 60)
    print(f'  Pasta: {PASTA}')

    if not os.path.exists(INPUT_HTML):
        print(f'\n  ERRO: arquivo não encontrado:\n  {INPUT_HTML}')
        input('\nPressione Enter para fechar...')
        return

    print(f'\n  Lendo: {os.path.basename(INPUT_HTML)}  '
          f'({os.path.getsize(INPUT_HTML)//1024} KB)')

    with open(INPUT_HTML, 'r', encoding='utf-8') as f:
        html = f.read()

    html = embed_images(html)
    html = scale_fonts(html)

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)

    kb = os.path.getsize(OUTPUT_HTML) // 1024
    print(f'\n{"=" * 60}')
    print(f'  CONCLUÍDO!')
    print(f'  Arquivo gerado: {os.path.basename(OUTPUT_HTML)}  ({kb} KB)')
    print(f'  Abra no navegador para visualizar.')
    print('=' * 60)
    input('\nPressione Enter para fechar...')


if __name__ == '__main__':
    main()
