"""Confere dimensões e pixels das peças importadas, sem comparar só nomes."""
from pathlib import Path
import json
from PIL import Image
from ler_rxdata import ler

raiz = Path(__file__).resolve().parents[1]
web = raiz/'web'
original = raiz/'originais/fire-ash-3.7'
padroes = json.loads((web/'data/autotiles.json').read_text())
assert len(padroes) == 48 and all(len(p) == 4 for p in padroes)
assert all(1 <= q <= 48 for p in padroes for q in p)
for id in [33, 5, 3]:
    j = json.loads((web/f'data/mapa-{id}.json').read_text())
    m = ler(original/f'Data/Map{id:03d}.rxdata')
    assert j['camadas'] == m['data']['valores'], 'Algum bloco foi modificado'
    assert len(j['camadas']) == j['largura']*j['altura']*3
    assert len(j['eventosOriginais']) == len(m['events']), 'Evento perdido na exportação'
    for pagina, nome in j['assets']['tileset'].items():
        recorte = Image.open(web/'assets'/nome).convert('RGBA')
        fonte = original/'Graphics/Tilesets'/(Path(nome).stem.rsplit('-', 1)[0]+'.png')
        im = Image.open(fonte).convert('RGBA')
        y = int(pagina)*512
        assert recorte.tobytes() == im.crop((0,y,256,min(im.height,y+512))).tobytes()
        assert recorte.width <= 512 and recorte.height <= 512
    for evento in j['eventosVisuais']:
        nome = evento['grafico']
        assert (web/'assets'/nome).read_bytes() == (original/'Graphics'/nome).read_bytes()
    print('OK:', id, 'blocos, eventos originais, sprites e páginas de atlas idênticos')
