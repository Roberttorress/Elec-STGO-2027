"""Calles de Santiago desde VIALIDAD (INE) -> red caminable por sección. Sustituye el export.osm."""
import json, math, collections
import shpread as S
OUT = '../out/'
D = json.load(open(OUT + 'dl02_data.json')); rings = D['sec_rings_wgs']
f, recs = S.read_dbf('../shp/VIALIDAD.DBF'); shp = S.read_shp('../shp/VIALIDAD.shp')
mf, mr = S.read_dbf('../shp/MUNICIPIO.DBF'); ms = S.read_shp('../shp/MUNICIPIO.shp')
mun = [s for r, s in zip(mr, ms) if r['MUNICIPIO'] == 49][0]
xs = [p[0] for rg in mun for p in rg]; ys = [p[1] for rg in mun for p in rg]; BB = (min(xs), min(ys), max(xs), max(ys))
def pip(x, y, ring):
    ins = False
    for i in range(len(ring)):
        x1, y1 = ring[i]; x2, y2 = ring[i - 1]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): ins = not ins
    return ins
secu = {}
for s, rr in rings.items():
    # back to UTM is not available; work in WGS for section test
    secu[int(s)] = rr
secbb = {s: (min(p[0] for rg in r for p in rg), min(p[1] for rg in r for p in rg), max(p[0] for rg in r for p in rg), max(p[1] for rg in r for p in rg)) for s, r in secu.items()}
def sec_of(lo, la):
    for s, b in secbb.items():
        if b[0] <= lo <= b[2] and b[1] <= la <= b[3]:
            ins = False
            for rg in secu[s]: ins ^= pip(lo, la, rg)
            if ins: return s
nodes = {}; key2id = {}; edges = []
def nid(x, y):
    k = (round(x), round(y))
    if k not in key2id:
        key2id[k] = len(key2id) + 1; lo, la = S.utm14n_to_wgs84(x, y); nodes[key2id[k]] = (round(lo, 6), round(la, 6))
    return key2id[k]
for r, sh in zip(recs, shp):
    if not sh: continue
    for part in sh:
        if not any(BB[0] - 50 <= x <= BB[2] + 50 and BB[1] - 50 <= y <= BB[3] + 50 for x, y in part): continue
        ids = [nid(x, y) for x, y in part]
        for a, b in zip(ids, ids[1:]):
            if a == b: continue
            pa, pb = nodes[a], nodes[b]; s = sec_of((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2)
            if s is None: continue
            edges.append((a, b, s, r['NOMBRE'] or '', r['CATEGORIA'], r['TIPO']))
used = {n for e in edges for n in e[:2]}
K = 111320 * math.cos(math.radians(25.39))
def L(a, b): pa, pb = nodes[a], nodes[b]; return math.hypot((pa[0] - pb[0]) * K, (pa[1] - pb[1]) * 110574)
km = collections.defaultdict(lambda: collections.Counter())
for a, b, s, nm, c, t in edges: km[s][(c, t)] += L(a, b) / 1000
for s in sorted(km): print(s, round(sum(km[s].values()), 1), {k: round(v, 1) for k, v in km[s].most_common(5)})
json.dump({'nodes': {i: nodes[i] for i in used}, 'edges': edges}, open(OUT + 'stgo_red.json', 'w'), ensure_ascii=False)
print('nodos', len(used), 'tramos', len(edges))
