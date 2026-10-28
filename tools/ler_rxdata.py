"""Leitura de dados Marshal do RPG Maker XP, sem executar Ruby ou scripts do jogo."""
import struct
import zlib
from pathlib import Path


class Leitor:
    def __init__(self, dados):
        self.dados = dados
        self.pos = 0
        self.simbolos = []
        self.objetos = []

    def bytes(self, n):
        if n < 0 or self.pos+n > len(self.dados):
            raise ValueError('Arquivo truncado')
        b = self.dados[self.pos:self.pos+n]
        self.pos += n
        return b

    def inteiro(self):
        n = struct.unpack('b', self.bytes(1))[0]
        if n == 0:
            return 0
        if n > 4:
            return n-5
        if n < -4:
            return n+5
        b = self.bytes(abs(n))
        return int.from_bytes(b, 'little') if n > 0 else int.from_bytes(b, 'little')-(1 << (8*abs(n)))

    def registrar(self, v):
        self.objetos.append(v)
        return v

    def valor(self):
        t = self.bytes(1)
        if t == b'0': return None
        if t == b'T': return True
        if t == b'F': return False
        if t == b'i': return self.inteiro()
        if t == b':':
            s = self.bytes(self.inteiro()).decode('utf-8', errors='replace')
            self.simbolos.append(s)
            return s
        if t == b';': return self.simbolos[self.inteiro()]
        if t == b'@': return self.objetos[self.inteiro()]
        if t == b'"': return self.registrar(self.bytes(self.inteiro()))
        if t == b'I':
            v = self.valor()
            for _ in range(self.inteiro()): self.valor(); self.valor()
            return v
        if t == b'[':
            a = self.registrar([])
            for _ in range(self.inteiro()): a.append(self.valor())
            return a
        if t in (b'{', b'}'):
            d = self.registrar({})
            for _ in range(self.inteiro()):
                k = self.valor(); d[k] = self.valor()
            if t == b'}': d['__padrao'] = self.valor()
            return d
        if t == b'o':
            nome = self.valor()
            d = self.registrar({'__classe': nome})
            for _ in range(self.inteiro()):
                k = self.valor(); d[k.removeprefix('@')] = self.valor()
            return d
        if t == b'u':
            nome = self.valor(); b = self.bytes(self.inteiro())
            d = self.registrar({'__classe': nome, '__dados': b})
            if nome == 'Table':
                dim, x, y, z, total = struct.unpack_from('<5i', b)
                if total < 0 or len(b) != 20+total*2: raise ValueError('Table inválida')
                d.update(dim=dim, x=x, y=y, z=z, valores=list(struct.unpack_from('<'+str(total)+'h', b, 20)))
            return d
        if t == b'f': return self.registrar(float(self.bytes(self.inteiro())))
        raise ValueError(f'Tipo Marshal não suportado: {t!r}, posição {self.pos-1}')

    def ler(self):
        if self.bytes(2) != b'\x04\x08': raise ValueError('Formato Marshal diferente de 4.8')
        v = self.valor()
        if self.pos != len(self.dados): raise ValueError('Bytes restantes após leitura')
        return v


def ler(caminho):
    return Leitor(Path(caminho).read_bytes()).ler()


def texto(v):
    if isinstance(v, bytes): return v.decode('utf-8', errors='replace')
    if isinstance(v, list): return [texto(i) for i in v]
    if isinstance(v, dict): return {str(texto(k)): texto(a) for k, a in v.items() if k != '__dados'}
    return v


if __name__ == '__main__':
    import json
    raiz = Path(__file__).resolve().parents[1]
    dados = raiz/'originais/fire-ash-3.7/Data'
    scripts = ler(dados/'Scripts.rxdata')
    nomes = []
    for s in scripts:
        if not s: continue
        codigo = zlib.decompress(s[2]).decode('utf-8', errors='replace')
        nomes.append({'nome': texto(s[1]), 'bytes': len(codigo.encode()), 'linhas': len(codigo.splitlines())})
    mapas = ler(dados/'MapInfos.rxdata')
    resumo = {'scripts': nomes, 'mapas': texto(mapas), 'sistema': texto(ler(dados/'System.rxdata'))}
    (raiz/'docs/estrutura.json').write_text(json.dumps(resumo, ensure_ascii=False, indent=2))
    print('Scripts:', len(nomes), 'Mapas:', len(mapas), 'Linhas Ruby:', sum(s['linhas'] for s in nomes))
    print('Partida:', {k:v for k,v in resumo['sistema'].items() if 'start' in k})
