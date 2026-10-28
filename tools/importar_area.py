"""Exporta uma área real sem redesenhar mapas ou executar seus eventos Ruby."""
import ast
import json
import shutil
import zlib
from pathlib import Path
from PIL import Image
from ler_rxdata import ler, texto

raiz = Path(__file__).resolve().parents[1]
original = raiz/'originais/fire-ash-3.7'
web = raiz/'web'
(web/'data').mkdir(parents=True, exist_ok=True)
(web/'assets').mkdir(parents=True, exist_ok=True)
mapas = ler(original/'Data/MapInfos.rxdata')
tilesets = ler(original/'Data/Tilesets.rxdata')
for s in ler(original/'Data/Scripts.rxdata'):
    if s and texto(s[1]) == 'TileDrawingHelper':
        fonte = zlib.decompress(s[2]).decode('utf-8')
        trecho = fonte.split('Autotiles =', 1)[1].lstrip()
        profundidade = 0
        for i, c in enumerate(trecho):
            if c == '[': profundidade += 1
            if c == ']': profundidade -= 1
            if profundidade == 0:
                padroes = ast.literal_eval(trecho[:i+1])
                break
        (web/'data/autotiles.json').write_text(json.dumps([p for linha in padroes for p in linha]))
        break


def imagem(pasta, nome):
    if not nome: return None
    orig = original/'Graphics'/pasta/(nome if Path(nome).suffix else nome+'.png')
    if not orig.exists(): raise FileNotFoundError(orig)
    rel = Path(pasta)/orig.name
    (web/'assets'/rel.parent).mkdir(parents=True, exist_ok=True)
    shutil.copy2(orig, web/'assets'/rel)
    return str(rel)


def atlas_por_paginas(nome, ids):
    # O atlas exterior original tem mais de 20 mil pixels de altura. Fatias
    # pequenas preservam todos os pixels e evitam limites de imagem no celular.
    orig = original/'Graphics/Tilesets'/(nome+'.png')
    im = Image.open(orig)
    paginas = sorted({(i-384)//128 for i in ids if i >= 384})
    saida = {}
    for p in paginas:
        rel = Path('Tilesets')/(nome+'-'+str(p)+'.png')
        (web/'assets'/rel.parent).mkdir(parents=True, exist_ok=True)
        im.crop((0,p*512,256,min(im.height,(p+1)*512))).save(web/'assets'/rel)
        saida[p] = str(rel)
    return saida


for id in [33, 5, 3]:
    m = texto(ler(original/f'Data/Map{id:03d}.rxdata'))
    ts = texto(tilesets[m['tileset_id']])
    assets = {'tileset': atlas_por_paginas(ts['tileset_name'],m['data']['valores']), 'autotiles': [imagem('Autotiles', n) for n in ts['autotile_names']]}
    eventos = []
    for e in m['events'].values():
        # Estado inicial apenas. Não confundir essa seleção com execução da história.
        paginas = [p for p in e['pages'] if not any(p['condition'].get(k) for k in ['switch1_valid', 'switch2_valid', 'variable_valid', 'self_switch_valid'])]
        if not paginas: continue
        p = paginas[-1]
        g = p['graphic']
        if g['character_name'] and g['character_name'].lower() != 'invisible':
            eventos.append({'id': e['id'], 'nome': e['name'], 'x': e['x'], 'y': e['y'], 'grafico': imagem('Characters', g['character_name']), 'direcao': g['direction'], 'quadro': g['pattern'], 'opacidade': g['opacity']})
    doc = {'id': id, 'nome': texto(mapas[id]['name']), 'largura': m['width'], 'altura': m['height'], 'camadas': m['data']['valores'], 'prioridades': ts['priorities']['valores'], 'passagens': ts['passages']['valores'], 'terrenos': ts['terrain_tags']['valores'], 'eventosVisuais': eventos, 'eventosOriginais': m['events'], 'assets': assets}
    (web/f'data/mapa-{id}.json').write_text(json.dumps(doc, ensure_ascii=False, separators=(',', ':')))
    print(id, doc['nome'], doc['largura'], doc['altura'], 'eventos originais:', len(m['events']))
imagem('Characters', 'trchar000_1')
(web/'data/catalogo.json').write_text(json.dumps([{'id': i, 'nome': texto(v['name'])} for i, v in mapas.items()], ensure_ascii=False))
