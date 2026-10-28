"""Inventário dos eventos originais: mede o que falta portar, sem executar nenhum."""
from collections import Counter
from pathlib import Path
import json
import re
from ler_rxdata import ler, texto

raiz = Path(__file__).resolve().parents[1]
dados = raiz/'originais/fire-ash-3.7/Data'
comandos = Counter()
chamadas = Counter()
eventos = paginas = mapas = 0
falhas = []
for p in sorted(dados.glob('Map[0-9][0-9][0-9].rxdata')):
    try:
        m = ler(p)
        mapas += 1
        eventos += len(m['events'])
        for e in m['events'].values():
            paginas += len(e['pages'])
            for pg in e['pages']:
                for c in pg['list']:
                    comandos[c['code']] += 1
                    if c['code'] in [355, 655, 111]:
                        for s in c['parameters']:
                            if isinstance(s, bytes):
                                for nome in re.findall(r'\b(?:pb[A-Z]\w+|TrainerBattle\.[a-zA-Z]+|WildBattle\.[a-zA-Z]+)', texto(s)):
                                    chamadas[nome] += 1
    except Exception as e:
        falhas.append({'arquivo': p.name, 'erro': str(e)})
doc = {'mapasLidos': mapas, 'eventos': eventos, 'paginasDeEvento': paginas, 'comandos': dict(comandos.most_common()), 'chamadasRuby': dict(chamadas.most_common()), 'falhasLeitura': falhas, 'eventosExecutadosNoNavegador': False, 'combateIntegrado': False}
(raiz/'docs/compatibilidade.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2))
print(json.dumps({k:v for k,v in doc.items() if k not in ['comandos','chamadasRuby']}, indent=2))
if falhas: raise SystemExit(1)
