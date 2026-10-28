"""Verifica o pacote publicado sem precisar da cópia completa do jogo original."""
from pathlib import Path
import json
import struct

raiz = Path(__file__).resolve().parents[1]/'web'
arquivos = {'index.html', 'app.js', 'creditos.txt', 'data/autotiles.json'}
for id in [33, 5, 3]:
    nome = f'data/mapa-{id}.json'
    arquivos.add(nome)
    m = json.loads((raiz/nome).read_text())
    assert len(m['camadas']) == m['largura']*m['altura']*3
    nomes = [*m['assets']['tileset'].values(), *m['assets']['autotiles'], *[e['grafico'] for e in m['eventosVisuais']], 'Characters/trchar000_1.png']
    for n in nomes:
        if n: arquivos.add('assets/'+n)
for n in sorted(arquivos):
    p = (raiz/n).resolve()
    assert p.is_relative_to(raiz.resolve()) and p.is_file(), 'Arquivo ausente ou fora do pacote: '+n
    if p.suffix == '.png':
        b = p.read_bytes()
        assert b[:8] == b'\x89PNG\r\n\x1a\n'
        w, h = struct.unpack('>II', b[16:24])
        assert 0 < w <= 1024 and 0 < h <= 1024, 'Imagem grande demais: '+n
print(f'OK: {len(arquivos)} arquivos referenciados, mapas e imagens pequenas presentes.')
